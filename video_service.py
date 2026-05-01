import os
import subprocess
import sys
import glob
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SADTALKER_DIR=PROJECT_ROOT / "SadTalker"
SADTALKER_RESULTS_DIR = SADTALKER_DIR / "results"


def generate_video(audio_path, image_path):

    cmd = [
        sys.executable, "inference.py",
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--result_dir", str(SADTALKER_RESULTS_DIR),
        "--still",
        "--preprocess", "crop",
        "--expression_scale", "1.2",
        "--enhancer", "gfpgan",
        "--pose_style", "0",
    ]

    print("Running SadTalker...")

    process = subprocess.Popen(
        cmd,
        cwd="str(SadTalker)",
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    process.wait()

    if process.returncode != 0:
        raise Exception("SadTalker failed")

    # ✅ Step 1: get final video
    video_path = get_final_video()

    # ✅ Step 2: fix codec (CRITICAL)
    video_path = fix_video_codec(video_path)

    return video_path


def fix_video_codec(input_path):
    output_path = input_path.replace(".mp4", "_fixed.mp4")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vcodec", "libx264",
        "-acodec", "aac",
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("FIXED VIDEO:", output_path)

    return output_path


def get_final_video():
    videos = glob.glob(str(SADTALKER_RESULTS_DIR / "**" / "*.mp4") recursive=True)

    final = [
        v for v in videos
        if "##" not in v and "_full" not in v
    ]

    if not final:
        raise Exception("No final video found")

    latest = max(final, key=os.path.getctime)

    print("FINAL VIDEO:", latest)

    return latest