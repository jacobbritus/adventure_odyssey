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
    BUFF = auto()
    RETURN = auto()
    DEATH = auto()
    HURT = auto()
    ITEM = auto()

class BattleState(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    PLAYER_ANIMATION = auto()
    ENEMY_ANIMATION = auto()
    END_MENU = auto()
    END_BATTLE = auto()

class LevelState(Enum):
    OVERWORLD = auto()
    BATTLE = auto()

class BookState(Enum):
    NEXT_PAGE = auto()
    PREVIOUS_PAGE = auto()
    OPEN_BOOK = auto()
    CLOSE_BOOK = auto()

class BattleMenuState(Enum):
    MAIN_MENU = auto()
    SKILLS_MENU = auto()
    END_MENU = auto()
    INVENTORY_MENU = auto()


class ButtonVariant(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    WIDE = "large"
    EXIT = "exit"

class AttackType(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    BUFF = "buff"

class StatusBarState(Enum):
    OPENED = auto()
    CLOSED = auto()

class StatusEffects(Enum):
    POISONED = {
        "name": "POISONED",
        "damage_percentage": 0.1,
        "turns": 6,
        "color": (102, 205, 170)
    }

    BURNED = {
        "name": "BURNED",
        "damage_percentage": 0.25,
        "turns": 2,
        "color": (255, 87, 34)
    }

