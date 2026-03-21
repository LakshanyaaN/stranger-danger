![Python](https://img.shields.io/badge/Python-3.8+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-orange)

# Stranger Danger

> A slightly dramatic system that locks your screen when a stranger shows up — because why should they get access *and* a normal experience?

---

## Overview

Stranger Danger is a fun (and mildly paranoid) real-time face recognition project that watches your webcam while you work.

If it sees someone it doesn't recognize — or notices that you've mysteriously disappeared — it doesn't just sit there quietly.  
It escalates.

First, a warning.  
Then… a full cinematic Matrix-style lockdown.

Everything runs locally, no cloud, no data sharing — just you, your camera, and a system that takes its job a little too seriously.

---

## Features

- Real-time face recognition using OpenCV (LBPH)
- Dual enrollment (with glasses / without glasses — because realism)
- Smart delay so it doesn't panic instantly
- Warning countdown before things go wrong
- Full Matrix-style lockdown (yes, the rain)
- Dramatic white flash → **ACCESS DENIED**
- Hidden password input with blinking cursor
- Runs quietly in the background
- Optional auto-start on boot (if you fully commit to the bit)

---

## Requirements

- Python 3.8+
- Windows OS
- Webcam

Install dependencies:

```bash
pip install opencv-contrib-python pygame pyttsx3 numpy
```

---

## How It Works

```
Camera watches you exist
        ↓
You leave OR a stranger appears
        ↓
System: "hmm."
        ↓
Warning appears (you get a chance to stop it)
        ↓
You ignore it (bad idea)
        ↓
Matrix rain takes over your screen
        ↓
Things escalate very quickly
        ↓
White flash
        ↓
ACCESS DENIED
        ↓
Enter code or accept your fate
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/LakshanyaaN/stranger-danger.git
cd stranger-danger
```

---

### 2. Set your unlock code

```python
# matrix_watcher.py
CANCEL_CODE = "your_code_here"
```

```python
# matrix_countdown.py
UNLOCK_CODE = "your_code_here"
```

> Use the same code in both. Future you will thank you.

---

### 3. Build the countdown executable

```bash
pyinstaller matrix_countdown.spec
```

---

### 4. Important step (don't skip this)

```
dist/
├── matrix_countdown.exe
└── matrix_watcher.py   <- copy this here manually
```

> If both files aren't in `dist/`, nothing works.

---

### 5. Run it

```bash
cd dist
python matrix_watcher.py
```

On first run, it'll guide you through face enrollment.

---

## Controls

| Command | What it does |
|--------|--------|
| `pause` | Stops monitoring temporarily |
| `resume` | Starts monitoring again |
| `status` | Shows current state |
| `quit` | Exits the program |

---

## Configuration

| Setting | Location | Default |
|--------|--------|--------|
| Detection delay | `matrix_watcher.py` | 5 seconds |
| Warning duration | `matrix_watcher.py` | 5 seconds |
| Face confidence threshold | `matrix_watcher.py` | 70 |
| Normal rain duration | `matrix_countdown.py` | 10 seconds |
| Overload duration | `matrix_countdown.py` | 4 seconds |

---

## What's Happening Under the Hood

- OpenCV handles face detection + recognition
- LBPH model decides if you're "you"
- A timer prevents instant false triggers
- PyGame renders the fullscreen lockdown
- PyInstaller packages the countdown into an `.exe`

Simple, local, and slightly overdramatic.

---

## Limitations

- Sensitive to lighting conditions
- Appearance changes may confuse it
- No anti-spoofing (photos might work)
- Requires continuous webcam access
- Windows-only

---

## Why This Exists

Mostly curiosity.  
Partly: "what if my laptop had trust issues?"

Also a fun way to explore:
- Face recognition
- Real-time systems
- Over-the-top UI design

---

## Data & Privacy

- Everything stays on your device
- Stored locally in `matrix_owner.yml`
- No internet usage, no APIs
- Delete `matrix_owner.yml` at any time to reset enrollment

---

## Auto-start on Boot

1. Update the path in `run_matrix.bat` to match your system
2. Press `Win + R`, type `shell:startup`, hit Enter
3. Copy `run_matrix.bat` into the startup folder

---

## Future Ideas

- Liveness detection
- Multi-user support
- Mobile alerts
- Smarter detection logic

---

## Inspiration

Inspired by *The Matrix* — but instead of saving the world, it just aggressively protects your screen.

---

## License

MIT License — free to use, modify, and distribute.

---

Built by [Lakshanya](https://github.com/LakshanyaaN)
