"""Minimal exerciser for typing_refined predicates, Validator, and validate_args."""

from typing import Annotated, Any
from typing_refined import (
    Predicate, 
    Ge, Gt, Le, Lt, Eq, Ne,
    IsFinite, IsNotFinite, IsNan, IsNotNan, IsInfinite, IsNotInfinite,
    HasAttr, IsInstance, IsPredicate, IsOperator,
    IsCongruentMod,
    PAll, PAny,
    MatchRE,
    Range, IsEmpty, NonEmpty, LengthLt, LengthRange,
    IsOneOf, HasAtLeastOf,
    ValidationError, validate, Validator, validate_args, validate_struct,
)


# Predicate exerciser.

PREDICATE_TESTS: list[tuple[Predicate, list[Any], list[Any]]] = [
    # (predicate_instance, values_that_should_pass, values_that_should_fail)
    (Ge(0), [0, 1, 100], [-1, -100]),
    (Gt(0), [1, 100], [0, -1]),
    (Le(10), [0, 5, 10], [11, 100]),
    (Lt(10), [0, 5, 9], [10, 11]),
    (Eq(5), [5], [4, 6, "5"]),
    (Ne(5), [4, 6, "5"], [5]),
    (IsFinite, [0, 1.5, -100], [float('inf'), float('-inf'), float('nan')]),
    (IsNotFinite, [float('inf'), float('-inf'), float('nan')], [0, 1.5]),
    (IsNan, [float('nan')], [0, float('inf')]),
    (IsNotNan, [0, 1.5, float('inf')], [float('nan')]),
    (IsInfinite, [float('inf'), float('-inf')], [0, 1.5, float('nan')]),
    (IsNotInfinite, [0, 1.5, float('nan')], [float('inf'), float('-inf')]),
    (HasAttr("__len__"), ["foo", "bar", []], [5, None]),
    (IsInstance(int), [1, 0, -5], ["1", 1.0, None]),
    (IsInstance(str), ["foo", ""], [1, None]),
    (IsPredicate, [Ge(0), Gt(1)], [1, "not a predicate"]),
    (IsOperator, [Ge(0), Gt(1)], [1, "not an operator"]),
    (IsCongruentMod(2, 0), [0, 2, 4, -2], [1, 3, -1]),
    (IsCongruentMod(3, 1), [1, 4, 7, -2], [0, 2, 3]),
    (PAll(Ge(0), Lt(10)), [0, 5, 9], [-1, 10, 100]),
    (PAny(Lt(0), Gt(10)), [-5, 15], [0, 5, 10]),
    (MatchRE(r"^foo.*bar$"), ["foobar", "foo123bar", "foo_bar"],
        ["foo", "bar", "baz", "foobaz"]),
    (Range(0, 10), [0, 5, 9], [-1, 10, 15]),
    (Range(10), [0, 5, 9], [-1, 10]),
    (Range(0, 10, 2), [0, 2, 4, 6, 8], [1, 3, 5, 10]),
    (IsEmpty, ["", [], {}], ["foo", [1], {"x": 1}]),
    (NonEmpty, ["foo", [1], {"x": 1}], ["", [], {}]),
    (LengthLt(4), ["foo", [1, 2], {"x": 1}], ["foobar", [1, 2, 3, 4]]),
    (LengthRange(1, 4), ["x", "foo", [1], [1, 2]], ["", "foobar", [1, 2, 3, 4]]),
    (LengthRange(4), ["", "x", "foo", [], [1], [1, 2]], ["foobar", [1, 2, 3, 4]]),
    # container predicates
    (IsOneOf(["red", "green", "blue"]), ["red", "green", "blue"], ["yellow", "", 1]),
    (HasAtLeastOf(3, "a"), ["aaa", "ababa", ["a", "a", "a"]],
        ["aa", "bb", ["a", "a"]]),
]


def test_predicates():
    """Exercise all predicates with pass/fail cases."""
    for pred, pass_vals, fail_vals in PREDICATE_TESTS:
        print(pred, pass_vals, fail_vals)
        for v in pass_vals:
            assert pred(v), f"{pred!r} should pass for {v!r}"
        for v in fail_vals:
            assert not pred(v), f"{pred!r} should fail for {v!r}"
    print(f"All {len(PREDICATE_TESTS)} predicate tests passed")


# Validator descriptor

class SampleClass:
    value: Annotated[int, Ge(0), Lt(100)] = Validator() # type: ignore[assignment]`
    name: Annotated[str, NonEmpty, MatchRE(r"^foo.*bar$")] = Validator() # type: ignore[assignment]`

class StructClass:
    port: Annotated[int, Ge(1), Lt(65536)]
    name: Annotated[str, NonEmpty]


def test_validator():
    """Exercise Validator descriptor."""
    obj = SampleClass()
    obj.value = 50
    obj.name = "foobar"

    # Fail on value
    try:
        obj.value = -1
        assert False, "should have raised"
    except ValidationError as e:
        assert e.name == "value" and e.value == -1

    # Fail on name
    try:
        obj.name = "foo"
        assert False, "should have raised"
    except ValidationError as e:
        assert e.name == "name" and e.value == "foo"

    print("Validator tests passed")


# validate_args decorator 

@validate_args
def greet(
    name: Annotated[str, NonEmpty, MatchRE(r"^foo.*bar$")], age: Annotated[int, Ge(0), Lt(150)]
) -> str:
    return f"{name} is {age}"


def test_validate_args():
    """Exercise validate_args decorator."""
    assert greet("foobar", 30) == "foobar is 30"

    try:
        greet("foo", 30)
        assert False, "should have raised"
    except ValidationError as e:
        assert e.name == "name"

    try:
        greet("foobar", -5)
        assert False, "should have raised"
    except ValidationError as e:
        assert e.name == "age"

    print("validate_args tests passed")


# validate() function

PositiveInt = Annotated[int, Ge(1)]
NonEmptyStr = Annotated[str, NonEmpty]


def test_validate_struct():
    """Exercise validate_struct() on a class with annotated fields."""
    obj = StructClass()
    obj.__dict__["port"] = 8080
    obj.__dict__["name"] = "foo"
    validate_struct(obj, StructClass)  # passes silently

    obj.__dict__["port"] = 0
    try:
        validate_struct(obj, StructClass)
        assert False, "should have raised"
    except ValidationError as e:
        assert e.name == "port" and e.value == 0

    obj.__dict__["port"] = 8080
    obj.__dict__["name"] = ""
    try:
        validate_struct(obj, StructClass)
        assert False, "should have raised"
    except ValidationError as e:
        assert e.name == "name" and e.value == ""

    print("validate_struct tests passed")


def test_validate_function():
    """Exercise validate() function directly."""
    assert validate("x", 5, PositiveInt) is None
    assert validate("y", "foo", NonEmptyStr) is None

    try:
        validate("x", 0, PositiveInt)
        assert False
    except ValidationError as e:
        assert e.name == "x" and e.value == 0

    try:
        validate("y", "", NonEmptyStr)
        assert False
    except ValidationError as e:
        assert e.name == "y"

    print("validate() function tests passed")


if __name__ == "__main__":
    test_predicates()
    test_validator()
    test_validate_args()
    test_validate_struct()
    test_validate_function()
    print("Done.")
