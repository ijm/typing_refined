import operator
import math
import re
from typing import Any, Optional, TypeGuard, TypeVar, Generic
from .classes import (CallL, Predicate, Operator, OperatorR, Combinator, 
    Compose, ComposePartial, make_predicate)
from collections.abc import Mapping

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

# Fanout combinators for Conjunction and Disjunction
PAll = make_predicate('All', Combinator, operator=all)
PAny = make_predicate('Any', Combinator, operator=any)

# Misc Derived predicates
class MatchRE(OperatorR):
    """Some {name} -> MatchRE({bound[0]})"""
    operator = staticmethod(re.search)
    
class IsCongruentMod(Operator):
    @classmethod
    def is_congruent(cls, x: int, step: int, offset: int):
        """x is in the congruence class of offset under mod step"""
        return (x - offset) % step == 0
        
    operator = is_congruent

    
class Range(PAll): # type: ignore[valid-type, misc]
    """Range predicate with same signature as built-in range()"""
    def __init__(self, a: int, b: Optional[int] = None, step: int = 1):
        if b is None:
            super().__init__(Ge(0), Lt(a), IsCongruentMod(step, 0))
        else:
            super().__init__(Ge(a), Lt(b), IsCongruentMod(step, a))


class HasShape(Operator):
    @classmethod
    def has_shape(cls, value: Any, shape: type) -> bool:
        """Check value exposes every attribute named on `shape`."""
        attrs = getattr(shape, '__protocol_attrs__', None)
        if attrs is None:
            attrs = set(shape.__dict__) | set(getattr(shape, '__annotations__', {}))
        return all(hasattr(value, a) for a in attrs)
        
    operator = has_shape


# Class predicates
HasAttr = make_predicate('HasAttr', Operator, operator=hasattr)

#IsInstance = make_predicate('IsInstance', Operator, operator=isinstance)

T = TypeVar('T')

class IsInstance(Operator, Generic[T]):
    operator = isinstance
    def __call__(self, obj: Any) -> TypeGuard[T]:
        return super().__call__(obj)

IsPredicate = IsInstance[Predicate](Predicate)
IsOperator = IsInstance[Operator](Operator)
IsMapping = IsInstance[Mapping[Any,Any]](Mapping)

# Container and size predicates
IsEmpty = make_predicate('IsEmpty', Compose)(Eq(0), len)
NonEmpty = make_predicate('NonEmpty', Compose)(Gt(0), len)
IsOneOf = make_predicate('IsOneOf', OperatorR, operator=operator.contains)
CountOf = make_predicate('CountOf', CallL, operator=operator.countOf)
LengthLt = make_predicate('LengthLt', ComposePartial, comp=(Lt, len))
LengthRange = make_predicate('LengthRange', ComposePartial, comp=(Range, len))
HasKeys = make_predicate('HasKeys', ComposePartial, comp=(Ge, dict.keys)) # pyright: ignore[reportUnknownMemberType]  

class HasAtLeastOf(Compose):
    def __init__(self, x: Any, y:Any):
        super().__init__(Ge(x), CountOf(y))
