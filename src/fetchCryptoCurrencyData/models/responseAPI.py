from typing import List, Generic, TypeVar

from dataclasses import dataclass
T = TypeVar('T')

@dataclass
class APICoinCapResponse(Generic[T]):
    data: List[T]
    timestamp: int
    def __init__(self, data: T, timestamp: int):
        self.data = data
        self.timestamp = timestamp