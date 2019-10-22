class NFUError(Exception):
    def __init__(self, message, code=1000):
        self.message = message
        self.code = code
