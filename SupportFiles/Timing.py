import time


class Timing():
    start_time = None
    end_time = None
    message = "Start or End time was not used"

    def start(self):
        self.start_time = time.perf_counter()

    def end(self):
        self.end_time = time.perf_counter()

    def compute_time(self):
        if (self.start_time is not None) and (self.end_time is not None):
            return round(self.end_time-self.start_time, 2)
        else:
            return self.message
