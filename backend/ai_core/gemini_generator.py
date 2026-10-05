from __future__ import annotations

from google import genai
from google.genai import types

from backend.config import Settings
from backend.utils.demo_documents import demo_document


SYSTEM_INSTRUCTION = """
You are LegalEase's document drafting assistant. Create structured legal-information drafts
from the user's supplied facts. Never invent case law, statutes, citations, registration numbers,
licenses, or facts that were not provided. Avoid claiming that a document is guaranteed enforceable.
Use placeholders such as [INSERT ...] when essential information is missing.
Write clear, professional language and preserve the user's requested parties, terms, and dates.
Organize the output with a title and numbered section headings. Include signature blocks when
appropriate. Do not provide legal advice; this is an editable informational draft for review by
qualified counsel where appropriate.
""".strip()


class GeminiDocumentGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = settings.gemini_model
        self._client = None
        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)

    @property
    def mode(self) -> str:
        return "gemini" if self._client else "demo"

    def _build_prompt(self, **kwargs) -> str:
        document_type = kwargs["document_type"]
        parties = kwargs["parties"]
        terms = kwargs["terms"]
        effective_date = kwargs["effective_date"]
        jurisdiction = kwargs.get("jurisdiction", "")
        language = kwargs.get("language", "English")
        tone = kwargs.get("tone", "Formal and professional")
        additional_instructions = kwargs.get("additional_instructions", "")

        return f"""
Draft a {document_type} using only the information supplied below.

PARTIES:
{parties}

TERMS / CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date}

JURISDICTION (if supplied):
{jurisdiction or '[Not specified]'}

LANGUAGE:
{language}

TONE:
{tone}

ADDITIONAL INSTRUCTIONS:
{additional_instructions or '[None]'}

Output requirements:
1. Start with a concise document title.
2. Use numbered headings and readable paragraphs.
3. Include the supplied terms as substantive clauses, without changing their meaning.
4. Add reasonable standard structural sections relevant to this document type, but mark missing
   material facts with [INSERT ...] rather than guessing.
5. Add signature blocks for the relevant parties.
6. End with a brief non-advice notice.
""".strip()

    def generate_document(self, **kwargs) -> str:
        if not self._client:
            if not self.settings.allow_demo_mode:
                raise RuntimeError("GEMINI_API_KEY is not configured and demo mode is disabled.")
            return demo_document(**kwargs)

        response = self._client.models.generate_content(
            model=self.model,
            contents=self._build_prompt(**kwargs),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=self.settings.generation_temperature,
                max_output_tokens=self.settings.generation_max_tokens,
            ),
        )
        text = getattr(response, "text", None)
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()

    def simplify(self, text: str, language: str = "English") -> str:
        if not self._client:
            if not self.settings.allow_demo_mode:
                raise RuntimeError("GEMINI_API_KEY is not configured and demo mode is disabled.")
            return (
                "Plain-language summary (demo mode)\n\n"
                "This draft should be reviewed against the actual agreement and applicable local law.\n\n"
                + text[:5000]
            )

        prompt = f"""
Explain the following legal document in plain language for a non-lawyer. Keep the explanation in
{language}. Do not change the legal document itself. Summarize the purpose, parties, payment or
performance duties, dates, confidentiality obligations, termination rules, dispute provisions,
and other important responsibilities. Clearly state when the source text is silent.

DOCUMENT:
{text}
""".strip()
        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Do not give individualized legal advice. Explain the supplied text accurately and flag uncertainty.",
                temperature=0.2,
                max_output_tokens=5000,
            ),
        )
        result = getattr(response, "text", None)
        if not result:
            raise RuntimeError("Gemini returned an empty explanation.")
        return result.strip()
