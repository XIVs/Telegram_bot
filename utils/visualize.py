# utils/visualize.py
import os
import uuid
import subprocess
from PIL import Image
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip # type: ignore
import numpy as np

def process_audio_to_video(file_path):
    try:
        # Конвертация в WAV
        wav_path = file_path.replace(".ogg", ".wav").replace(".mp3", ".wav")
        subprocess.run(["ffmpeg", "-y", "-i", file_path, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Аудио
        audio = AudioFileClip(wav_path)
        if audio.duration > 60:
            audio = audio.subclip(0, 60)

        # Изображение винила
        img = Image.open("assets/vinyl_base.png").convert("RGB")
        size = max(img.size)
        img = img.resize((size, size))  # делаем квадрат
        vinyl_temp_path = f"temp_vinyl_{uuid.uuid4()}.png"
        img.save(vinyl_temp_path)

        # Вращение винила
        vinyl = ImageClip(vinyl_temp_path).set_duration(audio.duration)
        rotating = vinyl.rotate(lambda t: t * 45, resample='bilinear').set_position("center")

        # Композиция и звук
        final = CompositeVideoClip([rotating.set_audio(audio)], size=vinyl.size).set_duration(audio.duration)

        out_path = f"video_{uuid.uuid4()}.mp4"
        final.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")

        # Освобождение ресурсов
        audio.close()
        rotating.close()

        os.remove(wav_path)
        os.remove(vinyl_temp_path)
        return out_path
    except Exception as e:
        print("Ошибка в process_audio_to_video:", e)
        return None