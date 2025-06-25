from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
import yt_dlp
import os
import re
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def sanitize_filename(title):
    return secure_filename(re.sub(r'[\\/*?:"<>|]', "", title))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        format_type = request.form["format"]

        try:
            if format_type == "audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'downloaded'))
                ext = 'mp3' if format_type == 'audio' else 'mp4'
                filename = f"{title}.{ext}"
                full_path = os.path.join(DOWNLOADS_DIR, filename)

                session['download_file'] = full_path  # store path in session

            return redirect(url_for('download'))

        except Exception as e:
            flash(f"❌ Error: {str(e)}")
            return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/download")
def download():
    path = session.get('download_file')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash("❌ File not found.")
        return redirect(url_for("index"))
