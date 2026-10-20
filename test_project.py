"""Focused tests for the digital data generation milestone."""

import random
import unittest

from data_generator import (
    generate_data_with_eight_zeros,
    generate_data_with_four_zeros,
    generate_data_with_zero_run,
    generate_random_bits,
    longest_zero_run,
    validate_binary_data,
)
from palindrome import PalindromeResult, longest_palindrome


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


if __name__ == "__main__":
    unittest.main()
