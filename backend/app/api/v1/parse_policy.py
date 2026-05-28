"""PDF lender policy parsing via pdfplumber + Claude API."""
from __future__ import annotations
import json
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.lender import EligibilityRule, LenderProgram
from app.schemas.policy import ParsedLenderPreview, PolicyImportRequest

router = APIRouter(prefix="/parse-policy", tags=["parse-policy"])

_EXTRACTION_PROMPT = """You are an expert at reading equipment finance lender policy documents.

Extract the following structured information from the policy text below and return ONLY valid JSON.

Required JSON structure:
{
  "lender_name": "string",
  "notes": "string or null - brief summary of the lender",
  "contact_email": "string or null",
  "contact_phone": "string or null",
  "programs": [
    {
      "name": "string - program name",
      "description": "string or null",
      "min_amount": number or null,
      "max_amount": number or null,
      "rules": [
        {
          "rule_type": "one of the valid rule types below",
          "label": "string or null - human readable label",
          "weight": number between 0.5 and 3.0,
          "parameters": object matching the rule type schema
        }
      ]
    }
  ]
}

Valid rule types and their parameter schemas:
- MIN_CREDIT_SCORE: {"min_score": integer}
- MAX_BANKRUPTCIES: {"max_count": integer}
- MIN_FICO_SBSS: {"min_score": integer}
- MIN_EXPERIAN_INTELLISCORE: {"min_score": integer}
- MIN_DUNS_PAYDEX: {"min_score": integer}
- MAX_DEROGATORY_MARKS: {"max_count": integer}
- MIN_YEARS_IN_BUSINESS: {"min_years": number}
- MIN_ANNUAL_REVENUE: {"min_revenue": number}
- ALLOWED_BUSINESS_TYPES: {"types": ["llc","corporation","s_corporation","sole_proprietor","partnership"]}
- MIN_EMPLOYEE_COUNT: {"min_count": integer}
- MAX_EMPLOYEE_COUNT: {"max_count": integer}
- MIN_OWNERSHIP_PCT: {"min_pct": number}
- NAICS_CODE_ALLOWLIST: {"codes": ["string"]}
- ALLOWED_EQUIPMENT_TYPES: {"types": ["heavy_equipment","trucks","trailers","construction","medical","manufacturing","technology","restaurant","agricultural","printing","office","other"]}
- MAX_EQUIPMENT_AGE_YRS: {"max_age_yrs": number}
- MIN_LOAN_AMOUNT: {"min_amount": number}
- MAX_LOAN_AMOUNT: {"max_amount": number}
- MAX_TERM_MONTHS: {"max_months": integer}
- MIN_DOWN_PAYMENT_PCT: {"min_pct": number}
- ALLOWED_EQUIPMENT_CONDITIONS: {"conditions": ["new","used","refurbished"]}
- ALLOWED_STATES: {"states": ["TX","CA",...]}
- EXCLUDED_STATES: {"states": ["NY","FL",...]}
- MIN_CREDIT_SCORE_BY_STATE: {"state_minimums": {"TX": 620, "CA": 650}}
- MAX_LOAN_AMOUNT_BY_STATE: {"state_maximums": {"TX": 500000}}
- MIN_YEARS_IN_BUSINESS_BY_STATE: {"state_minimums": {"TX": 2}}
- ALLOWED_STATES_FOR_EQUIPMENT: {"states": ["TX","CA",...]}

Assign higher weights (2.0-3.0) to hard knockout rules like credit score minimums and bankruptcy limits.
Assign moderate weights (1.0-1.5) to soft preference rules.

Policy document:
"""


@router.post("/upload", response_model=ParsedLenderPreview)
async def upload_and_parse(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY not configured — PDF parsing unavailable",
        )

    # Extract text from PDF
    try:
        import pdfplumber
        import io

        contents = await file.read()
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
        full_text = "\n\n".join(pages_text)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to read PDF: {exc}")

    if not full_text.strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from the PDF")

    # Truncate to avoid token limits (keep ~12k chars)
    if len(full_text) > 12000:
        full_text = full_text[:12000] + "\n\n[... document truncated ...]"

    # Call Claude
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": _EXTRACTION_PROMPT + full_text,
                }
            ],
        )
        raw_json = message.content[0].text.strip()

        # Strip markdown code fences if present
        if raw_json.startswith("```"):
            lines = raw_json.split("\n")
            raw_json = "\n".join(lines[1:-1])

        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Claude returned invalid JSON: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Claude API error: {exc}")

    try:
        return ParsedLenderPreview(**data)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Parsed data does not match schema: {exc}")


@router.post("/import", status_code=201)
async def import_policy(body: PolicyImportRequest, db: AsyncSession = Depends(get_db)):
    """Commit a parsed preview into the database under an existing lender."""
    from app.models.lender import Lender

    lender = await db.get(Lender, body.lender_id)
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")

    preview = body.preview
    created_programs = []

    for prog_data in preview.programs:
        program = LenderProgram(
            lender_id=body.lender_id,
            name=prog_data.name,
            description=prog_data.description,
            min_amount=prog_data.min_amount,
            max_amount=prog_data.max_amount,
        )
        db.add(program)
        await db.flush()

        for rule_data in prog_data.rules:
            rule = EligibilityRule(
                program_id=program.id,
                rule_type=rule_data.rule_type,
                label=rule_data.label,
                weight=rule_data.weight,
                parameters=rule_data.parameters,
            )
            db.add(rule)

        created_programs.append(str(program.id))

    return {"imported_programs": len(created_programs), "program_ids": created_programs}
