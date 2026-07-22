from collections.abc import Callable
from typing import (Any, get_args, get_type_hints, get_origin,
    Annotated, Unpack, Required, NotRequired)
from inspect import signature
from functools import wraps

from .classes import Predicate
from .predicates import IsPredicate, IsMapping

# Consumers for runtime validation
class ValidationError(ValueError):
    """Raised when a value fails an attached Predicate."""
    def __init__(self, name: str, value: Any, predicate: Predicate):
        self.name = name
        self.value = value
        self.predicate = predicate
        super().__init__(f"{value!r} for {name} failed validation {predicate!r}")

      
class IsRequiredField(Predicate):
    """Sentinel predicate for missing fields."""
    MISSING = object()


def validate(name: str,
    value: Any,
    hint: Any,
    unwrapped: frozenset[Any] = frozenset()
) -> None:
    """Recurse: validate `value` against `hint`, descending into nested
    structs as the hint dictates. `unwrapped` accumulates Required/
    NotRequired modifiers seen on the path from the root value to here.
    """

    def field_value(obj: Any, field: str) -> Any:
        """Fetch a field from a mapping or object; `MISSING` if absent."""
        if IsMapping(obj):
            return obj.get(field, IsRequiredField.MISSING) 
        return getattr(obj, field, IsRequiredField.MISSING)


    origin = get_origin(hint)

    #  Required/NotRequired modulate how a later missing-field case reads
    #  (Required -> failure, NotRequired -> pass).
    if origin in (Required, NotRequired):
        return validate(name, value, get_args(hint)[0], unwrapped | {origin})

    # 2. Annotated: run attached predicates against the present value,
    #    then recurse on the bare type so a struct-typed
    #    Annotated[X, preds] still descends into its fields.
    if origin is Annotated:
        if value is IsRequiredField.MISSING:
            if Required in unwrapped:
                raise ValidationError(name, IsRequiredField.MISSING, IsRequiredField())
            return
        for p in filter(IsPredicate, get_args(hint)[1:]):
            if not p(value):
                raise ValidationError(name, value, p)
        return validate(name, value, get_args(hint)[0], unwrapped)

    # 3. Struct: iterate declared fields, fetch the value for each.
    #    An Unpack[X] walks X's fields.
    field_hints: dict[str, Any] = {}
    if origin is Unpack:
        field_hints = get_type_hints(get_args(hint)[0], include_extras=True)
    elif origin is None and isinstance(hint, type):
        field_hints = get_type_hints(hint, include_extras=True)
    for field, field_hint in field_hints.items():
        full = f"{name}.{field}" if name else field
        sub = field_value(value, field)
        validate(full, sub, field_hint, frozenset())
    # 4. (Union would go here. Not today.)


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
    validate("", instance, typed_type)


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
