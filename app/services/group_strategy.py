from enum import StrEnum
from statistics import fmean
from collections.abc import Sequence, Callable


class GroupStrategy(StrEnum):
    AVERAGE = "average"
    LEAST_MISERY = "least_misery"
    MIXED = "mixed"


def average(similarities: Sequence[float], penalty: float) -> float:
    """Best overall satisfaction; one unhappy member can be outvoted."""
    return fmean(similarities)

def least_misery(similarities: Sequence[float], penalty: float) -> float:
    """The movie is only as good as it is for its least happy member."""
    return min(similarities)

def mixed(similarities: Sequence[float], penalty: float) -> float:
    """Average, minus a penalty for how unevenly the group would enjoy it."""
    return fmean(similarities) - penalty * (max(similarities) - min(similarities))

STRATEGIES: dict[GroupStrategy, Callable[[Sequence[float], float], float]] = {
    GroupStrategy.AVERAGE: average,
    GroupStrategy.LEAST_MISERY: least_misery,
    GroupStrategy.MIXED: mixed,
}

def group_score(similarities: Sequence[float], strategy: GroupStrategy, penalty: float = 0.5) -> float:
    return STRATEGIES[strategy](similarities, penalty)