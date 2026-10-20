"""Focused tests for the digital data generation milestone."""

import random
import unittest
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

from data_generator import (
    generate_data_with_eight_zeros,
    generate_data_with_four_zeros,
    generate_data_with_zero_run,
    generate_random_bits,
    longest_zero_run,
    validate_binary_data,
)
from palindrome import PalindromeResult, longest_palindrome
from line_coding import (
    encode_ami,
    encode_differential_manchester,
    encode_line_code,
    encode_manchester,
    encode_nrz_i,
    encode_nrz_l,
)
from scrambling import decode_b8zs, decode_hdb3, encode_b8zs, encode_hdb3
from modulation import delta_decode, delta_encode, pcm_decode, pcm_encode
from plotter import plot_delta_reconstruction, plot_modulation_reconstructions, plot_waveform

MATPLOTLIB_AVAILABLE = importlib.util.find_spec("matplotlib") is not None


class DataGeneratorTests(unittest.TestCase):
    def test_random_data_has_requested_length_and_binary_characters(self):
        bits = generate_random_bits(128, rng=random.Random(7))
        self.assertEqual(len(bits), 128)
        self.assertTrue(set(bits) <= {"0", "1"})

    def test_random_data_is_reproducible_with_seeded_rng(self):
        self.assertEqual(
            generate_random_bits(20, rng=random.Random(3)),
            generate_random_bits(20, rng=random.Random(3)),
        )

    def test_four_and_eight_zero_generators_include_requested_run(self):
        self.assertGreaterEqual(
            longest_zero_run(generate_data_with_four_zeros(12, rng=random.Random(2))), 4
        )
        self.assertGreaterEqual(
            longest_zero_run(generate_data_with_eight_zeros(16, rng=random.Random(2))), 8
        )

    def test_arbitrary_zero_run_is_included_and_length_is_preserved(self):
        bits = generate_data_with_zero_run(15, 6, rng=random.Random(1))
        self.assertEqual(len(bits), 15)
        self.assertGreaterEqual(longest_zero_run(bits), 6)

    def test_binary_input_is_validated_and_normalized(self):
        self.assertEqual(validate_binary_data("0101"), "0101")
        self.assertEqual(validate_binary_data([0, 1, 0]), "010")
        with self.assertRaises(ValueError):
            validate_binary_data("0102")

    def test_longest_zero_run_handles_boundaries(self):
        self.assertEqual(longest_zero_run("11000100000"), 5)
        self.assertEqual(longest_zero_run("111"), 0)
        self.assertEqual(longest_zero_run(""), 0)

    def test_invalid_lengths_and_zero_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            generate_random_bits(-1)
        with self.assertRaises(ValueError):
            generate_data_with_zero_run(3, 4)


class PalindromeTests(unittest.TestCase):
    def test_returns_substring_length_and_start_index(self):
        result = longest_palindrome("0010110")
        self.assertEqual(result, PalindromeResult("0110", 4, 3))

    def test_finds_even_length_palindrome(self):
        self.assertEqual(longest_palindrome("0110"), PalindromeResult("0110", 4, 0))

    def test_returns_earliest_when_longest_palindromes_tie(self):
        self.assertEqual(longest_palindrome("abacdc"), PalindromeResult("aba", 3, 0))

    def test_handles_empty_single_character_and_no_repeated_characters(self):
        self.assertEqual(longest_palindrome(""), PalindromeResult("", 0, 0))
        self.assertEqual(longest_palindrome("x"), PalindromeResult("x", 1, 0))
        self.assertEqual(longest_palindrome("abcd"), PalindromeResult("a", 1, 0))

    def test_input_may_contain_separator_like_characters(self):
        self.assertEqual(longest_palindrome("a#a"), PalindromeResult("a#a", 3, 0))

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            longest_palindrome([0, 1, 0])


class LineCodingTests(unittest.TestCase):
    def test_nrz_l_convention(self):
        self.assertEqual(encode_nrz_l("0101"), [1, -1, 1, -1])

    def test_nrz_i_transitions_for_ones_only(self):
        self.assertEqual(encode_nrz_i("1010"), [-1, -1, 1, 1])
        self.assertEqual(encode_nrz_i("10", initial_level=-1), [1, 1])

    def test_manchester_convention(self):
        self.assertEqual(encode_manchester("01"), [1, -1, -1, 1])

    def test_differential_manchester_has_middle_transition_and_zero_start_transition(self):
        self.assertEqual(encode_differential_manchester("01"), [-1, 1, 1, -1])

    def test_ami_alternates_one_pulse_polarity(self):
        self.assertEqual(encode_ami("110101"), [1, -1, 0, 1, 0, -1])
        self.assertEqual(encode_ami("11", initial_pulse=-1), [-1, 1])

    def test_scheme_dispatch_is_case_and_separator_flexible(self):
        self.assertEqual(encode_line_code("01", "Differential Manchester"), [-1, 1, 1, -1])
        self.assertEqual(encode_line_code("01", "NRZ_L"), [1, -1])

    def test_invalid_scheme_data_and_initial_level_are_rejected(self):
        with self.assertRaises(ValueError):
            encode_line_code("01", "unknown")
        with self.assertRaises(ValueError):
            encode_nrz_l("02")
        with self.assertRaises(ValueError):
            encode_nrz_i("1", initial_level=0)


class ScramblingTests(unittest.TestCase):
    def test_b8zs_uses_standard_pattern_for_both_preceding_polarities(self):
        self.assertEqual(encode_b8zs("100000000"), [1, 0, 0, 0, 1, -1, 0, -1, 1])
        self.assertEqual(encode_b8zs("00000000"), [0, 0, 0, -1, 1, 0, 1, -1])

    def test_hdb3_uses_000v_for_odd_mark_parity(self):
        self.assertEqual(encode_hdb3("10000"), [1, 0, 0, 0, 1])

    def test_hdb3_uses_b00v_for_even_mark_parity(self):
        self.assertEqual(encode_hdb3("110000"), [1, -1, 1, 0, 0, 1])

    def test_scramblers_round_trip_data_with_multiple_substitutions(self):
        data = "101000000000110000000010000"
        self.assertEqual(decode_b8zs(encode_b8zs(data)), data)
        self.assertEqual(decode_hdb3(encode_hdb3(data)), data)

    def test_initial_polarity_is_respected(self):
        self.assertEqual(encode_b8zs("00000000", initial_pulse=1)[3], -1)
        self.assertEqual(encode_hdb3("1", initial_pulse=-1), [-1])

    def test_invalid_data_levels_and_polarity_are_rejected(self):
        with self.assertRaises(ValueError):
            encode_hdb3("012")
        with self.assertRaises(ValueError):
            decode_b8zs([0, 0, 2])
        with self.assertRaises(ValueError):
            encode_b8zs("1", initial_pulse=0)


class ModulationTests(unittest.TestCase):
    def test_pcm_encodes_fixed_width_uniform_quantizer_codes(self):
        bits = pcm_encode([-1.0, -0.25, 0.0, 1.0], bits_per_sample=2)
        self.assertEqual(bits, "00011011")

    def test_pcm_decode_returns_quantizer_bin_midpoints(self):
        self.assertEqual(pcm_decode("00011011", bits_per_sample=2), [-0.75, -0.25, 0.25, 0.75])

    def test_pcm_clips_out_of_range_values_and_handles_empty_input(self):
        self.assertEqual(pcm_encode([-5.0, 5.0], bits_per_sample=2), "0011")
        self.assertEqual(pcm_encode([]), "")
        self.assertEqual(pcm_decode(""), [])

    def test_delta_modulation_encoding_and_staircase(self):
        bits = delta_encode([0.2, 0.8, -0.2, -0.8], step_size=0.5)
        self.assertEqual(bits, "1100")
        self.assertEqual(delta_decode(bits, step_size=0.5), [0.5, 1.0, 0.5, 0.0])

    def test_delta_initial_reference_and_empty_stream(self):
        self.assertEqual(delta_decode("10", step_size=0.25, initial_value=1.0), [1.25, 1.0])
        self.assertEqual(delta_encode([], step_size=1.0), "")

    def test_invalid_pcm_and_delta_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            pcm_encode([0.0], bits_per_sample=0)
        with self.assertRaises(ValueError):
            pcm_decode("101", bits_per_sample=2)
        with self.assertRaises(ValueError):
            delta_encode([0.0], step_size=0)
        with self.assertRaises(ValueError):
            delta_decode("102", step_size=0.5)


class PlotterTests(unittest.TestCase):
    def test_waveform_rejects_inconsistent_timing(self):
        with self.assertRaises(ValueError):
            plot_waveform([1, -1], "waveform.png", samples_per_bit=2, bit_count=2)

    @unittest.skipUnless(MATPLOTLIB_AVAILABLE, "Matplotlib is not installed")
    def test_waveform_is_saved_as_a_readable_png(self):
        from PIL import Image

        with TemporaryDirectory() as directory:
            path = plot_waveform(
                [1, -1, -1, 1], Path(directory) / "encoded.png", scheme="Manchester",
                samples_per_bit=2, bit_count=2,
            )
            with Image.open(path) as image:
                self.assertEqual(image.format, "PNG")
                self.assertGreater(image.width, 0)
                self.assertGreater(image.height, 0)

    @unittest.skipUnless(MATPLOTLIB_AVAILABLE, "Matplotlib is not installed")
    def test_reconstruction_plots_are_saved(self):
        from PIL import Image

        with TemporaryDirectory() as directory:
            delta_path = plot_delta_reconstruction([0.0, 0.5, 0.0], Path(directory) / "delta.png")
            combined_path = plot_modulation_reconstructions(
                [-0.5, 0.5], [0.0, 0.5], Path(directory) / "both.png"
            )
            for path in (delta_path, combined_path):
                with Image.open(path) as image:
                    self.assertEqual(image.format, "PNG")


if __name__ == "__main__":
    unittest.main()
