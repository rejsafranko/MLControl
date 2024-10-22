import sys
import time


class Spinner:
    def __init__(self):
        pass

    def _spinning_cursor(self):
        while True:
            for cursor in "|/-\\":
                yield cursor

    def spinner(self, stop_event):
        spinner_generator = self._spinning_cursor()
        while not stop_event.is_set():
            sys.stdout.write(next(spinner_generator))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")
