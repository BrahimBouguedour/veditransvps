import ffmpeg
import whisper
from elevenlabs import generate, clone, voices
from google.cloud import translate_v2 as translate
from google.cloud import speech_v1
import os
from typing import Optional
import tempfile

class VideoProcessor:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.translate_client = translate.Client()
        self.speech_client = speech_v1.SpeechClient()

    def extract_audio(self, video_path: str) -> str:
        """Extract audio from video file."""
        output_path = video_path.rsplit('.', 1)[0] + '.wav'
        
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ac=1, ar='16k')
            ffmpeg.run(stream, overwrite_output=True)
            return output_path
        except ffmpeg.Error as e:
            raise Exception(f"Failed to extract audio: {str(e)}")

    def transcribe_audio(self, audio_path: str) -> dict:
        """Transcribe audio to text using Whisper."""
        try:
            result = self.whisper_model.transcribe(audio_path)
            return {
                'text': result['text'],
                'segments': result['segments']
            }
        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language."""
        try:
            result = self.translate_client.translate(
                text,
                target_language=target_language
            )
            return result['translatedText']
        except Exception as e:
            raise Exception(f"Failed to translate text: {str(e)}")

    def clone_voice(self, audio_sample_path: str, text: str) -> bytes:
        """Clone voice and generate speech in target language."""
        try:
            # First, clone the voice
            voice = clone(
                name="custom_voice",
                files=[audio_sample_path],
            )

            # Generate speech with cloned voice
            audio = generate(
                text=text,
                voice=voice,
                model="eleven_multilingual_v1"
            )
            
            return audio
        except Exception as e:
            raise Exception(f"Failed to clone voice and generate speech: {str(e)}")

    def merge_audio_video(self, video_path: str, audio_path: str) -> str:
        """Merge translated audio with original video."""
        output_path = video_path.rsplit('.', 1)[0] + '_translated.mp4'
        
        try:
            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(audio_path)
            
            stream = ffmpeg.output(
                input_video,
                input_audio,
                output_path,
                vcodec='copy',
                acodec='aac'
            )
            ffmpeg.run(stream, overwrite_output=True)
            return output_path
        except ffmpeg.Error as e:
            raise Exception(f"Failed to merge audio and video: {str(e)}")

    def process_video(self, video_path: str, target_language: str, preserve_voice: bool = True) -> dict:
        """Process video through the complete translation pipeline."""
        try:
            # Extract audio
            audio_path = self.extract_audio(video_path)
            
            # Transcribe audio
            transcription = self.transcribe_audio(audio_path)
            
            # Translate text
            translated_text = self.translate_text(
                transcription['text'],
                target_language
            )
            
            # Generate new audio
            if preserve_voice:
                new_audio = self.clone_voice(audio_path, translated_text)
                
                # Save the generated audio to a temporary file
                temp_audio_path = tempfile.mktemp(suffix='.wav')
                with open(temp_audio_path, 'wb') as f:
                    f.write(new_audio)
            else:
                # Use standard TTS if voice preservation not required
                raise NotImplementedError("Standard TTS not implemented yet")
            
            # Merge audio and video
            final_video_path = self.merge_audio_video(video_path, temp_audio_path)
            
            # Clean up temporary files
            os.remove(audio_path)
            os.remove(temp_audio_path)
            
            return {
                'status': 'success',
                'video_path': final_video_path,
                'transcription': transcription,
                'translation': translated_text
            }
        except Exception as e:
            # Clean up any temporary files
            if 'audio_path' in locals():
                os.remove(audio_path)
            if 'temp_audio_path' in locals():
                os.remove(temp_audio_path)
            raise Exception(f"Video processing failed: {str(e)}") 