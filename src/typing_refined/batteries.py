"""
Batteries included predicates.

These are NOT in the core predicates module because they are either:
- Application-specific (email, URL, UUID, etc.)
- Pre-composed combinations of core primitives
- Have opinionated defaults (regex patterns)

Import explicitly when needed:
    from typing_refined.batteries import Email, URL, UUID, CountGe, LengthGe
"""
from typing import Any
import re
from .classes import (Operator, Compose, ComposePartial, make_predicate)
from .predicates import (
    MatchRE, Eq, Ge, Gt, Le, Lt, Ne, CountOf,
)


# More from std operator class
IsAlpha = make_predicate('IsAlpha', Operator, operator=staticmethod(str.isalpha))()
IsAlphaNumeric = make_predicate('IsAlphaNumeric', Operator, operator=staticmethod(str.isalnum))()
IsNumeric = make_predicate('IsNumeric', Operator, operator=staticmethod(str.isdigit))()
IsPrintable = make_predicate('IsPrintable', Operator, operator=staticmethod(str.isprintable))()


def _make_regex(name: str, pattern: str | re.Pattern[Any]):
    """Standardized MatchRE singleton factory."""
    return make_predicate(name, MatchRE, bound=(re.compile(pattern),))()


IsEmail_Zod = _make_regex('IsEmail_Zod', r"^(?!\.)(?!.*\.\.)([a-z0-9_'+\-\.]*)[a-z0-9_+\-]@([a-z0-9][a-z0-9\-]*\.)+[a-z]{2,}$")
IsSimpleURL = _make_regex('IsURL', r"^https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?$")
IsUUID = _make_regex('IsUUID', r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")

# ISO 8601 date
IsISODateFormat = _make_regex('IsISODateFormat', r"^\d{4}-\d{2}-\d{2}$")
IsISODateTimeFormat = _make_regex('IsISODateTimeFormat', r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$")

IsBase64 = _make_regex('Base64', r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
IsBase58Alphabet = _make_regex('Base58Alphabet', r"^[1-9A-HJ-NP-Za-km-z]+$") # Bitcoin addresses


def _isbn(regexp: re.Pattern[str], trans: dict[int, str | None], s: str) -> str | None:
    m : re.Match[str] | None = regexp.search(s)
    return m[1].translate(trans) if m else None
    
    
class IsISBN10Check(Operator):
    ISBN10_RE: re.Pattern[str] = re.compile(r'(?:ISBN[- ]*)?((?:\d[- ]*){9}[0-9Xx])')
    ISBN10_TRANS: dict[int, str | None] = str.maketrans(
        {'-': None, ' ': None, 'X': ':', 'x': ':', }
    )
    
    @classmethod 
    def checksum(cls, s: str) -> bool:
        x : str | None = _isbn(cls.ISBN10_RE, cls.ISBN10_TRANS, s)
        return sum((10 - i) * (ord(c) - 48)
            for i, c in enumerate(x)) % 11 == 0 if x else False
            
    operator = checksum
    
IsISBN10Format = _make_regex('IsISBN10Format', IsISBN10Check.ISBN10_RE)

class IsISBN13Check(Operator):
    ISBN13_RE: re.Pattern[str] = re.compile(r'(?:ISBN[- ]*)?((?:\d[- ]*){13})' )
    ISBN13_TRANS: dict[int, str | None] = str.maketrans({'-': None, ' ': None})
    
    @classmethod 
    def checksum(cls, s: str) -> bool:
        x : str | None = _isbn(cls.ISBN13_RE, cls.ISBN13_TRANS, s)
        return sum((1 + 2 * (i & 1)) * (ord(c) - 48)
            for i, c in enumerate(x)) % 10 == 0 if x else False
        
    operator = checksum
  
IsISBN13Format = _make_regex('IsISBN13Format', IsISBN13Check.ISBN13_RE)
        
# More Length predicates
LengthEq = make_predicate('LengthGe', ComposePartial, comp=(Eq, len))
LengthGe = make_predicate('LengthGe', ComposePartial, comp=(Ge, len))
LengthGt = make_predicate('LengthGt', ComposePartial, comp=(Gt, len))
LengthLe = make_predicate('LengthLe', ComposePartial, comp=(Le, len))

# More Count predicates (class pattern like HasAtLeastOf)

class CountGe(Compose):
    def __init__(self, n: int, x: Any):
        super().__init__(Ge(n), CountOf(x))

class CountGt(Compose):
    def __init__(self, n: int, x: Any):
        super().__init__(Gt(n), CountOf(x))

class CountLe(Compose):
    def __init__(self, n: int, x: Any):
        super().__init__(Le(n), CountOf(x))

class CountLt(Compose):
    def __init__(self, n: int, x: Any):
        super().__init__(Lt(n), CountOf(x))

# Numeric conveniences

Positive = Gt(0)
Negative = Lt(0)
NonZero = Ne(0)
NonNegative = Ge(0)
NonPositive = Le(0)
