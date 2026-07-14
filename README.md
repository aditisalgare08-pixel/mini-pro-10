# Color Detection System

Single-file VS Code project using Python, Flask, OpenCV, NumPy, Pandas, Matplotlib, SQLite, Tkinter, HTML, CSS and JavaScript.

## Run in VS Code

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

## Optional Tkinter mode

```bash
python app.py --tk
```

## Features

- Upload image and click any pixel to detect color
- Webcam capture support
- RGB, HEX and HSV output
- Nearest color name matching
- Dominant color palette using OpenCV KMeans
- SQLite database history
- CSV report using Pandas
- Matplotlib chart at `/chart.png`
- All UI HTML/CSS/JavaScript embedded inside `app.py`
