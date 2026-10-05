from __future__ import annotations

import base64
from datetime import date

import requests
import streamlit as st

st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")

DEFAULT_API = "https://legalease-8q7w.onrender.com"


def api_base() -> str:
    return st.session_state.get("api_base", DEFAULT_API).rstrip("/")


def api_post(path: str, payload: dict, timeout: int = 120):
    response = requests.post(f"{api_base()}{path}", json=payload, timeout=timeout)
    response.raise_for_status()
    return response


def logo_uri(uploaded_file) -> str | None:
    if not uploaded_file:
        return None
    raw = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/png"
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .hero { padding: 1.25rem 1.5rem; border: 1px solid rgba(128,128,128,.2); border-radius: 18px; background: linear-gradient(135deg, rgba(100,100,100,.10), rgba(255,255,255,.02)); }
        .hero h1 { margin: 0 0 .25rem 0; }
        .hero p { margin: 0; opacity: .82; }
        .preview { max-height: 700px; overflow-y: auto; border: 1px solid rgba(128,128,128,.22); padding: 1.2rem; border-radius: 14px; background: rgba(128,128,128,.06); }
        .smallcaps { text-transform: uppercase; letter-spacing: .08em; font-size: .75rem; opacity: .65; }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()

st.markdown('<div class="hero"><div class="smallcaps">AI-Powered Legal Document Generator</div><h1>⚖️ LegalEase</h1><p>Create editable legal-information drafts and export them as TXT, DOCX, or PDF.</p></div>', unsafe_allow_html=True)

if "document" not in st.session_state:
    st.session_state.document = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

with st.sidebar:
    st.header("Settings")
    st.session_state.api_base = st.text_input("Backend URL", value=api_base(), help="FastAPI server URL")
    company_name = st.text_input("Company / Brand", value="LegalEase")
    footer = st.text_input("Footer", value="Generated with LegalEase — informational use only; not legal advice.")
    uploaded_logo = st.file_uploader("Upload logo", type=["png", "jpg", "jpeg", "webp"])
    language = st.selectbox("Language", ["English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada"], index=0)
    tone = st.selectbox("Tone", ["Formal and professional", "Plain and accessible", "Detailed and traditional"])

try:
    health = requests.get(f"{api_base()}/health", timeout=5).json()
    st.sidebar.success(f"Backend: online ({health.get('ai_mode', 'unknown')} mode)")
except Exception:
    st.sidebar.warning("Backend is not reachable. Start FastAPI first.")

left, right = st.columns([1, 1.15], gap="large")
with left:
    st.subheader("1. Document details")
    doc_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Employment Offer Letter",
            "Non-Disclosure Agreement (NDA)",
            "Residential Lease Agreement",
            "Service Agreement",
            "Freelance Work Contract",
            "General Agreement",
            "Custom Legal Document",
        ],
    )
    parties = st.text_area("Parties involved", placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)", height=100)
    terms = st.text_area(
        "Terms & conditions",
        placeholder="Payment to be made within 30 days of invoice; Confidentiality must be maintained at all times; Either party may terminate with 15 days notice",
        height=170,
        help="Separate clauses with semicolons or put one clause per line.",
    )
    effective_date = st.date_input("Effective date", value=date.today()).strftime("%B %d, %Y")
    jurisdiction = st.text_input("Jurisdiction / governing law", placeholder="e.g. Tamil Nadu, India")
    additional = st.text_area("Additional instructions (optional)", height=100, placeholder="Add company-specific language, signature instructions, or formatting preferences.")

    generate_col, simplify_col = st.columns(2)
    with generate_col:
        generate_clicked = st.button("✨ Generate Document", type="primary", use_container_width=True)
    with simplify_col:
        simplify_clicked = st.button("🧠 Explain in Plain Language", use_container_width=True)

    if generate_clicked:
        if not parties.strip() or not terms.strip():
            st.error("Please enter the parties and terms before generating.")
        else:
            with st.spinner("Generating your document…"):
                try:
                    res = api_post(
                        "/generate",
                        {
                            "document_type": doc_type,
                            "parties": parties,
                            "terms": terms,
                            "effective_date": effective_date,
                            "jurisdiction": jurisdiction,
                            "language": language,
                            "tone": tone,
                            "additional_instructions": additional,
                        },
                    )
                    data = res.json()
                    st.session_state.document = data["document"]
                    st.session_state.summary = ""
                    st.success(f"Generated in {data.get('mode', 'AI')} mode using {data.get('model', 'configured model')}.")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")

    if simplify_clicked:
        if not st.session_state.document.strip():
            st.warning("Generate or paste a document first.")
        else:
            with st.spinner("Creating plain-language explanation…"):
                try:
                    res = api_post("/simplify", {"text": st.session_state.document, "language": language})
                    st.session_state.summary = res.json()["summary"]
                except Exception as exc:
                    st.error(f"Explanation failed: {exc}")

with right:
    st.subheader("2. Preview & edit")
    edited = st.checkbox("Click to edit document", value=True)
    if edited:
        st.session_state.document = st.text_area(
            "Editable document",
            value=st.session_state.document,
            height=620,
            label_visibility="collapsed",
        )
    else:
        st.markdown(f'<div class="preview">{st.session_state.document.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    st.caption("Review the wording, names, dates, amounts, and jurisdiction before using the document.")

    export_cols = st.columns(3)
    terms_for_table = [t.strip() for t in terms.replace("\n", ";").split(";") if t.strip()]
    logo = logo_uri(uploaded_logo)
    export_payload_base = {
        "text": st.session_state.document,
        "document_type": doc_type,
        "company_name": company_name,
        "footer": footer,
        "effective_date": effective_date,
        "terms": terms_for_table,
        "logo_data_uri": logo,
    }

    def export_button(target: str, label: str, media_ext: str):
        if not st.session_state.document.strip():
            st.button(label, disabled=True, use_container_width=True)
            return
        if st.button(label, use_container_width=True):
            try:
                payload = dict(export_payload_base)
                payload["format"] = target
                res = api_post("/export", payload)
                st.download_button(
                    label=f"Download {media_ext}",
                    data=res.content,
                    file_name=f"{doc_type.replace(' ', '_')}.{media_ext.lower()}",
                    mime=res.headers.get("content-type", "application/octet-stream"),
                    use_container_width=True,
                )
            except Exception as exc:
                st.error(f"Export failed: {exc}")

    with export_cols[0]:
        export_button("txt", "📄 Prepare TXT", "TXT")
    with export_cols[1]:
        export_button("docx", "📝 Prepare DOCX", "DOCX")
    with export_cols[2]:
        export_button("pdf", "📕 Prepare PDF", "PDF")

    if st.session_state.summary:
        st.divider()
        st.subheader("Plain-language explanation")
        st.markdown(st.session_state.summary)

st.divider()
st.caption("LegalEase follows the project specification for AI-assisted legal document drafting, editable preview, branding, and multi-format export. AI-generated material should be reviewed for accuracy and local legal requirements before use.")
