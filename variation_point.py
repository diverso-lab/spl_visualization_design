from typing import Any
from famapy.metamodels.fm_metamodel.models import Feature


class VariationPoint:

    def __init__(self, feature: Feature, handle: str, value: Any):
        self.feature = feature
        self.handle = handle
        self.value = value

    def __repr__(self) -> str:
        return f'{str(self.feature)} -> {str(self.handle)} ({self.value})'