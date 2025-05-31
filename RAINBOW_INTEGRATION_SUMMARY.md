# RoverSeer Rainbow Driver Integration Summary

## Features Added

### 1. Audio Feedback with Dynamic Thematic Tunes
- **Ollama Start**: Dynamic curious tune based on model name
  - Each model gets a unique musical signature
  - Longer, more complex tune (up to 15+ notes)
  - Model name characters guide the melodic progression
- **Ollama Complete**: Victorious fanfare (C4→E4→G4→C5→E5→G5)
- **Speech-to-Text**: Puzzle-solving pattern (D4→G4→F4→A4→G4)
- **Text-to-Speech**: Dynamic announcing fanfare based on voice model
  - Each voice gets its own unique fanfare
  - Special patterns for English (en) and British (gb) voices
  - Voice name characters create unique melodic patterns
  - TTS tune waits for previous tunes to finish
- **Timer Ticking Sounds** (NEW):
  - Two modes controlled by `TICK_TYPE` global variable
  - "clock" mode: Alternating tick (E5) and tock (C4) sounds
  - "music" mode: Melodic progression through pentatonic scale
  - Very soft sounds (0.02s for clock, 0.015s for music)
  - Only plays during LLM processing when timer is visible

### 2. Visual Timer Display
When calling Ollama/LLM:
1. Model name scrolls across 4-digit display
2. **0.5 second delay before timer starts** (NEW)
3. **Display cleared before timer begins** (NEW)
4. Timer shows elapsed seconds during processing with optional ticking sounds
5. On completion: elapsed time blinks for 4 seconds (non-blocking)
6. Final time remains on display until next request
7. **Display state tracking prevents overlap** (NEW)

### 3. Voice Assistant Mode (Button Controls)
- **Button A (Left)**: Select previous AI model
  - LED lights on press, off on release
  - Plays descending toggle sound + echo
  - Scrolls model name on display
  - Shows model index number
  - **Can interrupt audio playback** (NEW)
- **Button B (Center)**: Start voice recording
  - LED solid while held
  - **LED blinks during 10-second recording** (NEW)
  - Plays confirmation beep (2 quick tones)
  - Records for 10 seconds with countdown display
  - **Progressive LED stages** (NEW):
    - Red blinks during ASR, then stays solid
    - Green blinks during LLM with red solid
    - Blue blinks during TTS with red+green solid
    - All three blink during audio playback
    - All turn off when complete
  - **Can interrupt audio playback** (NEW)
  - Display clears after completion
- **Button C (Right)**: Select next AI model  
  - LED lights on press, off on release
  - Plays ascending toggle sound + echo
  - Scrolls model name on display
  - Shows model index number
  - **Can interrupt audio playback** (NEW)
- **All Buttons (A+B+C)**: Clear conversation history
  - Hold all three buttons for 3 seconds
  - Plays random 7-note tune (unique each time)
  - All LEDs flash 3 times
  - Clears button chat history

### 4. Conversation Memory
- **Cross-Model Conversations**: Each model can see what previous models said
- **Model Attribution**: Responses are tagged with `[model_name]:` when from different models
- **History Window**: Keeps last 10 exchanges for context
- **Separate Histories**: Button chats and web chats maintain separate histories
- **Persistent Context**: Switch models mid-conversation and ask about previous responses
- **PenphinMind History** (NEW): All three mind responses stored in conversation history

Example conversation flow:
1. Ask tinydolphin: "What's 2+2?"
2. Switch to llama, ask: "What did tinydolphin say?"
3. Llama sees: "[tinydolphin]: 2+2 equals 4"

### 5. Recording Features
- Auto-detects USB microphone device
- 10-second recording with visual countdown
- **Button B LED blinks during recording** (NEW)
- Recording complete sound (3 descending notes)
- Full pipeline uses existing timer and display features
- **Audio interruption support** (NEW)

### 6. Sensor Data Integration
- Temperature, pressure, and altitude displayed in web UI header
- Real-time BMP280 sensor readings
- Altitude calculated using standard atmosphere formula

### 7. Sound Effects System
- `play_toggle_left_sound()`: Descending beep for previous model
- `play_toggle_right_sound()`: Ascending beep for next model
- `play_confirmation_sound()`: Double beep for recording start
- `play_recording_complete_sound()`: Triple descending beep
- **Sound Queue System** (NEW):
  - Sequential playback prevents sound overlap
  - Voice intros play completely before other sounds
  - Background worker thread processes queue
- **Voice Intros** (NEW):
  - Each voice model has a unique intro phrase
  - Generated and cached on first use
  - Examples: "Ahh yes, hmm..." (Jarvis), "Curiouser, and Curiouser..." (Alba)

### 8. Speech Enhancement (NEW)
- **Markdown Header Conversion**:
  - `#` → "Title:"
  - `##` → "Heading:"
  - `###` → "Section:"
  - Works for both line-start and inline headers
- Improved symbol-to-speech conversion
- Better handling of punctuation and formatting

### 9. Bicameral Mind Enhancements (NEW)
- **System Message Support**:
  - Optional `system` parameter for API calls
  - Prepended to convergence prompt only
  - Logical and creative minds use default prompts
- **API Consistency**:
  - Changed from `text` to `prompt` parameter
  - Consistent with `/insight` endpoint
- **Full History Tracking**:
  - All three responses visible in web UI
  - Shows complete thought process

### 10. Audio Interruption (NEW)
- **Any button press interrupts playing audio**
- Works with all audio playback (TTS responses)
- Button B requires second press after interruption to start recording
- Seamless transition from interruption to new action

## Musical Signatures

### Model Tunes (Ollama)
Each AI model plays a unique "curious" tune when starting:
- `tinydolphin` - Playful ascending pattern
- `llama` - Thoughtful, measured progression
- Different models create different melodic journeys

### Voice Tunes (TTS)
Each voice model plays a unique fanfare:
- `en_US` voices - American-style fanfare ending
- `en_GB` voices - British-style fanfare ending  
- Voice characteristics influence the melodic pattern

### Timer Ticking (NEW)
- Clock mode: Traditional tick-tock pattern
- Music mode: Pentatonic scale progression with variation

## Usage

### Voice Assistant Mode
1. Press **A** or **C** to select an AI model
2. Press **B** to start recording
3. Speak for 10 seconds (watch countdown)
4. System automatically transcribes → processes → speaks response
5. Press any button to interrupt audio playback

### Web Interface
1. The Rainbow Driver initializes automatically when the API starts
2. Audio tunes play automatically for different operations
3. Timer display activates during LLM calls with optional ticking
4. Sensor data updates on page refresh
5. PenphinMind shows all three mind responses in history

## Configuration

### Timer Ticking Mode
Set `TICK_TYPE` global variable:
- `"clock"` - Traditional tick-tock sounds
- `"music"` - Musical scale progression

## Testing

Use the included `test_roverseer.py` script to test the integration:
```bash
python test_roverseer.py
```

## Button Quick Reference
- **A**: Previous Model (←) / Interrupt Audio
- **B**: Record & Process (●) / Interrupt Audio
- **C**: Next Model (→) / Interrupt Audio
- **A+B+C**: Clear History (hold 3 seconds)

## Recent Fixes (Latest Update)

### Display Layering
- **Scrolling takes precedence**: When text is scrolling, it completely overrides number display
- **Numbers are bottom layer**: Timer and other numbers only show when scrolling is not active
- **Smooth transitions**: Code waits for scrolling to complete before showing numbers

### LED Pipeline Fixes
- **Recording**: Button B LED blinks during 10-second recording
- **ASR (Speech-to-Text)**: Button A (Red) LED blinks, then stays solid when complete
- **LLM Processing**: Button B (Green) LED blinks, with A solid red
- **TTS (Text-to-Speech)**: Button C (Blue) LED blinks, with A & B solid
- **Audio Playback**: All three LEDs blink together
- **Completion**: All LEDs turn off when pipeline completes

### Timer Sound Improvements
- **Increased duration**: Tick sounds play for 0.05s (clock) and 0.04s (music) for better audibility
- **Clock mode**: Alternating E5 (tick) and C4 (tock) tones
- **Music mode**: Pentatonic scale progression with variation

### Code Simplification
- Uses rainbow driver's `display_number()` method directly
- Leverages built-in buzzer tones from the driver
- Cleaner state management with global `isScrolling` flag 