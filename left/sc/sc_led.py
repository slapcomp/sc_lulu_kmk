#
# sc_led.py
#
# Ok, here is the biggest piece of the puzzle for animated
# per-key LEDs. 
#
# Stuff that's important to know: In KMK parlance, this is
# an 'extension'. It's been explained to me that an extended uses
# a copy of the keyboard structure (a 'sandbox'), which offers the
# advantage of not crashing the keyboard outright if a mistake is
# introduced to the code. However, I find that it will often 
# fail silently, which can make debugging a little confusing. So,
# print early and often. 
#
# This file started as a fork of peg_rgb_matrix.py,
# but I think it is significantly different enough to warrant
# lots of explanantion. So, let's get after it.


# This module is from Adafruit, and lets us talk to our LEDs. 
import neopixel

# We need to model this as a KMK Extension
from kmk.extensions import Extension

# We use this module to create a timer, which lets us do animation
from kmk.kmktime import PeriodicTimer

# This is used to do a clever trick where we auto-detect which side
# of our split Lulu we're on. This is from Boardsource, not me. 
from storage import getmount

class sc_led(Extension):

    def __init__(   self,
                    rgb_order=(1, 0, 2),  # GRB WS2812
                    disable_auto_write=True,
                    split=True,
                    rightSide=False,
                    decay = 2,
                    refresh_rate = 60,
                    
        ):

        self.rgb_order = rgb_order
        self.disable_auto_write = disable_auto_write

        # Try to auto-determine which side of the keyboard
        # we're on.
        name = str(getmount('/').label)
        self.split = split
        self.rightSide = rightSide
        if name.endswith('L'):
            self.rightSide = False
        elif name.endswith('R'):
            self.rightSide = True

        # Decay is the rate at which our keys fade off after being illuminated. 
        # I tried doing this in one of two ways:
        # LED = LED * decay, where decay <1. So, decay = 0.95 causes sort of an
        # exponential-like falloff. Visually it feels like the light 'crashes off',
        # speeding up as it gets dimmer.
        #
        # Or, you can do LED = LED - decay, which is just a linear falloff. 
        # This feels more visually pleasant to me. The useful value range
        # will differ when you use the variable in this way. 
        self.decay = decay
        self.refresh_rate = refresh_rate
        print("SC LED right side:", self.rightSide)
        print("SC LED initialized.")

#
# ------------------------------------------
#

    def enable(self, sandbox):
        self._enabled = True
        self.on_runtime_enable(sandbox)

    def disable(self, sandbox):
        self._enabled = False
        self.on_runtime_disable(sandbox)

    def on_runtime_enable(self, sandbox):
        return

    def on_runtime_disable(self, sandbox):
        return

    def during_bootup(self, keyboard):
        # During bootup - so,once - initialize
        # our Neopixels and read our crazy data structures
        # from our sc/sc_lulu.py keyboard configuration file. 
        self.neopixel = neopixel.NeoPixel(
            keyboard.rgb_pixel_pin,
            keyboard.num_pixels,
            brightness=keyboard.brightness_limit,
            pixel_order=self.rgb_order,
            auto_write=not self.disable_auto_write,
        )
        self.num_pixels = keyboard.num_pixels
        self.key_led_dict = keyboard.key_led_dict
        self.led_colors_dict = keyboard.led_colors_dict
        self.underglow_weight_dict = keyboard.underglow_weight_dict
        self.underglow_leds = keyboard.underglow_leds
        self.led_mapping = keyboard.led_mapping
        self._timer = PeriodicTimer(1000 // self.refresh_rate)

        print("SC LED boot complete.")

        return

    def before_matrix_scan(self, sandbox):
        return

    def after_matrix_scan(self, sandbox):
        return

    def before_hid_send(self, sandbox):
        return

    # Here's where the magic is! This function is called
    # after each sweep of the board matrix. 
    def after_hid_send(self, sandbox):

        # First, see if there's been a matrix event
        key_event = sandbox.matrix_update

        # If we've pressed a key, light it up!
        if key_event:

            # Let's get the coordinate of the key:
            key_coord = key_event.key_number
            # As well as whether it was pressed or released:
            is_pressed = key_event.pressed
            # print("Key Coord:", key_coord)

            # If it's been pressed, do something!
            if is_pressed:

                # First, figure out which LED we should be talking to. 
                # We know this because of our associative LED dictionary
                led_coord = self.key_led_dict[key_coord]

                # If we're on the right side, we need to compensate our LED
                # coordinate. I think this could probably be made more elegant
                # by modifying how we declare these in sc/sc-lulu.py, but this is
                # how boardsource does it, so I'll stick with it
                if self.rightSide:
                    led_coord = int(self.key_led_dict[key_coord] - (self.num_pixels / 2))
            
                # print("LED Coord:", led_coord)

                # light up the key itself
                self.neopixel[led_coord] = self.led_colors_dict[key_coord]

                # then light up the underglows
                for i, underglow_led in enumerate(self.underglow_leds):
       
                    # Again, compensate for our coordinates if we're on the right
                    # side of our split board.
                    if self.rightSide:
                        underglow_led = int(underglow_led - (self.num_pixels / 2))
                    
                    # We are iterating through our underglow LEDS, so we want to see
                    # how much each one should be affected by the key that's just been
                    # pressed. 
                    weight = self.underglow_weight_dict[key_coord][i]
                    
                    # Get the current underglow color. 
                    current_c = self.neopixel[underglow_led]

                    # This is a little ugly, so: what I'm doing here is saying "are you already
                    # illuminated by another key press? If so, you can stay illuminated". 
                    # If you don't do the max() thing, the underglow LEDS will cut off on
                    # subsequent key presses abruptly, which makes the underglow look
                    # strobe-y. I disliked the look of that, so I made it work this way. 
                    r = max(current_c[0], self.led_colors_dict[key_coord][0] * weight)
                    g = max(current_c[1], self.led_colors_dict[key_coord][1] * weight)
                    b = max(current_c[2], self.led_colors_dict[key_coord][2] * weight)
                    
                    # Actually perform the illumination. 
                    self.neopixel[underglow_led] = [r, g, b]


        # Up until this point, we've just been dealing with the key that's been pressed, and the 
        # underglow. Basically, we've turned everything on. Now, globally, we fade the board.
        if self._timer.tick():

            # To do the decay, we iterate over ALL leds on the board
            for led in self.led_mapping:

                # Get the current value of the LED
                current_c = self.neopixel[led]

                # Dim it by our decay amount
                decay_c = [max(0, c - self.decay) for c in current_c]
                
                # Apply the result
                self.neopixel[led] = decay_c


        # Force the leds to refresh
        self.neopixel.show()

        # Beer time.
        return

    def on_powersave_enable(self, sandbox):
        return

    def on_powersave_disable(self, sandbox):
        return
