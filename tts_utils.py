import os
from gtts import gTTS
import pygame
from django.conf import settings
import tempfile

def text_to_speech(text, language='en'):
    """Convert text to speech and return audio file path"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def play_audio(file_path):
    """Play audio file using pygame"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
            
    except Exception as e:
        print(f"Audio playback error: {e}")

def speak_text(text, language='en'):
    """Convert text to speech and play it"""
    audio_file = text_to_speech(text, language)
    if audio_file:
        play_audio(audio_file)
        # Clean up temporary file
        try:
            os.unlink(audio_file)
        except:
            pass