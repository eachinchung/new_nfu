class NFUError(Exception):
    def __init__(self, message, code=2000):
        self.message = message
        self.code = code
