from enum import Enum, auto

# 1. prevent bugs from typos
# 2. autocomplete
# 3. cleaner and centralized state management
# 4. easier to track in contrast to strings that could be anything

class AnimationState(Enum):
    """Sets states to battle participants to handle animations.
        Before, I used multiple booleans (triggers) to change attack phases.
        This could lead to bugs when multiple are turned on, in contrast to
        this where only one can be active.
    """
    IDLE = auto()
    WAIT = auto()
    APPROACH = auto()
    ATTACK = auto()
    RETURN = auto()

