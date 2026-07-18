"""
Lightweight refinement types for static analysis and runtime validation.

A refined or refinement type is defined as "a type together with one or
more predicates restricting the set of values belonging to that type."
It is often written as `{x: T | P(x)}` and in python we can get close 
with `Annotated[T, P(x)]`.

This module provides lightweight refinement types by representing
the refinements as immutable predicate objects. The same predicate object
can be executed for runtime validation, attached to typing.Annotated as
metadata, and introspected by analysis tools.

The guiding principle is that a **refinement should be defined once and reused
everywhere**. So a ``Predicate``` is a callable object that serves
simultaneously as executable code via the ``__call__`` dunder function, 
annotation metadata by including in a Annotated[type, ...] type, and as
introspectable metadata via dataclasses.asdict() which will return the complete 
deep AST for the typing expression. 

Very little is added for the AST in that it mirrors standard logic forms,
and uses Python built-in or standard library function references for stable
unique IDs rather than defining things a new. Operators like '&' or 'not'
are not needed (nor wanted!)

There's a widespread habit of thinking of Annotated metadata as something that 
should merely be interpreted by other code. However annotations, introspection,
and execution are orthogonal concerns. This is important. There is no
difference in introspecting metadata if there is also a __call__ method that
implements a default validation strategy. Nothing is lost.

In fact, if the default validation path is used, then the path itself is an
executable specification that static analysis tools may reason about using
ordinary Python analysis, even if it cannot interpret the raw metadata.
"""


from .classes import Combinator, Compose, ComposePartial, Operator, OperatorR, Predicate, make_predicate
from .predicates import (
    Ge, Gt, Le, Lt, Eq, Ne,
    IsFinite, IsNotFinite, IsNan, IsNotNan, IsInfinite, IsNotInfinite,
    IsCongruentMod,
    HasAttr, HasShape, HasKeys,
    IsInstance, IsPredicate, IsOperator,
    PAll, PAny,
    MatchRE,
    Range,
    IsEmpty, NonEmpty, LengthLt, LengthRange,
    IsOneOf, CountOf, HasAtLeastOf,
)
from .consumer_validate import ValidationError, validate, Validator, validate_args, validate_struct
from ._version import __version__

__all__ = [
    "Predicate", "Operator", "OperatorR", "Combinator", "Compose", "ComposePartial", "make_predicate",
    "Ge", "Gt", "Le", "Lt", "Eq", "Ne",
    "IsFinite", "IsNotFinite", "IsNan", "IsNotNan", "IsInfinite", "IsNotInfinite",
    "HasAttr", "IsInstance", "IsPredicate", "IsOperator", "HasShape", "HasKeys",
    "IsCongruentMod",
    "PAll", "PAny",
    "MatchRE", 
    "Range",
    "IsEmpty", "NonEmpty", "LengthLt", "LengthRange",
    "IsOneOf", "CountOf", "HasAtLeastOf",
    "ValidationError",
    "validate", "Validator", "validate_args", "validate_struct",
    "__version__",
]
