from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar, cast
from dataclasses import dataclass

    
@dataclass(frozen=True, init=False, repr=False)
class OperadPartial(ABC):
    """Base Operad class to capture partial arguments"""
    class_: str = "---"
    bound: tuple[Any, ...] = ()
    operator: Callable[..., Any] = (lambda *_: None)
       
    def __init__(self, *args: Any):
        object.__setattr__(self, "class_", type(self).__name__)
        object.__setattr__(self, "bound", self.bound + args)

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass


class CallR(OperadPartial):
    """Free variables last (after bound)"""
    def __call__(self, *free: Any, **kwargs: Any) -> Any:
        return self.operator(*self.bound, *free, **kwargs)
        
class CallL(OperadPartial):        
    """Free variables first (before bound)"""
    def __call__(self, *free: Any, **kwargs: Any) -> Any:
        return self.operator(*free, *self.bound, **kwargs)

@dataclass(frozen=True, init=False, repr=False)
class Predicate(OperadPartial):
    """Marker and base class for Predicates. """
    neg: bool = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.neg ^ bool(super().__call__(*args, **kwargs))
        
    def __repr__(self):
        prefix = '!' if self.neg else ''
        return f"{prefix}{type(self).__name__}({self.bound})"

        
PredT = TypeVar('PredT', bound=OperadPartial)

def make_predicate(name: str, base: type[PredT], **attrs: Any) -> type[PredT]:
    """Factory for predicates.  Note 'type()' is used both to properly name objects
    and to massively cut down on the unhelpful level of boiler plate clutter.
    Doc-strings are populated versions of their parent strings."""
    
    cls = cast(type[PredT], type(name, (base,), attrs))
    cls.__doc__ = (base.__doc__ or "").format(name=name, **attrs)
    return cls


@dataclass(frozen=True, init=False, repr=False)
class Operator(Predicate, CallL):
    """Predicate partial construction wrapper with free argument first:
        {name}(args...)(x) -> {operator.__name__}(x, args...) """

        
@dataclass(frozen=True, init=False, repr=False)
class OperatorR(Predicate, CallR):
    """Predicate partial construction wrapper with free argument last:
         {name}(args...)(x) -> {operator.__name__}(args..., x) """

   
@dataclass(frozen=True, init=False, repr=False)
class Combinator(Predicate):
    """ Predicate partial construction wrapper for the fanout:
        {name}(predicates...)(x) -> {operator.__name__}(p(x) for p in predicates)"""
    #combinator: Callable[..., bool]
        
    def __call__(self, value: Any) -> bool:
        return self.neg ^ self.operator(p(value) for p in self.bound)

       
@dataclass(frozen=True, init=False, repr=False)
class Compose(Predicate):
    """Predicate partial construction for the function composition:
    {name}(predicate, f1, f2, ...)(x) -> predicate(f1(f2...(x)))"""
    
    def __init__(self, pred: Predicate, *funcs: Callable[[Any], Any]) -> None:
        super().__init__(pred, *funcs)
            
    def __call__(self, value: Any) -> bool:
        for func in reversed(self.bound):
            value = func(value)
        return value
        
# Special case for when the Predicate remains partial.
class ComposePartial(Compose):
    """Predicate partial construction for the function composition:
    {name}(predicate, f1, f2, ...)(args...)(x) -> predicate(args...)(f1(f2...(x)))"""
    comp: tuple[Callable[..., Predicate], *tuple[Callable[[Any], Any], ...]] 
    
    def __init__(self, *x: Any, **y: Any):
        super().__init__(self.comp[0](*x, **y), *self.comp[1:])
