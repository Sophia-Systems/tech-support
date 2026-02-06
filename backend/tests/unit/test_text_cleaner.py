"""Tests for text cleaner."""

from app.ingestion.processors.text_cleaner import TextCleaner


class TestTextCleaner:
    def setup_method(self):
        self.cleaner = TextCleaner()

    def test_normalize_line_endings(self):
        result = self.cleaner.clean("line1\r\nline2")
        assert result == "line1\nline2"

    def test_collapse_excessive_blank_lines(self):
        result = self.cleaner.clean("a\n\n\n\n\nb")
        assert result == "a\n\nb"

    def test_remove_control_characters(self):
        result = self.cleaner.clean("hello\x00world")
        assert result == "helloworld"

    def test_strip_whitespace(self):
        result = self.cleaner.clean("  hello  ")
        assert result == "hello"

    def test_preserve_single_newlines(self):
        result = self.cleaner.clean("line1\nline2")
        assert result == "line1\nline2"
