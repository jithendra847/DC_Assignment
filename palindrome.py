"""Longest contiguous palindromic substring using Manacher's algorithm."""

from __future__ import annotations

from typing import NamedTuple


class PalindromeResult(NamedTuple):
    """A longest palindrome and its location in the original string."""

    substring: str
    length: int
    start_index: int


def longest_palindrome(text: str) -> PalindromeResult:
    """Return the longest palindromic substring in O(n) time.

    If several longest palindromes exist, the earliest one is returned.
    An empty input returns an empty substring with length and index zero.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not text:
        return PalindromeResult("", 0, 0)

    # Use unique objects for separators and boundaries, so any character is
    # safe as input (including punctuation that might otherwise be a marker).
    separator = object()
    left_boundary = object()
    right_boundary = object()
    transformed: list[object] = [left_boundary, separator]
    for character in text:
        transformed.extend((character, separator))
    transformed.append(right_boundary)

    radii = [0] * len(transformed)
    center = right = 0
    best_center = best_radius = 0

    for index in range(1, len(transformed) - 1):
        mirror = 2 * center - index
        if index < right:
            radii[index] = min(right - index, radii[mirror])

        while transformed[index + radii[index] + 1] == transformed[index - radii[index] - 1]:
            radii[index] += 1

        if index + radii[index] > right:
            center = index
            right = index + radii[index]

        if radii[index] > best_radius:
            best_center = index
            best_radius = radii[index]

    start_index = (best_center - best_radius) // 2
    substring = text[start_index : start_index + best_radius]
    return PalindromeResult(substring, len(substring), start_index)
