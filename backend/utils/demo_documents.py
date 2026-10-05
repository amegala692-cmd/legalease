def _terms_list(terms: str) -> list[str]:
    return [item.strip() for item in terms.replace("\n", ";").split(";") if item.strip()]


def demo_document(document_type: str, parties: str, terms: str, effective_date: str, jurisdiction: str = "", language: str = "English", tone: str = "Formal and professional", additional_instructions: str = "") -> str:
    items = _terms_list(terms)
    party_lines = [p.strip() for p in parties.split(",") if p.strip()]
    party_text = ", ".join(party_lines) if party_lines else parties
    clause_lines = "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))
    return f"""{document_type.upper()}\n\n
Effective Date: {effective_date}\n
Parties\n
The parties to this draft are: {party_text}.\n
1. Purpose\n
This {document_type} records the understanding of the parties concerning the stated purpose and terms.\n
2. Terms and Conditions\n
{clause_lines or '1. [INSERT TERMS AND CONDITIONS]'}\n
3. General Provisions\n
The parties should verify all names, dates, amounts, notices, governing-law provisions, and other material details before signing.\n
4. Governing Law\n
{jurisdiction or '[INSERT GOVERNING LAW / JURISDICTION]'}\n
5. Entire Agreement\n
This draft is intended to capture the information supplied to LegalEase and may require further review or amendments.\n
Signatures\n
Party 1: ______________________________    Date: ______________\nName: ________________________________\n\nParty 2: ______________________________    Date: ______________\nName: ________________________________\n\nNotice\nThis document is an AI-generated informational draft and is not legal advice. Review all provisions and applicable local requirements before relying on or signing it.\n""".strip()
