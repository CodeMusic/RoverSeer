from flask import Flask, request, jsonify, send_file, redirect, render_template_string, send_file, url_for
from flask_cors import CORS
from flasgger import Swagger, swag_from
from faster_whisper import WhisperModel
import os
import requests
import subprocess
import uuid
import re
import json
import socket
import time
import threading
import random

import sys
sys.path.insert(0, "/home/codemusic/custom_drivers")

from rainbow_driver import RainbowDriver
from gpiozero.tones import Tone

# Global state for audio coordination
tune_playing = threading.Event()
current_display_value = None  # Track what's currently on display

# Global state for model selection and recording
available_models = []
selected_model_index = 0
recording_in_progress = False
MIC_DEVICE = None  # Will be initialized later
# Global system processing indicator
system_processing = False
processing_led_thread = None
stop_processing_led = threading.Event()

# Define tune sequences for different operations
def play_ollama_tune(model_name=None):
    """Play a curious ascending tune when starting Ollama requests - uses model name to guide composition"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            tune_playing.set()
            
            # Base curious tune - extended version
            base_notes = [
                Tone("C4"), Tone("D4"), Tone("E4"), Tone("F4"),
                Tone("G4"), Tone("A4"), Tone("B4"), Tone("C5")
            ]
            
            # If we have a model name, create a unique variation
            if model_name:
                # Extract just the model name part (before colon)
                model_base = model_name.split(':')[0] if ':' in model_name else model_name
                
                # Map letters to musical intervals for variation
                letter_to_interval = {
                    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7,
                    'i': 1, 'j': 2, 'k': 3, 'l': 4, 'm': 5, 'n': 6, 'o': 7, 'p': 0,
                    'q': 1, 'r': 2, 's': 3, 't': 4, 'u': 5, 'v': 6, 'w': 7, 'x': 0,
                    'y': 1, 'z': 2, '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
                    '5': 5, '6': 6, '7': 7, '8': 0, '9': 1
                }
                
                # Create melodic pattern based on model name
                notes = []
                durations = []
                
                # Start with ascending curiosity
                notes.extend([Tone("C4"), Tone("E4"), Tone("G4")])
                durations.extend([0.15, 0.15, 0.2])
                
                # Generate unique middle section based on model name
                for i, char in enumerate(model_base.lower()[:8]):  # Use first 8 chars
                    if char in letter_to_interval:
                        interval = letter_to_interval[char]
                        # Create note based on character position and value
                        base_note_index = (i + interval) % len(base_notes)
                        notes.append(base_notes[base_note_index])
                        # Vary duration based on position
                        duration = 0.1 + (0.05 * (i % 3))
                        durations.append(duration)
                
                # End with questioning rise
                notes.extend([Tone("A4"), Tone("B4"), Tone("C5"), Tone("D5")])
                durations.extend([0.15, 0.15, 0.2, 0.3])
                
            else:
                # Default extended curious tune if no model name
                notes = [
                    Tone("C4"), Tone("D4"), Tone("E4"), Tone("F4"),
                    Tone("G4"), Tone("F4"), Tone("A4"), Tone("G4"),
                    Tone("B4"), Tone("A4"), Tone("C5"), Tone("D5")
                ]
                durations = [
                    0.15, 0.15, 0.15, 0.2,
                    0.15, 0.1, 0.15, 0.1,
                    0.15, 0.1, 0.2, 0.3
                ]
            
            # Play the generated tune
            for note, duration in zip(notes, durations):
                rainbow.buzzer.play(note)
                time.sleep(duration)
                rainbow.buzzer.stop()
                time.sleep(0.05)
                
        except Exception as e:
            print(f"Error playing Ollama tune: {e}")
        finally:
            tune_playing.clear()

def play_ollama_complete_tune():
    """Play a victorious tune when Ollama completes successfully"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            tune_playing.set()
            # Victorious fanfare - major chord arpeggio ending high
            notes = [Tone("C4"), Tone("E4"), Tone("G4"), Tone("C5"), Tone("E5"), Tone("G5")]
            durations = [0.1, 0.1, 0.1, 0.15, 0.15, 0.3]
            for note, duration in zip(notes, durations):
                rainbow.buzzer.play(note)
                time.sleep(duration)
                rainbow.buzzer.stop()
                time.sleep(0.02)
        except Exception as e:
            print(f"Error playing victory tune: {e}")
        finally:
            tune_playing.clear()

def play_transcribe_tune():
    """Play a puzzle-solving pattern for transcription requests"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            tune_playing.set()
            # Puzzle-solving tune - thoughtful, searching pattern
            notes = [Tone("D4"), Tone("G4"), Tone("F4"), Tone("A4"), Tone("G4")]
            durations = [0.2, 0.15, 0.15, 0.2, 0.25]
            for note, duration in zip(notes, durations):
                rainbow.buzzer.play(note)
                time.sleep(duration)
                rainbow.buzzer.stop()
                time.sleep(0.08)
        except Exception as e:
            print(f"Error playing transcribe tune: {e}")
        finally:
            tune_playing.clear()

def play_tts_tune(voice_name=None):
    """Play an announcing fanfare for TTS requests - unique tune based on voice model"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            # Wait for any previous tune to finish
            while tune_playing.is_set():
                time.sleep(0.05)
            
            tune_playing.set()
            
            # Base announcing notes palette
            base_notes = [
                Tone("C5"), Tone("D5"), Tone("E5"), Tone("F5"),
                Tone("G5"), Tone("A5"), Tone("B5"), Tone("C6")
            ]
            
            if voice_name:
                # Extract voice base name (remove file extensions if present)
                voice_base = voice_name.split('.')[0].split('-')[0]
                
                # Map characters to create voice-specific fanfare
                char_to_pattern = {
                    'a': [5, 3, 5, 7], 'b': [0, 2, 4, 6], 'c': [1, 3, 5, 7],
                    'd': [2, 4, 6, 0], 'e': [3, 5, 7, 1], 'f': [4, 6, 0, 2],
                    'g': [5, 7, 1, 3], 'h': [6, 0, 2, 4], 'i': [7, 1, 3, 5],
                    'j': [0, 3, 6, 1], 'k': [1, 4, 7, 2], 'l': [2, 5, 0, 3],
                    'm': [3, 6, 1, 4], 'n': [4, 7, 2, 5], 'o': [5, 0, 3, 6],
                    'p': [6, 1, 4, 7], 'q': [7, 2, 5, 0], 'r': [0, 4, 1, 5],
                    's': [1, 5, 2, 6], 't': [2, 6, 3, 7], 'u': [3, 7, 4, 0],
                    'v': [4, 0, 5, 1], 'w': [5, 1, 6, 2], 'x': [6, 2, 7, 3],
                    'y': [7, 3, 0, 4], 'z': [0, 5, 2, 7], '_': [0, 2, 4, 6]
                }
                
                notes = []
                durations = []
                
                # Start with attention-getting pattern (flows from G5 if after victory)
                notes.extend([Tone("G5"), Tone("G5"), Tone("E5")])
                durations.extend([0.1, 0.1, 0.15])
                
                # Generate voice-specific pattern
                voice_chars = voice_base.lower()[:6]  # Use first 6 characters
                for i, char in enumerate(voice_chars):
                    if char in char_to_pattern:
                        pattern = char_to_pattern[char]
                        # Use character position to vary the pattern
                        note_index = pattern[i % len(pattern)]
                        notes.append(base_notes[note_index])
                        # Create rhythmic variation
                        if i % 2 == 0:
                            durations.append(0.15)
                        else:
                            durations.append(0.1)
                
                # End with distinctive voice signature
                # Different endings for different voice types
                if 'en' in voice_base:  # English voices
                    notes.extend([Tone("C5"), Tone("E5"), Tone("G5"), Tone("C6")])
                    durations.extend([0.1, 0.1, 0.2, 0.4])
                elif 'gb' in voice_base.lower():  # British voices
                    notes.extend([Tone("D5"), Tone("F5"), Tone("A5"), Tone("D6")])
                    durations.extend([0.1, 0.15, 0.2, 0.4])
                else:  # Other voices
                    notes.extend([Tone("E5"), Tone("G5"), Tone("B5"), Tone("E6")])
                    durations.extend([0.1, 0.15, 0.2, 0.4])
                    
            else:
                # Default announcing tune if no voice specified
                notes = [Tone("G5"), Tone("E5"), Tone("C5"), Tone("D5"), 
                        Tone("E5"), Tone("G5"), Tone("C6")]
                durations = [0.15, 0.1, 0.1, 0.15, 0.15, 0.2, 0.4]
            
            # Small pause to separate from previous tune
            time.sleep(0.1)
            
            # Play the generated fanfare
            for note, duration in zip(notes, durations):
                rainbow.buzzer.play(note)
                time.sleep(duration)
                rainbow.buzzer.stop()
                time.sleep(0.03)
                
        except Exception as e:
            print(f"Error playing TTS tune: {e}")
        finally:
            tune_playing.clear()

def get_sensor_data():
    """Get sensor data from BMP280"""
    if rainbow and hasattr(rainbow, 'bmp280'):
        try:
            temp = rainbow.bmp280.temperature
            pressure = rainbow.bmp280.pressure
            # Calculate altitude using standard atmosphere formula
            # P = P0 * (1 - 0.0065 * h / T0) ^ 5.257
            # Solving for h: h = T0/0.0065 * (1 - (P/P0)^(1/5.257))
            P0 = 1013.25  # sea level pressure in hPa
            T0 = 288.15   # standard temperature in K
            altitude = (T0 / 0.0065) * (1 - (pressure / P0) ** (1/5.257))
            return {
                "temperature": f"{temp:.1f}°C",
                "pressure": f"{pressure:.1f} hPa",
                "altitude": f"{altitude:.1f} m"
            }
        except Exception as e:
            print(f"Error reading sensor data: {e}")
    return {
        "temperature": "N/A",
        "pressure": "N/A",
        "altitude": "N/A"
    }

def scroll_text_on_display(text, scroll_speed=0.3):
    """Scroll text across the 4-digit display"""
    if rainbow:
        try:
            import fourletterphat as flp
            # Add spaces for smooth scrolling
            padded_text = "    " + text.upper() + "    "
            for i in range(len(padded_text) - 3):
                flp.clear()
                display_text = padded_text[i:i+4]
                flp.print_str(display_text)
                flp.show()
                time.sleep(scroll_speed)
        except Exception as e:
            print(f"Error scrolling text: {e}")

def display_timer(start_time, stop_event):
    """Display incrementing timer on the display until stop_event is set"""
    global current_display_value
    if rainbow:
        try:
            import fourletterphat as flp
            while not stop_event.is_set():
                elapsed = int(time.time() - start_time)
                rainbow.display_number(elapsed)
                current_display_value = elapsed
                time.sleep(0.1)
        except Exception as e:
            print(f"Error displaying timer: {e}")

def blink_number(number, duration=4, blink_speed=0.3):
    """Blink a number on the display for specified duration"""
    global current_display_value
    if rainbow:
        try:
            import fourletterphat as flp
            end_time = time.time() + duration
            while time.time() < end_time:
                rainbow.display_number(number)
                time.sleep(blink_speed)
                flp.clear()
                flp.show()
                time.sleep(blink_speed)
            # Leave the number on display after blinking
            rainbow.display_number(number)
            current_display_value = number
        except Exception as e:
            print(f"Error blinking number: {e}")

def setup_button_handlers():
    """Setup button handlers for model selection and voice recording"""
    global available_models, selected_model_index, recording_in_progress
    
    if not rainbow:
        return
    
    # Get available models
    available_models = get_model_tags()
    if not available_models:
        available_models = [DEFAULT_MODEL]
    
    # Track which buttons are currently pressed
    buttons_pressed = {'A': False, 'B': False, 'C': False}
    clear_history_timer = None
    
    def check_clear_history():
        """Check if all buttons are pressed to clear history"""
        global button_history, clear_history_timer
        
        if all(buttons_pressed.values()) and not recording_in_progress:
            # All buttons pressed - start timer
            if clear_history_timer is None:
                print("All buttons pressed - hold for 3 seconds to clear history")
                
                def clear_after_delay():
                    time.sleep(3)
                    if all(buttons_pressed.values()):  # Still all pressed
                        button_history.clear()
                        print("Button chat history cleared!")
                        
                        # Play confirmation sound - random 7-note tune
                        if rainbow and hasattr(rainbow, 'buzzer'):
                            # Available notes for random selection
                            available_notes = [
                                Tone("C4"), Tone("D4"), Tone("E4"), Tone("F4"),
                                Tone("G4"), Tone("A4"), Tone("B4"), Tone("C5"),
                                Tone("D5"), Tone("E5"), Tone("F5"), Tone("G5")
                            ]
                            # Generate random 7-note sequence
                            random_notes = [random.choice(available_notes) for _ in range(7)]
                            
                            # Play the random tune
                            for note in random_notes:
                                rainbow.buzzer.play(note)
                                time.sleep(random.uniform(0.08, 0.15))  # Vary timing too
                                rainbow.buzzer.stop()
                                time.sleep(0.02)
                        
                        # Flash all LEDs
                        for _ in range(3):
                            for led in ['A', 'B', 'C']:
                                rainbow.button_leds[led].on()
                            time.sleep(0.2)
                            for led in ['A', 'B', 'C']:
                                rainbow.button_leds[led].off()
                            time.sleep(0.2)
                
                clear_history_timer = threading.Thread(target=clear_after_delay)
                clear_history_timer.daemon = True
                clear_history_timer.start()
    
    def handle_button_a():
        """Toggle to previous model"""
        global selected_model_index
        buttons_pressed['A'] = True
        check_clear_history()
        
        if not recording_in_progress and not all(buttons_pressed.values()):
            print(f"Button A pressed, recording_in_progress={recording_in_progress}")
            rainbow.button_leds['A'].on()  # LED on when pressed
            play_toggle_left_sound()
            
            # Cycle to previous model
            selected_model_index = (selected_model_index - 1) % len(available_models)
            
            # Display model name briefly
            model_name = available_models[selected_model_index].split(':')[0]
            scroll_text_on_display(model_name, scroll_speed=0.2)
            
            # Show model index after scrolling
            rainbow.display_number(selected_model_index)
    
    def handle_button_a_release():
        """Handle button A release"""
        buttons_pressed['A'] = False
        if not recording_in_progress and not any(buttons_pressed.values()):
            rainbow.button_leds['A'].off()  # LED off when released
            play_toggle_left_echo()
    
    def handle_button_c():
        """Toggle to next model"""
        global selected_model_index
        buttons_pressed['C'] = True
        check_clear_history()
        
        if not recording_in_progress and not all(buttons_pressed.values()):
            rainbow.button_leds['C'].on()  # LED on when pressed
            play_toggle_right_sound()
            
            # Cycle to next model
            selected_model_index = (selected_model_index + 1) % len(available_models)
            
            # Display model name briefly
            model_name = available_models[selected_model_index].split(':')[0]
            scroll_text_on_display(model_name, scroll_speed=0.2)
            
            # Show model index after scrolling
            rainbow.display_number(selected_model_index)
    
    def handle_button_c_release():
        """Handle button C release"""
        buttons_pressed['C'] = False
        if not recording_in_progress and not any(buttons_pressed.values()):
            rainbow.button_leds['C'].off()  # LED off when released
            play_toggle_right_echo()
    
    def handle_button_b():
        """Start recording on button press - LED solid while held"""
        global recording_in_progress
        buttons_pressed['B'] = True
        check_clear_history()
        
        if recording_in_progress or all(buttons_pressed.values()):
            return  # Ignore if already recording or clearing history
        
        # LED solid on while button is held
        rainbow.button_leds['B'].on()
    
    def handle_button_b_release():
        """Start the recording pipeline on button release"""
        global recording_in_progress
        buttons_pressed['B'] = False
        
        if recording_in_progress or all(buttons_pressed.values()):
            return  # Ignore if already recording or clearing history
        
        recording_in_progress = True
        
        # Start system processing (transitions to blinking)
        start_system_processing()
        
        def recording_pipeline():
            global recording_in_progress
            try:
                # Play confirmation sound
                play_confirmation_sound()
                
                # Record audio for 10 seconds
                temp_recording = f"/tmp/recording_{uuid.uuid4().hex}.wav"
                
                # Display countdown during recording
                def show_countdown():
                    for i in range(10, 0, -1):
                        if rainbow:
                            rainbow.display_number(i)
                        time.sleep(1)
                
                # Start recording with arecord
                record_cmd = [
                    'arecord',
                    '-D', MIC_DEVICE,
                    '-f', 'S16_LE',
                    '-r', '16000',
                    '-c', '1',
                    '-d', '10',
                    temp_recording
                ]
                
                # Run recording and countdown in parallel
                record_process = subprocess.Popen(record_cmd, 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
                
                countdown_thread = threading.Thread(target=show_countdown)
                countdown_thread.start()
                
                # Wait for recording to complete
                record_process.wait()
                countdown_thread.join()
                
                # Play recording complete sound
                play_recording_complete_sound()
                
                # 1. Speech to Text
                transcript = None
                try:
                    transcript = transcribe_audio(temp_recording)
                    os.remove(temp_recording)
                except Exception as e:
                    print(f"Transcription error: {e}")
                    transcript = "Hello, testing the system."
                
                # 2. Run LLM with selected model (will keep LED blinking)
                selected_model = available_models[selected_model_index]
                
                # Build message history with model context
                messages = []
                
                # Add conversation history (including which model said what)
                for hist_user, hist_reply, hist_model in button_history[-MAX_BUTTON_HISTORY:]:
                    # Include model name in assistant messages for context
                    model_prefix = f"[{hist_model.split(':')[0]}]: " if hist_model != selected_model else ""
                    messages.append({"role": "user", "content": hist_user})
                    messages.append({"role": "assistant", "content": model_prefix + hist_reply})
                
                # Add current user message
                messages.append({"role": "user", "content": transcript})
                
                # System message that includes model switching context
                system_message = (
                    "You are RoverSeer, a helpful voice assistant. Keep responses concise and conversational. "
                    f"You are currently running as model '{selected_model.split(':')[0]}'. "
                    "Previous responses may be from different models, indicated by [model_name]: prefix. "
                    "You can reference what other models said if asked."
                )
                
                reply = run_chat_completion(selected_model, messages, system_message)
                
                # Save to button history
                button_history.append((transcript, reply, selected_model))
                if len(button_history) > MAX_BUTTON_HISTORY * 2:  # Keep some buffer
                    button_history.pop(0)
                
                print(f"Button chat history: {len(button_history)} exchanges")
                
                # 3. Text to Speech with default voice
                voice = DEFAULT_VOICE
                
                # Generate and play audio response
                model_path, config_path = find_voice_files(voice)
                tmp_wav = f"/tmp/{uuid.uuid4().hex}.wav"
                
                play_tts_tune(voice)
                
                tts_result = subprocess.run(
                    ["/home/codemusic/roverseer_venv/bin/piper",
                     "--model", model_path,
                     "--config", config_path,
                     "--output_file", tmp_wav],
                    input=reply.encode(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                if tts_result.returncode == 0:
                    # Play the audio response
                    play_process = subprocess.run(["aplay", "-D", AUDIO_DEVICE, tmp_wav])
                    os.remove(tmp_wav)
                
            except Exception as e:
                print(f"Error in recording pipeline: {e}")
            finally:
                # Stop system processing indicator
                stop_system_processing()
                
                # Reset recording flag
                recording_in_progress = False
                
                # Clear display
                if rainbow:
                    import fourletterphat as flp
                    flp.clear()
                    flp.show()
                
                print("Recording pipeline complete, buttons re-enabled")
        
        # Run pipeline in separate thread
        pipeline_thread = threading.Thread(target=recording_pipeline)
        pipeline_thread.daemon = True
        pipeline_thread.start()
    
    # Setup button handlers with both press and release
    rainbow.buttons['A'].when_pressed = handle_button_a
    rainbow.buttons['A'].when_released = handle_button_a_release
    rainbow.buttons['B'].when_pressed = handle_button_b
    rainbow.buttons['B'].when_released = handle_button_b_release
    rainbow.buttons['C'].when_pressed = handle_button_c
    rainbow.buttons['C'].when_released = handle_button_c_release

def play_toggle_left_sound():
    """Play a descending sound for toggling left/previous"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            notes = [Tone("E5"), Tone("C5")]
            for note in notes:
                rainbow.buzzer.play(note)
                time.sleep(0.1)
                rainbow.buzzer.stop()
        except Exception as e:
            print(f"Error playing toggle left sound: {e}")

def play_toggle_right_sound():
    """Play an ascending sound for toggling right/next"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            notes = [Tone("C5"), Tone("E5")]
            for note in notes:
                rainbow.buzzer.play(note)
                time.sleep(0.1)
                rainbow.buzzer.stop()
        except Exception as e:
            print(f"Error playing toggle right sound: {e}")

def play_confirmation_sound():
    """Play a confirmation sound for recording start"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            # Two quick high beeps
            for _ in range(2):
                rainbow.buzzer.play(Tone("A5"))
                time.sleep(0.08)
                rainbow.buzzer.stop()
                time.sleep(0.05)
        except Exception as e:
            print(f"Error playing confirmation sound: {e}")

def play_recording_complete_sound():
    """Play a sound when recording completes"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            # Descending completion sound
            notes = [Tone("G5"), Tone("E5"), Tone("C5")]
            for note in notes:
                rainbow.buzzer.play(note)
                time.sleep(0.08)
                rainbow.buzzer.stop()
        except Exception as e:
            print(f"Error playing recording complete sound: {e}")

def play_toggle_left_echo():
    """Play a quieter echo of the toggle left sound on release"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            # Same notes but shorter and quieter
            notes = [Tone("E4")]  # One octave lower for echo
            for note in notes:
                rainbow.buzzer.play(note)
                time.sleep(0.05)  # Shorter duration
                rainbow.buzzer.stop()
        except Exception as e:
            print(f"Error playing toggle left echo: {e}")

def play_toggle_right_echo():
    """Play a quieter echo of the toggle right sound on release"""
    if rainbow and hasattr(rainbow, 'buzzer'):
        try:
            # Same notes but shorter and quieter
            notes = [Tone("C4")]  # One octave lower for echo
            for note in notes:
                rainbow.buzzer.play(note)
                time.sleep(0.05)  # Shorter duration
                rainbow.buzzer.stop()
        except Exception as e:
            print(f"Error playing toggle right echo: {e}")

def start_system_processing():
    """Start the system processing indicator (blinking green LED)"""
    global system_processing, processing_led_thread, stop_processing_led
    
    if system_processing:
        return  # Already processing
    
    system_processing = True
    stop_processing_led.clear()
    
    def blink_processing_led():
        while not stop_processing_led.is_set():
            if rainbow:
                rainbow.button_leds['B'].on()
            time.sleep(0.3)
            if stop_processing_led.is_set():
                break
            if rainbow:
                rainbow.button_leds['B'].off()
            time.sleep(0.3)
        # Ensure LED is off when done
        if rainbow:
            rainbow.button_leds['B'].off()
    
    processing_led_thread = threading.Thread(target=blink_processing_led)
    processing_led_thread.daemon = True
    processing_led_thread.start()

def stop_system_processing():
    """Stop the system processing indicator"""
    global system_processing
    
    system_processing = False
    stop_processing_led.set()
    
    # Wait for thread to finish
    if processing_led_thread and processing_led_thread.is_alive():
        processing_led_thread.join(timeout=1)
    
    # Ensure LED is off
    if rainbow:
        rainbow.button_leds['B'].off()

# Define TCP services
tcp_services = {
    "Wyoming Piper": 10200,
    "Wyoming Whisper": 10300,
    "JupyterLab": 8888,
    "Ollama": 11434,
    "Open WebUI": 3000,
    "Redmine": 3333,
    "Home Assistant": 8123,
    "Custom API": 5000
}

def check_tcp_ports():
    results = {}
    for name, port in tcp_services.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            results[name] = {"status": "🟢", "port": port}
        else:
            results[name] = {"status": "🔴", "port": port}
        sock.close()
    return results

whisper_model = WhisperModel("base", compute_type="int8")  # or "medium" if you want higher quality

def transcribe_audio(file_path):
    play_transcribe_tune()  # Play tune when transcribing
    segments, info = whisper_model.transcribe(file_path)
    return " ".join([segment.text for segment in segments])

def run_chat_completion(model, messages, system_message=None):
    start_system_processing()  # Start blinking LED for any LLM request
    play_ollama_tune(model)  # Play curious tune with model-specific variation
    
    # Start timer and display handling
    start_time = time.time()
    stop_timer = threading.Event()
    
    # Extract model name (before the colon if present)
    model_display_name = model.split(':')[0] if ':' in model else model
    
    # Start a thread to handle display
    def display_handler():
        # First scroll the model name
        scroll_text_on_display(model_display_name, scroll_speed=0.2)
        # Then show the timer
        display_timer(start_time, stop_timer)
    
    display_thread = threading.Thread(target=display_handler)
    display_thread.daemon = True
    display_thread.start()
    
    try:
        if system_message and not any(msg.get("role") == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": system_message})

        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={"model": model, "messages": messages}
        )
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        
        # Stop timer and calculate elapsed time
        stop_timer.set()
        elapsed_time = int(time.time() - start_time)
        
        # Play victory tune
        play_ollama_complete_tune()
        
        # Blink the elapsed time in a separate thread (non-blocking)
        def blink_async():
            blink_number(elapsed_time, duration=4, blink_speed=0.3)
        
        blink_thread = threading.Thread(target=blink_async)
        blink_thread.daemon = True
        blink_thread.start()
        
        return result
        
    except Exception as e:
        stop_timer.set()
        stop_system_processing()
        raise e

def detect_usb_mic_device():
    """
    Detects the first USB capture device using arecord -l.
    Returns a string like 'plughw:0,0' or 'default' if not found.
    """
    try:
        result = subprocess.run(['arecord', '-l'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if 'USB Audio' in line or 'PnP Sound Device' in line:
                match = re.search(r'card (\d+): .*?\[.*?\], device (\d+):', line)
                if match:
                    card = match.group(1)
                    device = match.group(2)
                    return f"plughw:{card},{device}"
    except Exception as e:
        print(f"Mic detection failed: {e}")
    
    return "default"

def detect_usb_audio_device():
    try:
        result = subprocess.run(['aplay', '-l'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if 'USB Audio' in line:
                match = re.search(r'card (\d+):', line)
                if match:
                    return f"plughw:{match.group(1)},0"
    except Exception as e:
        print(f"Audio detection failed: {e}")
    return "default"

AUDIO_DEVICE = detect_usb_audio_device()
MIC_DEVICE = detect_usb_mic_device()  # Initialize microphone device
VOICES_DIR = "/home/codemusic/piper/voices"
DEFAULT_MODEL = "tinydolphin:1.1b"
DEFAULT_VOICE = os.environ.get("PIPER_VOICE", "en_GB-jarvis")
history = []
MAX_HISTORY = 10  # Max number of exchanges to retain for context
VOICES_DIR = "/home/codemusic/piper/voices"

# Separate history for button-initiated conversations
button_history = []
MAX_BUTTON_HISTORY = 10  # Max number of button chat exchanges to retain

# -------- DYNAMIC VOICE DETECTION -------- #
def list_voice_ids():
    base_names = set()
    for fname in os.listdir(VOICES_DIR):
        if fname.endswith(".onnx") and not fname.endswith(".onnx.json"):
            base = fname.rsplit("-", 1)[0]
            base_names.add(base)
    return sorted(base_names)

def find_voice_files(base_voice_id):
    pattern_prefix = f"{base_voice_id}-"
    model_file = None
    config_file = None
    for fname in os.listdir(VOICES_DIR):
        if fname.startswith(pattern_prefix):
            if fname.endswith(".onnx") and not fname.endswith(".onnx.json"):
                model_file = os.path.join(VOICES_DIR, fname)
            elif fname.endswith(".onnx.json"):
                config_file = os.path.join(VOICES_DIR, fname)
        if model_file and config_file:
            break
    if not model_file or not config_file:
        raise FileNotFoundError(f"Missing model or config for voice: {base_voice_id}")
    return model_file, config_file

# -------- DYNAMIC MODEL DETECTION -------- #

def get_model_tags():
    try:
        res = requests.get("http://roverseer.local:11434/api/tags")
        if res.ok:
            tags = res.json().get("models", [])
            return sorted(tag.get("name") for tag in tags if tag.get("name"))
    except Exception as e:
        print(f"Error fetching model tags: {e}")
    return []


# -------- FLASK APP + SWAGGER -------- #
app = Flask(__name__)
CORS(app)

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "RoverSeer API",
        "description": "Text-to-speech powered by Piper and gTTS.",
        "version": "1.0.0"
    },
    "basePath": "/",
}, config={
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
})

@app.route('/docs/')
def redirect_docs():
    return redirect("/docs", code=302)

@app.route("/static/<filename>")
def serve_static(filename):
    return send_file(os.path.join("/tmp", filename))


@app.route("/", methods=['GET', 'POST'])
def home():
    global history
    statuses = check_tcp_ports()
    models = get_model_tags()
    voices = list_voice_ids()

    global history
    statuses = check_tcp_ports()
    models = get_model_tags()
    voices = list_voice_ids()    
    sensor_data = get_sensor_data()  # Get sensor data
    selected_model = "tinydolphin:1.1b"
    selected_voice = "en_GB-jarvis"
    reply_text = ""
    audio_url = None
    if request.method == 'POST':
        output_type = request.form.get('output_type')
        model = request.form.get('model')
        voice = request.form.get('voice')
        selected_model = model
        selected_voice = voice
        system = request.form.get('system')
        user_input = request.form.get('user_input')

        # Build message history context
        messages = []
        for user_msg, ai_reply, _ in history[-MAX_HISTORY:]:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": ai_reply})
        messages.append({"role": "user", "content": user_input})

        endpoint = output_type
        payload = {
            "model": model,
            "system": system,
            "messages": messages
        }
        if endpoint in ['speak_chat']:
            payload["voice"] = voice

        try:
            if endpoint == 'chat_tts':
                tmp_audio = f"{uuid.uuid4().hex}.wav"
                res = requests.post(f"http://localhost:5000/chat_tts", json=payload)
                if res.ok:
                    with open(f"/tmp/{tmp_audio}", 'wb') as f:
                        f.write(res.content)
                    audio_url = url_for('serve_static', filename=tmp_audio)
                    reply_text = "(Audio response returned)"
                else:
                    reply_text = f"Error: {res.text}"
            else:
                res = requests.post(f"http://localhost:5000/{endpoint}", json=payload)
                if res.ok:
                    data = res.json()
                    reply_text = data.get("spoken_text") or data.get("reply") or data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    reply_text = f"Error: {res.text}"

            history.append((user_input, reply_text, model))
        except Exception as e:
            reply_text = f"Request failed: {e}"

    html = '''
    <html>
    <head>
        <title>RoverSeer Status</title>
        <style>
            body { font-family: Arial; background: #f4f4f4; color: #333; margin: 20px; }
            .topbar { background: #333; color: white; padding: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
            .status-container { display: flex; flex-wrap: wrap; align-items: center; gap: 15px; }
            .status-section { display: flex; flex-wrap: wrap; align-items: center; }
            .status-item { margin-right: 10px; }
            .sensor-data { background: #444; padding: 8px 12px; border-radius: 5px; display: flex; gap: 15px; }
            .sensor-item { display: flex; align-items: center; gap: 5px; }
            .refresh { cursor: pointer; font-size: 20px; }
            .chatbox { background: white; padding: 15px; border-radius: 8px; margin-top: 20px; box-shadow: 0 0 8px rgba(0,0,0,0.1); }
            textarea, input, select { width: 100%; padding: 8px; margin: 5px 0; }
            button { padding: 10px 15px; }
            .history { background: #eef; padding: 10px; margin-top: 20px; border-radius: 8px; }
        </style>
        <script>
            function refreshPage() {
                window.location.reload();
            }
        </script>
    </head>
    <body>
        <div class="topbar">
            <div><strong>RoverSeer TCP Status</strong></div>
            <div class="status-container">
                <div class="status-section">
                    {% for name, info in statuses.items() %}
                        <span class="status-item">{{ info.status }} {{ name }} ({{ info.port }})</span>
                    {% endfor %}
                </div>
                <div class="sensor-data">
                    <span class="sensor-item">🌡️ {{ sensor_data.temperature }}</span>
                    <span class="sensor-item">🌊 {{ sensor_data.pressure }}</span>
                    <span class="sensor-item">🏔️ {{ sensor_data.altitude }}</span>
                </div>
                <span class="refresh" onclick="refreshPage()">🔄</span>
            </div>
        </div>

        <div class="chatbox">
            <h2>RoverSeer Quick Dialog</h2>
            <form method="post">
                <label>Output Type:</label>
                <select name="output_type">
                    <option value="speak_chat">RoverSeer</option>
                    <option value="chat_tts">Local Audio</option>
                    <option value="chat">Local Text</option>
                </select>
                <label>System Message:</label>
                <input type="text" name="system" value="You are RoverSeer, a helpful assistant." />
                <label>Model:</label>
                <select name="model">
                    {% for tag in models %}
                        <option value="{{ tag }}" {% if tag == selected_model %}selected{% endif %}>{{ tag }}</option>
                    {% endfor %}
                </select>
                <label>Voice (if used):</label>
                <select name="voice">
                    {% for v in voices %}
                        <option value="{{ v }}" {% if v == selected_voice %}selected{% endif %}>{{ v }}</option>
                    {% endfor %}
                </select>
                <label>Your Message:</label>
                <textarea name="user_input">Tell me a fun science fact.</textarea>
                <button type="submit">Send</button>
            </form>
            <h3>Response:</h3>
            <p>{{ reply_text }}</p>
            {% if audio_url %}
            <audio controls autoplay>
                <source src="{{ audio_url }}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
            {% endif %}

            <div class="history">
                <h3>Conversation History:</h3>
                {% for user, reply, model in history %}
                    <p><strong>You:</strong> {{ user }}</p>
                    <p><strong>{{ model }}:</strong> {{ reply }}</p>
                    <hr>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, statuses=statuses, reply_text=reply_text, audio_url=audio_url, history=history, models=models, selected_model=selected_model, voices=voices, selected_voice=selected_voice, sensor_data=sensor_data)


# -------- STATIC SWAGGER for /say -------- #
say_spec = {
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "example": "Hello from RoverSeer!"
                    },
                    "voice": {
                        "type": "string",
                        "enum": list_voice_ids(),
                        "default": DEFAULT_VOICE
                    }
                },
                "required": ["text"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Audio spoken"
        }
    }
}

@app.route('/say', methods=['POST'])
@swag_from(say_spec)
def say():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid or missing JSON body"}), 400

    text = data.get("text", "").strip()
    voice_id = data.get("voice", DEFAULT_VOICE)

    if not text:
        return jsonify({"status": "error", "message": "No text provided"}), 400

    try:
        model_path, config_path = find_voice_files(voice_id)
        tmp_wav = f"/tmp/{uuid.uuid4().hex}.wav"

        play_tts_tune(voice_id)  # Play tune before TTS
        result = subprocess.run(
            ["/home/codemusic/roverseer_venv/bin/piper",
             "--model", model_path,
             "--config", config_path,
             "--output_file", tmp_wav],
            input=text.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "message": f"Piper TTS failed: {result.stderr.decode()}"
            }), 500

        subprocess.run(["aplay", "-D", AUDIO_DEVICE, tmp_wav])
        os.remove(tmp_wav)
        
        # Stop system processing after TTS completes
        stop_system_processing()

        return jsonify({"status": "success", "message": f"Spoken with {voice_id}: {text}"})
    except Exception as e:
        stop_system_processing()
        return jsonify({"status": "error", "message": str(e)}), 500

# -------- TTS-to-WAV Download Endpoint (Piper) -------- #
@app.route('/tts', methods=['POST'])
def tts():
    """
    Generate and return WAV audio using Piper TTS.
    ---
    consumes:
      - application/json
    parameters:
      - name: text
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              example: This is a downloadable file
    produces:
      - audio/wav
    responses:
      200:
        description: WAV file returned
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid or missing JSON body"}), 400

    text = data.get("text", "").strip()
    voice_id = data.get("voice", DEFAULT_VOICE)

    if not text:
        return jsonify({"status": "error", "message": "No text provided"}), 400

    try:
        model_path, config_path = find_voice_files(voice_id)
        tmp_wav = f"/tmp/{uuid.uuid4().hex}.wav"

        play_tts_tune(voice_id)  # Play tune before TTS
        result = subprocess.run(
            ["/home/codemusic/roverseer_venv/bin/piper",
             "--model", model_path,
             "--config", config_path,
             "--output_file", tmp_wav],
            input=text.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "message": f"Piper TTS failed: {result.stderr.decode()}"
            }), 500

        return send_file(tmp_wav, mimetype="audio/wav", as_attachment=True, download_name="tts.wav")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat with an Ollama model using OpenAI-compatible format.
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: chat
        required: true
        schema:
          type: object
          properties:
            model:
              type: string
              example: tinydolphin:1.1b
            system:
              type: string
              example: You are RoverSeer, a helpful assistant.
            messages:
              type: array
              items:
                type: object
                properties:
                  role:
                    type: string
                    example: user
                  content:
                    type: string
                    example: What's the weather like on Mars?
          required:
            - messages
    responses:
      200:
        description: Chat completion from Ollama
    """
    try:
        data = request.get_json(silent=True)
        if not data or "messages" not in data:
            return jsonify({"error": "Missing messages"}), 400

        model = data.get("model", DEFAULT_MODEL)
        messages = data.get("messages", [])
        system_message = data.get("system", "You are RoverSeer, a helpful assistant AI.")

        reply = run_chat_completion(model, messages, system_message)
        
        # Stop system processing since no TTS follows
        stop_system_processing()

        return jsonify({
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(uuid.uuid1().time),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(json.dumps(messages).split()),
                "completion_tokens": len(reply.split()),
                "total_tokens": len(json.dumps(messages).split()) + len(reply.split())
            }
        })

    except Exception as e:
        stop_system_processing()
        return jsonify({"error": str(e)}), 500

@app.route('/speak_chat', methods=['POST'])
def speak_chat():
    """
    Chat with Ollama and vocalize the assistant's response.
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            model:
              type: string
              example: tinydolphin:1.1b
            system:
              type: string
              example: You are a witty assistant named RoverSeer.
            voice:
              type: string
              example: en_GB-jarvis
            messages:
              type: array
              items:
                type: object
                properties:
                  role:
                    type: string
                    example: user
                  content:
                    type: string
                    example: Tell me a fun science fact.
          required:
            - messages
    responses:
      200:
        description: Assistant's reply spoken and returned.
    """
    data = request.get_json(silent=True)
    if not data or "messages" not in data:
        return jsonify({"status": "error", "message": "Missing messages"}), 400

    model = data.get("model", DEFAULT_MODEL)
    voice = data.get("voice", DEFAULT_VOICE)
    messages = data.get("messages", [])
    system_message = data.get("system", "You are RoverSeer, a voice-based assistant.")

    try:
        reply = run_chat_completion(model, messages, system_message)

        say_response = requests.post("http://localhost:5000/say", json={"text": reply, "voice": voice})
        say_response.raise_for_status()

        return jsonify({
            "status": "success",
            "model": model,
            "spoken_text": reply,
            "voice_used": voice
        })

    except Exception as e:
        stop_system_processing()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/insight', methods=['POST'])
def insight():
    """
    Quick single-prompt chat with optional system role.
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: input
        required: true
        schema:
          type: object
          properties:
            model:
              type: string
              example: tinydolphin:1.1b
            system:
              type: string
              example: You are RoverSeer, an expert on strange animal facts.
            prompt:
              type: string
              example: Tell me a weird fact about platypuses.
          required:
            - prompt
    responses:
      200:
        description: Ollama single-turn response
    """
    data = request.get_json(silent=True)
    if not data or "prompt" not in data:
        return jsonify({"status": "error", "message": "Missing prompt"}), 400

    model = data.get("model", DEFAULT_MODEL)
    prompt = data["prompt"].strip()
    messages = [{"role": "user", "content": prompt}]
    system_message = data.get("system", "You are RoverSeer, an insightful assistant.")

    try:
        reply = run_chat_completion(model, messages, system_message)
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat_tts', methods=['POST'])
def chat_tts():
    """
    Chat with Ollama and return spoken response as a WAV file.
    ---
    consumes:
      - multipart/form-data
    produces:
      - audio/wav
    parameters:
      - in: body
        name: chat
        required: true
        schema:
          type: object
          properties:
            model:
              type: string
              example: tinydolphin:1.1b
            system:
              type: string
              example: You are RoverSeer, a helpful and concise assistant.
            voice:
              type: string
              example: en_GB-jarvis
            messages:
              type: array
              items:
                type: object
                properties:
                  role:
                    type: string
                    example: user
                  content:
                    type: string
                    example: Tell me a surprising moon fact.
          required:
            - messages
    responses:
      200:
        description: Returns a .wav file with the assistant's reply
    """
    data = request.get_json(silent=True)
    if not data or "messages" not in data:
        return jsonify({"status": "error", "message": "Missing messages"}), 400

    model = data.get("model", DEFAULT_MODEL)
    voice = data.get("voice", DEFAULT_VOICE)
    system_message = data.get("system", "You are RoverSeer, an adaptive assistant.")
    messages = data["messages"]

    # Insert system message at the top of the conversation if not already present
    if not any(msg.get("role") == "system" for msg in messages):
        messages.insert(0, {"role": "system", "content": system_message})

    try:
        # Get response from Ollama
        r = requests.post(
            "http://localhost:11434/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={"model": model, "messages": messages}
        )
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]

        # Generate WAV with Piper
        model_path, config_path = find_voice_files(voice)
        tmp_wav = f"/tmp/{uuid.uuid4().hex}.wav"
        play_tts_tune(voice)  # Play tune before TTS
        tts_result = subprocess.run(
            ["/home/codemusic/roverseer_venv/bin/piper",
             "--model", model_path,
             "--config", config_path,
             "--output_file", tmp_wav],
            input=reply.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if tts_result.returncode != 0:
            return jsonify({
                "status": "error",
                "message": f"Piper TTS failed: {tts_result.stderr.decode()}"
            }), 500

        return send_file(tmp_wav, mimetype="audio/wav", as_attachment=True, download_name="chat_tts.wav")

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
  
@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcribe_openai_style():
    """
    OpenAI-style Whisper transcription endpoint
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        required: true
        type: file
    responses:
      200:
        description: Transcription in OpenAI format
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    tmp_path = f"/tmp/{uuid.uuid4().hex}.wav"
    file.save(tmp_path)

    try:
        transcript = transcribe_audio(tmp_path)
        os.remove(tmp_path)
        return jsonify({"text": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/audio/chat', methods=['POST'])
def transcribe_and_chat():
    """
    Transcribe audio and send result to LLM chat, returning assistant's reply.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
      - in: formData
        name: model
        type: string
        required: false
        default: tinydolphin:1.1b
      - in: formData
        name: voice
        type: string
        required: false
        default: en_GB-jarvis
    responses:
      200:
        description: Assistant's response to transcribed speech
    """
    if 'file' not in request.files:
        return jsonify({"error": "Missing audio file"}), 400

    file = request.files['file']
    model = request.form.get('model', DEFAULT_MODEL)
    voice = request.form.get('voice', DEFAULT_VOICE)

    tmp_path = f"/tmp/{uuid.uuid4().hex}.wav"
    file.save(tmp_path)

    try:
        # Transcribe audio
        transcript = transcribe_audio(tmp_path)
        os.remove(tmp_path)

        # Send to LLM
        messages = [{"role": "user", "content": transcript}]
        system_message = "You are RoverSeer, a helpful assistant responding to transcribed audio."

        reply = run_chat_completion(model, messages, system_message)

        return jsonify({
            "transcript": transcript,
            "model": model,
            "voice": voice,
            "reply": reply
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/v1/audio/speak_chat', methods=['POST'])
def transcribe_chat_and_speak():
    """
    Transcribe audio, get LLM response, and speak it aloud via speaker.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
      - in: formData
        name: model
        type: string
        required: false
        default: tinydolphin:1.1b
      - in: formData
        name: voice
        type: string
        required: false
        default: en_GB-jarvis
    responses:
      200:
        description: Assistant's reply spoken aloud and returned as text
    """
    if 'file' not in request.files:
        return jsonify({"error": "Missing audio file"}), 400

    file = request.files['file']
    model = request.form.get('model', DEFAULT_MODEL)
    voice = request.form.get('voice', DEFAULT_VOICE)

    tmp_audio = f"/tmp/{uuid.uuid4().hex}.wav"
    tmp_output = f"/tmp/{uuid.uuid4().hex}_spoken.wav"
    file.save(tmp_audio)

    try:
        # 1. Transcribe
        transcript = transcribe_audio(tmp_audio)
        os.remove(tmp_audio)

        # 2. LLM reply
        messages = [{"role": "user", "content": transcript}]
        system_message = "You are RoverSeer, a live voice assistant."
        reply = run_chat_completion(model, messages, system_message)

        # 3. TTS (Piper)
        model_path, config_path = find_voice_files(voice)
        play_tts_tune(voice)  # Play tune before TTS
        tts_result = subprocess.run(
            ["/home/codemusic/roverseer_venv/bin/piper",
             "--model", model_path,
             "--config", config_path,
             "--output_file", tmp_output],
            input=reply.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if tts_result.returncode != 0:
            return jsonify({
                "error": "Piper failed",
                "stderr": tts_result.stderr.decode()
            }), 500

        # 4. Speak it!
        subprocess.run(["aplay", "-D", AUDIO_DEVICE, tmp_output])
        os.remove(tmp_output)

        return jsonify({
            "transcript": transcript,
            "reply": reply,
            "voice": voice,
            "model": model
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/audio/chat_tts', methods=['POST'])
def transcribe_chat_tts():
    """
    Transcribe audio, get assistant response, and return spoken audio.
    ---
    consumes:
      - multipart/form-data
    produces:
      - audio/wav
    parameters:
      - in: formData
        name: file
        type: file
        required: true
      - in: formData
        name: model
        type: string
        required: false
        default: tinydolphin:1.1b
      - in: formData
        name: voice
        type: string
        required: false
        default: en_GB-jarvis
    responses:
      200:
        description: Assistant's spoken response (WAV)
    """
    if 'file' not in request.files:
        return jsonify({"error": "Missing audio file"}), 400

    file = request.files['file']
    model = request.form.get('model', DEFAULT_MODEL)
    voice = request.form.get('voice', DEFAULT_VOICE)

    tmp_audio = f"/tmp/{uuid.uuid4().hex}.wav"
    tmp_response = f"/tmp/{uuid.uuid4().hex}_response.wav"
    file.save(tmp_audio)

    try:
        # 1. Transcribe
        transcript = transcribe_audio(tmp_audio)
        os.remove(tmp_audio)

        # 2. LLM reply
        messages = [{"role": "user", "content": transcript}]
        system_message = "You are RoverSeer, a helpful assistant responding to transcribed voice input."
        reply = run_chat_completion(model, messages, system_message)

        # 3. TTS (Piper)
        model_path, config_path = find_voice_files(voice)
        play_tts_tune(voice)  # Play tune before TTS
        tts_result = subprocess.run(
            ["/home/codemusic/roverseer_venv/bin/piper",
             "--model", model_path,
             "--config", config_path,
             "--output_file", tmp_response],
            input=reply.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if tts_result.returncode != 0:
            return jsonify({
                "error": "Piper failed",
                "stderr": tts_result.stderr.decode()
            }), 500

        # 4. Return WAV
        return send_file(tmp_response, mimetype="audio/wav", as_attachment=True, download_name="response.wav")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize Rainbow Driver before running the app
rainbow = None
try:
    rainbow = RainbowDriver(num_leds=7, brightness=2)
    setup_button_handlers()  # Setup button handlers after initialization
    print("✅ Rainbow Driver initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Rainbow Driver: {e}")
    rainbow = None

# -------- MAIN -------- #
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
