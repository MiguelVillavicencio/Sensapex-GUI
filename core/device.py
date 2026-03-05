# core/device.py
from sensapex import UMP

class SensapexDevice:
    def __init__(self):
        self.ump = None
        self.manipulator = None
        self.dev_ids = []

    def connect_first(self):
        self.ump = UMP.get_ump()
        self.dev_ids = self.ump.list_devices()
        if not self.dev_ids:
            raise RuntimeError("No Sensapex devices found.")
        self.manipulator = self.ump.get_device(self.dev_ids[0])
        return self.manipulator

    def get_pos(self):
        if not self.manipulator:
            raise RuntimeError("Manipulator not connected.")
        return self.manipulator.get_pos()

    def calibrate_zero(self):
        if not self.manipulator:
            raise RuntimeError("Manipulator not connected.")
        self.manipulator.calibrate_zero_position()

    def goto(self, pos, speed=1000):
        # print("here: core/device")
        if not self.manipulator:
            raise RuntimeError("Manipulator not connected.")
        self.manipulator.goto_pos(pos, speed=speed)

    def is_busy(self):
        return bool(self.manipulator and self.manipulator.is_busy())

    def stop(self):
        if not self.manipulator:
            return
        self.manipulator.stop()
        self.manipulator.stop()
        self.manipulator.stop()
