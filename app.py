from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

@app.post("/analyze")
async def analyze_video(request: URLRequest):
    ydl_opts = {'quiet': True, 'no_warnings': True}
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
                        "url": f.get('url')
                    })
            return {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "formats": formats[-5:] # آخر 5 جودات متاحة
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail="الرابط غير مدعوم أو خاص")

@app.get("/")
def read_root():
    return {"status": "Online"}

