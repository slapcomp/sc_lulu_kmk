from supervisor import ticks_ms

from kmk.hid import HID_REPORT_SIZES, HIDReportTypes
from kmk.keys import make_key
from kmk.modules import Module


class PointingDevice:
    MB_LMB = 1
    MB_RMB = 2
    MB_MMB = 4
    _evt = bytearray(HID_REPORT_SIZES[HIDReportTypes.MOUSE] + 1)

    def __init__(self):
        self.key_states = {}
        self.hid_pending = False
        self.report_device = memoryview(self._evt)[0:1]
        self.report_device[0] = HIDReportTypes.MOUSE
        self.button_status = memoryview(self._evt)[1:2]
        self.report_x = memoryview(self._evt)[2:3]
        self.report_y = memoryview(self._evt)[3:4]
        self.report_w = memoryview(self._evt)[4:]


class sc_encoders(Module):

    def __init__(self):
        self.pointing_device = PointingDevice()
        self.max_speed = 10
        self.ac_interval = 100  # Delta ms to apply acceleration
        self._next_interval = 0  # Time for next tick interval
        self.move_step = 1

        make_key(
            names=('MW_UP',),
            on_press=self._mw_up_press,
            on_release=self._mw_up_release,
        )
        make_key(
            names=(
                'MW_DOWN',
                'MW_DN',
            ),
            on_press=self._mw_down_press,
            on_release=self._mw_down_release,
        )

    def _mw_up_press(self, key, keyboard, *args, **kwargs):
        self.pointing_device.report_w[0] = self.move_step
        self.pointing_device.hid_pending = True

    def _mw_up_release(self, key, keyboard, *args, **kwargs):
        self.pointing_device.report_w[0] = 0
        self.pointing_device.hid_pending = True

    def _mw_down_press(self, key, keyboard, *args, **kwargs):
        self.pointing_device.report_w[0] = 0xFF & (0 - self.move_step)  # This is the thing I (Slapcomp) modified;
                                                                        # It seems to work, but unsure if this is how 
                                                                        # one is intended to do this.
        self.pointing_device.hid_pending = True

    def _mw_down_release(self, key, keyboard, *args, **kwargs):
        self.pointing_device.report_w[0] = 0
        self.pointing_device.hid_pending = True


    def during_bootup(self, keyboard):
        return

    def matrix_detected_press(self, keyboard):
        return keyboard.matrix_update is None

    def before_matrix_scan(self, keyboard):
        return

    def after_matrix_scan(self, keyboard):
        return

    def before_hid_send(self, keyboard):
        if self.pointing_device.hid_pending:
            keyboard._hid_helper.hid_send(self.pointing_device._evt)
        return

    def after_hid_send(self, keyboard):
        return

    def on_powersave_enable(self, keyboard):
        return

    def on_powersave_disable(self, keyboard):
        return



 