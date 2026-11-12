import cv2
import numpy as np
import logging
from typing import Tuple, List, Dict, Any

logger = logging.getLogger(__name__)

class SmartFaceReframer:
    def __init__(self):
        # Load OpenCV Haar cascade for face detection (fast, lightweight, runs without heavy dependencies on CPU)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze_crop_coordinates(self, video_path: str, target_aspect: float = 9/16, sample_fps: int = 4) -> Dict[str, Any]:
        """
        Samples video frames at `sample_fps` to detect faces and compute smooth crop boundaries.
        Returns:
            Dict containing crop parameters (w, h, smoothed_x_offset, etc.)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.warning(f"Could not open video {video_path} for face analysis. Defaulting to center crop.")
            return {"crop_x": None, "center_crop": True}

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_step = max(1, int(fps / sample_fps))
        detected_centers_x = []

        crop_w = int(height * target_aspect)
        if crop_w > width:
            crop_w = width

        default_center_x = width // 2

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_step == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.15,
                    minNeighbors=5,
                    minSize=(60, 60)
                )

                if len(faces) > 0:
                    # Choose largest face (main speaker)
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    fx, fy, fw, fh = largest_face
                    center_x = fx + (fw // 2)
                    detected_centers_x.append(center_x)
                else:
                    # If not found in current frame, use previous or center
                    detected_centers_x.append(detected_centers_x[-1] if detected_centers_x else default_center_x)

            frame_idx += 1

        cap.release()

        if not detected_centers_x:
            detected_centers_x = [default_center_x]

        # Calculate smoothed average position (Exponential Moving Average / Window smoothing)
        window_size = 5
        smoothed = np.convolve(detected_centers_x, np.ones(window_size)/window_size, mode='valid')
        avg_x = int(np.mean(smoothed)) if len(smoothed) > 0 else int(np.mean(detected_centers_x))

        # Clamp crop_x so crop rectangle remains within [0, width - crop_w]
        crop_x = avg_x - (crop_w // 2)
        crop_x = max(0, min(crop_x, width - crop_w))

        logger.info(f"Smart Reframing computed: Video {width}x{height} -> Crop {crop_w}x{height} at X={crop_x}")
        return {
            "source_w": width,
            "source_h": height,
            "crop_w": crop_w,
            "crop_h": height,
            "crop_x": crop_x,
            "crop_y": 0,
            "center_crop": False
        }

    def get_ffmpeg_crop_filter(self, crop_info: Dict[str, Any], output_w: int = 1080, output_h: int = 1920) -> str:
        """
        Builds high quality FFmpeg filter chain: crop -> scale 1080x1920 -> setsar=1.
        """
        if crop_info.get("center_crop") or crop_info.get("crop_x") is None:
            # Fallback center crop
            return f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale={output_w}:{output_h},setsar=1"

        w = crop_info["crop_w"]
        h = crop_info["crop_h"]
        x = crop_info["crop_x"]
        y = crop_info["crop_y"]
        return f"crop={w}:{h}:{x}:{y},scale={output_w}:{output_h},setsar=1"

