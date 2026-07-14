"""
Color Detection System - Single File Project
Tech used: Python, Flask, OpenCV, NumPy, Pandas, Matplotlib, SQLite, Tkinter, HTML, CSS, JavaScript
Run: python app.py
Open: http://127.0.0.1:5000
"""

import os
import io
import csv
import base64
import sqlite3
import datetime as dt
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template_string, send_file, Response

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    TKINTER_AVAILABLE = True
except Exception:
    TKINTER_AVAILABLE = False

APP_TITLE = "Color Detection System"
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "color_detection.db"
UPLOAD_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

COLOR_TABLE: List[Tuple[str, int, int, int]] = [
    ("Black", 0, 0, 0), ("White", 255, 255, 255), ("Red", 255, 0, 0),
    ("Lime", 0, 255, 0), ("Blue", 0, 0, 255), ("Yellow", 255, 255, 0),
    ("Cyan", 0, 255, 255), ("Magenta", 255, 0, 255), ("Silver", 192, 192, 192),
    ("Gray", 128, 128, 128), ("Maroon", 128, 0, 0), ("Olive", 128, 128, 0),
    ("Green", 0, 128, 0), ("Purple", 128, 0, 128), ("Teal", 0, 128, 128),
    ("Navy", 0, 0, 128), ("Orange", 255, 165, 0), ("Pink", 255, 192, 203),
    ("Brown", 165, 42, 42), ("Gold", 255, 215, 0), ("Violet", 238, 130, 238),
    ("Indigo", 75, 0, 130), ("Coral", 255, 127, 80), ("Salmon", 250, 128, 114),
    ("Khaki", 240, 230, 140), ("Lavender", 230, 230, 250), ("Beige", 245, 245, 220),
    ("Mint", 189, 252, 201), ("Sky Blue", 135, 206, 235), ("Turquoise", 64, 224, 208),
    ("Crimson", 220, 20, 60), ("Tomato", 255, 99, 71), ("Chocolate", 210, 105, 30),
    ("Plum", 221, 160, 221), ("Orchid", 218, 112, 214), ("Deep Pink", 255, 20, 147),
    ("Royal Blue", 65, 105, 225), ("Sea Green", 46, 139, 87), ("Forest Green", 34, 139, 34),
    ("Slate Gray", 112, 128, 144), ("Light Gray", 211, 211, 211), ("Dark Red", 139, 0, 0),
    ("Dark Green", 0, 100, 0), ("Dark Blue", 0, 0, 139), ("Light Blue", 173, 216, 230),
    ("Light Green", 144, 238, 144), ("Light Yellow", 255, 255, 224), ("Peach", 255, 218, 185),
    ("Aqua", 127, 255, 212), ("Ivory", 255, 255, 240), ("Charcoal", 54, 69, 79),
]

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Color Detection System</title>
<style>
:root{--bg:#10131a;--card:#171b24;--card2:#202737;--text:#eef3ff;--muted:#9ca9bf;--accent:#6ee7ff;--ok:#8bffb0;--bad:#ff7a90;--line:#2e384d;}
*{box-sizing:border-box;margin:0;padding:0;font-family:Inter,Segoe UI,Arial,sans-serif}
body{min-height:100vh;background:radial-gradient(circle at top left,#23315a,#10131a 45%,#07080c);color:var(--text)}
header{padding:28px 18px;text-align:center;border-bottom:1px solid var(--line);background:rgba(12,15,22,.86);backdrop-filter:blur(8px);position:sticky;top:0;z-index:5}
h1{font-size:clamp(26px,5vw,48px);letter-spacing:.5px;margin-bottom:8px;background:linear-gradient(90deg,#6ee7ff,#8bffb0,#ffd166);-webkit-background-clip:text;color:transparent}
header p{color:var(--muted);font-size:15px}.wrap{width:min(1180px,94vw);margin:28px auto;display:grid;gap:22px}.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:22px}.card{background:linear-gradient(180deg,rgba(32,39,55,.95),rgba(23,27,36,.95));border:1px solid var(--line);border-radius:24px;padding:22px;box-shadow:0 20px 70px rgba(0,0,0,.25)}
.card h2{font-size:22px;margin-bottom:14px}.controls{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:18px}.btn,input[type=file]{border:1px solid var(--line);background:#0f1420;color:var(--text);border-radius:14px;padding:12px 15px;cursor:pointer}.btn{font-weight:700;transition:.2s}.btn:hover{transform:translateY(-2px);border-color:var(--accent);box-shadow:0 8px 20px rgba(110,231,255,.12)}.btn.primary{background:linear-gradient(135deg,#1677ff,#00c2ff);border:none}.btn.good{background:linear-gradient(135deg,#159957,#8bffb0);border:none;color:#08120d}.btn.warn{background:linear-gradient(135deg,#ff9f1c,#ffd166);border:none;color:#1b1200}.btn.danger{background:linear-gradient(135deg,#ff477e,#ff7a90);border:none}.stage{position:relative;min-height:360px;background:#090c12;border:1px dashed #41506a;border-radius:22px;overflow:hidden;display:flex;align-items:center;justify-content:center}.stage canvas{max-width:100%;max-height:620px;display:block}.placeholder{text-align:center;color:var(--muted);padding:26px}.placeholder b{display:block;color:var(--text);font-size:26px;margin-bottom:8px}.lens{position:absolute;width:92px;height:92px;border:3px solid var(--accent);border-radius:50%;pointer-events:none;display:none;box-shadow:0 0 0 9999px rgba(0,0,0,.22),0 0 22px rgba(110,231,255,.45)}.panel{display:grid;gap:15px}.color-preview{height:150px;border-radius:22px;border:1px solid var(--line);display:flex;align-items:end;justify-content:space-between;padding:18px;background:#333;box-shadow:inset 0 0 40px rgba(0,0,0,.25)}.color-preview strong{font-size:28px;text-shadow:0 3px 8px rgba(0,0,0,.5)}.badge{background:rgba(0,0,0,.38);border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:8px 12px;font-weight:700}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.metric{background:#0e1320;border:1px solid var(--line);border-radius:18px;padding:14px}.metric span{display:block;color:var(--muted);font-size:12px}.metric b{font-size:20px}.palette{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}.chip{min-height:84px;border-radius:18px;padding:12px;display:flex;flex-direction:column;justify-content:end;box-shadow:inset 0 -50px 35px rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.14)}.chip b{text-shadow:0 2px 8px rgba(0,0,0,.8)}.chip small{opacity:.9;text-shadow:0 2px 8px rgba(0,0,0,.8)}.table-wrap{overflow:auto;max-height:310px;border-radius:18px;border:1px solid var(--line)}table{width:100%;border-collapse:collapse;background:#0e1320}th,td{padding:11px 12px;border-bottom:1px solid #263249;text-align:left;font-size:14px}th{position:sticky;top:0;background:#172033}.dot{width:22px;height:22px;border-radius:8px;border:1px solid rgba(255,255,255,.3);display:inline-block;vertical-align:middle;margin-right:7px}.notice{padding:12px 14px;border-radius:16px;background:#0e1320;border:1px solid var(--line);color:var(--muted);line-height:1.55}.footer{text-align:center;color:var(--muted);padding:18px}.hidden{display:none!important}.camera-box{display:none;gap:12px;align-items:center;flex-wrap:wrap}.camera-box video{width:280px;max-width:100%;border-radius:16px;border:1px solid var(--line);background:#000}@media(max-width:850px){.grid{grid-template-columns:1fr}.metrics{grid-template-columns:1fr}.card{padding:16px}}
</style>
</head>
<body>
<header>
  <h1>🎨 Color Detection System</h1>
  <p>Upload image किंवा webcam frame वापरा. Image वर click करा आणि exact RGB/HEX + nearest color name मिळवा.</p>
</header>
<main class="wrap">
  <section class="grid">
    <div class="card">
      <h2>1) Image / Camera Input</h2>
      <div class="controls">
        <input id="fileInput" type="file" accept="image/*">
        <button class="btn primary" id="detectBtn">Detect Dominant Colors</button>
        <button class="btn" id="cameraBtn">Start Camera</button>
        <button class="btn good" id="snapBtn">Capture Frame</button>
        <button class="btn warn" id="clearBtn">Clear</button>
      </div>
      <div class="camera-box" id="cameraBox"><video id="video" autoplay playsinline></video><span class="notice">Camera सुरू झाल्यावर Capture Frame दाबा.</span></div>
      <div class="stage" id="stage">
        <div class="placeholder" id="placeholder"><b>Upload Image</b>Click कोणत्याही pixel वर करून color detect करा.</div>
        <canvas id="canvas"></canvas><div class="lens" id="lens"></div>
      </div>
    </div>
    <aside class="card panel">
      <h2>2) Selected Color</h2>
      <div class="color-preview" id="preview"><strong id="colorName">No Color</strong><span class="badge" id="hexText">#------</span></div>
      <div class="metrics">
        <div class="metric"><span>RGB</span><b id="rgbText">-</b></div>
        <div class="metric"><span>HSV</span><b id="hsvText">-</b></div>
        <div class="metric"><span>Match</span><b id="matchText">-</b></div>
      </div>
      <div class="notice">Tip: bright light आणि clear image वापरा. Click केल्यानंतर result database मध्ये save होतो.</div>
      <div class="controls">
        <a class="btn" href="/report.csv">Download CSV</a>
        <a class="btn" href="/chart.png" target="_blank">View Chart</a>
        <button class="btn danger" id="resetDbBtn">Reset History</button>
      </div>
    </aside>
  </section>
  <section class="card"><h2>3) Dominant Palette</h2><div id="palette" class="palette"><div class="notice">Dominant colors इथे दिसतील.</div></div></section>
  <section class="card"><h2>4) Detection History - SQLite + Pandas Report</h2><div class="table-wrap"><table><thead><tr><th>Time</th><th>Color</th><th>HEX</th><th>RGB</th><th>Source</th></tr></thead><tbody id="historyBody"></tbody></table></div></section>
</main>
<div class="footer">Made with Python, OpenCV, NumPy, Pandas, Matplotlib, Flask, SQLite, HTML, CSS and JavaScript.</div>
<script>
const fileInput=document.getElementById('fileInput'),canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d');
const placeholder=document.getElementById('placeholder'),lens=document.getElementById('lens'),preview=document.getElementById('preview');
const colorName=document.getElementById('colorName'),hexText=document.getElementById('hexText'),rgbText=document.getElementById('rgbText'),hsvText=document.getElementById('hsvText'),matchText=document.getElementById('matchText');
const palette=document.getElementById('palette'),historyBody=document.getElementById('historyBody'),video=document.getElementById('video'),cameraBox=document.getElementById('cameraBox');
let stream=null, hasImage=false, currentSource='upload';
function rgbToHex(r,g,b){return '#'+[r,g,b].map(x=>x.toString(16).padStart(2,'0')).join('').toUpperCase()}
function drawImageToCanvas(img){const maxW=1000,maxH=620;let w=img.width,h=img.height;const ratio=Math.min(maxW/w,maxH/h,1);w=Math.round(w*ratio);h=Math.round(h*ratio);canvas.width=w;canvas.height=h;ctx.drawImage(img,0,0,w,h);placeholder.classList.add('hidden');hasImage=true;}
fileInput.addEventListener('change',e=>{const f=e.target.files[0];if(!f)return;currentSource='upload';const img=new Image();img.onload=()=>drawImageToCanvas(img);img.src=URL.createObjectURL(f);});
canvas.addEventListener('mousemove',e=>{if(!hasImage)return;const r=canvas.getBoundingClientRect();lens.style.display='block';lens.style.left=(e.clientX-r.left-46)+'px';lens.style.top=(e.clientY-r.top-46)+'px';});
canvas.addEventListener('mouseleave',()=>lens.style.display='none');
canvas.addEventListener('click',async e=>{if(!hasImage)return;const r=canvas.getBoundingClientRect();const x=Math.floor((e.clientX-r.left)*(canvas.width/r.width));const y=Math.floor((e.clientY-r.top)*(canvas.height/r.height));const d=ctx.getImageData(x,y,1,1).data;await detectPixel(d[0],d[1],d[2],x,y);});
async function detectPixel(r,g,b,x,y){const res=await fetch('/api/detect_pixel',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({r,g,b,x,y,source:currentSource})});const data=await res.json();showColor(data);loadHistory();}
function showColor(data){preview.style.background=data.hex;colorName.textContent=data.color_name;hexText.textContent=data.hex;rgbText.textContent=`${data.rgb.r},${data.rgb.g},${data.rgb.b}`;hsvText.textContent=`${data.hsv.h},${data.hsv.s},${data.hsv.v}`;matchText.textContent=data.distance.toFixed(1);}
document.getElementById('detectBtn').addEventListener('click',async()=>{if(!hasImage){alert('First upload image or capture camera frame');return;}const imageData=canvas.toDataURL('image/png');const res=await fetch('/api/dominant_colors',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:imageData,source:currentSource})});const data=await res.json();renderPalette(data.colors);loadHistory();});
function renderPalette(colors){palette.innerHTML='';colors.forEach(c=>{const div=document.createElement('div');div.className='chip';div.style.background=c.hex;div.innerHTML=`<b>${c.color_name}</b><small>${c.hex} • ${c.percent}%</small>`;palette.appendChild(div);});}
document.getElementById('cameraBtn').addEventListener('click',async()=>{try{stream=await navigator.mediaDevices.getUserMedia({video:true});video.srcObject=stream;cameraBox.style.display='flex';currentSource='camera';}catch(err){alert('Camera permission denied or not available');}});
document.getElementById('snapBtn').addEventListener('click',()=>{if(!stream){alert('Start camera first');return;}canvas.width=video.videoWidth||640;canvas.height=video.videoHeight||480;ctx.drawImage(video,0,0,canvas.width,canvas.height);placeholder.classList.add('hidden');hasImage=true;currentSource='camera';});
document.getElementById('clearBtn').addEventListener('click',()=>{ctx.clearRect(0,0,canvas.width,canvas.height);canvas.width=0;canvas.height=0;hasImage=false;placeholder.classList.remove('hidden');palette.innerHTML='<div class="notice">Dominant colors इथे दिसतील.</div>';showColor({hex:'#333333',color_name:'No Color',rgb:{r:'-',g:'-',b:'-'},hsv:{h:'-',s:'-',v:'-'},distance:0});});
document.getElementById('resetDbBtn').addEventListener('click',async()=>{if(!confirm('Clear all history?'))return;await fetch('/api/reset',{method:'POST'});loadHistory();});
async function loadHistory(){const res=await fetch('/api/history');const rows=await res.json();historyBody.innerHTML='';rows.forEach(row=>{const tr=document.createElement('tr');tr.innerHTML=`<td>${row.created_at}</td><td><span class="dot" style="background:${row.hex}"></span>${row.color_name}</td><td>${row.hex}</td><td>${row.r}, ${row.g}, ${row.b}</td><td>${row.source}</td>`;historyBody.appendChild(tr);});}
loadHistory();
</script>
</body>
</html>
"""


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS detections(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                color_name TEXT NOT NULL,
                hex TEXT NOT NULL,
                r INTEGER NOT NULL,
                g INTEGER NOT NULL,
                b INTEGER NOT NULL,
                h INTEGER NOT NULL,
                s INTEGER NOT NULL,
                v INTEGER NOT NULL,
                distance REAL NOT NULL,
                source TEXT NOT NULL
            )
            """
        )
        conn.commit()


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02X}{:02X}{:02X}".format(int(r), int(g), int(b))


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[int, int, int]:
    pixel = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
    return int(hsv[0]), int(hsv[1]), int(hsv[2])


def nearest_color_name(r: int, g: int, b: int) -> Tuple[str, float]:
    target = np.array([r, g, b], dtype=np.float32)
    best_name = "Unknown"
    best_distance = float("inf")
    for name, cr, cg, cb in COLOR_TABLE:
        current = np.array([cr, cg, cb], dtype=np.float32)
        distance = float(np.linalg.norm(target - current))
        if distance < best_distance:
            best_distance = distance
            best_name = name
    return best_name, best_distance


def save_detection(color_name: str, hex_code: str, rgb: Tuple[int, int, int], hsv: Tuple[int, int, int], distance: float, source: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO detections(created_at,color_name,hex,r,g,b,h,s,v,distance,source) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), color_name, hex_code, rgb[0], rgb[1], rgb[2], hsv[0], hsv[1], hsv[2], distance, source),
        )
        conn.commit()


def analyze_rgb(r: int, g: int, b: int, source: str = "manual") -> Dict:
    color_name, distance = nearest_color_name(r, g, b)
    hsv = rgb_to_hsv(r, g, b)
    hex_code = rgb_to_hex(r, g, b)
    save_detection(color_name, hex_code, (r, g, b), hsv, distance, source)
    return {
        "color_name": color_name,
        "hex": hex_code,
        "rgb": {"r": r, "g": g, "b": b},
        "hsv": {"h": hsv[0], "s": hsv[1], "v": hsv[2]},
        "distance": distance,
    }


def decode_base64_image(data_url: str) -> np.ndarray:
    header, encoded = data_url.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Invalid image data")
    return image


def get_dominant_colors(image: np.ndarray, k: int = 6) -> List[Dict]:
    resized = cv2.resize(image, (240, 180), interpolation=cv2.INTER_AREA)
    pixels = resized.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 60, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(labels.flatten())
    total = int(counts.sum())
    order = np.argsort(counts)[::-1]
    results = []
    for idx in order:
        b, g, r = centers[idx].astype(int).tolist()
        r, g, b = int(r), int(g), int(b)
        name, distance = nearest_color_name(r, g, b)
        hsv = rgb_to_hsv(r, g, b)
        hex_code = rgb_to_hex(r, g, b)
        percent = round((int(counts[idx]) / total) * 100, 2)
        results.append({"color_name": name, "hex": hex_code, "rgb": {"r": r, "g": g, "b": b}, "hsv": {"h": hsv[0], "s": hsv[1], "v": hsv[2]}, "distance": round(distance, 2), "percent": percent})
    return results


def history_rows(limit: int = 50) -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM detections ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def history_dataframe() -> pd.DataFrame:
    with get_db() as conn:
        df = pd.read_sql_query("SELECT * FROM detections ORDER BY id DESC", conn)
    return df


def make_chart_png() -> io.BytesIO:
    df = history_dataframe()
    if df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No detections yet", ha="center", va="center", fontsize=18)
        ax.axis("off")
    else:
        counts = df["color_name"].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(9, 5))
        counts.plot(kind="bar", ax=ax)
        ax.set_title("Top Detected Colors")
        ax.set_xlabel("Color Name")
        ax.set_ylabel("Count")
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
    output = io.BytesIO()
    fig.savefig(output, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    output.seek(0)
    return output


def launch_tkinter_picker() -> None:
    if not TKINTER_AVAILABLE:
        print("Tkinter not available on this system.")
        return
    root = tk.Tk()
    root.title("Color Detection - Tkinter Image Picker")
    root.geometry("420x240")
    label = tk.Label(root, text="Select image and get average detected color", font=("Arial", 13))
    label.pack(pady=18)
    result = tk.Label(root, text="No image selected", font=("Arial", 12))
    result.pack(pady=8)
    preview = tk.Label(root, width=32, height=4, bg="#333333")
    preview.pack(pady=10)
    def choose_image():
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if not path:
            return
        image = cv2.imread(path)
        if image is None:
            messagebox.showerror("Error", "Could not read image")
            return
        avg_bgr = image.reshape(-1, 3).mean(axis=0).astype(int)
        b, g, r = avg_bgr.tolist()
        data = analyze_rgb(int(r), int(g), int(b), "tkinter")
        preview.config(bg=data["hex"])
        result.config(text=f"{data['color_name']} | {data['hex']} | RGB({r},{g},{b})")
    tk.Button(root, text="Choose Image", command=choose_image, bg="#1677ff", fg="white", padx=20, pady=8).pack(pady=10)
    root.mainloop()

# -----------------------------
# Student Project Notes
# 1. Flask handles the web server.
# 2. OpenCV reads and processes images.
# 3. NumPy calculates color distance and KMeans input arrays.
# 4. Pandas creates CSV reports from SQLite records.
# 5. Matplotlib creates a chart image from detection history.
# 6. SQLite stores every clicked or dominant color detection.
# 7. Tkinter mode is optional for a desktop image picker.
# 8. HTML, CSS and JavaScript are embedded above in one Python file.
# 9. Keep app.py as the main single code file for VS Code submission.
# 10. Use run.bat on Windows for easy startup.
# -----------------------------

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/api/detect_pixel", methods=["POST"])
def api_detect_pixel():
    data = request.get_json(force=True)
    r, g, b = int(data.get("r", 0)), int(data.get("g", 0)), int(data.get("b", 0))
    source = str(data.get("source", "web-click"))
    result = analyze_rgb(r, g, b, source)
    return jsonify(result)


@app.route("/api/dominant_colors", methods=["POST"])
def api_dominant_colors():
    data = request.get_json(force=True)
    image = decode_base64_image(data["image"])
    source = str(data.get("source", "web-image"))
    colors = get_dominant_colors(image, k=6)
    for item in colors:
        rgb = item["rgb"]
        hsv = item["hsv"]
        save_detection(item["color_name"], item["hex"], (rgb["r"], rgb["g"], rgb["b"]), (hsv["h"], hsv["s"], hsv["v"]), float(item["distance"]), source + "-dominant")
    return jsonify({"colors": colors})


@app.route("/api/history")
def api_history():
    return jsonify(history_rows(60))


@app.route("/api/reset", methods=["POST"])
def api_reset():
    with get_db() as conn:
        conn.execute("DELETE FROM detections")
        conn.commit()
    return jsonify({"status": "ok"})


@app.route("/report.csv")
def report_csv():
    df = history_dataframe()
    if df.empty:
        df = pd.DataFrame(columns=["id", "created_at", "color_name", "hex", "r", "g", "b", "h", "s", "v", "distance", "source"])
    output = io.StringIO()
    df.to_csv(output, index=False)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=color_detection_report.csv"})


@app.route("/chart.png")
def chart_png():
    return send_file(make_chart_png(), mimetype="image/png", download_name="color_chart.png")


def print_startup_help() -> None:
    print("=" * 65)
    print(APP_TITLE)
    print("Run URL: http://127.0.0.1:5000")
    print("Features: image upload, webcam capture, click color detection, palette, SQLite history, CSV, chart, Tkinter picker")
    print("Install packages: pip install -r requirements.txt")
    print("=" * 65)


if __name__ == "__main__":
    init_db()
    print_startup_help()
    if "--tk" in os.sys.argv:
        launch_tkinter_picker()
    else:
        app.run(debug=True, host="127.0.0.1", port=5000)
