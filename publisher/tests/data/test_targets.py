
from typing import TypeAlias, Any

class BaseTestTarget:

    def __init__(self: Any, attr1: str, attr2: dict): 
        self._attr1 = attr1
        self._attr2 = attr2

    @property
    def attr1(self) -> str:
        """is read-only"""
        return self._attr1
    
    @property
    def attr2(self) -> dict:
        """is read-only"""
        return self._attr2

    def random_method_1(self) -> str:
        return "hello"
    
    def __repr__(self):
        clsname: str = type(self).__name__
        return f"{clsname}(attr1: {self.attr1}, attr2: {self.attr2})"

class DerivedTestTarget(BaseTestTarget):
    def __init__(self: Any, attr1: str, attr2: dict, attr3: str): 
        self._attr3= attr3
        super().__init__(attr1, attr2)

    @property
    def attr3(self) -> str:
        """is read-only"""
        return self._attr3
    
    
