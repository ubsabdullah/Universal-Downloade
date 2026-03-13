# import yt_dlp


# def gen():
#     ydl_opts = {'quiet': True, 'no_warnings': True}
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         print(ydl.extract_info("https://www.youtube.com/watch?v=m8E3Dh-gfhM&list=PLRddFemFCXX9oME3sQ9hR9brh-TmiJUGq&index=52", False))
        
#         # ydl.download([
#         #     "https://www.youtube.com/watch?v=m8E3Dh-gfhM&list=PLRddFemFCXX9oME3sQ9hR9brh-TmiJUGq&index=52"
#         # ])


# # for i in range(100):
# #     print(gen())



import subprocess
import os

def convert_webm_to_mp4(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-movflags', 'faststart',
        output_file
    ]

    try:
        print(f"Starting conversion of {input_file} to {output_file}...")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Conversion successful!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e.stderr}")
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please ensure ffmpeg is installed and added to your system PATH.")


def filter_formats(formats):
    qualities = ["144p", "240p", "360p", "480p", "720p", "1080p"]
    MP4s = list(filter(lambda x: x["ext"] == "mp4" and x["quality"] in qualities, formats))
        
    seen_qualities = set()
    for i in MP4s.copy():
        if i["quality"] in seen_qualities:
            MP4s.remove(i)
        else:
            seen_qualities.add(i["quality"])
        
    return MP4s

# input_video = "Eminem - The Way I Am (Dirty Version) [m8E3Dh-gfhM].webm"
# output_video = "output_video.mp4"

# convert_webm_to_mp4(input_video, output_video)
