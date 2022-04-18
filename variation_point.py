from typing import Any
from famapy.metamodels.fm_metamodel.models import Feature


class Variant:

    def __init__(self, identifier: str, value: Any = None):
        self.identifier = identifier  # Feature or Attribute
        self.value = value

    def __repr__(self) -> str:  
        return f'V({str(self.identifier)}, {str(self.value)})'


class VariationPoint:

    def __init__(self, feature: Feature, handler: str, variants: list[Variant] = None):
        self.feature = feature
        self.handler = handler
        self.variants = [] if variants is None else variants

    def __repr__(self) -> str:
        return f'VP({str(self.feature)}, {str(self.handler)}, {str(self.variants)})'
