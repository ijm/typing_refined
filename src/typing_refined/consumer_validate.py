from collections.abc import Callable
from typing import Any, get_args, get_type_hints
from inspect import signature
from functools import wraps

from .classes import Predicate
from .predicates import IsPredicate

# Consumers for runtime validation
class ValidationError(ValueError):
    """Raised when a value fails an attached Predicate."""
    def __init__(self, name: str, value: Any, predicate: Predicate):
        self.name = name
        self.value = value
        self.predicate = predicate
        super().__init__(f"{value!r} for {name} failed validation {predicate!r}")

      
def validate(name:str, value: Any, annotation: Any) -> None:
    """
    Run all predicates attached to `annotation` against `value` and raise
    on failure. This is a shallow search and does not recurse into sub-annotations
    """
    for predicate in filter(IsPredicate, get_args(annotation)[1:]):
        if not predicate(value):
            raise ValidationError(name, value, predicate)


class Validator:
    """
    Descriptor enforcing a field's `Annotated[...]` Predicates on assignment.
        Usage::
            class SomeClass:
                value: Annotated[int, Ge(0), Lt(100)] = Validator()
    
        Resolves the hint via `__set_name__` at class-definition time.
        Raises `ValidationError` on assignment of a value that fails any
        attached Predicate.
        """
        
    def __set_name__(self, owner: Any, name: str) -> None:
        self.name: str = name
        self.annotation: Any = get_type_hints(owner, include_extras=True)[name]

    def __set__(self, obj: Any, value: Any) -> None:
        validate(self.name, value, self.annotation)
        obj.__dict__[self.name] = value


def validate_struct(instance: Any, typed_type: type) -> None:
    """
    Validate every annotated field of `instance` against predicates in
    the type hints of `typed_type`.
    """
    for name, hint in get_type_hints(typed_type, include_extras=True).items():
        validate(name, getattr(instance, name), hint)


def validate_args(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator validating all annotated arguments of `fn` at call time.
    Usage::
        class SomeClass:
            class Options(TypedDict):
                x: Annotated[int, Ge(0)]
                name: Annotated[str, Ne("")]
            @validate_args
            def __init__(self, **kwargs: Unpack[Options]) -> None: ...
            
    Raises `ValidationError` for any argument that fails its Predicates.
    """
    
    hints: dict[str, Any] = get_type_hints(fn, include_extras=True)

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        for k, v in signature(fn).bind(*args, **kwargs).arguments.items():
            if k in hints:
                validate(k, v, hints[k])
        return fn(*args, **kwargs)

    object.__setattr__(wrapper, "_hints", hints)
    return wrapper
