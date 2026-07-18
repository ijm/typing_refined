"""Battery predicates exerciser for typing_refined."""

from typing import Any
from typing_refined.batteries import (
    IsAlpha, IsAlphaNumeric, IsNumeric, IsPrintable,
    IsEmail_Zod, IsSimpleURL, IsUUID,
    IsISBN10Check, IsISBN13Check, IsISBN10Format, IsISBN13Format,
    IsISODateFormat, IsISODateTimeFormat, IsBase64, IsBase58Alphabet,
    LengthEq, LengthGe, LengthGt, LengthLe,
    CountGe, CountGt, CountLe, CountLt,
    Positive, Negative, NonZero, NonNegative, NonPositive,
)
from typing_refined import Predicate

import typing_refined as V
print(f"{V.__file__=}")

# Predicate exerciser for batteries.

PREDICATE_TESTS: list[tuple[Predicate, list[Any], list[Any]]] = [
    # str.is* predicates (instantiated singletons)
    (IsAlpha, ["abc", "ABC", "fooBar"], ["", "123", "abc123", "foo bar", "foo-bar"]),
    (IsAlphaNumeric, ["abc", "ABC", "123", "abc123"], ["", "foo bar", "foo-bar", "foo.bar"]),
    (IsNumeric, ["123", "0", "456"], ["", "12.3", "abc", "-123", "12a"]),
    (IsPrintable, ["abc", "123", "foo bar", "foo-bar"], ["\x00", "\x1f", "\u0000"]),

    # Regex-based predicates
    (IsEmail_Zod, ["foo@bar.com", "test.email+tag@domain.co.uk", "user123@site.org"],
        ["notanemail", "@domain.com", "foo@.com", "foo@bar", "foo@bar."]),
    (IsSimpleURL, ["http://example.com", "https://foo.bar/path", "http://sub.domain.org"],
        ["notaurl", "ftp://example.com", "http://", "http:/example.com"]),
    (IsUUID, ["123e4567-e89b-12d3-a456-426614174000", "00000000-0000-4000-8000-000000000000"],
        ["not-a-uuid", "123e4567-e89b-12d3-a456-42661417400", "123e4567-e89b-12d3-a456-42661417400g"]),
    (IsISBN10Check(), ["0321146530", "080442957X"], ["notanisbn", "032114653", "abcdefghij"]),
        (IsISBN13Check(), ["9780321146533"], ["notanisbn", "978032114653", "abcdefghijklm"]),
        (IsISBN10Format, ["ISBN 0-321-14653-0", "0321146530", "0-321-14653-X"],
            ["notanisbn", "032114653", "abcdefghij"]),
        (IsISBN13Format, ["ISBN 978-0-321-14653-3", "9780321146533"],
            ["notanisbn", "978032114653", "abcdefghijklm"]),
    (IsISODateFormat, ["2024-01-15", "2024-12-31", "2000-02-29"],
        ["not-a-date", "15-01-2024", "2024/01/15", "2024-1-5"]),
    (IsISODateTimeFormat, ["2024-01-15T10:30:00", "2024-01-15T10:30:00.123", "2024-01-15T10:30:00Z", "2024-01-15T10:30:00+05:00"],
        ["not-a-datetime", "2024-01-15 10:30:00", "15-01-2024T10:30:00"]),
    (IsBase64, ["", "YQ==", "YWI=", "YWJj", "YWJjZA=="],
        ["not-base64!", "YWI", "YWJjZ", "===="]),
    (IsBase58Alphabet, ["1", "12", "1A", "1a", "z", "11111111111111111111111111111111111111111111111111111"],
        ["0", "O", "I", "l", "not-base58", ""]),

    # Length predicates (ComposePartial)
    (LengthEq(3), ["foo", [1, 2, 3], {"a": 1, "b": 2, "c": 3}], ["", "fo", "foob", [1, 2]]),
    (LengthGe(3), ["foo", "foobar", [1, 2, 3], [1, 2, 3, 4]], ["", "fo", [1, 2]]),
    (LengthGt(3), ["foob", "foobar", [1, 2, 3, 4]], ["foo", "fo", [1, 2, 3], ""]),
    (LengthLe(3), ["", "fo", "foo", [1, 2]], ["foob", [1, 2, 3, 4]]),

    # Count predicates (Compose classes)
    (CountGe(2, "a"), ["aa", "aaa", "ababa", ["a", "a", "b"]], ["a", "b", ["a"]]),
    (CountGt(2, "a"), ["aaa", "ababa", ["a", "a", "a"]], ["aa", "a", ["a", "a"]]),
    (CountLe(2, "a"), ["", "a", "aa", "b", "bb", ["a", "b"]], ["aaa", ["a", "a", "a"]]),
    (CountLt(2, "a"), ["", "a", "b", "bb", ["a", "b"]], ["aa", "aaa", ["a", "a"]]),

    # Numeric conveniences (from core predicates)
    (Positive, [1, 0.5, 100], [0, -1, -0.5]),
    (Negative, [-1, -0.5, -100], [0, 1, 0.5]),
    (NonZero, [1, -1, 0.5, -0.5], [0]),
    (NonNegative, [0, 1, 0.5, 100], [-1, -0.5]),
    (NonPositive, [0, -1, -0.5, -100], [1, 0.5]),
]


def test_battery_predicates():
    """Exercise all battery predicates with pass/fail cases."""
    for pred, pass_vals, fail_vals in PREDICATE_TESTS:
        print(pred, pass_vals, fail_vals)
        for v in pass_vals:
            assert pred(v), f"{pred!r} should pass for {v!r}"
        for v in fail_vals:
            assert not pred(v), f"{pred!r} should fail for {v!r}"
    print(f"All {len(PREDICATE_TESTS)} battery predicate tests passed")


if __name__ == "__main__":
    test_battery_predicates()
    print("Done.")
