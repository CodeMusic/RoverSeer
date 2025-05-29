from gpiozero import Button, PWMLED, TonalBuzzer
from gpiozero.tones import Tone
import board, busio, time, colorsys
import fourletterphat as flp
import adafruit_bmp280
import sys
import signal
sys.path.insert(0, "/home/codemusic/APA102_Pi")
from apa102_pi.driver.apa102 import APA102

# ------- CONFIG -------
NUM_LEDS = 7
BRIGHTNESS = 2  # Reduced from 5 to 2 for dimmer LEDs
SLEEP = 0.2
# Direct RGB values for ROYGBIV colors
ROYGBIV_COLORS = [
    (255, 0, 0),     # Red
    (255, 127, 0),   # Orange
    (255, 255, 0),   # Yellow
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (75, 0, 130),    # Indigo
    (148, 0, 211)    # Violet
]
BUTTON_TONES = {'A': Tone("C5"), 'B': Tone("E5"), 'C': Tone("G5")}

# ------- INIT -------
i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)

# APA102 LED strip
strip = APA102(num_led=NUM_LEDS, global_brightness=BRIGHTNESS)
strip.clear_strip()  # Clear any previous state
strip.show()

# Button LEDs and sounds
button_leds = {
    'A': PWMLED(6),   # Red LED
    'B': PWMLED(19),  # Green LED  
    'C': PWMLED(26),  # Blue LED
}
buttons = {
    'A': Button(21),  # BCM21
    'B': Button(20),  # BCM20
    'C': Button(16),  # BCM16
}
buzzer = TonalBuzzer(13)

def on_button(btn):
    # Find which button was pressed by checking button objects
    name = None
    for btn_name, button_obj in buttons.items():
        if button_obj == btn:
            name = btn_name
            break
    
    if name:
        print(f"Button {name} pressed")
        button_leds[name].pulse(fade_in_time=0.1, fade_out_time=0.1, n=1)
        buzzer.play(BUTTON_TONES[name])
        time.sleep(0.2)
        buzzer.stop()

for name, btn in buttons.items():
    btn.when_pressed = on_button

# Shutdown handler
def shutdown_handler(sig, frame):
    print("\n🛑 Exit requested. Clearing display and LEDs...")
    strip.clear_strip()
    strip.show()
    flp.clear()
    flp.show()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)

# ------- MAIN LOOP -------
counter = 0

# Track what color each LED should be
led_states = [(0, 0, 0)] * NUM_LEDS

# Start with all LEDs off
strip.clear_strip()
strip.show()

while True:
    # Which LED position to update (6→5→4→3→2→1→0)
    led_position = 6 - (counter % NUM_LEDS)
    
    # Which color to use (cycles through ROYGBIV)
    color_index = (counter // NUM_LEDS) % len(ROYGBIV_COLORS)
    
    # Get the color directly
    r, g, b = ROYGBIV_COLORS[color_index]
    
    # Update our state tracking
    led_states[led_position] = (r, g, b)
    
    # Update ALL LEDs based on our state (back to RGB order)
    for i in range(NUM_LEDS):
        strip.set_pixel(i, led_states[i][0], led_states[i][1], led_states[i][2])  # RGB order
    strip.show()

    # Display on 4-letter display
    flp.clear()
    flp.print_number_str(str(counter).rjust(4)[-4:])
    flp.show()

    # Read and print BMP280 sensor data
    color_names = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Indigo', 'Violet']
    print(f"LED {led_position} → {color_names[color_index]} ({r}, {g}, {b}) | Counter: {counter} | Temp: {bmp280.temperature:.1f}°C | Pressure: {bmp280.pressure:.1f} hPa")

    counter += 1
    time.sleep(SLEEP)
