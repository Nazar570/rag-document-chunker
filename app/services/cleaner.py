import re


class TextCleaner:
    def remove_html_tags(self, text: str) -> str:
        pattern = re.compile(r"<[^>]+>")
        return pattern.sub("", text)

    def remove_markdown(self, text: str) -> str:
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"[*_~`#>]", "", text)
        return text

    def normalize_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def clean(self, text: str) -> str:
        if not text:
            return ""
        cleaned = self.remove_html_tags(text)
        cleaned = self.remove_markdown(cleaned)
        return self.normalize_whitespace(cleaned)