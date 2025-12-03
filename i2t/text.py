"""Audio transcription"""
from . import log
from openai import OpenAI


# Whisper-1 only uses the last 224 tokens, and is not an instruct model
def transcribe(audio_path, prompt='', model='whisper-1'):
    log(f'transcribing {audio_path.stem}...')

    client = OpenAI()
    with open(audio_path, 'rb') as audio_path:
        transcription = client.audio.transcriptions.create(
            model=model,
            response_format='srt',
            file=audio_path,
            language='en',
            prompt=prompt
        )

    return transcription


def gen(user_prompt, system_prompt, model='gpt-4.1', temperature=None):
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_prompt
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


def transform_to_nvivo(transcript, interviewer="interviewer", interviewee=["interviewee"], system_prompt=None):
    if system_prompt is None:
        system_prompt = (
            "Can you transform this srt transcript into Nvivo15 compatible text so that, "
            "using your best guess, connect the sentences together under the same timestamp combining them"
            "into 5-10 second pieces. Label the speaker accordingly i.e. those "
            "that belong to the interviewer and those for the interviewee. The timeblocks should stay "
            "relatively short – max 20-30 seconds per timestamp, but mostly between 5-10 seconds. Use the names "
            f"{interviewer} for the interviewer and {interviewee} for the interviewee. "
            "Only output the final transcript without further acknowledgements."
            "Here are 2 examples of correct results:\n"
            "<example1>\n"
            "00:00:01\n"
            f"{interviewer}: Do you want to have the video on? The audio quality might be better without the video.\n\n"
            "00:00:07\n"
            f"{interviewee}: Sure, we can turn off the video if that's better. We can turn off the video if that's better for the audio.\n\n"
            "00:00:16\n"
            f"{interviewer}: I think it's okay, but sometimes, I don't know, whichever you prefer.We can leave it on.\n\n"
            "00:00:23\n"
            f"{interviewee}: Yeah, let's leave it on and then we can turn it off later.\n\n"
            "00:00:26\n"
            f"{interviewer}: Okay, it's okay. Can you state your name for the record?\n\n"
            "</example1>\n"
            "<example2>\n"
            "00:05:10\n"
            f"{interviewer}: So it also, like, covers the team or the organizational kind of roles and responsibilities.So you'll have information of who to contact, who's the responsible party that knows about certain things.\n\n"
            "00:05:28\n"
            f"{interviewee}: No, no, no.\n\n"
            "00:05:29\n"
            f"{interviewer}: Oh, okay.\n\n"
            "00:05:30\n"
            f"{interviewee}: So what I meant is, if I didn't have custom GPT, I have to talk to, like, two or three people about this issue. Thanks to chat GPT, I don't have to talk to any person.I can just resolve my issue just asking.\n\n"
            "00:05:46\n"
            f"{interviewer}: Yeah.So it's like a knowledge base of all the details.\n\n"
            "00:05:51\n"
            f"{interviewee}: Yeah.\n\n"
            "00:05:56\n"
            f"{interviewer}: And I repeat, I don't want to kind of put you into any risk of leaking IP. But is it possible for you to open up what type of details, like, on a course level maybe?\n\n"
            "00:06:17\n"
            f"{interviewee}: Hmm.Like, what are helpful details?\n\n"
            "</example2>\n"
        )

    return gen(transcript, system_prompt)


def to_row_format(trcs, interviewer, interviewee):
    for i, t in enumerate(trcs):
        log(f'Transforming to final format ({i:02d})...')
        result = transform_to_nvivo(t, interviewer, interviewee)
        yield result
