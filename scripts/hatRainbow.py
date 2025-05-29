import gpiod
import time
import board, busio, sys, signal
import adafruit_bmp280
import fourletterphat as flp
from gpiozero.tones import Tone
from apa102_pi.driver.apa102 import APA102

# ------- CONFIG -------
NUM_LEDS = 7
BRIGHTNESS = 2
SLEEP = 0.2
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
BUTTON_LINES = {'A': 21, 'B': 20, 'C': 16}  # BCM pins
LED_LINES = {'A': 6, 'B': 19, 'C': 26}      # BCM pins

# ------- INIT -------
i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)
strip = APA102(num_led=NUM_LEDS, global_brightness=BRIGHTNESS)
strip.clear_strip()
strip.show()

# GPIOD setup
#chip = gpiod.Chip("gpiochip4")
chip = gpiod.Chip("/dev/gpiochip4")
button_lines = {k: chip.get_line(v) for k, v in BUTTON_LINES.items()}
led_lines = {k: chip.get_line(v) for k, v in LED_LINES.items()}

for line in button_lines.values():
    line.request(consumer="button", type=gpiod.LINE_REQ_EV_FALLING_EDGE)

for line in led_lines.values():
    line.request(consumer="led", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

# Placeholder for buzzer (PWM not handled by gpiod directly—left out or handled via separate script)

# ------- MAIN LOOP -------
def shutdown_handler(sig, frame):
    print("\n🛑 Exit requested. Clearing display and LEDs...")
    strip.clear_strip()
    strip.show()
    flp.clear()
    flp.show()
    for led in led_lines.values():
        led.set_value(0)
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)

counter = 0
led_states = [(0, 0, 0)] * NUM_LEDS
strip.clear_strip()
strip.show()

print("Listening for buttons...")
while True:
    for name, line in button_lines.items():
        event = line.event_wait(0.05)
        if event and line.event_read().type == gpiod.LineEvent.FALLING_EDGE:
            print(f"Button {name} pressed")
            led_lines[name].set_value(1)
            time.sleep(0.1)
            led_lines[name].set_value(0)
            # Tone buzzer logic would go here if PWM was handled

    led_position = 6 - (counter % NUM_LEDS)
    color_index = (counter // NUM_LEDS) % len(ROYGBIV_COLORS)
    r, g, b = ROYGBIV_COLORS[color_index]
    led_states[led_position] = (r, g, b)

    for i in range(NUM_LEDS):
        strip.set_pixel(i, *led_states[i])
    strip.show()

    flp.clear()
    flp.print_number_str(str(counter).rjust(4)[-4:])
    flp.show()

    print(f"LED {led_position} → {['Red','Orange','Yellow','Green','Blue','Indigo','Violet'][color_index]} "
          f"({r}, {g}, {b}) | Counter: {counter} | Temp: {bmp280.temperature:.1f}°C | "
          f"Pressure: {bmp280.pressure:.1f} hPa")

    counter += 1
    time.sleep(SLEEP)
