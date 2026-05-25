"""65b: 渲染更新后的S3 SVG→PNG并注入PPTX"""
import subprocess, time, threading, os, shutil
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE = Path(__file__).resolve().parent.parent
FIG_DIR = BASE / "results" / "figures_final"
SVG_FILE = FIG_DIR / "_s2_cell_states_en_v2.svg"
PNG_FILE = FIG_DIR / "_s2_cell_states_en_v2.png"

# Chrome path
CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"
if not Path(CHROME).exists():
    CHROME = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
    if not Path(CHROME).exists():
        CHROME = "C:/Program Files/Microsoft/Edge/Application/msedge.exe"
assert Path(CHROME).exists(), f"No Chrome/Edge at {CHROME}"

PORT = 18851
os.chdir(str(FIG_DIR))

# Start HTTP server
server = HTTPServer(("127.0.0.1", PORT), SimpleHTTPRequestHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
time.sleep(1)

URL = f"http://127.0.0.1:{PORT}/_s2_cell_states_en_v2.svg"

# Chrome headless screenshot
out = str(PNG_FILE.absolute())
result = subprocess.run([
    CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
    f"--window-size=1860,660",
    f"--screenshot={out}",
    URL,
], capture_output=True, text=True, timeout=30)

server.shutdown()

# Check result
print(f"Chrome stderr: {result.stderr[:200] if result.stderr else '(none)'}")
print(f"Chrome stdout: {result.stdout[:200] if result.stdout else '(none)'}")

if PNG_FILE.exists():
    print(f"[PNG] {PNG_FILE.name}: {PNG_FILE.stat().st_size} bytes")
else:
    print(f"[WARN] {PNG_FILE} not found, searching FIG_DIR...")
    for p in sorted(FIG_DIR.glob("*.png")):
        print(f"  {p.name}: {p.stat().st_size}")
