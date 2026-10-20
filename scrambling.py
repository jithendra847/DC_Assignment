"""B8ZS and HDB3 zero substitution for AMI voltage-level streams."""

from __future__ import annotations

from collections.abc import Sequence

from data_generator import validate_binary_data


def encode_b8zs(data: str, initial_pulse: int = 1) -> list[int]:
    """Apply B8ZS to bits and return AMI voltage levels.

    Eight zeroes become ``000VB0VB``. ``initial_pulse`` is the polarity a
    normal first 1 bit would use; the assumed preceding mark is its opposite.
    This also makes leading-zero substitutions deterministic.
    """
    bits = validate_binary_data(data)
    _validate_initial_pulse(initial_pulse)
    previous = -initial_pulse
    output: list[int] = []
    index = 0

    while index < len(bits):
        if bits.startswith("00000000", index):
            violation = previous
            balancing = -violation
            output.extend((0, 0, 0, violation, balancing, 0, balancing, violation))
            previous = violation
            index += 8
        elif bits[index] == "0":
            output.append(0)
            index += 1
        else:
            previous *= -1
            output.append(previous)
            index += 1
    return output


def decode_b8zs(levels: Sequence[int], initial_pulse: int = 1) -> str:
    """Replace recognized B8ZS patterns with eight zero bits."""
    samples = _validate_levels(levels)
    _validate_initial_pulse(initial_pulse)
    previous = -initial_pulse
    bits: list[str] = []
    index = 0

    while index < len(samples):
        violation = previous
        balancing = -violation
        pattern = (0, 0, 0, violation, balancing, 0, balancing, violation)
        if tuple(samples[index : index + 8]) == pattern:
            bits.extend("00000000")
            previous = violation
            index += 8
        else:
            level = samples[index]
            if level == 0:
                bits.append("0")
            else:
                bits.append("1")
                previous = level
            index += 1
    return "".join(bits)


def encode_hdb3(data: str, initial_pulse: int = 1) -> list[int]:
    """Apply HDB3 and return AMI voltage levels.

    Each group of four zeroes uses ``000V`` when the number of nonzero marks
    since the preceding substitution is odd, and ``B00V`` when it is even.
    V has the same polarity as the preceding mark; B is opposite to it.
    ``initial_pulse`` sets the polarity of a normal first 1 bit.
    """
    bits = validate_binary_data(data)
    _validate_initial_pulse(initial_pulse)
    previous = -initial_pulse
    marks_since_violation = 0
    output: list[int] = []
    index = 0

    while index < len(bits):
        if bits.startswith("0000", index):
            if marks_since_violation % 2:
                violation = previous
                output.extend((0, 0, 0, violation))
            else:
                balancing = -previous
                violation = balancing
                output.extend((balancing, 0, 0, violation))
            previous = violation
            marks_since_violation = 0
            index += 4
        elif bits[index] == "0":
            output.append(0)
            index += 1
        else:
            previous *= -1
            output.append(previous)
            marks_since_violation += 1
            index += 1
    return output


def decode_hdb3(levels: Sequence[int], initial_pulse: int = 1) -> str:
    """Decode AMI levels and replace recognized HDB3 substitutions by zeroes."""
    samples = _validate_levels(levels)
    _validate_initial_pulse(initial_pulse)
    previous = -initial_pulse
    marks_since_violation = 0
    bits: list[str] = []
    index = 0

    while index < len(samples):
        if marks_since_violation % 2:
            expected = (0, 0, 0, previous)
        else:
            balancing = -previous
            expected = (balancing, 0, 0, balancing)

        if tuple(samples[index : index + 4]) == expected:
            bits.extend("0000")
            previous = expected[-1]
            marks_since_violation = 0
            index += 4
            continue

        level = samples[index]
        if level == 0:
            bits.append("0")
        else:
            bits.append("1")
            previous = level
            marks_since_violation += 1
        index += 1
    return "".join(bits)


def _validate_levels(levels: Sequence[int]) -> list[int]:
    if isinstance(levels, (str, bytes)) or not isinstance(levels, Sequence):
        raise TypeError("levels must be a sequence of integer voltage levels")
    result: list[int] = []
    for level in levels:
        if isinstance(level, bool) or not isinstance(level, int) or level not in (-1, 0, 1):
            raise ValueError("voltage levels must be integer -1, 0, or +1")
        result.append(level)
    return result


def _validate_initial_pulse(polarity: int) -> None:
    if isinstance(polarity, bool) or not isinstance(polarity, int) or polarity not in (-1, 1):
        raise ValueError("initial_pulse must be +1 or -1")
