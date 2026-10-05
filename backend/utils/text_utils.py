import html
import re
import unicodedata


def sanitize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\r\n?", "\n", text)
    return text.strip()


def split_terms(terms_text: str) -> list[str]:
    normalized = (terms_text or "").replace("\r\n", "\n")
    parts = re.split(r";|\n(?=\s*(?:[-*•]|\d+[.)]))", normalized)
    cleaned = []
    for part in parts:
        item = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", part).strip()
        if item:
            cleaned.append(item)
    return cleaned


def safe_filename(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", sanitize_text(name))
    return value.strip("._") or "LegalEase_Document"


def markdown_to_html(text: str) -> str:
    lines = sanitize_text(text).splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        escaped = html.escape(stripped)
        if re.match(r"^\d+[.)]\s+", stripped):
            out.append(f"<h3>{escaped}</h3>")
        elif len(stripped) <= 90 and stripped == stripped.upper() and re.search(r"[A-Z]", stripped):
            out.append(f"<h2>{escaped}</h2>")
        else:
            out.append(f"<p>{escaped}</p>")
    return "".join(out)
