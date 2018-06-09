from model import Data, State, Callback
from threading import Thread, Event
from logger import logger

class Manager:

    def __init__(self):
        self.stopEvent = Event()
        self.sessions = {} # Dict {session identifer: Data}; All sessions (rooms, videos)
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
        for key, value in list(self.sessions.items()):
            value: Data = value

            # Remove if no listeners
            if len(value.calbacks) == 0:
                logger.info('No listeners for session ' +  key + ' remove...')
                self.sessions.pop(key, None)

            # Check if playing
            if value.state == State.Playing:
                if value.position < value.duration:
                    value.position += 1.0;

                #temp
                #self.callSessionCallbacks(key)
    
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

        if identifer in self.sessions:
            for callback in self.sessions[identifer].calbacks:
                callback: Callback = callback
                callback.function(self.sessions[identifer], callback)
               


    # Subscribe on session update
    def subscribe(self, identifer, callback: Callback, host: bool):

        # create session of not exist
        if identifer not in self.sessions:

            if host:
                # create session, it will be updated later by set
                self.set(identifer, Data("", 0, 0, State.Closed))
            else:
                # throw no session error
                callback.function(None, callback)
                return

        self.sessions[identifer].calbacks.append(callback)



    # Unsubscribe from session update
    def unsubscribe(self, identifer, callback):
        if identifer in self.sessions and callback in self.sessions[identifer].calbacks:
            self.sessions[identifer].calbacks.remove(callback)


# Update
class sessionsThread(Thread):
    
    def __init__(self, manager: Manager):
        Thread.__init__(self)
        self.manager = manager

    def run(self):
        while not self.manager.stopEvent.wait(1.0):
            self.manager.threadTick()