import io
from typing import *


ALPHABET_SIZE = 256


class BmInputType(object):
    STRING = 0
    FILE = 1


class BmInputStream(object):
    def __init__(self, obj, offset=0):
        self.data_type = None
        self.pos = offset
        self.data_size = 0

        if isinstance(obj, io.IOBase):
            self.data_type = BmInputType.FILE
            obj.seek(0, 2)
            self.data_size = obj.tell()
            obj.seek(self.pos)
            self.obj = obj
        elif isinstance(obj, str):
            self.data_type = BmInputType.STRING
            self.data_size = len(obj)
            self.obj = obj.encode()
        elif isinstance(obj, bytes):
            self.data_type = BmInputType.STRING
            self.data_size = len(obj)
            self.obj = obj
        else:
            raise ValueError(f"Invalid data type {type(obj)}")

    def peek(self, pos):
        ret = None
        if self.data_type == BmInputType.STRING:
            ret = self.obj[pos]
        elif self.data_type == BmInputType.FILE:
            self.obj.seek(pos)
            ret = self.obj.read(1)[0]

        return ret


def match_length(S: bytes, idx1: int, idx2: int) -> int:
    """Return the length of the match of the substrings of S beginning at idx1 and idx2."""
    if idx1 == idx2:
        return len(S) - idx1

    match_count = 0
    while idx1 < len(S) and idx2 < len(S) and S[idx1] == S[idx2]:
        match_count += 1
        idx1 += 1
        idx2 += 1

    return match_count

def fundamental_preprocess(S: bytes) -> List[int]:
    """Return Z, the Fundamental Preprocessing of S.

    Z[i] is the length of the substring beginning at i which is also a prefix of S.
    This pre-processing is done in O(n) time, where n is the length of S.
    """
    if len(S) == 0:  # Handles case of empty string
        return []

    if len(S) == 1:  # Handles case of single-character string
        return [1]

    z = [0 for x in S]
    z[0] = len(S)
    z[1] = match_length(S, 0, 1)

    for i in range(2, 1 + z[1]):  # Optimization from exercise 1-5
        z[i] = z[1] - i + 1

    # Defines lower and upper limits of z-box
    l = 0
    r = 0
    for i in range(2 + z[1], len(S)):
        if i <= r:  # i falls within existing z-box
            k = i - l
            b = z[k]
            a = r - i + 1
            if b < a:  # b ends within existing z-box
                z[i] = b
            else:  # b ends at or after the end of the z-box, we need to do an explicit match to the right of the z-box
                z[i] = a + match_length(S, a, r + 1)
                l = i
                r = i + z[i] - 1
        else:  # i does not reside within existing z-box
            z[i] = match_length(S, 0, i)
            if z[i] > 0:
                l = i
                r = i + z[i] - 1

    return z

def bad_character_table(S: bytes) -> List[List[int]]:
    """
    Generates R for S, which is an array indexed by the position of some character c in the
    English alphabet. At that index in R is an array of length |S|+1, specifying for each
    index i in S (plus the index after S) the next location of character c encountered when
    traversing S from right to left starting at i. This is used for a constant-time lookup
    for the bad character rule in the Boyer-Moore string search algorithm, although it has
    a much larger size than non-constant-time solutions.
    """
    if len(S) == 0:
        return [[] for a in range(ALPHABET_SIZE)]

    R = [[-1] for a in range(ALPHABET_SIZE)]
    alpha = [-1 for a in range(ALPHABET_SIZE)]

    for i, c in enumerate(S):
        alpha[c] = i
        for j, a in enumerate(alpha):
            R[j].append(a)

    return R

def good_suffix_table(S: str) -> List[int]:
    """
    Generates L for S, an array used in the implementation of the strong good suffix rule.
    L[i] = k, the largest position in S such that S[i:] (the suffix of S starting at i) matches
    a suffix of S[:k] (a substring in S ending at k). Used in Boyer-Moore, L gives an amount to
    shift P relative to T such that no instances of P in T are skipped and a suffix of P[:L[i]]
    matches the substring of T matched by a suffix of P in the previous match attempt.
    Specifically, if the mismatch took place at position i-1 in P, the shift magnitude is given
    by the equation len(P) - L[i]. In the case that L[i] = -1, the full shift table is used.
    Since only proper suffixes matter, L[0] = -1.
    """
    L = [-1 for c in S]
    N = fundamental_preprocess(S[::-1])  # S[::-1] reverses S
    N.reverse()

    for j in range(0, len(S) - 1):
        i = len(S) - N[j]
        if i != len(S):
            L[i] = j

    return L

def full_shift_table(S: str) -> List[int]:
    """
    Generates F for S, an array used in a special case of the good suffix rule in the Boyer-Moore
    string search algorithm. F[i] is the length of the longest suffix of S[i:] that is also a
    prefix of S. In the cases it is used, the shift magnitude of the pattern P relative to the
    text T is len(P) - F[i] for a mismatch occurring at i-1.
    """
    F = [0 for c in S]
    Z = fundamental_preprocess(S)

    longest = 0
    for i, zv in enumerate(reversed(Z)):
        longest = max(zv, longest) if zv == i + 1 else longest
        F[-i - 1] = longest

    return F

def _base_search(R, L, F, P, T) -> List[int]:
    """
    Implementation of the Boyer-Moore string search algorithm. This finds all occurrences of P
    in T, and incorporates numerous ways of pre-processing the pattern to determine the optimal
    amount to shift the string and skip comparisons. In practice it runs in O(m) (and even
    sublinear) time, where m is the length of T. This implementation performs a case-insensitive
    search on ASCII alphabetic characters, spaces not included.
    """
    matches = []

    stream = BmInputStream(T)

    if len(P) == 0 or stream.data_size == 0 or stream.data_size < len(P):
        return []

    k = len(P) - 1      # Represents alignment of end of P relative to T
    previous_k = -1     # Represents alignment in previous phase (Galil's rule)

    while k < stream.data_size:
        i = len(P) - 1  # Character to compare in P
        h = k           # Character to compare in T

        while i >= 0 and h > previous_k and P[i] == stream.peek(h):  # Matches starting from end of P
            i -= 1
            h -= 1

        if i == -1 or h == previous_k:  # Match has been found (Galil's rule)
            matches.append(k - len(P) + 1)
            k += len(P) - F[1] if len(P) > 1 else 1

        else:  # No match, shift by max of bad character and good suffix rules
            char_shift = i - R[stream.peek(h)][i]
            if i + 1 == len(P):  # Mismatch happened on first attempt
                suffix_shift = 1
            elif L[i + 1] == -1:  # Matched suffix does not appear anywhere in P
                suffix_shift = len(P) - F[i + 1]
            else:               # Matched suffix appears in P
                suffix_shift = len(P) - 1 - L[i + 1]
            shift = max(char_shift, suffix_shift)
            previous_k = k if shift >= i + 1 else previous_k  # Galil's rule
            k += shift

    return matches

def boyermoore_preprocess(P):
    if isinstance(P, str):
        P = P.encode()
    elif not isinstance(P, bytes):
        raise ValueError("Pattern must be str or bytes")

    R = bad_character_table(P)
    L = good_suffix_table(P)
    F = full_shift_table(P)

    return R, L, F, P

def boyermoore_string_pp(pp_data, string):
    R, L, F, P = pp_data
    return _base_search(R, L, F, P, string)

def boyermoore_string(pattern, string):
    R, L, F, P = boyermoore_preprocess(pattern)
    return _base_search(R, L, F, P, string)

def boyermoore_file(pattern, filename):
    R, L, F, P = boyermoore_preprocess(pattern)
    return _base_search(R, L, F, P, open(filename, 'rb'))

def boyermoore_file_pp(pp_data, filename):
    R, L, F, P = pp_data
    return _base_search(R, L, F, P, open(filename, 'rb'))


#s = b"ABC\u0327\u0327ABCABCABCABC\u0327\u0327ABCABCABCABC\u0327\u0327"
#print(string_search(b'\u0327\u0327', s))
print(boyermoore_file("À Á Â Ã Ä Å", "big_file.txt"))
