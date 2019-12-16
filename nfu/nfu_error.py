from dataclasses import dataclass


@dataclass
class NFUError(Exception):
    message: str
    code: str = '2000'
