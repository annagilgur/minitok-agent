import requests
import openai
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip, AudioFileClip
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# Load from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

openai.api_key = OPENAI_API_KEY

def get_random_fact():
    url = "https://en.wikipedia.org/wiki/Wikipedia:Unusual_articles"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.select("div.mw-parser-output ul li a")
    article = items[5]
    title = article.text
    article_url = f"https://en.wikipedia.org{article['href']}"
    return title, article_url

def summarize_article(article_url):
    article_res = requests.get(article_url)
    soup = BeautifulSoup(article_res.content, "html.parser")
    paragraphs = soup.select("p")
    text = "\n".join(p.text for p in paragraphs[:3])
    prompt = f"Summarize this article in 3 fun, casual sentences for a 30-second TikTok:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_voiceover(script, filename="voice.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
    }
    response = requests.post(url, headers=headers, json=data)
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

def make_video(voice_path, stock_path="stock.mp4", out_path="output.mp4"):
    video = VideoFileClip(stock_path).subclip(0, 30)
    audio = AudioFileClip(voice_path)
    final = video.set_audio(audio).set_duration(audio.duration)
    final.write_videofile(out_path, codec="libx264", audio_codec="aac")
    return out_path

def email_video(file_path, subject="Your Daily MiniDoc"):
    with open(file_path, "rb") as f:
        data = f.read()
    encoded = data.encode("base64") if hasattr(data, "encode") else data

    message = Mail(
        from_email="minidoc@yourdomain.com",
        to_emails=RECIPIENT_EMAIL,
        subject=subject,
        html_content="Here is your daily auto-generated MiniDoc video.")

    attachedFile = Attachment(
        FileContent(data),
        FileName("output.mp4"),
        FileType("video/mp4"),
        Disposition("attachment")
    )
    message.attachment = attachedFile

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

def run_agent():
    title, url = get_random_fact()
    print("Pulled article:", title)
    print("URL:", url)
    script = summarize_article(url)
    print("Generated script:", script)
    voice_file = generate_voiceover(script)
    video_path = make_video(voice_file)
    email_video(video_path)
    print("✅ Video sent to email.")

run_agent()