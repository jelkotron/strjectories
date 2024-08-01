import time
import threading

class Engine():
    def __init__(self):
        self.i = 0
        self.running = False
        self.start_button = None
        self.thread = None
        print("Info: Engine initialized") 

    def start(self):
        print("Info: Engine started")
        self.running = True
        self.thread = threading.Thread(target=self.run) 
        self.thread.start()

    def stop(self):
        self.running = False
        print("Info: Engine stopped")

    def run(self):
        while True:
            print("thread running")
            time.sleep(1)
            if not self.running:
                break