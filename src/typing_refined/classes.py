from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True, init=False, repr=False)
class Predicate(ABC):
    """
    Marker base, anything recognized by validate_annotation as a validation
    thing.
    """
    bound: tuple[Any, ...]
    neg: bool = False

    @abstractmethod
    def __call__(self, value: Any) -> bool:
        ...
        
    def __init__(self, *args: Any):
        object.__setattr__(self, "bound", args)
        
    def __repr__(self):
        prefix = '!' if self.neg else ''
        return f"{prefix}{type(self).__name__}({self.bound})"


@dataclass(frozen=True, init=False, repr=False)
class Operator(Predicate):
    """
    Predicate partial construction wrapper with free argument first:
        {name}(args...)(x) -> {operator.__name__}(x, args...)
    """
    
    operator: Callable[..., bool]
    
    def __call__(self, value: Any) -> bool:
        return self.neg ^ self.operator(value, *self.bound)

        
@dataclass(frozen=True, init=False, repr=False)
class OperatorR(Predicate):
     """
     Predicate partial construction wrapper with free argument last:
         {name}(args...)(x) -> {operator.__name__}(args..., x)
    """
     
     operator: Callable[..., bool]
     
     def __call__(self, value: Any) -> bool:
         return self.neg ^ self.operator(*self.bound, value)

   
@dataclass(frozen=True, init=False, repr=False)
class Combinator(Predicate):
    """
    Predicate partial construction wrapper for the fanout:
        {name}(predicates...)(x) -> {combinator.__name__}(p(x) for p in predicates)
    """
    
    combinator: Callable[..., bool]
        
    def __call__(self, value: Any) -> bool:
        return self.neg ^ self.combinator(p(value) for p in self.bound)

       
@dataclass(frozen=True, init=False, repr=False)
class Compose(Predicate):
    """
    Predicate partial construction for the function composition:
    {name}(predicate, f1, f2, ...)(x) -> predicate(f1(f2...(x)))
    """
    
    compose: bool = True # marker for metadata
    
    def __init__(self, pred: Predicate, *funcs: Callable[[Any], Any]) -> None:
        object.__setattr__(self, "bound", (pred, *funcs))
            
    def __call__(self, value: Any) -> bool:
        for func in reversed(self.bound):
            value = func(value)
        return value
