"""Helpers for creating and validating binary data."""

from __future__ import annotations

import random
from collections.abc import Sequence


def generate_random_bits(length: int, *, rng: random.Random | None = None) -> str:
    """Return a random bit string of *length* bits.

    Pass a ``random.Random`` instance as ``rng`` to make output reproducible
    in a lesson or test. Length must be a non-negative integer.
    """
    _validate_length(length)
    bit_source = rng if rng is not None else random
    return "".join(bit_source.choice("01") for _ in range(length))


def generate_data_with_zero_run(
    length: int,
    zero_count: int,
    *,
    rng: random.Random | None = None,
) -> str:
    """Generate bits containing a consecutive run of ``zero_count`` zeros.

    Other positions are filled with random bits. The requested run is placed
    at a random valid position. ``zero_count`` must be at least one and no
    greater than ``length``.
    """
    _validate_length(length)
    if isinstance(zero_count, bool) or not isinstance(zero_count, int):
        raise TypeError("zero_count must be an integer")
    if zero_count < 1 or zero_count > length:
        raise ValueError("zero_count must be between 1 and length")

    bit_source = rng if rng is not None else random
    bits = [bit_source.choice("01") for _ in range(length)]
    start = bit_source.randrange(length - zero_count + 1)
    bits[start : start + zero_count] = "0" * zero_count
    return "".join(bits)


def generate_data_with_four_zeros(
    length: int, *, rng: random.Random | None = None
) -> str:
    """Generate data containing at least four consecutive zeros."""
    return generate_data_with_zero_run(length, 4, rng=rng)


def generate_data_with_eight_zeros(
    length: int, *, rng: random.Random | None = None
) -> str:
    """Generate data containing at least eight consecutive zeros."""
    return generate_data_with_zero_run(length, 8, rng=rng)


def validate_binary_data(data: str | Sequence[int]) -> str:
    """Validate binary input and return it as a normalized bit string.

    Strings may contain only ``0`` and ``1``. A sequence may contain integer
    zeroes and ones (booleans are not accepted). Empty data is valid.
    """
    if isinstance(data, str):
        if any(bit not in "01" for bit in data):
            raise ValueError("binary data must contain only '0' and '1'")
        return data

    if isinstance(data, Sequence):
        normalized: list[str] = []
        for bit in data:
            if isinstance(bit, bool) or not isinstance(bit, int) or bit not in (0, 1):
                raise ValueError("binary data sequence may contain only integer 0 and 1")
            normalized.append(str(bit))
        return "".join(normalized)

    raise TypeError("binary data must be a string or a sequence of integer bits")


def longest_zero_run(data: str | Sequence[int]) -> int:
    """Return the longest contiguous run of zeroes in O(n) time."""
    bits = validate_binary_data(data)
    longest = current = 0
    for bit in bits:
        if bit == "0":
            current += 1
            if current > longest:
                longest = current
        else:
            current = 0
    return longest


def _validate_length(length: int) -> None:
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("length must be an integer")
    if length < 0:
        raise ValueError("length must be non-negative")
