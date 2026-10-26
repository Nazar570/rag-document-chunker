import pytest
from app.services.cleaner import TextCleaner


@pytest.fixture
def text_cleaner():
    return TextCleaner()