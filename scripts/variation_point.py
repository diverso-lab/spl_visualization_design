from typing import Any
from famapy.metamodels.fm_metamodel.models import Feature


class Variant:

    def __init__(self, feature: Feature, value: Any):
        self.feature = feature
        self.value = value

    def __repr__(self) -> str:  
        return f'V({str(self.feature)}, {str(self.value)})'


class VariationPoint:

    def __init__(self, feature: Feature, handle: str, variants: list[Variant]):
        self.feature = feature
        self.handle = handle
        self.variants = variants

    def __repr__(self) -> str:
        return f'VP({str(self.feature)}, {str(self.handle)}, {str(self.variants)})'
