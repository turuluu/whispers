# Interview transcriber

A quick-and-dirty transcribing script for transforming audio interviews into NVivo 15 format (rows).

## Brief

The script chunks audio into 25 minute pieces creating them in a subfolder. Then it proceeds to transcribe them 
using OpenAI Whisper into a preliminary format, and eventually runs that once more through OpenAI GPT to fix so as 
to comply to the NVivo format.

## Usage 

Audio setup
1. Transform the audio into mp3 (saves bandwidth, use e.g. Audacity)

OpenAI setup
1. Register a user account at OpenAI 
2. Transfer money to the OpenAI account (just the pro account won't suffice)

Script setup
1. Find the console and create a "project key"
2. Copy the project key to a local file ".env" (See below)
3. Install requirements
    
    pip install -r requirements.txt

4. Run in terminal

    python i2t.py <path to interview as .mp3>

### .env file

Rename the `template.env` file as `.env` and fill in your project token key:
OPENAI_API_KEY=sk-proj-****

## Costs and performance

An hour long interview is cut into chunks as Whisper limits the max length to 30 min.

Transcribing an hour long interview as mp3 and transforming it using the script runs in 5 minutes and costs <1 euro.
