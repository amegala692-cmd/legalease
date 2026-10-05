from typing import Optional
from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=10000)
    terms: str = Field(..., min_length=2, max_length=30000)
    effective_date: str = Field(..., min_length=2, max_length=120)
    jurisdiction: str = Field(default="", max_length=300)
    language: str = Field(default="English", max_length=80)
    tone: str = Field(default="Formal and professional", max_length=120)
    additional_instructions: str = Field(default="", max_length=10000)

    @field_validator("document_type", "parties", "terms", "effective_date", "jurisdiction", "language", "tone", "additional_instructions")
    @classmethod
    def clean_whitespace(cls, value: str) -> str:
        return "\n".join(line.rstrip() for line in value.strip().splitlines())


class SimplifyRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=50000)
    language: str = Field(default="English", max_length=80)


class ExportRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100000)
    format: str = Field(..., pattern=r"^(txt|docx|pdf)$")
    document_type: str = Field(default="Legal Document", max_length=120)
    company_name: str = Field(default="LegalEase", max_length=120)
    footer: str = Field(default="", max_length=500)
    effective_date: str = Field(default="", max_length=120)
    terms: list[str] = Field(default_factory=list)
    logo_data_uri: Optional[str] = None

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Document text cannot be blank")
        return value


class DocumentResponse(BaseModel):
    success: bool
    document: str
    model: str
    mode: str
