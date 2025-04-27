import math
import unittest
from unittest.mock import patch

from src.summary_model import SummaryModel


class TestTextSummarizer(unittest.TestCase):

    def setUp(self):
        """Set up a TextSummarizer instance for the tests."""
        self.summarizer = SummaryModel(model_name="t5-small")

    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.T5ForConditionalGeneration.from_pretrained')
    def test_initialization(self, mock_model, mock_tokenizer):
        """Test if the summarizer is initialized correctly."""
        mock_tokenizer.return_value = 'mock_tokenizer'
        mock_model.return_value = 'mock_model'

        summarizer = SummaryModel(model_name="t5-small", max_input_length=500)

        self.assertEqual(summarizer.tokenizer, 'mock_tokenizer')
        self.assertEqual(summarizer.model, 'mock_model')
        self.assertEqual(summarizer.max_input_length, 500)

    def test_split_text_into_blocks(self):
        """Test if the text is split into blocks properly."""
        text = "This is a test text to be split into blocks."
        blocks = self.summarizer._split_text_into_blocks(text)

        # Check if text is split into blocks of appropriate size
        self.assertEqual(len(blocks), 1)  # Only one block because it's shorter than max_input_length
        self.assertEqual(blocks[0], text)

        long_text = "A" * 1000  # Text longer than the max_input_length
        blocks = self.summarizer._split_text_into_blocks(long_text)

        # Should be split into two blocks of size 500 each
        self.assertEqual(len(blocks), 2)
        self.assertEqual(len(blocks[0]), 500)
        self.assertEqual(len(blocks[1]), 500)

    def test_generate_summary(self):
        """Test if the summary generation works properly."""
        text_block = "This is a test block."
        summary = self.summarizer._generate_summary(text_block)
        assert isinstance(summary, str)

    def test_summarize(self):
        text = "This is a long text that needs to be summarized." * 100
        summary = self.summarizer.summarize(text)
        assert isinstance(summary, str)

    def test_summarize_with_multiple_blocks(self):
        n_copies = 400
        test_str = 'abc'
        long_text = test_str * n_copies
        blocks = self.summarizer._split_text_into_blocks(long_text)

        exp_n_blocks = math.ceil(len(test_str) * n_copies / self.summarizer.max_input_length)
        self.assertTrue(len(blocks) == exp_n_blocks)


def test_model():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
