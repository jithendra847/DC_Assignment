# Digital Signal Encoder & Decoder

A Python-based signal processing toolkit for digital line coding, bipolar scrambling, analog-to-digital modulation, waveform visualization, and image-based signal decoding.

The project provides an interactive command-line interface for generating digital data, experimenting with different encoding schemes, processing analog samples, and recovering transmitted bits from saved waveform images.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?logo=numpy&logoColor=white" alt="NumPy">
  <img src="https://img.shields.io/badge/Matplotlib-Signal%20Visualization-11557c" alt="Matplotlib">
  <img src="https://img.shields.io/badge/Pillow-Image%20Processing-green" alt="Pillow">
  <img src="https://img.shields.io/badge/Tests-unittest-brightgreen" alt="unittest">
</p>

---

## Overview

Digital communication systems represent information as signals that can be transmitted and reconstructed at the receiving end. Different encoding techniques use voltage levels and transitions to represent binary data, while scrambling methods help manage long sequences of zeros.

This project brings several of these concepts together in a single application. Users can generate or enter binary data, select a line-coding technique, visualize the resulting waveform, and optionally decode the signal. Analog samples can also be processed using Pulse Code Modulation (PCM) or Delta Modulation (DM), with reconstructed signals displayed as staircase plots.

The implementation uses separate Python modules for data generation, encoding, scrambling, modulation, plotting, and decoding.

## Key Features

| Component | Capabilities |
|---|---|
| Digital data generation | Random bitstreams, user-provided data, and patterns containing four or eight consecutive zeros |
| Sequence analysis | Longest zero-run detection and longest palindromic substring identification |
| Line coding | NRZ-L, NRZ-I, Manchester, Differential Manchester, and AMI |
| Bipolar scrambling | B8ZS and HDB3 encoding and corresponding descrambling |
| PCM | Uniform quantization, binary codeword generation, and reconstructed samples |
| Delta Modulation | One-bit-per-sample encoding and staircase reconstruction |
| Signal visualization | Voltage-versus-time waveforms and reconstructed analog plots |
| Image-based decoding | Sampling a saved waveform image to recover voltage levels and transmitted bits |
| Automated testing | Unit tests for algorithms, input validation, and supported processing workflows |

## How It Works

### 1. Digital data generation

The program generates random binary sequences or accepts a bitstream from the user. It can also generate test data containing at least four or eight consecutive zeros, which is useful for evaluating the scrambling algorithms.

The data-analysis functions validate binary input, calculate the longest run of zeros, and identify the longest contiguous palindrome.

Manacher's algorithm is used for palindrome detection, providing \(O(n)\) time complexity for a string of length \(n\).

### 2. Digital line coding

The selected line-coding algorithm converts the input bits into a sequence of voltage levels.

| Scheme | Encoding convention |
|---|---|
| NRZ-L | `0 = +1 V`, `1 = -1 V` |
| NRZ-I | A `1` causes a transition at the beginning of the bit; a `0` causes no transition. |
| Manchester | `0 = [+1, -1]`, `1 = [-1, +1]` |
| Differential Manchester | Every bit transitions in the middle; a `0` also transitions at the beginning. |
| AMI | `0 = 0 V`; successive `1` pulses alternate between positive and negative voltage. |

NRZ-L, NRZ-I, and AMI use one voltage interval per bit. Manchester and Differential Manchester use two half-bit intervals, with the transition pattern determined by the encoding convention.

### 3. AMI scrambling

The application supports two scrambling techniques for AMI signals:

- **B8ZS:** replaces eight consecutive zeros using the standard `000VB0VB` substitution pattern.
- **HDB3:** replaces four consecutive zeros using `000V` or `B00V`, according to the applicable pulse-polarity and parity rules.

The corresponding descrambling functions identify the substitution patterns and reconstruct the original zero sequences.

### 4. Analog-to-digital modulation

**Pulse Code Modulation (PCM)** quantizes analog samples and represents them using fixed-width binary codewords. Its decoder reconstructs approximate sample values from the encoded data and quantization parameters.

**Delta Modulation (DM)** encodes whether the reconstructed signal needs to increase or decrease. Its decoder rebuilds the signal using a configurable step size and initial reference value.

Both techniques produce digital data that can be passed to the line-coding pipeline. The reconstructed signals are displayed as staircase plots, making the effect of quantization and step size easier to observe.

### 5. Waveform visualization and image-based decoding

Matplotlib generates PNG waveforms from the encoded voltage levels. It also produces plots of the reconstructed PCM and Delta Modulation signals.

For optional decoding, Pillow reads the saved waveform image. The decoder samples the waveform trace, estimates its voltage levels, and interprets them according to the selected line-coding scheme and timing parameters. Scrambled AMI signals are passed through the appropriate descrambler.

The image decoder operates on the saved image and required decoding metadata rather than receiving the original bitstream or encoder voltage array directly. It is designed for images produced using this project's waveform style, not arbitrary screenshots.

---

## Project Structure

All source files are kept directly in the project root for straightforward navigation.

```text
DC_Assignment/
│
├── main.py
├── data_generator.py
├── palindrome.py
├── line_coding.py
├── scrambling.py
├── modulation.py
├── plotter.py
├── decoder.py
├── test_project.py
│
├── requirements.txt
├── README.md
├── SPECIFICATION_REPORT.md
└── .gitignore
```

### Module Responsibilities

| File | Responsibility |
|---|---|
| `main.py` | Interactive command-line interface and workflow coordination |
| `data_generator.py` | Random bit generation, test-pattern generation, validation, and zero-run detection |
| `palindrome.py` | Longest palindromic substring detection |
| `line_coding.py` | Implementation of the five line-coding schemes |
| `scrambling.py` | B8ZS/HDB3 scrambling and descrambling |
| `modulation.py` | PCM and Delta Modulation encoding and reconstruction |
| `plotter.py` | Digital waveform and analog staircase visualization |
| `decoder.py` | Image-based recovery of encoded voltage levels and bits |
| `test_project.py` | Automated tests for the project |
| `requirements.txt` | External Python dependencies |
| `SPECIFICATION_REPORT.md` | Technical specification, implementation assumptions, and references |

---

## Technology Stack

- **Python 3.10+** — implementation language.
- **NumPy** — numerical operations where required.
- **Matplotlib** — waveform and staircase visualization.
- **Pillow** — image loading and waveform pixel sampling.
- **unittest** — automated testing.
- **Git and GitHub** — version control and source-code management.

## Installation

### Prerequisites

Install Python 3.10 or newer and Git. Visual Studio Code is recommended for development.

Clone the repository:

```powershell
git clone https://github.com/jithendra847/DC_Assignment.git
cd DC_Assignment
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the Application

Launch the interactive command-line interface:

```powershell
python main.py
```

Select digital or analog input and follow the displayed prompts.

For digital input, enter a binary sequence or generate one, select a line-coding scheme, and choose optional AMI scrambling where applicable. The application displays the encoded signal and offers an optional decoding step.

For analog input, enter comma-separated samples, select PCM or Delta Modulation, and provide the required parameters. The program produces the digital representation and plots the reconstructed staircase. The resulting digital stream can also be passed to a line-coding scheme.

An example analog input is:

```text
-0.5, 0, 0.7, 1.0, 0.4, -0.2, -0.8
```

Waveform and reconstruction images are saved as PNG files using the default paths or the custom paths provided by the user.

## Algorithms and Complexity

### Longest palindromic substring

Manacher's algorithm avoids checking every possible substring independently by reusing information about previously examined palindromes.

- **Time complexity:** \(O(n)\)
- **Auxiliary space:** \(O(n)\)

The result includes the longest contiguous palindrome, its length, and its zero-based starting index. If multiple longest palindromes exist, the earliest occurrence is returned.

### Longest consecutive-zero run

A single-pass scan keeps track of the current zero run and the longest run encountered so far.

- **Time complexity:** \(O(n)\)
- **Auxiliary space:** \(O(n)\) in the current implementation, including input normalization.

## Testing

Run the automated tests from the repository root:

```powershell
python -m unittest -v
```

The tests are intended to cover:

- Data generation and binary input validation.
- Longest zero-run and palindrome calculations.
- Line-coding voltage levels and transitions.
- AMI, B8ZS, and HDB3 patterns.
- PCM quantization and Delta Modulation reconstruction.
- Waveform plotting and image-based decoding.
- Invalid input and boundary conditions.

Manual execution is also recommended to verify the interactive workflows and inspect the generated images.

## Limitations and Assumptions

- Encoders and decoders must use consistent voltage, polarity, timing, and initial-reference conventions.
- PCM reconstruction is approximate because of quantization, and samples outside the configured range may be clipped.
- Delta Modulation reconstruction depends on the selected step size and initial level.
- Image decoding depends on the waveform image's plotting style and visual calibration. Some constant-level or ambiguous waveforms may not contain enough information for reliable recovery.
- Generated PNG files are excluded from Git by the project's `.gitignore`; output images needed for demonstrations should be saved separately.

## Future Improvements

Possible extensions include adding an interactive graphical interface, improving waveform sampling robustness, expanding automated round-trip testing, and supporting additional signal formats or communication schemes.


## Technical References and Acknowledgements

### Learning Resources and Documentation

- [DeepLearning.AI — AI Python for Beginners](https://www.deeplearning.ai/courses/ai-python-for-beginners) — Used to learn Python fundamentals, functions, working with modules, and using external libraries.
- [NumPy Official Documentation](https://numpy.org/doc/stable/) — Consulted for numerical operations and array-related concepts.
- [Matplotlib Official Documentation](https://matplotlib.org/stable/) — Consulted for plotting digital waveforms and reconstructed staircase signals.

### AI Assistance Acknowledgement

**Claude (Anthropic)** and **ChatGPT (OpenAI)** were used as supporting tools during development. They helped break down the project requirements, understand the implementation approach and relevant technical concepts, explore the appropriate technology stack, and investigate errors encountered while debugging the code. Their explanations were also used to clarify selected algorithms and signal-processing concepts. Suggestions were reviewed and applied as appropriate during implementation and testing.

These resources supported the learning and development process. The project was tested against its intended functionality, and the implementation and its limitations should be understood and verified before use or further development.

