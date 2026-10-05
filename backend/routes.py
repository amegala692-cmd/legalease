from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.config import get_settings
from backend.schemas import DocumentRequest, DocumentResponse, ExportRequest, SimplifyRequest
from backend.utils.exporters import decode_logo, format_docx, format_pdf, format_txt
from backend.utils.text_utils import safe_filename

router = APIRouter()
settings = get_settings()
generator = GeminiDocumentGenerator(settings)


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version, "ai_mode": generator.mode, "model": settings.gemini_model}


@router.get("/document-types")
def document_types() -> dict:
    return {
        "document_types": [
            "Employment Contract",
            "Employment Offer Letter",
            "Non-Disclosure Agreement (NDA)",
            "Residential Lease Agreement",
            "Service Agreement",
            "Freelance Work Contract",
            "General Agreement",
            "Custom Legal Document",
        ]
    }


@router.post("/generate", response_model=DocumentResponse)
def generate(request: DocumentRequest) -> DocumentResponse:
    if sum(len(v) for v in request.model_dump().values() if isinstance(v, str)) > settings.max_request_chars:
        raise HTTPException(status_code=413, detail="Request is too large.")
    try:
        document = generator.generate_document(**request.model_dump())
        return DocumentResponse(success=True, document=document, model=settings.gemini_model, mode=generator.mode)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Document generation failed: {exc}") from exc


@router.post("/simplify")
def simplify(request: SimplifyRequest) -> dict:
    try:
        return {"success": True, "summary": generator.simplify(request.text, request.language), "mode": generator.mode}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Simplification failed: {exc}") from exc


@router.post("/export")
def export_document(request: ExportRequest) -> Response:
    try:
        logo = decode_logo(request.logo_data_uri)
        filename_base = safe_filename(request.document_type)
        if request.format == "txt":
            return Response(
                format_txt(request.text),
                media_type="text/plain; charset=utf-8",
                headers={"Content-Disposition": f'attachment; filename="{filename_base}.txt"'},
            )
        if request.format == "docx":
            data = format_docx(request.text, request.document_type, request.company_name, request.footer, request.effective_date, request.terms, logo)
            return Response(
                data,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f'attachment; filename="{filename_base}.docx"'},
            )
        data = format_pdf(request.text, request.document_type, request.company_name, request.footer, request.effective_date, logo)
        return Response(
            data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.pdf"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}") from exc
