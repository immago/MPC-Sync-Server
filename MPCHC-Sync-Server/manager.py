from model import Data, State, Callback
from threading import Thread, Event


class Manager:

    def __init__(self):
        self.stopEvent = Event()
        self.sessions = {} # Dict {session identifer: Data}; All sessions (rooms, videos)
        self.callbacks = [] # Array [Callback, ...]; Callbacks of subscribed users
        self.sessionsThread = None
        self.updateSessionsThread()


    # Start or stop update thread depending on active sessions count
    def updateSessionsThread(self):
        # If has sessions
        if len(self.sessions) > 0:
            # Start update if not started
            if self.sessionsThread is None or not self.sessionsThread.isAlive():
                self.runSessionsThread()
        else:
            # Nothing to update go idle
            self.stopSessionsThread()

    # Run update thread
    def runSessionsThread(self):
        self.stopEvent.clear();
        self.sessionsThread = sessionsThread(self)
        self.sessionsThread.start()

    # Stop update thread
    def stopSessionsThread(self):
        self.stopEvent.set()


    # Called by updateSessionsThread one time per second
    def threadTick(self):
        for key, value in self.sessions.items():
            value: Data = value
            # Check if playing
            if value.state == State.Playing:
                value.position += 1;

                #temp
                self.callSessionCallbacks(key)

                # Remove from sessions if ended 
                if value.position >= value.duration:
                    self.sessions.pop(key, None)
                    self.updateSessionsThread()
    
    # User api
    # Set session data
    def set(self, identifer, data: Data):
        self.sessions[identifer] = data;
        self.updateSessionsThread()
        self.callSessionCallbacks(identifer)

    # Get session data
    def get(self, identifer):

        if identifer in self.sessions:
            return self.sessions[identifer]
        else:
            return None

    # Trigger callback for session
    def callSessionCallbacks(self, identifer):
        for callback in self.callbacks:
            callback: Callback = callback
            if callback.identifer == identifer:
                callback.function(self.sessions[identifer])
               
    # Subscribe on session update
    def subscribe(self, identifer, callback):
        self.callbacks.append(Callback(identifer, callback))

    # Unsubscribe from session update
    def unsubscribe(self, callback):
        self.callbacks.remove(callback)


# Update
class sessionsThread(Thread):
    
    def __init__(self, manager: Manager):
        Thread.__init__(self)
        self.manager = manager

    def run(self):
        while not self.manager.stopEvent.wait(1.0):
            self.manager.threadTick()