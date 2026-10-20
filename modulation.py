"""PCM and Delta Modulation encoders and staircase decoders."""

from __future__ import annotations

import math
from collections.abc import Iterable
from numbers import Real

from data_generator import validate_binary_data


def pcm_encode(
    samples: Iterable[Real],
    bits_per_sample: int = 8,
    minimum: float = -1.0,
    maximum: float = 1.0,
) -> str:
    """Uniformly quantize samples and return fixed-width PCM bits.

    This uses a mid-rise quantizer: each of the ``2**bits_per_sample`` equal
    intervals maps to its integer code, represented with exactly the requested
    number of bits. Values outside the configured range are clipped.
    """
    _validate_bit_width(bits_per_sample)
    low, high = _validate_range(minimum, maximum)
    values = _as_finite_samples(samples)
    levels = 1 << bits_per_sample
    interval_width = (high - low) / levels
    encoded: list[str] = []

    for value in values:
        code = int((value - low) / interval_width)
        code = min(max(code, 0), levels - 1)
        encoded.append(format(code, f"0{bits_per_sample}b"))
    return "".join(encoded)


def pcm_decode(
    bitstream: str,
    bits_per_sample: int = 8,
    minimum: float = -1.0,
    maximum: float = 1.0,
) -> list[float]:
    """Decode PCM bits to the midpoint reconstruction of each quantizer bin."""
    _validate_bit_width(bits_per_sample)
    low, high = _validate_range(minimum, maximum)
    bits = validate_binary_data(bitstream)
    if len(bits) % bits_per_sample:
        raise ValueError("PCM bitstream length must be a multiple of bits_per_sample")

    levels = 1 << bits_per_sample
    interval_width = (high - low) / levels
    return [
        low + (int(bits[index : index + bits_per_sample], 2) + 0.5) * interval_width
        for index in range(0, len(bits), bits_per_sample)
    ]


def delta_encode(
    samples: Iterable[Real],
    step_size: float,
    initial_value: float = 0.0,
) -> str:
    """Encode samples as Delta Modulation bits.

    A bit is 1 when the next sample is at or above the current estimate, and
    0 when it is below. Each bit moves the estimate by one positive ``step_size``.
    """
    step = _validate_positive_finite(step_size, "step_size")
    estimate = _validate_finite_number(initial_value, "initial_value")
    values = _as_finite_samples(samples)
    bits: list[str] = []

    for value in values:
        if value >= estimate:
            bits.append("1")
            estimate += step
        else:
            bits.append("0")
            estimate -= step
    return "".join(bits)


def delta_decode(
    bitstream: str,
    step_size: float,
    initial_value: float = 0.0,
) -> list[float]:
    """Reconstruct a staircase, returning one estimate per input bit."""
    bits = validate_binary_data(bitstream)
    step = _validate_positive_finite(step_size, "step_size")
    estimate = _validate_finite_number(initial_value, "initial_value")
    staircase: list[float] = []

    for bit in bits:
        estimate += step if bit == "1" else -step
        staircase.append(estimate)
    return staircase


def _as_finite_samples(samples: Iterable[Real]) -> list[float]:
    if isinstance(samples, (str, bytes)):
        raise TypeError("samples must be an iterable of finite numbers")
    try:
        values = list(samples)
    except TypeError as error:
        raise TypeError("samples must be an iterable of finite numbers") from error
    return [_validate_finite_number(value, "sample") for value in values]


def _validate_finite_number(value: Real, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _validate_positive_finite(value: Real, name: str) -> float:
    number = _validate_finite_number(value, name)
    if number <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return number


def _validate_range(minimum: Real, maximum: Real) -> tuple[float, float]:
    low = _validate_finite_number(minimum, "minimum")
    high = _validate_finite_number(maximum, "maximum")
    if low >= high:
        raise ValueError("minimum must be less than maximum")
    return low, high


def _validate_bit_width(bits_per_sample: int) -> None:
    if isinstance(bits_per_sample, bool) or not isinstance(bits_per_sample, int):
        raise TypeError("bits_per_sample must be an integer")
    if bits_per_sample < 1:
        raise ValueError("bits_per_sample must be at least 1")
