import os
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)

VIRALITY_ANALYSIS_SYSTEM_PROMPT = """Jsi špičkový expert na virální krátká videa pro YouTube Shorts, TikTok a Instagram Reels.
Tvým úkolem je analyzovat transkript videa s časovými značkami a identifikovat NEJVÍCE VIRÁLNÍ segmenty s virálním skóre 8.0 až 10.0.

Kritéria pro virální skóre 8+:
- Silný hook během prvních 3 sekund (nečekaná hláška, kontroverze, šokující fakt, silná emoce, vysoké napětí).
- Rychlá gradace děje, ucelená myšlenka s pointou.
- Žádná hluchá místa ani nudný úvod.
- Ideální délka jednoho Shorts klipu je mezi 25 až 55 sekundami.

Podle zadaného režimu (mode):
1. 'client':
   - Zaměř se na čistý, reprezentativní obsah se zachováním autorského tónu mluvčího.
   - Připrav atraktivní název, popisek a hashtagy.
2. 'aggressive_monetization':
   - Cílem je bypass pravidel o 'Reused content' a vytvoření plnohodnotného Fair Use rozboru / reakce.
   - Musíš vygenerovat komentátorský text (commentary_script) pro AI vypravěče rozdělený do 3 částí:
     a) 'intro_hook': Úvodní hook (např. "Tohle je důvod, proč [jméno/téma] naprosto šokoval internet...")
     b) 'middle_commentary': Kontextové vysvětlení situace a pointy během videa.
     c) 'outro_recap': Rekapitulace a silná otázka do komentářů / výzva k odběru.

Vrať VÝHRADNĚ platný JSON formát odpovídající následující struktuře:
{
  "clips": [
    {
      "clip_id": "clip_1",
      "start_time": 12.5,
      "end_time": 48.0,
      "duration": 35.5,
      "virality_score": 9.4,
      "virality_reason": "Vysvětlení, proč má klip virální potenciál",
      "hook_text": "První slova klipu pro rychlé upoutání",
      "title": "NEUVĚŘITELNÝ ZVRAT! 😱 Tohle nikdo nečekal",
      "description": "Exkluzivní moment ze streamu. Zanechte odběr pro další denní shorts!",
      "hashtags": ["#shorts", "#viral", "#podcast", "#fyp", "#trending"],
      "commentary_script": {
        "intro_hook": "Tohle je přesně ten důvod, proč je tato scéna hitem sociálních sítí.",
        "middle_commentary": "Všimněte si reakce v této chvíli, situace se zcela vymkla kontrole.",
        "outro_recap": "Co si o této reakci myslíte vy? Napište nám svůj názor do komentářů."
      }
    }
  ]
}
"""

class ViralAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for AI viral analysis.")
        self.client = OpenAI(api_key=self.api_key)

    def analyze_transcript(
        self,
        transcript_data: Dict[str, Any],
        mode: str = "client",
        theme_focus: str = "",
        min_score: float = 8.0,
        max_clips: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Analyze transcript with GPT-4o to identify segments with virality score >= 8.
        """
        logger.info(f"Analyzing transcript for virality (Mode: {mode}, Theme: {theme_focus})")

        # Format transcript segments for prompt
        formatted_segments = []
        for s in transcript_data.get("segments", []):
            formatted_segments.append(
                f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}"
            )
        transcript_text = "\n".join(formatted_segments)

        user_prompt = f"""Režim zpracování: {mode}
Uživatelské zaměření / Téma: {theme_focus or 'Hledej nejzajímavější a nejvirálnější moment'}
Požadované minimální virální skóre: {min_score}/10
Maximální počet klipů: {max_clips}

Zde je kompletní transkript videa s časovými značkami:
---
{transcript_text[:35000]}
---

Vyber maximálně {max_clips} nejlepších úseků o délce 25 až 58 sekund se skóre virality alespoň {min_score}/10.
Vrať pouze JSON.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": VIRALITY_ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        clips = parsed.get("clips", [])

        # Filter and validate clips
        qualified_clips = []
        for c in clips:
            score = float(c.get("virality_score", 0))
            if score >= min_score:
                # Associate word timestamps for subtitle generation
                start = float(c.get("start_time", 0))
                end = float(c.get("end_time", 0))
                c["words"] = [
                    w for w in transcript_data.get("words", [])
                    if start <= w["start"] <= end
                ]
                qualified_clips.append(c)

        logger.info(f"Analysis complete: {len(qualified_clips)} clips qualified with score >= {min_score}")
        return qualified_clips[:max_clips]

