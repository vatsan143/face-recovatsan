import os, cv2, numpy as np, face_recognition, datetime, csv
from flask import Flask, render_template, request, jsonify, send_file
import os, cv2, face_recognition, numpy as np, base64, csv, datetime

app = Flask(__name__)
os.makedirs("backend/uploads", exist_ok=True)
os.makedirs("backend/exports", exist_ok=True)
os.makedirs("backend/encodings_store", exist_ok=True)

# ✅ Load known encodings
def load_known_faces():
    encodings, names = [], []
    for file in os.listdir("backend/encodings_store"):
        if file.lower().endswith(("AI_Face_Attendance_Personalized/backend/known face/212222060055.jpg", "AI_Face_Attendance_Personalized/backend/known face/212222060185.jpg", "AI_Face_Attendance_Personalized/backend/known face/bau.jpg", "AI_Face_Attendance_Personalized/backend/known face/WhatsApp Image 2024-08-01 at 07.26.47.jpeg", "AI_Face_Attendance_Personalized/backend/known face/WhatsApp Image 2025-06-18 at 18.15.22_061450c1.jpg", "AI_Face_Attendance_Personalized/backend/known face/WhatsApp Image 2025-10-30 at 10.40.54_8d1e506e.jpg", "AI_Face_Attendance_Personalized/backend/known face/new.jpg")):
            path = os.path.join("backend/encodings_store", file)
            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)
            if enc:
                encodings.append(enc[0])
                names.append(os.path.splitext(file)[0])
    return encodings, names

known_encodings, known_names = load_known_faces()

# ✅ Save attendance
def mark_attendance(name):
    filename = "backend/exports/attendance.csv"
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as f:
            csv.writer(f).writerow(["Name", "Timestamp"])

    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

@app.route("/")
def home():
    return render_template("index.html")

# ✅ Receive real-time frames
@app.route("/detect_face", methods=["POST"])
def detect_face():
    global known_encodings, known_names
    data = request.json
    image_data = data["image"].split(",")[1]
    img_bytes = base64.b64decode(image_data)
    npimg = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Detect face
    faces = face_recognition.face_locations(img)
    encs = face_recognition.face_encodings(img, faces)

    if not encs:
        return jsonify({"status": "no_face"})

    for enc in encs:
        matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.45)
        if True in matches:
            name = known_names[matches.index(True)]
            mark_attendance(name)
            return jsonify({"status": "recognized", "name": name})

    return jsonify({"status": "unknown"})

@app.route("/export_attendance")
def export_attendance():
    return send_file("backend/exports/attendance.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
