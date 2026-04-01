import pytest
from app.infrastructure.utils.text_utils import split_text

def test_split_text_short():
    text = "Short text"
    chunks = split_text(text, max_length=100)
    assert chunks == [text]

def test_split_text_long_paragraphs():
    text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    chunks = split_text(text, max_length=15)
    # "Paragraph 1" is 11 chars
    # "Paragraph 2" is 11 chars
    # "Paragraph 3" is 11 chars
    assert len(chunks) == 3
    assert chunks[0] == "Paragraph 1"
    assert chunks[1] == "Paragraph 2"
    assert chunks[2] == "Paragraph 3"

def test_split_text_long_newlines():
    text = "Line 1\nLine 2\nLine 3"
    chunks = split_text(text, max_length=8)
    assert len(chunks) == 3
    assert chunks[0] == "Line 1"
    assert chunks[1] == "Line 2"
    assert chunks[2] == "Line 3"

def test_split_text_no_good_split():
    text = "ThisIsALongWordWithoutSpaces"
    chunks = split_text(text, max_length=10)
    assert len(chunks) == 3
    assert chunks[0] == "ThisIsALon"
    assert chunks[1] == "gWordWitho"
    assert chunks[2] == "utSpaces"

def test_split_text_spaces():
    text = "Word1 Word2 Word3"
    chunks = split_text(text, max_length=6)
    assert len(chunks) == 3
    assert chunks[0] == "Word1"
    assert chunks[1] == "Word2"
    assert chunks[2] == "Word3"
