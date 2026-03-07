from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import yt_dlp
import uvicorn
import asyncio
import json
import os
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_file(filename):
    with open(filename, "rb") as f:
        return f.readlines()


class URLRequest(BaseModel):
    id: str | None = None
    title: str | None = None
    url: str
        
ydl_opts = {'quiet': True, 'no_warnings': True}
@app.post("/analyze")
async def analyze_video(request: URLRequest):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(request.url, download=False)            
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
            return {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "formats": formats[-5:]
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail="الرابط غير مدعوم أو خاص")
        
        
        


@app.post("/download_video")
async def downalod_video(request: URLRequest):
    try:    
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([request.url])

        return {
            "finished": True
        }
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to download")

    

    
@app.post("/langs")
async def send_langs():
    langs = load_file("./langs.json")
    return json.loads(b"\n".join(langs))


@app.get("/", response_class=HTMLResponse)
def read_root():
    html_file_content = load_file("./index.html")    
    return b"\n".join(html_file_content)


if __name__ == "__main__":
    uvicorn.run("app:app", host="192.168.31.7")