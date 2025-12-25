from flask import Flask, render_template, request, url_for
from collections import Counter
from ultralytics import YOLO
import subprocess
import time
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Model
model = YOLO("model/best.pt")

@app.route("/", methods=["GET", "POST"])
def index():
    input_video = None
    output_video = None
    stats = None

    if request.method == "POST":
        file = request.files.get("video")
        if file:
            # Save uploaded video
            timestamp = str(int(time.time()))
            input_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{file.filename}")
            file.save(input_path)

            # Create unique result folder for this upload
            result_folder = os.path.join(OUTPUT_FOLDER, f"result_{timestamp}")
            os.makedirs(result_folder, exist_ok=True)

            # YOLO prediction
            results = model.predict(
                source=input_path,
                save=True,
                conf=0.4,
                iou=0.5,
                project=OUTPUT_FOLDER,
                name=f"result_{timestamp}",
                exist_ok=True
            )

            # Process Analytics
            max_counts = Counter()
            for r in results:
                frame_counts = Counter()
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    frame_counts[label] += 1
                for label, count in frame_counts.items():
                    if count > max_counts[label]:
                        max_counts[label] = count

            total_ppl = max_counts.get("Person", 0)
            no_helmet = min(max_counts.get("no_helmet", 0), total_ppl)
            no_vest = min(max_counts.get("none", 0), total_ppl)
            no_gloves = min(max_counts.get("no_gloves", 0), total_ppl)

            # Safety Score
            if total_ppl > 0:
                total_possible_points = total_ppl * 3
                deductions = no_helmet + no_vest + no_gloves
                score = int(((total_possible_points - deductions) / total_possible_points) * 100)
                safety_score = max(0, min(100, score))
            else:
                safety_score = 100

            stats = {
                "total_persons": total_ppl,
                "safety_score": safety_score,
                "violations": {
                    "No Helmet": no_helmet,
                    "No Vest": no_vest,
                    "No Gloves": no_gloves
                }
            }

            # FFMPEG Web Conversion
            raw_videos = [f for f in os.listdir(result_folder) if f.endswith((".avi", ".mp4"))]
            if raw_videos:
                raw_output_path = os.path.join(result_folder, raw_videos[0])
                web_output_path = os.path.join(result_folder, f"web_out_{timestamp}.mp4")
                
                try:
                    subprocess.run([
                        "ffmpeg", "-y", "-i", raw_output_path,
                        "-vcodec", "libx264", "-acodec", "aac",
                        "-movflags", "faststart", web_output_path
                    ], check=True)
                    input_video = url_for('static', filename=f"uploads/{timestamp}_{file.filename}")
                    output_video = url_for('static', filename=f"output/result_{timestamp}/web_out_{timestamp}.mp4")
                except Exception as e:
                    # fallback if ffmpeg fails
                    output_video = url_for('static', filename=f"output/result_{timestamp}/{raw_videos[0]}")

    return render_template("index.html", input_video=input_video, output_video=output_video, stats=stats)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)