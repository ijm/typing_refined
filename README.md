# typing_refined

Lightweight refinement types for static analysis and runtime validation.

## Installation

```bash
pip install typing_refined
```

## Design Principles

- **Refinement types**: `{x: T | P(x)}` expressed as `Annotated[T, P(x)]`
- **Predicates are triple-duty**: callable as `pred(x)`, annotation metadata as `Annotated[T, pred(x)]`, introspectable AST as `dataclasses.asdict(pred)`)
- **Define once, reuse everywhere**: Same predicate object for runtime validation, static analysis, tooling, etc.
- **No operator overloading**: compose with `PAll`, `PAny`, `Compose`. These are explicit and introspectable, and extensive enough without needing to build a complete expression algrbra.

### Available Predicates

| Category | Predicates |
|----------|------------|
| Comparison | `Ge`, `Gt`, `Le`, `Lt`, `Eq`, `Ne` |
| Numeric | `IsFinite`, `IsNan`, `IsInfinite`, `IsCongruentMod` |
| String | `MatchRE` |
| Length/size | `NonEmpty`, `IsEmpty`, `LengthLt`, `LengthRange` |
| Type/Structure | `IsInstance`, `HasAttr`, `HasShape` |
| Combinators | `PAll`, `PAny`, `Compose` |

All predicates work as:
- Callable : `predicate(value)` returns `bool`
- Annotation metadata : inside `Annotated[T, predicate]`
- Introspectable : `dataclasses.asdict(predicate)` returns full AST

## Quick example for the runtime validation comsumer.

### Explicit (manual) validation

```python
from typing import Annotated
from typing_refined import Ge, Lt, validate

# Define a refined type such as positive integers < 100
PositiveUnder100 = Annotated[int, Ge(1), Lt(100)]

# Manual validation
validate("foo", PositiveUnder100, 50)   # returns 50
validate("foo", PositiveUnder100, 200)  # raises ValidationError
```

### Class Field Validation with Validator()

Use `Validator` as a descriptor to enforce predicates on attribute assignment:

```python
from typing import Annotated
from typing_refined import Ge, Lt, Validator, ValidationError

class Config:
    port: Annotated[int, Ge(1), Lt(65536)] = Validator()
    timeout: Annotated[float, Ge(0.1), Le(60.0)] = Validator()

cfg = Config()
cfg.port = 8080      # ok
cfg.port = 70000     # raises ValidationError
cfg.timeout = 30.0   # ok
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
