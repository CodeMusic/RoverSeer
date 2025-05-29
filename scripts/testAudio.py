import subprocess
import re

def get_usb_aplay_device():
    try:
        output = subprocess.check_output(["aplay", "-L"]).decode()
        match = re.search(r"(plughw:CARD=\w+,DEV=\d+).+?USB Audio", output, re.DOTALL)
        if match:
            return match.group(1)
    except Exception as e:
        print("Device detection failed:", e)
    return "default"  # fallback

AUDIO_DEVICE = get_usb_aplay_device()
