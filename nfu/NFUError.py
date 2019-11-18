class NFUError(Exception):
    def __init__(self, message: str, code: str = '2000'):
        self.message = message
        self.code = code
