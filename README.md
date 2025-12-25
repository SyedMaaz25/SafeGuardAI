# SafeGuard AI

**Watch. Detect. Protect!**  

SafeGuard AI is a Flask-based web application that detects PPE compliance (helmets, gloves, vests) in video footage using a YOLOv8 model. It provides real-time analytics, a safety score, and visually highlights violations in the processed video.

---

## Features

- Detects personnel and PPE compliance:
  - Helmet
  - Gloves
  - Vest
- Generates a **safety score** based on detected violations.
- Side-by-side video display: original vs. processed output.
- Modern Tailwind CSS interface with live stats.
- FFMPEG integration for web-compatible video output.

---

## Demo

Upload a video to see:

- Total personnel detected
- PPE violations per category
- Safety rating percentage
- Input and inference result videos side by side

**⚠️ Tip:** For faster results, upload **short videos** (around 5–7 seconds). Long videos may take more time to process.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/SyedMaaz25/SafeGuardAI
cd SafeGuardAI