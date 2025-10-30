import os, zipfile, textwrap

root = "AI_Face_Attendance_Personalized"
paths = [
    f"{root}/backend/templates",
    f"{root}/backend/static",
    f"{root}/backend/encodings_store",
    f"{root}/backend/uploads",
    f"{root}/backend/exports",
    f"{root}/backend/react_dashboard/src/components",
    f"{root}/backend/react_dashboard/public",   # 🧩 Added line
]

for p in paths:
    os.makedirs(p, exist_ok=True)


# === BACKEND: app.py ===
app_py = textwrap.dedent("""\
import os, cv2, numpy as np, face_recognition, datetime, csv
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path

app = Flask(__name__)
UPLOADS = Path("backend/uploads")
EXPORTS = Path("backend/exports")
ENCODINGS = Path("backend/encodings_store")

UPLOADS.mkdir(exist_ok=True)
EXPORTS.mkdir(exist_ok=True)
ENCODINGS.mkdir(exist_ok=True)

# Load known encodings
def load_known_faces():
    known_encodings, known_names = [], []
    for img_file in ENCODINGS.glob("*.*"):
        img = face_recognition.load_image_file(img_file)
        enc = face_recognition.face_encodings(img)
        if enc:
            known_encodings.append(enc[0])
            known_names.append(img_file.stem)
    return known_encodings, known_names

known_encodings, known_names = load_known_faces()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    global known_encodings, known_names
    if 'photo' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['photo']
    filename = file.filename
    save_path = UPLOADS / filename
    file.save(save_path)

    img = face_recognition.load_image_file(save_path)
    locs = face_recognition.face_locations(img)
    encs = face_recognition.face_encodings(img, locs)

    marked_names = []
    for enc in encs:
        matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.5)
        if True in matches:
            name = known_names[matches.index(True)]
            marked_names.append(name)
            mark_attendance(name)
        else:
            marked_names.append("Unknown")

    return jsonify({'message': f"Attendance marked for: {', '.join(marked_names)}"})

def mark_attendance(name):
    today = datetime.date.today().strftime("%Y-%m-%d")
    file_path = EXPORTS / f"attendance_{today}.csv"
    exists = file_path.exists()
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Name", "Time"])
        writer.writerow([name, datetime.datetime.now().strftime("%H:%M:%S")])

@app.route('/export_attendance')
def export_attendance():
    today = datetime.date.today().strftime("%Y-%m-%d")
    file_path = EXPORTS / f"attendance_{today}.csv"
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'No attendance file yet'})

@app.route('/reload_encodings')
def reload_encodings():
    global known_encodings, known_names
    known_encodings, known_names = load_known_faces()
    return jsonify({'message': f'Reloaded {len(known_names)} encodings'})

if __name__ == "__main__":
    app.run(debug=True)
""")

open(f"{root}/backend/app.py", "w", encoding="utf-8").write(app_py)

# === templates/index.html ===
index_html = """<!DOCTYPE html>
<html lang='en'><head>
<meta charset='UTF-8'><title>AI Attendance</title>
<link rel='stylesheet' href='/static/style.css'>
</head><body>
<h1>AI-Based Classroom Attendance</h1>
<div class='upload-section'>
  <h3>📸 Upload Photo</h3>
  <form id='uploadForm' enctype='multipart/form-data'>
    <input type='file' id='photo' name='photo' accept='image/*' required>
    <button type='submit'>Upload & Mark</button>
  </form><p id='uploadMessage'></p>
</div>
<div class='export-section'>
  <h3>📂 Export Attendance</h3>
  <button id='exportBtn'>Download CSV</button>
</div>
<script>
uploadForm.addEventListener('submit',async e=>{
 e.preventDefault();
 const fd=new FormData();fd.append('photo',photo.files[0]);
 const r=await fetch('/upload_photo',{method:'POST',body:fd});
 const j=await r.json();uploadMessage.innerText=j.message||j.error;
});
exportBtn.onclick=()=>window.location='/export_attendance';
</script>
</body></html>"""
open(f"{root}/backend/templates/index.html", "w", encoding="utf-8").write(index_html)

# === static/style.css ===
style_css = """body{font-family:sans-serif;text-align:center;background:#0a0a23;color:#fff}
.upload-section,.export-section{margin:30px auto;padding:20px;width:60%;background:#1c1c3c;border-radius:10px}
button{background:#28a745;color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer}
button:hover{background:#218838}"""
open(f"{root}/backend/static/style.css", "w", encoding="utf-8").write(style_css)

# === React dashboard scaffold ===
vite_config = """export default { root: 'src', server: { port: 5173 } }"""
open(f"{root}/backend/react_dashboard/vite.config.js", "w", encoding="utf-8").write(vite_config)

package_json = """{
  "name": "react_dashboard",
  "version": "1.0.0",
  "scripts": { "dev": "vite" },
  "dependencies": { "react": "^18.0.0", "react-dom": "^18.0.0" }
}"""
open(f"{root}/backend/react_dashboard/package.json", "w", encoding="utf-8").write(package_json)

main_jsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
ReactDOM.createRoot(document.getElementById('root')).render(<App />)
"""
open(f"{root}/backend/react_dashboard/src/main.jsx", "w", encoding="utf-8").write(main_jsx)

app_jsx = """export default function App(){
  return(<div style={{textAlign:'center',marginTop:'50px'}}>
    <h2>Teacher Dashboard</h2>
    <p>This is a placeholder React dashboard.</p>
  </div>);
}"""
open(f"{root}/backend/react_dashboard/src/App.jsx", "w", encoding="utf-8").write(app_jsx)

index_css = "body{font-family:sans-serif;background:#fafafa;margin:0;padding:0;text-align:center}"
open(f"{root}/backend/react_dashboard/src/index.css", "w", encoding="utf-8").write(index_css)

# === Components ===
for c in ["RegisterForm", "AttendanceUpload", "AttendanceView", "ExportButton"]:
    open(f"{root}/backend/react_dashboard/src/components/{c}.jsx", "w", encoding="utf-8").write(
        f"export default function {c}(){{return <div>{c}</div>}}"
    )

public_html = "<!DOCTYPE html><html><body><div id='root'></div><script type='module' src='/src/main.jsx'></script></body></html>"
open(f"{root}/backend/react_dashboard/public/index.html", "w", encoding="utf-8").write(public_html)

# === README & requirements.txt ===
readme = """# AI-Based Classroom Attendance

### 🧩 How to Run
1. Create a virtual environment:
   python -m venv venv
   venv\\Scripts\\activate
2. Install dependencies:
   pip install -r requirements.txt
3. Run Flask backend:
   python backend/app.py
4. Open in browser:
   http://127.0.0.1:5000/
"""
open(f"{root}/README.md", "w", encoding="utf-8").write(readme)
open(f"{root}/requirements.txt", "w", encoding="utf-8").write("flask\nopencv-python\nface-recognition\nnumpy\n")

# === ZIP CREATION ===
zipname = f"{root}.zip"
with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as z:
    for r, _, files in os.walk(root):
        for f in files:
            z.write(os.path.join(r, f))
print(f"✅ Created {zipname}")
