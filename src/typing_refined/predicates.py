import operator
import math
from typing import Any, Optional
from re import search
from .classes import Predicate, Operator, OperatorR, Combinator, Compose

# Factory for predicates
def make_predicate(name: str, base: type, **attrs: Any):
    cls = type(name, (base,), attrs)
    cls.__doc__ = base.__doc__.format(name=name, **attrs)
    return cls
    
# Note 'type()' is used both to properly name objects and to massivly cut
# down on the unhelpful level of boiler plate clutter.
#         
# Numerical predicates
# Comparisons
Ge = make_predicate('Ge', Operator, operator=operator.ge)
Gt = make_predicate('Gt', Operator, operator=operator.gt)
Le = make_predicate('Le', Operator, operator=operator.le)
Lt = make_predicate('Lt', Operator, operator=operator.lt)
Eq = make_predicate('Eq', Operator, operator=operator.eq)
Ne = make_predicate('Ne', Operator, operator=operator.ne)

# Unary test
IsFinite = make_predicate('IsFinite', Operator, operator=math.isfinite)()
IsNotFinite = make_predicate('IsNotFinite', Operator, operator=math.isfinite, neg=True)()
IsNan = make_predicate('IsNan', Operator, operator=math.isnan)()
IsNotNan = make_predicate('IsNotNan', Operator, operator=math.isnan, neg=True)()
IsInfinite = make_predicate('IsInfinite', Operator, operator=math.isinf)()
IsNotInfinite = make_predicate('IsNotInfinite', Operator, operator=math.isinf, neg=True)()

class IsCongruentMod(Operator):
    @classmethod
    def is_congruent(cls, x: int, step: int, offset: int):
        """x is in the congruence class of offset under mod step"""
        return (x - offset) % step == 0
        
    operator = is_congruent 

# Class predicates
HasAttr = make_predicate('HasAttr', Operator, operator=hasattr)
IsInstance = make_predicate('IsInstance', Operator, operator=isinstance)

IsPredicate = IsInstance(Predicate)
IsOperator = IsInstance(Operator)

# Container predicates
IsOneOf = make_predicate('IsOneOf', OperatorR, operator=operator.contains)
CountOf = make_predicate('CountOf', Operator, operator=operator.countOf)


class HasAtLeastOf(Compose):
    def __init__(self, x: Any, y:Any):
        super().__init__(Ge(x), CountOf(y))

        
# Fanout combinators for Conjunction and Disjunction
PAll = make_predicate('All', Combinator, combinator=all)
PAny = make_predicate('Any', Combinator, combinator=any)


# String predicates
class MatchRE(Operator):
    @classmethod
    def is_match_re(cls, value: str, pattern: str) -> bool:
        return search(pattern, value) is not None
        
    operator = is_match_re


# Derived predicates
class Range(PAll):
    """Range predicate with same signature as built-in range()"""
    def __init__(self, a: int, b: Optional[int] = None, step: int = 1):
        if b is None:
            object.__setattr__(self, "bound", (Ge(0), Lt(a), IsCongruentMod(step, 0)))
        else:
            object.__setattr__(self, "bound", (Ge(a), Lt(b), IsCongruentMod(step, a)))

     
IsEmpty = make_predicate('IsEmpty', Compose)(Eq(0), len)
NonEmpty = make_predicate('NonEmpty', Compose)(Gt(0), len)


class LengthLt(Compose):
    def __init__(self, x: Any):
        super().__init__(Lt(x), len)

        
class LengthRange(Compose):
    def __init__(self, a: int, b: Optional[int] = None, step: int = 1):
        super().__init__(Range(a, b, step), len)       


class HasShape(Operator):
    @classmethod
    def has_shape(cls, value: Any, shape: type) -> bool:
        """Check value exposes every attribute named on `shape`."""
        attrs = getattr(shape, '__protocol_attrs__', None)
        if attrs is None:
            attrs = set(shape.__dict__) | set(getattr(shape, '__annotations__', {}))
        return all(hasattr(value, a) for a in attrs)
        
    operator = has_shape
