import ffmpeg
import whisper
from gtts import gTTS
import google.generativeai as genai
import os
import time
from typing import Optional
import tempfile
from dotenv import load_dotenv
from subprocess import TimeoutExpired

def wait_for_file_access(file_path: str, max_retries: int = 5, delay: int = 2):
    """Wait for a file to become accessible."""
    for i in range(max_retries):
        try:
            with open(file_path, 'rb') as f:
                return True
        except (IOError, PermissionError):
            if i < max_retries - 1:
                time.sleep(delay)
            continue
    return False

class VideoProcessor:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        # Load environment variables and configure Gemini
        load_dotenv()
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    def extract_audio(self, video_path: str) -> str:
        """Extract audio from video file."""
        output_path = video_path.rsplit('.', 1)[0] + '.wav'
        
        try:
            # Remove output file if it already exists
            if os.path.exists(output_path):
                os.remove(output_path)
                time.sleep(1)  # Reduced wait time
            
            # Optimize FFmpeg parameters for faster extraction
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path,
                acodec='pcm_s16le',
                ac=1,
                ar='16k',
                loglevel='error',  # Reduce logging overhead
                threads='auto'  # Use all available CPU threads
            )
            
            # Run FFmpeg with timeout
            process = ffmpeg.run_async(stream, overwrite_output=True)
            
            # Wait for process with timeout
            try:
                process.wait(timeout=30)  # 30 seconds timeout
            except TimeoutExpired:
                process.kill()
                raise Exception("Audio extraction timed out after 30 seconds")
            
            # Quick file check
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("Audio extraction failed - output file is missing or empty")
            
            # Verify file is accessible
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    with open(output_path, 'rb') as f:
                        # Read a small portion to verify file access
                        f.read(1024)
                    return output_path
                except (IOError, PermissionError) as e:
                    if attempt == max_retries - 1:
                        raise Exception(f"Failed to access audio file after {max_retries} attempts: {str(e)}")
                    time.sleep(retry_delay)
            
            return output_path
            
        except ffmpeg.Error as e:
            error_message = str(e.stderr.decode()) if e.stderr else str(e)
            print(f"FFmpeg error: {error_message}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            raise Exception(f"Failed to extract audio: {error_message}")
        except Exception as e:
            print(f"Error during audio extraction: {str(e)}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            raise Exception(f"Failed to extract audio: {str(e)}")

    def transcribe_audio(self, audio_path: str) -> dict:
        """Transcribe audio to text using Whisper."""
        try:
            # Ensure the file exists and is accessible
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            # Wait for the file to be accessible
            if not wait_for_file_access(audio_path):
                raise Exception("Failed to access the audio file for transcription")
            
            result = self.whisper_model.transcribe(audio_path)
            return {
                'text': result['text'],
                'segments': result['segments']
            }
        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language using Gemini."""
        try:
            print(f"\nStarting translation to {target_language}")
            print(f"Original text: {text[:100]}...")  # Print first 100 chars
            
            # Normalize language code
            lang_code = target_language.lower().strip()
            print(f"Using language code: {lang_code}")
            
            # Construct prompt with clear instructions
            prompt = f"""
            Translate the following text to {target_language}.
            Return ONLY the translation, no additional text or explanations.
            Text to translate: '{text}'
            """
            
            print("Sending translation request to Gemini...")
            response = self.model.generate_content(prompt)
            translated_text = response.text.strip()
            
            # Verify translation
            if not translated_text:
                raise Exception("Received empty translation from Gemini")
            
            print(f"Received translation: {translated_text[:100]}...")  # Print first 100 chars
            
            # Basic validation
            if translated_text.lower() == text.lower():
                raise Exception("Translation appears to be identical to source text")
                
            if len(translated_text) < len(text) * 0.5:
                print("Warning: Translation is significantly shorter than source text")
            
            return translated_text
            
        except Exception as e:
            error_msg = f"Failed to translate text: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    def generate_speech(self, text: str, lang: str) -> str:
        """Generate speech using Google Text-to-Speech."""
        temp_audio_path = None
        wav_path = None
        
        try:
            print(f"\nStarting speech generation for language: {lang}")
            print(f"Text to convert: {text[:100]}...")  # Print first 100 chars
            
            # Map language codes for gTTS
            lang_mapping = {
                'spanish': 'es',
                'french': 'fr',
                'german': 'de',
                'italian': 'it',
                'portuguese': 'pt',
                'russian': 'ru',
                'japanese': 'ja',
                'korean': 'ko',
                'chinese': 'zh-cn',
                'arabic': 'ar'  # Adding Arabic support
            }
            
            # Get correct language code
            tts_lang = lang_mapping.get(lang.lower(), lang.lower())
            print(f"Using TTS language code: {tts_lang}")
            
            # Create a temporary file for the audio
            temp_audio_path = tempfile.mktemp(suffix='.mp3')
            print(f"Created temporary MP3 file: {temp_audio_path}")
            
            # Generate speech
            print("Initializing Google TTS...")
            tts = gTTS(text=text, lang=tts_lang)
            print("Saving audio to temporary file...")
            tts.save(temp_audio_path)
            
            # Verify MP3 file
            if not os.path.exists(temp_audio_path):
                raise Exception("Failed to create MP3 file")
            
            mp3_size = os.path.getsize(temp_audio_path)
            print(f"MP3 file created successfully. Size: {mp3_size} bytes")
            
            if mp3_size < 1024:  # Less than 1KB
                raise Exception("Generated audio file is suspiciously small")
            
            # Convert mp3 to wav for better compatibility
            wav_path = temp_audio_path.rsplit('.', 1)[0] + '.wav'
            print(f"Converting to WAV format: {wav_path}")
            
            # Convert using ffmpeg with detailed logging
            try:
                stream = ffmpeg.input(temp_audio_path)
                stream = ffmpeg.output(stream, wav_path,
                    acodec='pcm_s16le',
                    ac=1,
                    ar='16k',
                    loglevel='info'  # Increased logging level
                )
                ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
                
                # Verify WAV file
                if os.path.exists(wav_path):
                    wav_size = os.path.getsize(wav_path)
                    print(f"WAV conversion successful. Size: {wav_size} bytes")
                    
                    if wav_size < 1024:  # Less than 1KB
                        raise Exception("Converted WAV file is suspiciously small")
                else:
                    raise Exception("WAV file not created")
                
            except ffmpeg.Error as e:
                error_message = str(e.stderr.decode()) if e.stderr else str(e)
                print(f"FFmpeg conversion error: {error_message}")
                raise Exception(f"Failed to convert audio: {error_message}")
            
            # Clean up the mp3 file
            try:
                os.remove(temp_audio_path)
                print("Temporary MP3 file cleaned up successfully")
            except Exception as e:
                print(f"Warning: Failed to clean up MP3 file: {str(e)}")
            
            print("Speech generation completed successfully")
            return wav_path
            
        except Exception as e:
            print(f"Error during speech generation: {str(e)}")
            # Clean up any temporary files
            for file_path in [temp_audio_path, wav_path]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up temporary file: {file_path}")
                    except Exception as cleanup_error:
                        print(f"Warning: Failed to clean up {file_path}: {str(cleanup_error)}")
            raise Exception(f"Failed to generate speech: {str(e)}")

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

    def process_video(self, video_path: str, target_language: str, preserve_voice: bool = False) -> dict:
        """Process video through the complete translation pipeline."""
        audio_path = None
        temp_audio_path = None
        start_time = time.time()
        step_timing = {}
        results = {
            'audio_extraction': {'status': 'not_started'},
            'transcription': {'status': 'not_started'},
            'translation': {'status': 'not_started'},
            'speech_generation': {'status': 'not_started'},
            'audio_merge': {'status': 'not_started'}
        }
        
        try:
            print(f"Starting video processing at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Input video: {video_path}")
            print(f"Target language: {target_language}")
            
            # Step 1: Extract Audio
            step_start = time.time()
            print("Step 1: Extracting audio from video...")
            audio_path = self.extract_audio(video_path)
            step_timing['audio_extraction'] = time.time() - step_start
            
            # Get audio details
            audio_duration = self._get_audio_duration(audio_path)
            audio_size = os.path.getsize(audio_path)
            results['audio_extraction'] = {
                'status': 'success',
                'file_path': audio_path,
                'size': audio_size,
                'duration': audio_duration
            }
            print(f"Audio extraction completed in {step_timing['audio_extraction']:.2f} seconds")
            
            # Step 2: Transcribe
            step_start = time.time()
            print("Step 2: Transcribing audio...")
            transcription = self.transcribe_audio(audio_path)
            step_timing['transcription'] = time.time() - step_start
            results['transcription'] = {
                'status': 'success',
                'text': transcription['text'],
                'text_length': len(transcription['text']),
                'segments': len(transcription['segments'])
            }
            print(f"Transcription completed in {step_timing['transcription']:.2f} seconds")
            
            # Step 3: Translate
            step_start = time.time()
            print("Step 3: Translating text...")
            translated_text = self.translate_text(
                transcription['text'],
                target_language
            )
            step_timing['translation'] = time.time() - step_start
            results['translation'] = {
                'status': 'success',
                'original_text': transcription['text'][:100],
                'translated_text': translated_text[:100],
                'original_length': len(transcription['text']),
                'translated_length': len(translated_text)
            }
            print(f"Translation completed in {step_timing['translation']:.2f} seconds")
            
            # Step 4: Generate Speech
            step_start = time.time()
            print("Step 4: Generating speech...")
            temp_audio_path = self.generate_speech(translated_text, target_language.lower())
            step_timing['speech_generation'] = time.time() - step_start
            
            # Get generated audio details
            speech_duration = self._get_audio_duration(temp_audio_path)
            speech_size = os.path.getsize(temp_audio_path)
            results['speech_generation'] = {
                'status': 'success',
                'file_path': temp_audio_path,
                'size': speech_size,
                'duration': speech_duration
            }
            print(f"Speech generation completed in {step_timing['speech_generation']:.2f} seconds")
            
            # Step 5: Merge Audio
            step_start = time.time()
            print("Step 5: Merging audio with video...")
            final_video_path = self.merge_audio_video(video_path, temp_audio_path)
            step_timing['audio_merge'] = time.time() - step_start
            
            # Get final video details
            final_size = os.path.getsize(final_video_path)
            results['audio_merge'] = {
                'status': 'success',
                'file_path': final_video_path,
                'size': final_size
            }
            print(f"Merging completed in {step_timing['audio_merge']:.2f} seconds")
            
            total_time = time.time() - start_time
            print(f"Total processing time: {total_time:.2f} seconds")
            
            # Cleanup temporary files
            self._cleanup_files([audio_path, temp_audio_path])
            
            return {
                'status': 'success',
                'video_path': final_video_path,
                'transcription': transcription,
                'translation': translated_text,
                'processing_time': total_time,
                'step_timing': step_timing,
                'results': results,
                'audio_duration': audio_duration,
                'file_size': final_size
            }
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            self._cleanup_files([audio_path, temp_audio_path])
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _cleanup_files(self, file_paths: list):
        """Clean up temporary files safely."""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Successfully removed: {file_path}")
                except Exception as e:
                    print(f"Failed to remove {file_path}: {str(e)}")

    def test_process(self, video_path: str, target_language: str) -> dict:
        """Test each step of the video processing pipeline independently."""
        results = {
            'audio_extraction': {'status': 'not_started'},
            'transcription': {'status': 'not_started'},
            'translation': {'status': 'not_started'},
            'speech_generation': {'status': 'not_started'},
            'audio_merge': {'status': 'not_started'}
        }
        
        audio_path = None
        temp_audio_path = None
        
        try:
            print("\n=== Starting Test Process ===")
            print(f"Testing video: {video_path}")
            print(f"Target language: {target_language}")
            
            # Test 1: Audio Extraction
            print("\n1. Testing Audio Extraction...")
            try:
                audio_path = self.extract_audio(video_path)
                audio_size = os.path.getsize(audio_path)
                results['audio_extraction'] = {
                    'status': 'success',
                    'file_path': audio_path,
                    'size': audio_size,
                    'duration': self._get_audio_duration(audio_path)
                }
                print("✓ Audio extraction successful")
            except Exception as e:
                results['audio_extraction'] = {'status': 'error', 'error': str(e)}
                print(f"✗ Audio extraction failed: {str(e)}")
                raise e
            
            # Test 2: Transcription
            print("\n2. Testing Transcription...")
            try:
                transcription = self.transcribe_audio(audio_path)
                results['transcription'] = {
                    'status': 'success',
                    'text': transcription['text'],
                    'text_length': len(transcription['text']),
                    'segments': len(transcription['segments'])
                }
                print("✓ Transcription successful")
                print(f"Transcribed text: {transcription['text'][:200]}...")
            except Exception as e:
                results['transcription'] = {'status': 'error', 'error': str(e)}
                print(f"✗ Transcription failed: {str(e)}")
                raise e
            
            # Test 3: Translation
            print("\n3. Testing Translation...")
            try:
                translated_text = self.translate_text(transcription['text'], target_language)
                results['translation'] = {
                    'status': 'success',
                    'original_text': transcription['text'][:100],
                    'translated_text': translated_text[:100],
                    'original_length': len(transcription['text']),
                    'translated_length': len(translated_text)
                }
                print("✓ Translation successful")
                print(f"Original text: {transcription['text'][:100]}...")
                print(f"Translated text: {translated_text[:100]}...")
            except Exception as e:
                results['translation'] = {'status': 'error', 'error': str(e)}
                print(f"✗ Translation failed: {str(e)}")
                raise e
            
            # Test 4: Speech Generation
            print("\n4. Testing Speech Generation...")
            try:
                temp_audio_path = self.generate_speech(translated_text, target_language)
                audio_size = os.path.getsize(temp_audio_path)
                results['speech_generation'] = {
                    'status': 'success',
                    'file_path': temp_audio_path,
                    'size': audio_size,
                    'duration': self._get_audio_duration(temp_audio_path)
                }
                print("✓ Speech generation successful")
            except Exception as e:
                results['speech_generation'] = {'status': 'error', 'error': str(e)}
                print(f"✗ Speech generation failed: {str(e)}")
                raise e
            
            # Test 5: Audio Merge
            print("\n5. Testing Audio Merge...")
            try:
                final_path = self.merge_audio_video(video_path, temp_audio_path)
                results['audio_merge'] = {
                    'status': 'success',
                    'file_path': final_path,
                    'size': os.path.getsize(final_path)
                }
                print("✓ Audio merge successful")
            except Exception as e:
                results['audio_merge'] = {'status': 'error', 'error': str(e)}
                print(f"✗ Audio merge failed: {str(e)}")
                raise e
            
            print("\n=== Test Process Complete ===")
            return results
            
        except Exception as e:
            print(f"\n✗ Test process failed: {str(e)}")
            return results
        finally:
            # Cleanup temporary files
            self._cleanup_files([audio_path, temp_audio_path])
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of an audio file in seconds."""
        try:
            probe = ffmpeg.probe(audio_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            return float(probe['format']['duration'])
        except Exception as e:
            print(f"Warning: Could not get audio duration: {str(e)}")
            return 0.0 