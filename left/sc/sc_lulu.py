#
# SC_lulu.py
#
# This is mostly-copied code from the kb.py file that shipped with the Lulu. 
# It's been reformatted for readability; the biggest change is the addition
# of a few extra data structures that associate the key coordinates with their
# LED counterparts, and make it a little easier to handle per-key animation.
# I'm very sure there is a tidier way to do this; this
# was just the most obvious solution for me at the time I wrote it. 
#

import board

from kmk.kmk_keyboard import KMKKeyboard as _KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.scanners.encoder import RotaryioEncoder
from kmk.scanners.keypad import MatrixScanner

class KMKKeyboard(_KMKKeyboard):
    
    def __init__(self):

        # create and register the scanner
        self.matrix =[MatrixScanner(
                                    # required arguments:
                                    column_pins=self.col_pins,
                                    row_pins=self.row_pins,
                                    # optional arguments with defaults:
                                    columns_to_anodes=DiodeOrientation.COL2ROW,
                                    interval=0.02,
                                    max_events=64
                                ),
                                RotaryioEncoder(
                                    pin_a=board.GP08,
                                    pin_b=board.GP09,
                                    # optional
                                    divisor=4,
                                )]


    col_pins = (
                    board.GP02,
                    board.GP03,
                    board.GP04,
                    board.GP05,
                    board.GP06,
                    board.GP07,
                )

    row_pins = (board.GP14, board.GP15, board.GP16, board.GP17, board.GP18)

    diode_orientation = DiodeOrientation.COLUMNS
    rx = board.RX
    tx = board.TX
    rgb_pixel_pin = board.GP29
    i2c = board.I2C
    data_pin = board.RX
    rgb_pixel_pin = board.GP29 # unsure why this line and the next are repeated.
    i2c = board.I2C
    SCL=board.SCL
    SDA=board.SDA
    encoder_a=board.GP08
    encoder_b=board.GP09

    # Unsure what this actually does; I don't use it myself anywhere.
    brightness_limit = 0.6
    num_pixels = 70

    # This controls what keycode gets returned by a key event
    coord_mapping = [
                         0,  1,  2,  3,  4,  5,         37, 36, 35, 34, 33, 32,
                         6,  7,  8,  9, 10, 11,         43, 42, 41, 40, 39, 38,
                        12, 13, 14, 15, 16, 17,         49, 48, 47, 46, 45, 44,
                        18, 19, 20, 21, 22, 23, 29, 61, 55, 54, 53, 52, 51, 50,
                                25, 26, 27, 28,         60, 59, 58, 57,
                                
                                #encoders
                                30, 31, 62, 63 
                    ]

    # These are the id coords of the leds. So, e.g. LED 11 is under Key 0
    led_mapping =   [ 
                        11, 10,  9,  8,  7,  6,         41, 42, 43, 44, 45, 46,
                        12, 13, 14, 15, 16, 17,         52, 51, 50, 49, 48, 47,
                        23, 22, 21, 20, 19, 18,         53, 54, 55, 56, 57, 58,
                        24, 25, 26, 27, 28, 29, 30, 65, 64, 63, 62, 61, 60, 59,
                                34, 33, 32, 31,         66, 67, 68, 69,
                                     
                                     # underglow
                                     3,  4,  5,         40, 39, 38,
                                     2,  1,  0,         35, 36, 37
                    ]

    # Here I create a map of color that you can imagine laying over the keys. 
    # In this case, I made a gradient of color (yellow to orange) in Photoshop
    # then copied some values from it here. I stash these RGB color triplets
    # as variables below...
    c_k = [0,  0,  0]
    c_r = [120,  20,  0]
    c_m = [120,  30,  0]
    c_y = [120,  40,  0]

    # ...which makes it tidier to concoct this. So, if you imagine all the LEDS
    # are on, you'd see a nice gradient going from the outermost columns to the 
    # innermost. 
    led_color_mapping = [
                        c_r, c_r, c_m, c_m, c_y, c_y,           c_y, c_y, c_m, c_m, c_r, c_r,
                        c_r, c_r, c_m, c_m, c_y, c_y,           c_y, c_y, c_m, c_m, c_r, c_r,
                        c_r, c_r, c_m, c_m, c_y, c_y,           c_y, c_y, c_m, c_m, c_r, c_r,
                        c_r, c_r, c_m, c_m, c_y, c_y, c_y, c_y, c_y, c_y, c_m, c_m, c_r, c_r,
                                  c_m, c_y, c_y, c_y,           c_y, c_y, c_y, c_m,

                                            # underglow
                                            c_r, c_m, c_y, c_y, c_m, c_r,
                                            c_r, c_m, c_y, c_y, c_m, c_r
                        ]
    # Ok, some wierd stuff. I want to light up my underglow LEDS based on the keys 'above' them. 
    # How to do this? Well, in my case, I made some 6x2 'weight' matrix. 
    w00 = [1,0,0,0,0,0,
           1,0,0,0,0,0]
    w01 = [0,1,0,0,0,0,
           0,1,0,0,0,0]
    w02 = [0,0,1,0,0,0,
           0,0,1,0,0,0]
    w03 = [0,0,0,1,0,0,
           0,0,0,1,0,0]
    w04 = [0,0,0,0,1,0,
           0,0,0,0,1,0]
    w05 = [0,0,0,0,0,1,
           0,0,0,0,0,1]

    w06 = [1,0,0,0,0,0,
           1,0,0,0,0,0]
    w07 = [0,1,0,0,0,0,
           0,1,0,0,0,0]
    w08 = [0,0,1,0,0,0,
           0,0,1,0,0,0]
    w09 = [0,0,0,1,0,0,
           0,0,0,1,0,0]
    w10 = [0,0,0,0,1,0,
           0,0,0,0,1,0]
    w11 = [0,0,0,0,0,1,
           0,0,0,0,0,1]

    # Then, what I do is associate one of the above matrices with each key. What this means, e.g. is that
    # Key 0 (ESC on my lulu) uses weights in w00, which - if you imagine the underglow LEDs spatially -
    # indicates that the ESC key should light up the leftmost underglow LEDS only. 
    #
    # Right now these are simply 0/1 values, but eventually I would like to add more interesting
    # floats to help create a 'falloff radius' around each key.
    #
    # Someone more clever than I could definitely make this better. It's not very understandable as is, I think.  
    underglow_key_weights = [
                                w00, w00, w01, w01, w02, w02,           w03, w03, w04, w04, w05, w05, 
                                w00, w00, w01, w01, w02, w02,           w03, w03, w04, w04, w05, w05,
                                w06, w06, w07, w07, w08, w08,           w09, w09, w10, w10, w11, w11,
                                w06, w06, w07, w07, w08, w08, w08, w09, w09, w09, w10, w10, w11, w11,
                                          w07, w07, w08, w08,           w09, w09, w10, w10
                            ]

    # Rather than trying to cleverly traverse all these maps at runtime, I reason it might be easier to make
    # some associative dictionaries, where I can quickly look up which key affects which LED. 
    key_led_dict = {}
    for i in range(58):
        key_led_dict[coord_mapping[i]] = led_mapping[i]

    # Similarly, which color should be associated with which LED.
    led_colors_dict = {}
    for i in range(58):
        led_colors_dict[coord_mapping[i]] = led_color_mapping[i]

    # and again for the weights
    underglow_weight_dict = {} 
    for i in range(58):
        underglow_weight_dict[coord_mapping[i]] = underglow_key_weights[i]


    # Because I have to handle the animation of the underglow LEDs separately from the
    # ones beneath the keys, I make a few standalone lists here of just the underglow
    # coords/colors. 
    underglow_leds = led_mapping[58:70]
    underglow_colors = led_color_mapping[58:70]
