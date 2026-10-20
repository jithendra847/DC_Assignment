"""Recover line-coded bits by sampling a saved waveform image with Pillow."""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

from scrambling import decode_b8zs, decode_hdb3


_TRACE_BLUE = (23, 105, 170)  # Color used by plotter.plot_waveform.


def decode_waveform_image(
    image_path: str | Path,
    scheme: str,
    bit_count: int,
    *,
    bit_duration: float = 1.0,
    samples_per_bit: int | None = None,
    initial_level: int = 1,
    scrambling: str | None = None,
) -> str:
    """Read voltage levels from a saved PNG and recover the transmitted bits.

    The decoder samples the blue waveform trace at the center of each signal
    interval. Manchester schemes use two samples per bit; other line codes use
    one. ``initial_level`` is the level before the first bit, and for AMI it
    selects the first normal pulse polarity. ``scrambling`` may be ``"b8zs"`
    or ``"hdb3"`` for a scrambled AMI waveform.

    The decoder receives only the image and signal metadata; it does not take
    the original bit stream or voltage array.
    """
    normalized_scheme = _normalize_scheme(scheme)
    if isinstance(bit_count, bool) or not isinstance(bit_count, int) or bit_count < 1:
        raise ValueError("bit_count must be a positive integer")
    if isinstance(initial_level, bool) or not isinstance(initial_level, int) or initial_level not in (-1, 1):
        raise ValueError("initial_level must be +1 or -1")
    if isinstance(bit_duration, bool) or not isinstance(bit_duration, (int, float)):
        raise TypeError("bit_duration must be a real number")
    if not math.isfinite(bit_duration) or bit_duration <= 0:
        raise ValueError("bit_duration must be finite and greater than zero")

    expected_samples_per_bit = 2 if normalized_scheme in {
        "manchester", "differential-manchester"
    } else 1
    if samples_per_bit is None:
        samples_per_bit = expected_samples_per_bit
    if (
        isinstance(samples_per_bit, bool)
        or not isinstance(samples_per_bit, int)
        or samples_per_bit != expected_samples_per_bit
    ):
        raise ValueError(
            f"{normalized_scheme} requires {expected_samples_per_bit} sample(s) per bit"
        )

    scramble_mode = _normalize_scrambling(scrambling)
    if scramble_mode is not None and normalized_scheme != "ami":
        raise ValueError("B8ZS and HDB3 descrambling can only be used with AMI")

    pixel_rows = _sample_trace(image_path, bit_count * samples_per_bit)
    sample_levels = _classify_levels(pixel_rows, normalized_scheme)

    if normalized_scheme == "nrz-l":
        return "".join("0" if level == 1 else "1" for level in sample_levels)
    if normalized_scheme == "nrz-i":
        bits: list[str] = []
        previous = initial_level
        for level in sample_levels:
            bits.append("1" if level != previous else "0")
            previous = level
        return "".join(bits)
    if normalized_scheme == "manchester":
        return "".join(
            "0" if first == 1 and second == -1 else "1"
            for first, second in _pairs(sample_levels)
        )
    if normalized_scheme == "differential-manchester":
        bits = []
        previous_end = initial_level
        for first, second in _pairs(sample_levels):
            if first == second:
                raise ValueError("image does not contain valid Differential Manchester transitions")
            bits.append("0" if first != previous_end else "1")
            previous_end = second
        return "".join(bits)

    bits = "".join("0" if level == 0 else "1" for level in sample_levels)
    if scramble_mode == "b8zs":
        return decode_b8zs(sample_levels, initial_pulse=initial_level)
    if scramble_mode == "hdb3":
        return decode_hdb3(sample_levels, initial_pulse=initial_level)
    return bits


def _sample_trace(image_path: str | Path, sample_count: int) -> list[int]:
    if not isinstance(image_path, (str, Path)):
        raise TypeError("image_path must be a filesystem path")
    try:
        from PIL import Image
    except ImportError as error:
        raise ImportError("Pillow is required for image decoding; install requirements.txt") from error
    try:
        image = Image.open(image_path).convert("RGB")
    except (OSError, ValueError) as error:
        raise ValueError(f"could not open waveform image: {image_path}") from error

    with image:
        width, height = image.size
        trace_columns: list[int] = []
        for x in range(width):
            if any(_is_trace_pixel(image.getpixel((x, y))) for y in range(height)):
                trace_columns.append(x)
        if not trace_columns:
            raise ValueError("image does not contain the expected blue waveform trace")

        left, right = trace_columns[0], trace_columns[-1]
        if right <= left:
            raise ValueError("waveform trace is too narrow to sample")
        samples: list[int] = []
        for index in range(sample_count):
            x = round(left + (index + 0.5) * (right - left) / sample_count)
            rows = [
                y
                for column in range(max(left, x - 2), min(right, x + 2) + 1)
                for y in range(height)
                if _is_trace_pixel(image.getpixel((column, y)))
            ]
            if not rows:
                raise ValueError(f"waveform trace could not be sampled at interval {index}")
            samples.append(round(_median(rows)))
        return samples


def _classify_levels(pixel_rows: list[int], scheme: str) -> list[int]:
    clusters: list[list[int]] = []
    for row in sorted(pixel_rows):
        if not clusters or row - clusters[-1][-1] > 7:
            clusters.append([row])
        else:
            clusters[-1].append(row)
    centers = [round(sum(cluster) / len(cluster)) for cluster in clusters]
    if len(centers) > 3:
        raise ValueError("waveform has more than three distinct voltage levels")
    if not centers:
        raise ValueError("waveform contains no sampleable voltage levels")

    # Image rows increase downward: the highest trace is +1 V and lowest is -1 V.
    if scheme == "ami":
        if len(centers) == 3:
            voltage_by_center = {centers[0]: 1, centers[1]: 0, centers[2]: -1}
        elif len(centers) == 2:
            counts = Counter(_nearest_center(row, centers) for row in pixel_rows)
            if counts[centers[0]] == counts[centers[1]]:
                raise ValueError("two-level AMI image is ambiguous without a zero-level sample")
            zero_center = counts.most_common(1)[0][0]
            pulse_center = centers[1] if zero_center == centers[0] else centers[0]
            voltage_by_center = {zero_center: 0, pulse_center: 1 if pulse_center < zero_center else -1}
        else:
            if len(pixel_rows) == 1:
                raise ValueError("single-sample AMI image cannot distinguish 0 V from a pulse")
            # With only one visible level, a valid multi-bit AMI stream can only
            # be an all-zero stream; repeated marks would have alternating signs.
            voltage_by_center = {centers[0]: 0}
        return [voltage_by_center[_nearest_center(row, centers)] for row in pixel_rows]

    if len(centers) < 2:
        raise ValueError(
            "single-level waveform is ambiguous because the plot auto-scales its voltage axis"
        )
    upper, lower = centers[0], centers[-1]
    return [1 if row <= (upper + lower) / 2 else -1 for row in pixel_rows]


def _nearest_center(row: int, centers: list[int]) -> int:
    return min(centers, key=lambda center: abs(row - center))


def _is_trace_pixel(pixel: tuple[int, int, int]) -> bool:
    red, green, blue = pixel
    return blue > 115 and blue - red > 65 and blue - green > 35


def _median(values: list[int]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def _pairs(values: list[int]):
    return zip(values[::2], values[1::2])


def _normalize_scheme(scheme: str) -> str:
    if not isinstance(scheme, str):
        raise TypeError("scheme must be a string")
    normalized = "-".join(scheme.strip().lower().replace("_", "-").split())
    aliases = {
        "nrzl": "nrz-l",
        "nrzi": "nrz-i",
        "diff-manchester": "differential-manchester",
        "differential-manchester": "differential-manchester",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {
        "nrz-l", "nrz-i", "manchester", "differential-manchester", "ami"
    }:
        raise ValueError(f"unsupported line coding scheme: {scheme!r}")
    return normalized


def _normalize_scrambling(scrambling: str | None) -> str | None:
    if scrambling is None:
        return None
    if not isinstance(scrambling, str):
        raise TypeError("scrambling must be 'b8zs', 'hdb3', or None")
    normalized = scrambling.strip().lower()
    if normalized not in {"b8zs", "hdb3"}:
        raise ValueError("scrambling must be 'b8zs', 'hdb3', or None")
    return normalized
