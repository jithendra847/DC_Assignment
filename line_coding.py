"""Digital line coding schemes that map bits to voltage levels.

Voltage levels are represented as integers: +1 is +1 V, -1 is -1 V,
and 0 is 0 V. Manchester schemes produce two levels per input bit; the
other schemes produce one level per bit.
"""

from __future__ import annotations

from collections.abc import Callable

from data_generator import validate_binary_data


def encode_nrz_l(data: str) -> list[int]:
    """Encode NRZ-L: 0 = +1 V and 1 = -1 V."""
    bits = validate_binary_data(data)
    return [1 if bit == "0" else -1 for bit in bits]


def encode_nrz_i(data: str, initial_level: int = 1) -> list[int]:
    """Encode NRZ-I; each 1 changes level at the bit's start.

    ``initial_level`` is the level immediately before the first bit and must
    be +1 V or -1 V. A 0 keeps the current level.
    """
    bits = validate_binary_data(data)
    _validate_initial_level(initial_level)
    level = initial_level
    levels: list[int] = []
    for bit in bits:
        if bit == "1":
            level *= -1
        levels.append(level)
    return levels


def encode_manchester(data: str) -> list[int]:
    """Encode Manchester: 0 = [+1, -1], 1 = [-1, +1]."""
    bits = validate_binary_data(data)
    levels: list[int] = []
    for bit in bits:
        levels.extend((1, -1) if bit == "0" else (-1, 1))
    return levels


def encode_differential_manchester(data: str, initial_level: int = 1) -> list[int]:
    """Encode Differential Manchester with a middle transition every bit.

    There is also a transition at the bit start for 0; a 1 has no start
    transition. ``initial_level`` is the level before the first bit.
    """
    bits = validate_binary_data(data)
    _validate_initial_level(initial_level)
    level = initial_level
    levels: list[int] = []
    for bit in bits:
        if bit == "0":
            level *= -1
        levels.append(level)
        level *= -1  # Mandatory middle-of-bit transition.
        levels.append(level)
    return levels


def encode_ami(data: str, initial_pulse: int = 1) -> list[int]:
    """Encode AMI: zero = 0 V; successive one pulses alternate polarity.

    ``initial_pulse`` selects the polarity of the first 1 pulse (+1 V or
    -1 V). It has no effect when the input contains no 1 bits.
    """
    bits = validate_binary_data(data)
    _validate_initial_level(initial_pulse)
    pulse = -initial_pulse
    levels: list[int] = []
    for bit in bits:
        if bit == "0":
            levels.append(0)
        else:
            pulse *= -1
            levels.append(pulse)
    return levels


_ENCODERS: dict[str, Callable[..., list[int]]] = {
    "nrz-l": encode_nrz_l,
    "nrz-i": encode_nrz_i,
    "manchester": encode_manchester,
    "differential-manchester": encode_differential_manchester,
    "ami": encode_ami,
}


def encode_line_code(
    data: str,
    scheme: str,
    *,
    initial_level: int = 1,
) -> list[int]:
    """Encode bits using a scheme name and return its voltage samples.

    Scheme names are case-insensitive. ``initial_level`` is used by NRZ-I,
    Differential Manchester, and as the first AMI pulse polarity.
    """
    normalized = scheme.strip().lower().replace("_", "-").replace(" ", "-")
    try:
        encoder = _ENCODERS[normalized]
    except (AttributeError, KeyError) as error:
        names = ", ".join(_ENCODERS)
        raise ValueError(f"unknown scheme {scheme!r}; choose one of: {names}") from error

    if normalized in {"nrz-i", "differential-manchester", "ami"}:
        return encoder(data, initial_level)
    return encoder(data)


def _validate_initial_level(level: int) -> None:
    if isinstance(level, bool) or not isinstance(level, int) or level not in (-1, 1):
        raise ValueError("initial level must be +1 or -1")
