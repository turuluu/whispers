import os
import sys

from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional
from glob import glob

from i2t.utlz import log, rm, clean_dir
from i2t.text import transcribe_request, to_row_format_request
from i2t.audio import trim_start, to_audio

if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} <path to audio>')
    sys.exit(1)

load_dotenv()

# TODO : refactor into a simple list of people
interviewer = os.environ.get('interviewer', 'interviewer')
interviewee = os.environ.get('interviewee', 'interviewee')

spelling_context = os.environ.get('spelling_context', '')
segments_in_megabytes = os.environ.get('segments_in_megabytes', 25)


@dataclass
class Paths:
    orig_audio: Path
    output_dir: Path


@dataclass
class Transcripts:
    listings: Optional[list[str]] = None


def parse_paths(filepath):
    """Parses input file location and infers a directory location according to the
    base file name"""
    orig_audio_path = Path(filepath)
    if not orig_audio_path.exists():
        raise FileNotFoundError(orig_audio_path)

    output_dir = Path(orig_audio_path.parent) / orig_audio_path.stem

    return Paths(orig_audio_path, output_dir)


def reset_output(paths: Paths):
    """Clear and create anew the output directory"""
    # Contain results in a single folder
    clean_dir(paths.output_dir)
    log(f'Created results directory: {paths.output_dir}')


def in_mb(size):
    return f'{(size / (10 ** 6)):.1f}MB'


def optimize(paths: Paths, audio_format='mp3'):
    """Whisper accepts audio with max size of 25MB, so split audio
    into segments and some other conversions"""

    def whisper_optimize(filepath, samplerate=16000, bitrate='64k'):
        """Internally Whisper converts to mono, 16kHz, 64k/128k, mp3
        If that is done beforehand, it saves costs"""
        orig_size = Path(filepath).stat().st_size
        log(f'File:\t{filepath} - size: {in_mb(orig_size)}')
        log(f'\tTrimming the start')
        path = Path(filepath)

        directory = path.parent
        filename = path.name

        samplerate = 16000
        log(f'\tconverting (mono, samplerate: {samplerate}, bitrate: {bitrate})')
        audio = to_audio(filepath)
        audio = trim_start(audio)
        audio = audio.set_frame_rate(samplerate).set_channels(1)
        new_filename = directory / f'whisper_{filename}'
        audio.export(new_filename, format="mp3", bitrate=bitrate)

        return audio, new_filename

    start_time = 0
    i = 0
    bitrate = '64k'

    whisper_audio, whisper_filename = whisper_optimize(paths.orig_audio, bitrate=bitrate)
    # calculate chunks in ms according to whisper API's limitations
    whisper_filesize = Path(whisper_filename).stat().st_size
    log(f'\t-> {whisper_filename} - size: {in_mb(whisper_filesize)}')
    chunks_n = whisper_filesize / (segments_in_megabytes * (10 ** 6))
    interval_ms = int(len(whisper_audio) / chunks_n)
    audio_files = []
    log(f'\t{chunks_n=}, {interval_ms=}')
    log(f'Splitting audio into {segments_in_megabytes} MB segments...')
    while start_time < len(whisper_audio):
        segment = whisper_audio[start_time:start_time + interval_ms]
        segment_path = paths.output_dir / f'{paths.orig_audio.stem}_{i:02d}.{audio_format}'
        segment.export(segment_path, format=audio_format, bitrate=bitrate)
        audio_files.append(segment_path)
        log(f'\t{segment_path.stem}')
        start_time += interval_ms
        i += 1

    return audio_files


def transcribe(audio_files, paths: Paths):
    """Send audio files for transcription collating them into an intermediary format"""

    # Whisper transcribes fillers, punctuation, and should correct initialisms etc if given as prompt
    # It's a bit hit-and-miss
    whisper_prompt = f"{spelling_context}. Umm... So it's like, let me think. Or? Really!? 100 000 people."
    prompt = whisper_prompt
    transcripts = []
    for i, file in enumerate(audio_files):
        trc = transcribe_request(file, prompt)
        transcripts.append(trc)
        # Upon trial and error, srt seemed to yield best results
        out_path = paths.output_dir / f'{paths.orig_audio.stem}_{i:02d}.srt'
        with open(out_path, 'w', encoding='UTF-8') as trsc_f:
            trsc_f.write(trc)
        # whisper transcribes more coherently when using the previous piece for context
        prompt = whisper_prompt + trc[-500:]

    return Transcripts(transcripts)


def collate(transcripts: Transcripts, paths: Paths):
    """The srt format comes in short 5 second lines so this tries to collate them into more
    coherent, but relatively short paragraphs retaining the timestamps.
    Typically Whisper does not produce NVivo compatible format, so it needs to be
    reformatted into rows."""

    fixed_transcripts = []

    # TODO : generalize beyond one-off tests
    if transcripts.listings is None:
        listings = []
        for p in glob(f'{str(paths.output_dir)}/{paths.orig_audio.stem}_*.srt'):
            with open(p, 'r', encoding='UTF-8') as trcf:
                listings.append(trcf.read())
        transcripts.listings = listings

    log(f'Requesting row format...')
    for i, fixed in enumerate(to_row_format_request(transcripts.listings, interviewer, interviewee)):
        fixed_transcripts.append(fixed)

    return Transcripts(fixed_transcripts)


def save_rows(transcripts: Transcripts, paths: Paths):
    for i, fixed in enumerate(transcripts.listings):
        out_path = paths.output_dir / f'{paths.orig_audio.stem}_{i:02d}.txt'
        rm(out_path)
        with open(out_path, 'w', encoding='UTF-8') as trsc_f:
            trsc_f.write(fixed)


def save_concatenated(transcripts: Transcripts, paths: Paths):
    """Save the full transcript for good measure."""
    # TODO :  The timestamps will be off as they restart on every segment
    full_trc_path = paths.output_dir / f'{paths.orig_audio.stem}_concat.txt'
    log(f'Saving full transcript to {full_trc_path}...')
    rm(full_trc_path)
    with open(full_trc_path, 'w', encoding='UTF-8') as full_f:
        full_f.write(' '.join(transcripts.listings))


if __name__ == '__main__':
    paths = parse_paths(sys.argv[1])
    reset_output(paths)
    optimized_files = optimize(paths)

    log(f'Transcription pass 1...')
    transcripts = transcribe(optimized_files)

    log(f'Transcription pass 2...')
    result = collate(transcripts, paths)
    # result = collate(Transcripts(), paths)

    save_rows(result, paths)
    save_concatenated(result, paths)
