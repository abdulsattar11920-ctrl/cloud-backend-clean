from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.txt")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")  # SAME UI

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    quality = request.form.get("quality", "720")

    file_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4")

    ydl_opts = {
        # 🎯 UNIVERSAL + LOW CPU + MOBILE SAFE
        "format": (
            "bv*[height<=" + quality + "][vcodec^=avc1][ext=mp4]"
            "+ba[acodec^=mp4a]/mp4"
        ),
        "merge_output_format": "mp4",
        "outtmpl": output_path,
        "restrictfilenames": True,

        # cookies (cloud jugaar)
        "cookiefile": COOKIES_FILE,

        # low cpu + compatibility
        "postprocessor_args": [
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "160k",
            "-movflags", "+faststart"
        ],

        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(
            output_path,
            as_attachment=True,
            download_name="video.mp4"
        )

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
