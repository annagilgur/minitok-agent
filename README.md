# MiniDoc TikTok Agent

This project automatically:
- Pulls a weird Wikipedia article
- Summarizes it using GPT-3.5
- Generates a voiceover via ElevenLabs
- Combines it with stock footage into a TikTok-style video
- Emails the finished video to a recipient every day

## Setup

1. Fork this repo
2. Add the following secrets in GitHub:
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `SENDGRID_API_KEY`
- `RECIPIENT_EMAIL`

3. Push to `main`. The agent will run daily at 8AM PT via GitHub Actions.

Ensure `stock.mp4` is present in the root directory.