from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import yt_dlp
import json
import os
from urllib.parse import quote
from helpers import *
import time

app = Flask(__name__)
CORS(app)

def load_file(filename):
    with open(filename, "rb") as f:
        return f.readlines()

def delete_old_files():
    for i in os.listdir():
        if i.endswith(".mp4") or i.endswith(".webm"):    
            file_creation_time = os.path.getctime(i)
            seconds_since_creation = time.time() - file_creation_time
            
            if seconds_since_creation / 3600 >= 12: # turn into hours
                os.remove(i)
    

ydl_opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True }
@app.route("/analyze", methods=["POST"])
def analyze_video():
    delete_old_files()
    
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"detail": "No URL provided"}), 400

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)            
            formats = []
            for f in info.get('formats', []):
                if f.get('height'):
                    formats.append({
                        "id": f['format_id'],
                        "ext": f['ext'],
                        "quality": f'{f["height"]}p',
                        "url": f.get('url'),
                        "title": info.get("title")
                    })
            formats = filter_formats(formats)

            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "formats": formats[-5:]
            })
        except Exception as e:
            return jsonify({"detail": "الرابط غير مدعوم أو خاص"}), 400
        
        

def find_filename_from_value(value):
    for i in os.listdir():
        if value in i:
            return i
        
    return False


def ydl_download(url, title): 
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("starting downloading ", url)
        ydl.download([url])
        print("finished downloading ", url)
        
    filename = find_filename_from_value(title)
    print("FILENAME: ", filename)
    if not filename:
        raise FileNotFoundError("file not found: ", filename)
    
    if filename.endswith(".mp4"):
        return
        
    print("FILE IS NOT .MP4, CONVERTING IT TO MP4")
    output = filename.split(".")
    output[-1] = ".mp4"
    
    print("".join(output))
    convert_webm_to_mp4(filename, "".join(output))
    

@app.route("/download_video", methods=["POST"])
def download_video():
    try:        
        data = request.get_json()
        title = data.get("title")
        url = data.get("url")
        
        print("TITLE: ", title[:10] + "...")
        print("URL: ", url[:10] + "...")

        ydl_download(url, title)
        
        return jsonify({
            "filePath": f"/file/{quote(title)}"
        })
        
    except Exception as e:
        print(e)
        return jsonify({"detail": "Failed to download"}), 500

    
@app.route("/file/<title>")
def send_video_file(title="NOT_PROVIDED"):
    if title == "NOT_PROVIDED":
        return jsonify({"detail": "No file id was passed"}), 400
    
    
    print(os.listdir())
    print("TITLE FROM SEND FILE: ", title)
    filename = find_filename_from_value(title)
    print("FILENAME1: ", filename)
    if not filename and not filename.endswith(".mp4"):
        return jsonify({"detail": "Video not found, Maybe wait until it finishes downloading?"}), 500
    print("FILENAME2: ", filename)
    
    
    return send_file(
        filename,
        mimetype="video/mp4",
        as_attachment=True,
        download_name=title
    )
    
    
    
@app.route("/langs", methods=["POST"])
def send_langs():
    langs = load_file("./langs.json")
    return json.loads(b"\n".join(langs))


@app.route("/")
def read_root():
    html_file_content = load_file("./index.html")    
    return b"\n".join(html_file_content)



if __name__ == "__main__":
    app.run(host="CHANGE_TO_YOUR_LOCAL_IP_ADDRESS", debug=True)