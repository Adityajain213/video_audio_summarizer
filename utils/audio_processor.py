import os
import sys

import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── FFmpeg setup ──────────────────────────────────────────────────────────────
# On your Windows PC we point to the WinGet install.
# On Linux (Railway) ffmpeg is already on PATH, so nothing is needed.
FFMPEG_DIR = None

if sys.platform.startswith("win") and os.environ.get("LOCALAPPDATA"):
    _win_dir = os.path.join(
        os.environ["LOCALAPPDATA"],
        "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe",
        "ffmpeg-9.0.2-full_build-shared", "bin",
    )
    if os.path.isdir(_win_dir):
        FFMPEG_DIR = _win_dir
        AudioSegment.converter = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
        AudioSegment.ffmpeg = AudioSegment.converter
        AudioSegment.ffprobe = os.path.join(FFMPEG_DIR, "ffprobe.exe")
        os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")  # video id avoids odd characters

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    if FFMPEG_DIR:  # only set on Windows
        ydl_opts["ffmpeg_location"] = FFMPEG_DIR

    # Optional: cookies help when YouTube blocks the server's IP.
    cookies = os.environ.get("YOUTUBE_COOKIES_FILE")
    if cookies and os.path.exists(cookies):
        ydl_opts["cookiefile"] = cookies

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".wav"

    return filename


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # mono, 16 kHz
    audio.export(output_path, format="wav")

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("detected youtube url, now downloading")
        wav_path = download_youtube_audio(source)
    else:
        print("detected local file, converting to wav")
        wav_path = convert_to_wav(source)

    print("chunking audio")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready - {len(chunks)} chunk(s) created")
    return chunks
