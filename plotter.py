"""Save line-code waveforms and PCM/Delta reconstructed staircases."""

from __future__ import annotations

import math
from collections.abc import Sequence
from numbers import Real
from pathlib import Path


def plot_waveform(
    levels: Sequence[Real],
    image_path: str | Path,
    *,
    scheme: str = "Encoded waveform",
    samples_per_bit: int = 1,
    bit_duration: float = 1.0,
    bit_count: int | None = None,
) -> Path:
    """Plot encoded voltage levels against time and save a PNG image.

    Use ``samples_per_bit=2`` for Manchester schemes. If ``bit_count`` is
    provided, it must agree with the number of samples and samples per bit.
    The returned path is the path where the image was saved.
    """
    values = _validate_values(levels, "levels")
    _validate_samples_per_bit(samples_per_bit)
    duration = _validate_positive(bit_duration, "bit_duration")
    if len(values) % samples_per_bit:
        raise ValueError("level count must be divisible by samples_per_bit")
    inferred_bit_count = len(values) // samples_per_bit
    if bit_count is not None:
        if isinstance(bit_count, bool) or not isinstance(bit_count, int) or bit_count < 0:
            raise ValueError("bit_count must be a non-negative integer")
        if bit_count != inferred_bit_count:
            raise ValueError("bit_count does not match the number of voltage levels")

    target = _png_path(image_path)
    if values:
        edges = [i * duration / samples_per_bit for i in range(len(values) + 1)]
        bit_edges = [i * duration for i in range(inferred_bit_count + 1)]
        low, high = min(values), max(values)
    else:
        edges = [0.0]
        bit_edges = [0.0]
        low, high = -1.0, 1.0

    plt = _matplotlib_pyplot()
    figure, axis = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
    try:
        if values:
            axis.stairs(values, edges, color="#1769aa", linewidth=2.2)
        for edge in bit_edges:
            axis.axvline(edge, color="#9aa4ae", linewidth=0.7, linestyle="--", zorder=0)
        padding = max((high - low) * 0.2, 0.25)
        axis.set_ylim(low - padding, high + padding)
        axis.set_xlim(0, max(inferred_bit_count * duration, duration * 0.5))
        axis.set_xticks(bit_edges)
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Voltage (V)")
        axis.set_title(scheme)
        axis.grid(axis="y", color="#d9dee5", linewidth=0.7)
        axis.spines[["top", "right"]].set_visible(False)
        figure.savefig(target, dpi=160, facecolor="white")
    finally:
        plt.close(figure)
    return target


def plot_pcm_reconstruction(
    samples: Sequence[Real], image_path: str | Path
) -> Path:
    """Plot reconstructed PCM samples as a staircase and save a PNG."""
    return _plot_staircase(samples, image_path, "PCM reconstructed signal", "#1769aa")


def plot_delta_reconstruction(
    samples: Sequence[Real], image_path: str | Path
) -> Path:
    """Plot reconstructed Delta Modulation samples as a staircase and save a PNG."""
    return _plot_staircase(
        samples, image_path, "Delta Modulation reconstructed signal", "#d05a28"
    )


def plot_modulation_reconstructions(
    pcm_samples: Sequence[Real],
    delta_samples: Sequence[Real],
    image_path: str | Path,
) -> Path:
    """Plot PCM and Delta reconstructed staircases in a shared PNG figure."""
    pcm = _validate_values(pcm_samples, "pcm_samples")
    delta = _validate_values(delta_samples, "delta_samples")
    target = _png_path(image_path)
    plt = _matplotlib_pyplot()
    figure, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
    try:
        _draw_staircase(axes[0], pcm, "PCM reconstructed signal", "#1769aa")
        _draw_staircase(axes[1], delta, "Delta Modulation reconstructed signal", "#d05a28")
        figure.savefig(target, dpi=160, facecolor="white")
    finally:
        plt.close(figure)
    return target


def _plot_staircase(
    samples: Sequence[Real], image_path: str | Path, title: str, color: str
) -> Path:
    values = _validate_values(samples, "samples")
    target = _png_path(image_path)
    plt = _matplotlib_pyplot()
    figure, axis = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
    try:
        _draw_staircase(axis, values, title, color)
        figure.savefig(target, dpi=160, facecolor="white")
    finally:
        plt.close(figure)
    return target


def _draw_staircase(axis, values: list[float], title: str, color: str) -> None:
    if values:
        axis.stairs(values, range(len(values) + 1), color=color, linewidth=2.2)
        axis.set_xlim(0, len(values))
        low, high = min(values), max(values)
        padding = max((high - low) * 0.2, 0.1)
        axis.set_ylim(low - padding, high + padding)
    else:
        axis.set_xlim(0, 1)
        axis.set_ylim(-1, 1)
    axis.set_xlabel("Sample")
    axis.set_ylabel("Amplitude")
    axis.set_title(title)
    axis.grid(color="#d9dee5", linewidth=0.7)
    axis.spines[["top", "right"]].set_visible(False)


def _validate_values(values: Sequence[Real], name: str) -> list[float]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of finite numbers")
    converted: list[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{name} must contain only real numbers")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"{name} must contain only finite numbers")
        converted.append(number)
    return converted


def _validate_samples_per_bit(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("samples_per_bit must be a positive integer")


def _validate_positive(value: Real, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be finite and greater than zero")
    return number


def _png_path(image_path: str | Path) -> Path:
    if not isinstance(image_path, (str, Path)) or not str(image_path):
        raise TypeError("image_path must be a non-empty path")
    target = Path(image_path)
    if target.suffix.lower() != ".png":
        raise ValueError("image_path must use the .png extension")
    return target


def _matplotlib_pyplot():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as pyplot
    except ImportError as error:
        raise ImportError("Matplotlib is required for plotting; install requirements.txt") from error
    return pyplot
