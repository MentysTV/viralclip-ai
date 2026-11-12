# 🎬 ViralClip AI - Cloudová Továrna na YouTube Shorts & TikToky

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/MentysTV/viralclip-ai)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/MentysTV/viralclip-ai/tree/main/frontend&root-directory=frontend&env=NEXT_PUBLIC_API_URL)

Kompletní architektura a produkční kód pro cloudovou aplikaci (Next.js frontend + FastAPI backend v Dockeru), která plně automatizuje proces tvorby vertikálních videí (9:16) ze zadaného YouTube URL. Běží **čistě na cloudu bez nutnosti lokálního GPU a bez spouštění kódu na vlastním počítači**.

---

## 🚀 Klíčové Funkce & 2 Pracovní Režimy

Aplikace disponuje přepínačem mezi dvěma konkrétními pracovními režimy:

| Funkce / Režim | **REŽIM 1: Pro Klienty & Tvůrce** | **REŽIM 2: Agresivní Monetizace** |
| :--- | :--- | :--- |
| **Primární cíl** | Čistý zakázkový střih se souhlasem autora | Bypass filtru Reused Content & Content ID (Fair Use) |
| **Layout videa** | 9:16 Celá obrazovka (1080x1920) | Split-Screen (Nahoře video, dole dynamický B-roll) |
| **Sledování obličeje** | OpenCV / MediaPipe auto-reframe centrování | Smart crop do horní poloviny (1080x960) |
| **Vizuální úpravy** | Původní čistý obraz v maximální kvalitě | Barevné LUT tónování, dynamický mikro-zoom, hflip zrcadlení |
| **Rychlost videa/audia** | 1.00x (Standardní) | **1.02x** (Narušení digitálních audio/video otisků) |
| **Komentář & Audio** | Původní zvuk mluvčího (320kbps AAC) | **ElevenLabs AI hlas** (Hook + Shrnutí + Rekapitulace) |
| **Audio Ducking** | Žádné (100% původní hlas) | **Původní zvuk utlumen na ~18%**, AI hlas na 100% |
| **Titulky** | Karaoke styl s barevným zvýrazněním slov | Karaoke styl pro hlavní sdělení a AI komentář |
| **Branding / Prvky** | Vodoznak / sociální sítě klienta v rohu | Grafický dělící pruh a banner "EXKLUZIVNÍ ROZBOR / REAKCE" |
| **Exportní specifikace** | 1080x1920, 60fps, CRF 18 | 1080x1920, 60fps, CRF 19 |

---

## 🏛️ Architektura Systému

```
[ Uživatel v prohlížeči ]
        │
        ▼ (Zadání YouTube URL + Volba režimu + Instrukce)
[ Next.js Frontend (Vercel) ]
        │
        ▼ POST /api/jobs
[ FastAPI Cloud Worker (Docker na Railway / Render) ]
        │
        ├─► 1. yt-dlp: Extrakce komprimovaného mono audia (16kHz)
        │
        ├─► 2. OpenAI Whisper API: Transkripce s časovými značkami každého slova (word-level)
        │
        ├─► 3. OpenAI GPT-4o: Výběr virálních úseků se skóre 8+/10, tvorba titulků, hashtagů
        │       └─► (Pro Režim 2: Vygenerování 3fázového komentáře - Hook, Kontext, Rekapitulace)
        │
        ├─► 4. OpenCV Face Tracking: Detekce obličeje mluvčího & plynulé vyhlazené centrování
        │
        ├─► 5. ElevenLabs API: Vygenerování realistického hlasu pro komentář (pouze Režim 2)
        │
        ├─► 6. Subtitle Engine: Generování .ass karaoke titulků se zvýrazňováním aktivního slova
        │
        └─► 7. FFmpeg Engine:
                ├─► Režim 1: 9:16 Auto-reframe crop + Karaoke titulky + Branding vodoznak
                └─► Režim 2: Split-screen (Top video + B-roll) + Speed 1.02x + Ducking na 18% +
                             ElevenLabs voiceover + Anti-Content ID LUT + Reakční rámeček
        │
        ▼
[ Hotová videa v 1080x1920 60fps ke stažení na Dashboardu s Clickbait názvem a hashtagy ]
```

---

## 🛠️ Seznam Environmentálních Proměnných

### Backend (`backend/.env`):
```ini
# Port pro server (Railway / Render doplňují automaticky)
PORT=8000

# Povolené adresy frontendu pro CORS (nahraďte svou Vercel doménou)
ALLOWED_ORIGINS=http://localhost:3000,https://*.vercel.app

# OpenAI API klíč (Vyžadován pro Whisper transkripci a GPT-4o virální analýzu)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ElevenLabs API klíč (Vyžadován pro generování komentáře v Režimu 2)
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Výchozí ID hlasu na ElevenLabs (Adam = pNInz6obpgDQGcFmaJgB, Rachel = 21m00Tcm4TlvDq8ikWAM)
DEFAULT_ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB

# Cesty k adresářům (v Dockeru nastaveny automaticky)
TEMP_DIR=/app/temp
OUTPUTS_DIR=/app/outputs

# Minimální skóre virality pro zařazení do výběru (1-10)
MIN_VIRALITY_SCORE=8.0

# Maximální počet klipů na jedno zpracování
MAX_CLIPS_PER_VIDEO=3
```

### Frontend (`frontend/.env.local`):
```ini
# URL adresa nasazeného backendu
NEXT_PUBLIC_API_URL=https://viralclip-backend-production.up.railway.app
```

---

## ☁️ Návod na Nasazení do Cloudu na Jeden Klik

### KROK 1: Nasazení Backend Workeru (Railway nebo Render)

Backend je vybaven předpřipraveným `Dockerfile` s nainstalovaným FFmpeg, Pythonem 3.11, systémovými fonty pro vypalování titulků a knihovnami pro OpenCV.

#### Možnost A: Railway (Doporučeno - rychlý start)
1. Nahrajte složku projektu do svého Git repozitáře (např. GitHub).
2. Přihlaste se na [railway.app](https://railway.app) a klikněte na **"New Project"** -> **"Deploy from GitHub repo"**.
3. Jako **Root Directory** nastavte složku `/backend`.
4. Railway automaticky detekuje soubor `backend/Dockerfile` a `backend/railway.json`.
5. V sekci **Variables** přidejte:
   - `OPENAI_API_KEY` = váš klíč
   - `ELEVENLABS_API_KEY` = váš klíč
   - `ALLOWED_ORIGINS` = `*`
6. V sekci **Settings** -> **Networking** klikněte na **"Generate Domain"** (získáte URL např. `https://viralclip-backend-production.up.railway.app`).

#### Možnost B: Render.com
1. Na [render.com](https://render.com) zvolte **"New Web Service"** -> propojte svůj GitHub.
2. Zvolte **Environment:** `Docker`.
3. Nastavte **Dockerfile Path:** `./backend/Dockerfile`.
4. Vložte env proměnné `OPENAI_API_KEY` a `ELEVENLABS_API_KEY`.
5. Zvolte plán (Starter pro stabilní RAM na video rendering).

---

### KROK 2: Nasazení Frontendu (Vercel)

1. Přihlaste se na [vercel.com](https://vercel.com) a klikněte na **"Add New Project"**.
2. Vyberte svůj GitHub repozitář.
3. Jako **Root Directory** zvolte `/frontend`.
4. V sekci **Environment Variables** nastavte:
   - Název: `NEXT_PUBLIC_API_URL`
   - Hodnota: URL vašeho běžícího backendu z Kroku 1 (např. `https://viralclip-backend-production.up.railway.app`)
5. Klikněte na **"Deploy"**. Během 60 sekund máte hotový produkční dashboard!

---

## 🧩 Detaily Technických Modulů

### 1. Extrakce & Whisper Word-Level Timestamps (`transcriber.py`)
- Stahuje pouze vysoce komprimovaný 16kHz mono audio stream, což snižuje objem přenášených dat na minimum a zaručuje, že soubor nepřekročí 25MB limit OpenAI API.
- Volá `client.audio.transcriptions.create(..., timestamp_granularities=["word", "segment"])`.
- Každé jednotlivé slovo získává přesný počáteční a koncový čas v sekundách pro přesné karaoke titulkování.

### 2. Virality Scoring & Skriptování (`analyzer.py`)
- Využívá GPT-4o s vynuceným JSON schématem (`response_format={"type": "json_object"}`).
- Identifikuje úseky s virálním skóre 8.0+/10 na základě dynamiky konverzace, silného hooku v prvních 3 sekundách a ucelené pointy.
- V **Režimu 2** automaticky vygeneruje strukturovaný scénář:
  - `intro_hook`: Upoutávka s vysokým retention faktorem
  - `middle_commentary`: Shrnutí a kontextová pointa
  - `outro_recap`: Výzva k odběru / zamyšlení

### 3. Smart Face Reframer (`reframer.py`)
- Prochází vzorkované snímky videa (4 fps) a detekuje souřadnice obličeje mluvčího přes OpenCV.
- Aplikuje časové vyhlazování (Moving Average / EMA) horizontálního posunu, čímž eliminuje trhání virtuální kamery a vytváří přirozený kinematografický pohyb.
- Generuje optimalizovaný FFmpeg crop filter `crop=w:h:x:y,scale=1080:1920`.

### 4. Dynamické Karaoke Titulky (`subtitles.py`)
- Vytváří standardní formát `.ass` (Advanced SubStation Alpha) s předpočítanou bezpečnou zónou (aby nepřekrýval ovládací prvky na TikToku / Shorts).
- Seskupuje slova do dynamických 3–4 slovních bloků (styl MrBeast / Alex Hormozi).
- Aktivně vyslovované slovo v danou setinu sekundy svítí sytě žlutou barvou (`&H0000FFFF`) s jemným zvětšením o 12% a černým obrysem pro dokonalou čitelnost na jakémkoliv pozadí.

### 5. ElevenLabs Voiceover Engine (`voiceover.py`)
- Využívá model `eleven_multilingual_v2` s přirozenou intonací.
- Převede vygenerovaný komentář na audio soubor, který slouží jako primární vypravěčská stopa.

### 6. FFmpeg Transformation & Split-Screen Engine (`video_engine.py`)
- **Pro Režim 1**: Precizní auto-reframe crop, vypálení karaoke titulků, overlay vodoznaku/loga a export v 60fps CRF 18.
- **Pro Režim 2**:
  - Split-screen vertikální stack (nahoře upravené video mluvčího 1080x960, dole dynamický Minecraft/GTA b-roll 1080x960).
  - Vizuální Anti-Content ID úpravy: zrcadlení (`hflip`), barevná korekce kontrastu a saturace, interpolace na 60 snímků/s.
  - Změna rychlosti audia a videa na **1.02x** (`setpts=PTS/1.02` a `atempo=1.02`).
  - **Audio Ducking**: původní zvuk videa je utlumen na pouhých ~18% hlasitosti a ElevenLabs komentář běží zřetelně na 100%.
  - Grafický oddělovací pruh a štítek `"EXKLUZIVNÍ ROZBOR / REAKCE"` pro splnění podmínek Fair Use.

---

## 💻 Spuštění pro Lokální Testování (Volitelné)

Pokud chcete aplikaci otestovat lokálně:

### Spuštění Backend:
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Doplňte své OPENAI_API_KEY a ELEVENLABS_API_KEY v .env
python main.py
```
Backend poběží na `http://localhost:8000` (dokumentace na `http://localhost:8000/docs`).

### Spuštění Frontend:
```bash
cd frontend
npm install
npm run dev
```
Frontend poběží na `http://localhost:3000`.

