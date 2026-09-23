"""Planning strategies."""
from __future__ import annotations
from enum import Enum

class StrategyType(str, Enum):
    CHAIN_OF_THOUGHT = "chain_of_thought"
    REACT = "react"
    TREE_OF_THOUGHT = "tree_of_thought"
    DIRECT = "direct"
