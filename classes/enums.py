from enum import Enum, auto

class TurnPhase(Enum):
    START = auto()
    APPROACHING = auto()
    ATTACKING = auto()
    RETURNING = auto()
    DONE = auto()