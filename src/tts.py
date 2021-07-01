import subprocess
from .config import espeak_path

from gi.repository import GLib
import os


def readText(text, lang):
    file = os.path.join(GLib.get_tmp_dir(), "out.wav")
    # print("tmp file:",file)
    subprocess.check_call(
        ["espeak", "-v", lang, text, "-w", file])
    return file
