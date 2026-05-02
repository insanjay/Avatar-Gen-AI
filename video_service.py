import os
import subprocess
import sys
import glob


def generate_video(audio_path, image_path):

    # Absolute SadTalker path (CRITICAL FIX)
    sadtalker_path = os.path.abspath("SadTalker")

    cmd = [
        sys.executable, "inference.py",
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--result_dir", "results",
        "--still",
        "--preprocess", "crop",
        "--expression_scale", "1.2",
        "--enhancer", "gfpgan",
        "--pose_style", "0",
    ]

    print("Running SadTalker...")

    # 🔍 DEBUG (very important)
    print("CWD:", sadtalker_path)
    print("Checkpoint exists:",
          os.path.exists(os.path.join(sadtalker_path, "checkpoints/epoch_20.pth")))

    # ✅ Run process with proper cwd + output capture
    process = subprocess.run(
        cmd,
        cwd=sadtalker_path,
        capture_output=True,
        text=True
    )

    print("\n===== STDOUT =====\n", process.stdout)
    print("\n===== STDERR =====\n", process.stderr)

    if process.returncode != 0:
        raise Exception("SadTalker failed")

    # ✅ Get final video
    video_path = get_final_video(sadtalker_path)

    # ✅ Fix codec
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


def get_final_video(sadtalker_path):
    search_path = os.path.join(sadtalker_path, "results/**/*.mp4")

    videos = glob.glob(search_path, recursive=True)

    final = [
        v for v in videos
        if "##" not in v and "_full" not in v
    ]

    if not final:
        raise Exception("No final video found")

    latest = max(final, key=os.path.getctime)

    print("FINAL VIDEO:", latest)

    return latest
