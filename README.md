# Interview transcriber

A transcription script that converts and chunks audio into whisper optimized chunks creating them in a subfolder. Then
it proceeds to transcribe them using OpenAI Whisper. Finally it uses OpenAI GPT to transcode the whisper output into
NVivo row-format.

## Usage 

Note: Accepts .wav and .mp3 files.

OpenAI setup (unrelated, but mandatory to use its API)
1. Register a user account at OpenAI 
2. Transfer money to the OpenAI account (just the pro account won't suffice)
3. Find the console and create a "project key"
4. Copy the project key to a local file ".env" (See below ".env file")

Script setup
1. Install requirements
    
    pip install -r requirements.txt

2. Run in terminal

    python i2t.py <path to interview file>

### .env file

Rename the `template.env` file as `.env` and fill in your OpenAI project's token key from the previous steps:

   OPENAI_API_KEY=sk-proj-****

## Costs and performance

An hour long interview is cut into chunks as Whisper limits the max length to 30 min.

Transcribing an hour long interview as mp3 and transforming it using the script runs in 5 minutes and costs <1 euro.

## Tested

Used on MacOS for my own project. Should work on other platforms just the same.