import subprocess
from .Audio_Player import Player
from .config import espeak_path


def readText(text, lang):
    subprocess.check_call(
        [espeak_path, "-v", lang, text, "-w", "out.wav"])
    send = Player('out.wav')
    return send
