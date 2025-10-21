import os
import sys

from dotenv import load_dotenv
from pathlib import Path

from i2t import log, rm, clean_dir
from i2t import transcribe, to_row_format
from i2t import trim_start

if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} <path to audio>')
    sys.exit(1)

load_dotenv()
interviewer = os.environ.get('interviewer', 'interviewer')
interviewee = os.environ.get('interviewee', 'interviewee')
spelling_context = os.environ.get('spelling_context', '')
segments_in_minutes = os.environ.get('segments_in_minutes', 25)

orig_audio_path = Path(sys.argv[1])
if not orig_audio_path.exists():
    raise FileNotFoundError(orig_audio_path)

# Contain results in a single folder
output_dir = Path(orig_audio_path.parent) / orig_audio_path.stem
clean_dir(output_dir)
log(f'Created results directory: {output_dir}')

# Whisper accepts audio with max length of 30 minutes, so split audio
# into segments
log(f'Splitting audio into {segments_in_minutes} minute segments...')
interval_ms = int(segments_in_minutes) * 60 * 1000
start_time = 0
i = 0
trimmed_audio, trimmed_filename = trim_start(orig_audio_path)
audio_format = Path(orig_audio_path).suffix[1:]
audio_files = []
while start_time < len(trimmed_audio):
    segment = trimmed_audio[start_time:start_time + interval_ms]
    segment_path = output_dir / f'{orig_audio_path.stem}_{i:02d}.{audio_format}'
    segment.export(segment_path, format=audio_format)
    audio_files.append(segment_path)
    log(f'\t{segment_path.stem}')
    start_time += interval_ms
    i += 1

# Whisper transcribes fillers, punctuation, and should correct initialisms etc if given as prompt
whisper_prompt = f"{spelling_context}. Umm... So it's like, let me think. Or? Really!? 100 000 people."
log(f'Transcription pass 1...')
prompt = whisper_prompt
transcriptions = []
for i, file in enumerate(audio_files):
    trc = transcribe(file, prompt)
    transcriptions.append(trc)
    out_path = output_dir / f'{orig_audio_path.stem}_{i:02d}.srt'
    with open(out_path, 'w', encoding='UTF-8') as trsc_f:
        trsc_f.write(trc)
    # whisper transcribes more coherently when using the previous piece for context
    prompt = whisper_prompt + trc[-500:]

# Typically Whisper does not produce NVivo compatible format, so it needs to be
# reformatted into "rows"
log(f'Transcription pass 2...')
fixed_transcripts = []
for i, fixed in enumerate(to_row_format(transcriptions, interviewer, interviewee)):
    out_path = output_dir / f'{orig_audio_path.stem}_{i:02d}.txt'
    rm(out_path)
    with open(out_path, 'w', encoding='UTF-8') as trsc_f:
        trsc_f.write(fixed)
    fixed_transcripts.append(fixed)

# Save the full transcript for good measure. The timestamps will be off as they restart
# on every segment
full_trc_path = output_dir / f'{orig_audio_path.stem}_concat.txt'
log(f'Saving full transcript to {full_trc_path}...')
rm(full_trc_path)
with open(full_trc_path, 'w', encoding='UTF-8') as full_f:
    full_f.write(' '.join(fixed_transcripts))
