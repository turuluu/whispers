from pathlib import Path
from pydub import AudioSegment
from . import log


################################################################################
# Trimming audio

# Function to detect leading silence
# Returns the number of milliseconds until the first sound (chunk averaging more than X decibels)
def milliseconds_until_sound(sound, silence_threshold_db=-20.0, chunk_size=10):
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold_db and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def trim_start(filepath):
    log(f'Trimming the start')
    log(f'\t{filepath}')
    path = Path(filepath)
    directory = path.parent
    filename = path.name
    audio_format = Path(filepath).suffix[1:]
    audio = AudioSegment.from_file(filepath, format=audio_format)
    start_trim = milliseconds_until_sound(audio)
    trimmed = audio[start_trim:]

    new_filename = directory / f'trimmed_{filename}'
    return trimmed, new_filename
