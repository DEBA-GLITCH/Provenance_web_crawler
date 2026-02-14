
from enum import Enum


class ActionType(str, Enum):
    SEARCH = "SEARCH"
    FETCH = "FETCH"
    REASON = "REASON"
    HALT = "HALT"
