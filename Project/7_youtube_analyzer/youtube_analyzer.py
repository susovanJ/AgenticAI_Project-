from openai import OpenAI
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import parse_qs, urlparse
import streamlit as st

load_dotenv()

client = OpenAI()

def extract_youtube_video(url:str)->str|None:
    if "://" not in url:
        url = f"https://{url}"

    parsed_url = urlparse(url)

    host = (parsed_url.hostname)

    if host.lower() not in {
        "youtube.com","www.youtube.com","m.youtube.com",
        "music.youtube.com","youtu.be","www.youtu.be","youtube-nocookie.com","www.youtube-nocookie.com"
    }:
        return None
    
    elif host.endswith("youtu.be"):
        return parsed_url.path.strip("/").split("/",1)[0] or None
    
    video_url = parse_qs(parsed_url.query).get("v",[])

    if video_url and video_url[0]:
        return video_url[0]
    
    path_parts = parsed_url.path.strip('/').split('/')

    if len(path_parts)>=2 and path_parts[0] in {"shorts","embed","live","v"}:
        return path_parts[1] or None


st.title("Youtube Content Analyzed Agent: ")

urlText = st.text_input("Paste Your Youtube URL: ")

questionText = st.text_input("Asked Question: ")

btn = st.button("Analyzed")
if btn:
    video_link = extract_youtube_video(urlText.strip())
    if not video_link:
        st.error("Enter a valid URL.")
    else:
        vt = YouTubeTranscriptApi()
        video_transcript = vt.fetch(video_link,languages=["bn","en"])
        video_text = "".join(item.text for item in video_transcript)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages= [
                {
                    "role":"system",
                    "content":'''
                    -You are an Youtube video summarizer.
                    -You can answer from video transcript.
                    -Apart from that Please Reply 'I can't help with Out specified Video link'              
                    '''
                },
                {
                    "role":"user",
                    "content":f"Prompt:{questionText},Context:{video_text}, please use this context to reply"
                }
            ]
        )
        result = response.choices[0].message.content
        st.write("Agent:",result)