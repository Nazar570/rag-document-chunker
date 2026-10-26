from app.services.cleaner import TextCleaner


def test_remove_html_tags(text_cleaner: TextCleaner):
    # Arrange
    raw_html = "<p>Hello <b>World</b>!</p><br/>"
    expected = "Hello World!"

    # Act
    result = text_cleaner.remove_html_tags(raw_html)

    # Assert
    assert result == expected


def test_remove_markdown_links_and_formatting(text_cleaner: TextCleaner):
    # Arrange
    raw_markdown = "# Header\nThis is [Google](https://google.com) and **bold** text."
    expected = " Header\nThis is Google and bold text."

    # Act
    result = text_cleaner.remove_markdown(raw_markdown)

    # Assert
    assert result == expected


def test_normalize_whitespace(text_cleaner: TextCleaner):
    # Arrange
    messy_text = "   This   is   a\n\ntext\twith   spaces.   "
    expected = "This is a text with spaces."

    # Act
    result = text_cleaner.normalize_whitespace(messy_text)

    # Assert
    assert result == expected


def test_clean_full_pipeline(text_cleaner: TextCleaner):
    # Arrange
    dirty_input = "<div># Title</div>\nClick [here](https://site.com) for **info**!   "
    expected = "Title Click here for info!"

    # Act
    result = text_cleaner.clean(dirty_input)

    # Assert
    assert result == expected


def test_clean_empty_string(text_cleaner: TextCleaner):
    # Arrange
    empty_input = ""
    expected = ""

    # Act
    result = text_cleaner.clean(empty_input)

    # Assert
    assert result == expected


def test_clean_none_handling(text_cleaner: TextCleaner):
    # Arrange
    none_input = None

    # Act
    result = text_cleaner.clean(none_input)

    # Assert
    assert result == ""