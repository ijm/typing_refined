# Changelog

## [1.0.1] - initial version

## [1.1.0] - 2026-07-21

### Added
- `TypeGuard[]` machinery on `IsInstance` predicates. 
- Recursive descent in `validate`: nesting through `Annotated[X, preds]`, `Unpack[Struct]`, bare TypedDicts/classes, and `Required`/`NotRequired` wrapper, etc. (No Union support yet)
- Missing-field handling: a missing `Required`-wrapped annotated field raises `ValidationError`
