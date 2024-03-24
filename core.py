import cv2
import time
import librosa
import numpy as np
import os
import json
from TTS.api import TTS
import soundfile as sf
from shutil import copyfile
from utils import push_new_asset
import whisper
import asyncio
from transformers import T5Tokenizer, T5ForConditionalGeneration


def text_to_video(text):
    # Define video properties
    font_scale = 1.5
    font_thickness = 2
    text_color = (255, 0, 0)  # Blue
    # Red  # Consistent red color for background
    background_color = (0, 0, 255)
    frame_width = 640
    frame_height = 480
    fps = 1  # Frames per second
    video_duration = 5  # Video length in seconds

    # Create a video writer object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Video codec (adjust if needed)
    out = cv2.VideoWriter("output.mp4", fourcc, fps,
                          (frame_width, frame_height))

    # Create base image with background color
    base_image = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    base_image[:] = background_color

    # Get text size
    text_size, _ = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

    # Calculate text placement coordinates
    text_x = int((frame_width - text_size[0]) / 2)
    text_y = int((frame_height + text_size[1]) / 2)

    # Loop for video frames
    start_time = time.time()
    while (time.time() - start_time) < video_duration:
        frame = base_image.copy()

        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, text_color, font_thickness)

        out.write(frame)

    out.release()
    asset_id = push_new_asset(
        './output.mp4', "output.mp4",  delete_orig_file=True)
    return asset_id


def text_to_speech(text):
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

    wav = tts.tts(text=text)
    wav = np.array(wav)

    sf.write("output.wav", wav, 22050)
    asset_id = push_new_asset(
        './output.wav', "output.wav",  delete_orig_file=True)
    return asset_id


def speech_to_text(audio_filepath: str):
    model_name = "base"
    model = whisper.load_model(model_name)
    return model.transcribe(audio_filepath)


def text_generative_model(prompt: str):
    tokenizer = T5Tokenizer.from_pretrained("google-t5/t5-small")
    model = T5ForConditionalGeneration.from_pretrained("google-t5/t5-small")
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_new_tokens=30)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result
