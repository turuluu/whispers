"""Audio transcription"""
from . import log
from openai import OpenAI


# Whisper-1 only uses the last 224 tokens, and is not an instruct model
def transcribe(audio_path, prompt):
    log(f'transcribing {audio_path.stem}...')

    client = OpenAI()
    with open(audio_path, "rb") as audio_path:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            response_format='srt',
            # timestamp_granularities=["segment"],
            file=audio_path,
            language='en',
            prompt=prompt
        )

    return transcription


def gen(user_prompt, system_prompt, temperature=None):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )
    return response.choices[0].message.content


# Results were just worse than without
# def generate_corrected_transcript(transcript, spelling_context, temperature=0, system_prompt=None):
#     if system_prompt is None:
#         system_prompt = (
#             "You are a helpful assistant for correcting interview transcripts. Fix "
#             "any spelling discrepancies in the transcribed text. Make sure that the names and "
#             "initialism are correct, for example: "
#             f"{spelling_context}"
#             " Only add necessary "
#             "punctuation such as periods, commas, and capitalization. ")
#
#     return gen(transcript, system_prompt, temperature)


def transform_to_nvivo(transcript, interviewer="interviewer", interviewee="interviewee", system_prompt=None):
    if system_prompt is None:
        system_prompt = (
            "Can you transform this srt transcript into Nvivo15 compatible text so that, "
            "using your best guess, connect the sentences together labeling according those "
            "that belong to the interviewer and those for the interviewee. Use the names "
            f"{interviewer} for the interviewer and {interviewee} for the interviewee. "
            "Combine dialogue turns under the same timestamp when "
            "they are split during the same turn. Only output the final transcript without further acknowledgements."
            "Here is a sample of a correct result:\n"
            "00:00:01\n"
            f"{interviewer}: Do you want to have the video on? The audio quality might be better without the video.\n\n"
            "00:00:07\n"
            f"{interviewee}: Sure, we can turn off the video if that's better. We can turn off the video if that's better for the audio.\n\n"
            "00:00:16\n"
            f"{interviewer}: I think it's okay, but sometimes, I don't know, whichever you prefer.We can leave it on.\n\n"
            "00:00:23\n"
            f"{interviewee}: Yeah, let's leave it on and then we can turn it off later.\n\n"
            "00:00:26\n"
            f"{interviewer}: Let's do that. The interview is going to be for coursework, potentially for a paper because the degree does basically exactly this area of research, as far as "
            "I know. Then it might kind of spawn something, other steps later on. I need to ask you, do you consent that I record and later transcribe this interview?\n\n"
            "00:01:00\n"
            f"{interviewee}: No, I don't mind.\n\n"
            "00:01:02\n"
            f"{interviewer}: Okay, it's okay. Can you state your name for the record?\n\n"
        )

    return gen(transcript, system_prompt)
