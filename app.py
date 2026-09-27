import streamlit as st
import cv2
import os
import base64
import numpy as np
import pyttsx3
from dotenv import load_dotenv

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

mood = ""

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame = None
    def recv(self, frame):
        self.frame = frame.to_ndarray(format="bgr24")
        return frame


st.title("MOOD TRACKER 👨🏾‍⚕️")

ctx = webrtc_streamer(
    key="camera",

    video_processor_factory=VideoProcessor,

    media_stream_constraints={
        "video": True,
        "audio": False
    },

    rtc_configuration={
        "iceServers": [
            {
                "urls": [
                    "stun:stun.l.google.com:19302"
                ]
            }
        ]
    }
)

if ctx.video_processor:
    image = ctx.video_processor.frame

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0
)

def predict_mood(img):
    success, buffer = cv2.imencode(".jpg", img)

    if not success:
        return "Could not encode image"
    
    jpeg_bytes = buffer.tobytes()

    base64_image = base64.b64encode(jpeg_bytes).decode("utf-8")
    

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """
                    You are a mood classification agent.

                    Look at the person's visible facial expression and choose
                    ONE mood from this list:

                    Happy, Sad, Angry, Fearful, Surprised, Disgusted, Neutral,
                    Excited, Calm, Anxious, Confused, Bored, Frustrated, Relaxed,
                    Worried, Embarrassed, Proud, Curious, Tired, Amused.

                    Return ONLY the mood name.
                    Do not explain your answer.
                    """,
            },
            {   
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
        ]
    )

    #Run LLm call in another thread?
    response = llm.invoke([message])

    return response.content

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

if st.button("Detect Mood"):
    if image.size == 0:
        st.warning("Waiting for camera frame...")
    else:
        mood = predict_mood(image).strip()
        mood_str = f"You're {mood}"
        st.success(f"Mood detected: {mood}")

        speak(mood_str)