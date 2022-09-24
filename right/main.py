#
# Slapcomp Lulu main.py
# This is the main file called by CircuitPython 
# to govern the functionality of our keyboard. 
#

# Import my own modules, which I keep at the 
# root folder level (same as this file)
# to make it easy to update kmk without
# clobbering my own work. 
from sc.sc_lulu import KMKKeyboard
from sc.sc_led import sc_led
from sc.sc_encoders import sc_encoders

# Import kmk modules
from kmk.keys import KC
from kmk.modules.layers import Layers
from kmk.hid import HIDModes
from kmk.handlers.sequences import send_string
import supervisor
from kmk.extensions.peg_oled_Display import Oled,OledDisplayMode,OledReactionType,OledData
from kmk.modules.split import Split, SplitSide, SplitType


# 
# Init 
#
# Init keyboard
# 
# Note that this is my own keyboard file, not the one offered by Boardsource. 
# I needed to make some extra data structures to handle animated per-key LED
# stuff, and wasn't sure the right place to do that, so I sequestered it in
# this file. Be sure to check out sc/sc_lulu.py
keyboard = KMKKeyboard()

# Init layers
layers_ext = Layers()
keyboard.modules.append(layers_ext)


# Init sc_encoders, for wheel scrollinpg on the encoders
# I wanted to have my encoders do verticaly/horizontal scrolling, 
# rather than the default media controls. What I found when I did 
# this might be a bug: I could adjust the speed of scrolling DOWN, 
# but not the speed of scrolling UP. Maybe I was doing something
# wrong, but to be nondestructive I copied the default mousekeys
# module to sc/sc_encoders.py, so that I could monkey around with
# this without screwing anything up. 
sc_encoders_ext = sc_encoders()
sc_encoders_ext.move_step = 10
sc_encoders_ext.ac_interval = 100000
keyboard.modules.append(sc_encoders_ext)

# Init Oled
oled_ext = Oled(
                 OledData(
                          image={0:OledReactionType.LAYER,
                                 1:["images/base.bmp",
                                    "images/layer_1.bmp",
                                    "images/layer_2.bmp",
                                    "images/layer_3.bmp"]
                                 }
                         ),
                         toDisplay=OledDisplayMode.IMG,
                         flip=False)


keyboard.extensions.append(oled_ext)

# Init per-key Leds
# This is the core of how I'm doing per-key animation. 
# I copied some code from the peg_rgb_matrix.py extension, 
# then hacked away until I got it working the way I wanted. 
# Consult sc/sc_led.py for this. 
sc_led_ext = sc_led()
keyboard.extensions.append(sc_led_ext)

# TODO Comment one of these on each side
# SC NOTE: These lines are from Boardsource. 
# I tried just putting this in the Split() call below,
# but it broke everything so I'm not sure what the TODO actually is.
#split_side = SplitSide.LEFT
#split_side = SplitSide.RIGHT

split = Split(  data_pin=keyboard.rx, 
                data_pin2=keyboard.tx, 
                uart_flip=False,
                split_side = None)
keyboard.modules.append(split)


#
# keymap
#
# I formatted this to make it a little easier to understand visually, which is a convention I see
# done in QMK a lot. I find this way easier to read/edit. 

# A macro to help make our code a little more readable.
_______ = KC.TRNS

keyboard.keymap = [
                # Layer 0
                [   KC.ESC,     KC.N1,     KC.N2,      KC.N3,      KC.N4,      KC.N5,                              KC.N6,      KC.N7,      KC.N8,      KC.N9,      KC.N0,      KC.BSPC,
                    KC.TAB,      KC.Q,      KC.W,       KC.E,       KC.R,       KC.T,                               KC.Y,       KC.U,       KC.I,       KC.O,       KC.P,       KC.QUOTE,
                    KC.LCTRL,    KC.A,      KC.S,       KC.D,       KC.F,       KC.G,                               KC.H,       KC.J,       KC.K,       KC.L,       KC.SCOLON,  KC.ENTER,
                    KC.LSHIFT,   KC.Z,      KC.X,       KC.C,       KC.V,       KC.B,       KC.LBRACKET,KC.RBRACKET,KC.N,       KC.M,       KC.COMMA,   KC.DOT,     KC.SLASH,   KC.RSHIFT,
                                                        KC.MO(1),   KC.LALT,    KC.LGUI,    KC.SPACE,   KC.SPACE,   KC.MO(2),   _______,    KC.RGUI,
                    KC.LEFT,
                    KC.RIGHT,
                    KC.MW_UP,
                    KC.MW_DOWN
                ],
                # MO(1)
                [   KC.GRAVE,   KC.F1,      _______,    _______,    _______,    _______,                            _______,    _______,    _______,    _______,    _______,    _______,
                    _______,    _______,    _______,    _______,    _______,    _______,                            _______,    _______,    _______,    _______,    _______,    _______,
                    _______,    _______,    _______,    _______,    _______,    _______,                            _______,    _______,    _______,    _______,    KC.UP,      _______,
                    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    KC.LEFT,    KC.DOWN,    KC.RIGHT,
                                                        _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,
                    _______,
                    _______,
                    _______,
                    _______
                ], 

                # M0(2)
                [   _______,    _______,    _______,    _______,    _______,    _______,                            _______,    _______,    _______,    KC.MINUS,   KC.EQUAL,   KC.PGUP,
                    _______,    _______,    _______,    _______,    _______,    _______,                            _______,    KC.HOME,    KC.UP,      KC.END,     _______,    KC.PGDN,
                    _______,    _______,    _______,    _______,    _______,    _______,                            _______,    KC.LEFT,    KC.DOWN,    KC.RIGHT,   _______,    _______,
                    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    KC.BSLASH,  _______,
                                                        KC.LGUI,    _______,    _______,    _______,    _______,    _______,    _______,    _______,
                    _______,
                    _______,
                    _______,
                    _______
                ], 
                
                # M0(3)
                [   _______,    _______,    _______,    _______,    _______,    _______,                            _______,    _______,    _______,    _______,    KC.HOME,    KC.PGUP,
                    _______,    _______,    _______,    _______,    _______,    _______,                            _______,    _______,    _______,    _______,    KC.END,     KC.PGDN,
                    _______,    _______,    _______,    _______,    _______,    _______,                            _______,    _______,    _______,    _______,    _______,    _______,
                    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,
                                                        _______,    _______,    _______,    _______,    _______,    _______,    _______,    _______,
                    _______,
                    _______,
                    _______,
                    _______
                ], 
            ] 



#
# MAIN
# 
if __name__ == '__main__':
    print("SC Lulu Initialized.")
    keyboard.go(hid_type=HIDModes.USB)