import re


class TextCleaner:
    _HTML_PATTERN = re.compile(r"<[^>]+>")
    _MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
    _MD_FORMATTING_PATTERN = re.compile(r"[*_~`#>]")
    _WHITESPACE_PATTERN = re.compile(r"\s+")

    @staticmethod
    def remove_html_tags(text: str) -> str:
        if not text:
            return ""
        return TextCleaner._HTML_PATTERN.sub("", text)

    @staticmethod
    def remove_markdown(text: str) -> str:
        if not text:
            return ""
        text = TextCleaner._MD_LINK_PATTERN.sub(r"\1", text)
        return TextCleaner._MD_FORMATTING_PATTERN.sub("", text)

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        if not text:
            return ""
        return TextCleaner._WHITESPACE_PATTERN.sub(" ", text).strip()

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
        cleaned = TextCleaner.remove_html_tags(text)
        cleaned = TextCleaner.remove_markdown(cleaned)
        return TextCleaner.normalize_whitespace(cleaned)