from utils.event_system import event_system

class Pauser():
    def __init__(self):
        event_system.subscribe("pause", self.pause_func)
        self.pause = False

    def pause_func(self):
        self.pause = True

pauser = Pauser()