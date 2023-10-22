import threading


class RepeatedTimer:
    def __init__(self, interval, target):
        self.interval = interval
        self.target = target

    def core(self):
        self.target()
        threading.Timer(self.interval, self.core).start()

    def start(self):
        threading.Timer(self.interval, self.core).start()
