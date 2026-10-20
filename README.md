# Data Communication Encoder and Decoder

A Python command-line project for exploring digital signal generation, line coding, scrambling, analog-to-digital modulation, waveform plotting, and image-based decoding.

## Features

- Generate random bits or patterns containing four or eight consecutive zeros, or enter a bit string.
- Find the longest run of zeros and optionally find the longest palindromic substring.
- Encode data using NRZ-L, NRZ-I, Manchester, Differential Manchester, or AMI.
- Apply B8ZS or HDB3 scrambling to AMI signals.
- Encode analog samples using PCM or Delta Modulation, then view a reconstructed staircase.
- Save digital waveforms as PNG files and optionally decode a saved waveform image.

## Requirements and setup

Use Python 3.10 or newer. From this directory, create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The required packages are NumPy, Matplotlib, and Pillow.

## Run the program

```powershell
python main.py
```

Choose digital or analog input and follow the prompts. Digital input can be generated or entered directly. Analog samples should be comma-separated numbers, such as `-0.5, 0, 0.7`. The program saves plots in the current directory by default; each plot prompt accepts a custom path.

For PCM, choose the bits per sample and quantizer range. For Delta Modulation, choose a positive step size and optional initial reconstruction value. Either resulting bitstream can be passed to a line-coding scheme.

## Signal conventions

| Scheme | Convention |
|---|---|
| NRZ-L | `0` is +1 V; `1` is −1 V. |
| NRZ-I | `1` changes the level at the start of the bit; `0` leaves it unchanged. |
| Manchester | `0` is [+1, −1]; `1` is [−1, +1]. |
| Differential Manchester | Every bit changes level in the middle; `0` also changes at the start. |
| AMI | `0` is 0 V; successive `1` pulses alternate between +1 V and −1 V. |
| B8ZS | Replaces eight-zero runs using the standard `000VB0VB` substitution. |
| HDB3 | Replaces four-zero runs using `000V` or `B00V` according to pulse polarity and parity. |

The initial reference or pulse polarity is +1 unless changed in the prompts. Encoders and decoders must use the same convention.

## Project files

| File | Purpose |
|---|---|
| `main.py` | Interactive command-line workflows. |
| `data_generator.py` | Bit generation, validation, and zero-run detection. |
| `palindrome.py` | Longest palindromic substring detection using Manacher's algorithm. |
| `line_coding.py` | Five line-coding encoders. |
| `scrambling.py` | B8ZS/HDB3 encoding and decoding. |
| `modulation.py` | PCM and Delta Modulation encoding and decoding. |
| `plotter.py` | Waveform and reconstruction plots. |
| `decoder.py` | Recovers bits by sampling a plotted waveform image. |
| `test_project.py` | Automated unit and workflow tests. |
| `SPECIFICATION_REPORT.md` | Detailed project specification, algorithms, assumptions, and references. |

## Notes and limitations

- Image-based decoding expects a compatible waveform PNG produced with this project's plot style and requires the bit count, line code, initial level, and scrambling mode where applicable.
- PCM clips samples outside the selected quantizer range. The reconstruction is quantized and may differ from the input samples.
- Delta Modulation produces a staircase approximation; the step size affects tracking accuracy.
- PNG output files are ignored by Git. Copy any plots you need to submit separately.

## Tests

Run the test suite from this directory with:

```powershell
python -m unittest -v
```
