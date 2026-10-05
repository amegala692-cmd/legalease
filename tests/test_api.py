from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root_and_health():
    root = client.get("/")
    health = client.get("/health")
    assert root.status_code == 200
    assert health.status_code == 200
    assert health.json()["status"] == "ok"


def sample_payload():
    return {
        "document_type": "Non-Disclosure Agreement (NDA)",
        "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
        "terms": "Confidentiality must be maintained at all times; Payment to be made within 30 days of invoice",
        "effective_date": "October 1, 2026",
        "jurisdiction": "Tamil Nadu, India",
        "language": "English",
        "tone": "Formal and professional",
        "additional_instructions": "Include signature blocks.",
    }


def test_generate_demo_mode():
    response = client.post("/generate", json=sample_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "NON-DISCLOSURE AGREEMENT" in body["document"].upper()


def test_txt_export():
    payload = {
        "text": "TEST LEGAL DOCUMENT\n\n1. Purpose\nThis is a test.",
        "document_type": "Test Agreement",
        "format": "txt",
        "company_name": "LegalEase",
        "footer": "Footer",
        "effective_date": "October 1, 2026",
        "terms": ["One", "Two"],
    }
    response = client.post("/export", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert b"TEST LEGAL DOCUMENT" in response.content


def test_docx_export():
    payload = {
        "text": "TEST AGREEMENT\n\n1. Purpose\nThis is a test.",
        "document_type": "Test Agreement",
        "format": "docx",
        "company_name": "LegalEase",
        "footer": "Footer",
        "effective_date": "October 1, 2026",
        "terms": ["One", "Two"],
    }
    response = client.post("/export", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert len(response.content) > 1000


def test_pdf_export():
    payload = {
        "text": "TEST AGREEMENT\n\n1. Purpose\nThis is a test.",
        "document_type": "Test Agreement",
        "format": "pdf",
        "company_name": "LegalEase",
        "footer": "Footer",
        "effective_date": "October 1, 2026",
        "terms": ["One", "Two"],
    }
    response = client.post("/export", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF")
