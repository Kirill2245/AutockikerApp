import logging

class LogEmitter:
    def __init__(self):
        self.callbacks = []
        
    def register_callback(self, callback):
        self.callbacks.append(callback)
        
    def emit_log(self, message, level=logging.INFO):
        for callback in self.callbacks:
            try:
                callback(message, level)
                print(f"LOGI -- {message},{level}")
            except Exception as e:
                print(f"Error in log callback: {e}")

global_emitter = LogEmitter()