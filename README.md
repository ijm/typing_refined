# typing_refined

Lightweight refinement types for static analysis and runtime validation.

## Installation

```bash
pip install typing_refined
```

## Design Principles
A refined or refinement type is defined as "a type together with one or more predicates restricting the set of values belonging to that type." It is often written as `{x: T | P(x)}` and in python we can get close with `Annotated[T, P]`.

Python's `Annotated[]` types are often seen as passive information to be interpreted by some external library or application. Without affecting that interpretation, typing_refined represents refinements as ordinary immutable Python objects. There are three orthogonal concerns: the same object can be attached to type annotations, executed directly, or inspected structurally without requiring separate representations or translation between them.

- **Refinement types**: `{x: T | P(x)}` expressed as `Annotated[T, P]`
- **Predicates are triple-role**: callable as `predicate(x)`, annotation metadata as `Annotated[T, predicate]`, introspectable AST as `dataclasses.asdict(predicate)`
- **Define once, reuse everywhere**: Same predicate object for runtime validation, static analysis, tooling, etc. (DRY)
- **Simple Algebra**: compose with `PAll`, `PAny`, `Compose`. These are explicit and introspectable, and extensive enough without needing to build an complex expression algebra.

### Available Predicates

| Category | Predicates |
|----------|------------|
| Comparison | `Ge`, `Gt`, `Le`, `Lt`, `Eq`, `Ne` |
| Numeric | `IsFinite`, `IsNotFinite`, `IsNan`, `IsNotNan`, `IsInfinite`, `IsNotInfinite`, `IsCongruentMod`, `Range` |
| String | `MatchRE` |
| Container | `IsOneOf`, `CountOf`, `HasAtLeastOf`, `HasKeys` |
| Length/size | `NonEmpty`, `IsEmpty`, `LengthLt`, `LengthRange` |
| Type/Structure | `IsInstance`, `HasAttr`, `HasShape`, `IsPredicate`, `IsOperator` |
| Combinators | `PAll`, `PAny`, `Compose` |

All predicates work as:
- Callable : `predicate(value)` returns `bool`
- Annotation metadata : inside `Annotated[T, predicate]`
- Introspectable : `dataclasses.asdict(predicate)` returns full AST

## Batteries Included (Additional Predicates)

Additional example predicates for uncommon or application specific validation scenarios are available in the `batteries` module:

| Category | Predicates |
|----------|------------|
| String checks | `IsAlpha`, `IsAlphaNumeric`, `IsNumeric`, `IsPrintable` |
| Format validation | `IsEmail_Zod`, `IsSimpleURL`, `IsUUID`, `IsISBN10Check`, `IsISBN13Check`, `IsISBN10Format`, `IsISBN13Format` |
| Date/Time formats | `IsISODateFormat`, `IsISODateTimeFormat` |
| Encoding | `IsBase64`, `IsBase58Alphabet` |
| Length (extended) | `LengthEq`, `LengthGe`, `LengthGt`, `LengthLe` |
| Count (extended) | `CountGe`, `CountGt`, `CountLe`, `CountLt` |
| Numeric conveniences | `Positive`, `Negative`, `NonZero`, `NonNegative`, `NonPositive` |

Import from `typing_refined.batteries` and use the same way as core predicates.

## Quick example for the runtime validation consumer.

### Explicit (manual) validation

```python
from typing import Annotated
from typing_refined import Ge, Lt, validate

# Define a refined type such as positive integers < 100
PositiveUnder100 = Annotated[int, Ge(1), Lt(100)]

# Manual validation
validate("foo", 50, PositiveUnder100)   # Ok
validate("foo", 200, PositiveUnder100)  # raises ValidationError
```

### Class Field Validation with Validator()

Use `Validator` as a descriptor to enforce predicates on attribute assignment:

```python
from typing import Annotated
from typing_refined import Ge, Lt, Le, Validator, ValidationError

class Config:
    port: Annotated[int, Ge(1), Lt(65536)] = Validator()
    timeout: Annotated[float, Ge(0.1), Le(60.0)] = Validator()

cfg = Config()
cfg.port = 8080      # ok
cfg.port = 70000     # raises ValidationError
cfg.timeout = 30.0   # ok
```

### Object Validation with validate_struct()

Validate all annotated fields of an object at once:

```python
from typing import Annotated
from typing_refined import Ge, Lt, validate_struct

class Config:
    port: Annotated[int, Ge(1), Lt(65536)]
    timeout: Annotated[float, Ge(0.1), Le(60.0)]

cfg = Config()
cfg.port = 8080
cfg.timeout = 30.0
validate_struct(cfg, Config)  # raises ValidationError if any field fails
```

### Function Argument Validation with @validate_args decorator

Decorate functions to validate all annotated arguments at call time:

```python
from typing import Annotated
from typing_refined import Ge, Lt, MatchRE, validate_args

@validate_args
def create_user(
    age: Annotated[int, Ge(18), Lt(120)],
    email: Annotated[str, MatchRE(r"^[^@]+@[^@]+\.[^@]+$")],
    name: Annotated[str, NonEmpty],
) -> None:
    ...

create_user(25, "alice@example.com", "Alice")   # ok 
create_user(15, "alice@example.com", "Alice")   # raises ValidationError (age)
create_user(25, "not-an-email", "Alice")        # raises ValidationError (email)
```


## License

MIT : see [LICENSE](LICENSE).
