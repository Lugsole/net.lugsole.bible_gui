import subprocess
from .Audio_Player import Player


def readText(text, lang):
    subprocess.check_call(
        ["/app/bin/espeak", "-v", lang, text, "-w", "out.wav"])
    send = Player('out.wav')
    return send
