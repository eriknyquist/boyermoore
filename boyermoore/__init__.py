__version__ = "1.0.0"

# Implementation of the boyer-moore string search algorithm, based on the python
# implementation provided at https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm ,
# but modified to support Unicode and also to support searching in files.
#
# Erik K. Nyquist 2022

import array
import io
from typing import *

# We want to support Unicode strings, so instead of having an alphabet based
# on ASCII chars or UTF-8 code points, the alphabet is based on byte values,
# which requires an alphabet size of 256 for all possible byte values (0x0-0xff)
ALPHABET_SIZE = 256


def _match_length(S: bytes, idx1: int, idx2: int) -> int:
    """Return the length of the match of the substrings of S beginning at idx1 and idx2."""
    if idx1 == idx2:
        return len(S) - idx1

    match_count = 0
    while idx1 < len(S) and idx2 < len(S) and S[idx1] == S[idx2]:
        match_count += 1
        idx1 += 1
        idx2 += 1

    return match_count

def _fundamental_preprocess(S: bytes) -> List[int]:
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
    z[1] = _match_length(S, 0, 1)

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
                z[i] = a + _match_length(S, a, r + 1)
                l = i
                r = i + z[i] - 1
        else:  # i does not reside within existing z-box
            z[i] = _match_length(S, 0, i)
            if z[i] > 0:
                l = i
                r = i + z[i] - 1

    return z

def _bad_character_table(S: bytes) -> List[List[int]]:
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

def _good_suffix_table(S: str) -> List[int]:
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
    N = _fundamental_preprocess(S[::-1])  # S[::-1] reverses S
    N.reverse()

    for j in range(0, len(S) - 1):
        i = len(S) - N[j]
        if i != len(S):
            L[i] = j

    return L

def _full_shift_table(S: str) -> List[int]:
    """
    Generates F for S, an array used in a special case of the good suffix rule in the Boyer-Moore
    string search algorithm. F[i] is the length of the longest suffix of S[i:] that is also a
    prefix of S. In the cases it is used, the shift magnitude of the pattern P relative to the
    text T is len(P) - F[i] for a mismatch occurring at i-1.
    """
    F = [0 for c in S]
    Z = _fundamental_preprocess(S)

    longest = 0
    for i, zv in enumerate(reversed(Z)):
        longest = max(zv, longest) if zv == i + 1 else longest
        F[-i - 1] = longest

    return F

def _base_search_file(R, L, F, P, T, T_size, greedy) -> List[int]:
    """
    Implementation of the Boyer-Moore string search algorithm. This finds all occurrences of P
    in T, and incorporates numerous ways of pre-processing the pattern to determine the optimal
    amount to shift the string and skip comparisons. In practice it runs in O(m) (and even
    sublinear) time, where m is the length of T. This implementation performs a case-insensitive
    search on ASCII alphabetic characters, spaces not included.
    """
    matches = []
    plen = len(P)


    if plen == 0 or T_size == 0 or T_size < plen:
        return []

    k = plen - 1      # Represents alignment of end of P relative to T
    previous_k = -1     # Represents alignment in previous phase (Galil's rule)

    while k < T_size:
        i = plen - 1  # Character to compare in P
        h = k         # Character to compare in T

        T.seek(h)
        peeked = T.read(1)[0]

        while i >= 0 and h > previous_k and P[i] == peeked:  # Matches starting from end of P
            i -= 1
            h -= 1

            T.seek(h if h >= 0 else 0)
            peeked = T.read(1)[0]

        if i == -1 or h == previous_k:  # Match has been found (Galil's rule)
            matches.append(k - plen + 1)

            if not greedy:
                return matches

            k += plen - F[1] if plen > 1 else 1

        else:  # No match, shift by max of bad character and good suffix rules
            char_shift = i - R[peeked][i]

            if i + 1 == plen:  # Mismatch happened on first attempt
                suffix_shift = 1
            elif L[i + 1] == -1:  # Matched suffix does not appear anywhere in P
                suffix_shift = plen - F[i + 1]
            else:               # Matched suffix appears in P
                suffix_shift = plen - 1 - L[i + 1]

            shift = char_shift if char_shift > suffix_shift else suffix_shift
            previous_k = k if shift >= i + 1 else previous_k  # Galil's rule
            k += shift

    return matches


def _base_search_str(R, L, F, P, T, T_size, greedy) -> List[int]:
    """
    Copy of _base_search_file, but slightly modified to handle a byte string instead
    of a file handle. Duplicates a lot of code, BUT avoids additional branches or
    function calls in the inner loop.
    """
    matches = []
    plen = len(P)

    if plen == 0 or T_size == 0 or T_size < plen:
        return []

    k = plen - 1      # Represents alignment of end of P relative to T
    previous_k = -1     # Represents alignment in previous phase (Galil's rule)

    while k < T_size:
        i = plen - 1  # Character to compare in P
        h = k         # Character to compare in T

        peeked = T[h]

        while i >= 0 and h > previous_k and P[i] == peeked:  # Matches starting from end of P
            i -= 1
            h -= 1

            peeked = T[h]

        if i == -1 or h == previous_k:  # Match has been found (Galil's rule)
            matches.append(k - plen + 1)

            if not greedy:
                return matches

            k += plen - F[1] if plen > 1 else 1

        else:  # No match, shift by max of bad character and good suffix rules
            char_shift = i - R[peeked][i]

            if i + 1 == plen:  # Mismatch happened on first attempt
                suffix_shift = 1
            elif L[i + 1] == -1:  # Matched suffix does not appear anywhere in P
                suffix_shift = plen - F[i + 1]
            else:               # Matched suffix appears in P
                suffix_shift = plen - 1 - L[i + 1]

            shift = char_shift if char_shift > suffix_shift else suffix_shift
            previous_k = k if shift >= i + 1 else previous_k  # Galil's rule
            k += shift

    return matches


def preprocess(pattern) -> Tuple:
    """
    Pre-process a pattern, for use with boyermoore_string_pp or boyermoore_file_pp.

    :param pattern: pattern to pre-process. Must be either str or bytes.
    :return: tuple of preprocessed data
    :rtype: tuple
    """
    if isinstance(pattern, str):
        pattern = pattern.encode()
    elif not isinstance(pattern, bytes):
        raise ValueError("Pattern must be str or bytes")

    R = _bad_character_table(pattern)
    L = array.array('q', _good_suffix_table(pattern))
    F = array.array('q', _full_shift_table(pattern))

    return R, L, F, array.array('B', list(pattern))


def search_string_pp(pp_data, string, greedy=True) -> List[int]:
    """
    Search for all occurrences of a pre-processed pattern inside a string.

    :param pp_data: return value from boyermoore.preprocess
    :param string: input data to search for pattern inside. Must be either str or bytes.
    :param bool greedy: If True, all occurrences will be returned. If False, \
        the search will stop after the first occurrence and only the first \
        occurrence will be returned.
    :return: list of byte offsets of all occurrences that were found
    :rtype: [int]
    """
    R, L, F, P = pp_data
    return _base_search_str(R, L, F, P, string, len(string), greedy)


def search_file_pp(pp_data, filename, greedy=True) -> List[int]:
    """
    Search for all occurrences of a pre-processed pattern inside a file.

    :param pp_data: return value from boyermoore.preprocess
    :param str filename: name of file search for pattern in
    :param bool greedy: If True, all occurrences will be returned. If False, \
        the search will stop after the first occurrence and only the first \
        occurrence will be returned.
    :return: list of byte offsets of all occurrences that were found
    :rtype: [int]
    """
    R, L, F, P = pp_data
    fh = open(filename, 'rb')
    fh.seek(0, 2)
    data_size = fh.tell()
    fh.seek(0)
    return _base_search_file(R, L, F, P, fh, data_size, greedy)


def search_string(pattern, string, greedy=True) -> List[int]:
    """
    Pre-process a pattern and search for all occurences inside a string.

    :param pattern: pattern to search for. Must be either str or bytes.
    :param string: input data to search for pattern inside. Must be either str or bytes.
    :param bool greedy: If True, all occurrences will be returned. If False, \
        the search will stop after the first occurrence and only the first \
        occurrence will be returned.
    :return: list of byte offsets of all occurrences that were found
    :rtype: [int]
    """
    R, L, F, P = preprocess(pattern)
    return _base_search_str(R, L, F, P, string, len(string), greedy)


def search_file(pattern, filename, greedy=True) -> List[int]:
    """
    Pre-process a pattern and search for all occurences inside a file.

    :param pattern: pattern to search for. Must be either str or bytes.
    :param filename: name of file to search for pattern in
    :param bool greedy: If True, all occurrences will be returned. If False, \
        the search will stop after the first occurrence and only the first \
        occurrence will be returned.
    :return: list of byte offsets of all occurrences that were found
    :rtype: [int]
    """
    R, L, F, P = preprocess(pattern)
    fh = open(filename, 'rb')
    fh.seek(0, 2)
    data_size = fh.tell()
    fh.seek(0)
    return _base_search_file(R, L, F, P, fh, data_size, greedy)
