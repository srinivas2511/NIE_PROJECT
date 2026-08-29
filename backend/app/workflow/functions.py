import re

# Simulated enterprise data -- real ERP/CRM/HRMS integration is out of scope
# for this project (REQUIREMENTS.md SS13); these mock the same departments
# referenced in the RAG seed documents.
MOCK_HEADCOUNT = {"Engineering": 42, "Sales": 18, "HR": 6, "Finance": 9, "Marketing": 12}
MOCK_EXPENSE_TOTALS_USD = {
    "Engineering": 125000,
    "Sales": 98000,
    "HR": 31000,
    "Finance": 45000,
    "Marketing": 67000,
}
DEPARTMENTS = list(MOCK_HEADCOUNT)


def _match_department(description: str) -> str | None:
    lowered = description.lower()
    for dept in DEPARTMENTS:
        if re.search(rf"\b{re.escape(dept.lower())}\b", lowered):
            return dept
    return None


def retrieve_data(description: str) -> dict:
    dept = _match_department(description)
    if dept:
        return {
            "department": dept,
            "headcount": MOCK_HEADCOUNT[dept],
            "expense_total_usd": MOCK_EXPENSE_TOTALS_USD[dept],
        }
    return {"headcount_by_department": MOCK_HEADCOUNT}


def generate_report(description: str) -> dict:
    dept = _match_department(description) or "Company-wide"
    return {
        "report_title": f"{dept} Summary Report",
        "covers": dept,
        "summary": f"Simulated report generated for {dept}, compiled from current mock enterprise data.",
    }


def update_status(description: str) -> dict:
    lowered = description.lower()
    if any(kw in lowered for kw in ("complete", "done", "close")):
        new_status = "completed"
    elif any(kw in lowered for kw in ("block", "hold")):
        new_status = "blocked"
    else:
        new_status = "in_progress"
    return {"new_status": new_status}


FUNCTION_REGISTRY = {
    "retrieve_data": retrieve_data,
    "generate_report": generate_report,
    "update_status": update_status,
}
