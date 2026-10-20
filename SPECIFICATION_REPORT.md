# Digital Signal Encoder and Decoder — Specification Report

## Purpose and platform

This beginner-friendly Python 3.10+ project demonstrates digital data generation, line coding, zero-substitution scrambling, analog-to-digital modulation, waveform plotting, and image-based decoding. It runs as a command-line program with files kept in the project root. Install the listed dependencies with `python -m pip install -r requirements.txt`; start the program with `python main.py`.

## Inputs and outputs

The interactive program accepts generated or user-entered binary data, or comma-separated analog samples. It validates bit strings and numeric parameters, reports the longest zero run, and can find the longest contiguous palindrome. The output includes encoded voltage levels, PCM or Delta Modulation bit streams, reconstructed staircase plots, saved PNG waveforms, and optionally decoded bits.

| Feature | Specification |
| --- | --- |
| Binary data | Random bits; data containing at least four or eight consecutive zeroes; validated user input; longest zero run found in O(n) time. |
| Palindrome | Manacher’s algorithm finds the longest contiguous palindromic substring in O(n) time and returns its text, length, and zero-based start index. Ties return the earliest match. |
| NRZ-L | `0 = +1 V`; `1 = -1 V`. |
| NRZ-I | `1` changes level at the start of the bit; `0` keeps the level. |
| Manchester | `0 = [+1, -1]`; `1 = [-1, +1]`. |
| Differential Manchester | Every bit transitions in the middle; `0` also transitions at the start; `1` does not. |
| AMI | `0 = 0 V`; successive `1` pulses alternate between `+1 V` and `-1 V`. |
| Scrambling | B8ZS substitutes `000VB0VB` for eight zeroes. HDB3 uses `000V` for odd mark parity and `B00V` for even mark parity, counting marks since the preceding substitution. Both can descramble AMI levels. |
| PCM | Uniform mid-rise quantization produces fixed-width binary codes; out-of-range samples are clipped. Decoding reconstructs each quantizer-bin midpoint. |
| Delta Modulation | A configurable positive step encodes each sample as one bit and reconstructs a staircase from an initial reference value. |
| Plots and decoding | PNG line-code waveforms and PCM/Delta staircases are saved. Pillow samples the plotted trace using the scheme, bit count, samples per bit, and initial reference level; B8ZS/HDB3 decoding is supported. |

## Validation and limits

Invalid bits, unsupported schemes, malformed PCM widths, non-finite analog samples, non-positive Delta steps, and inconsistent waveform timing are rejected with clear exceptions. Image decoding depends on the blue waveform style written by this project’s plotter. Since that plotter auto-scales voltage, a constant-level waveform may not contain enough visual information to distinguish its absolute level; the decoder reports ambiguous cases instead of guessing. Install NumPy, Matplotlib, and Pillow from `requirements.txt` to use all plotting and image-decoding functions.

## Project modules and verification

`data_generator.py`, `palindrome.py`, `line_coding.py`, `scrambling.py`, `modulation.py`, `plotter.py`, and `decoder.py` hold the feature implementations; `main.py` connects them interactively. `test_project.py` contains the `unittest` suite. Run it with `python -m unittest`.
