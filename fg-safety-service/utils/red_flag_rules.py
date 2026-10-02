_RED_FLAG_TERMS = {
    "severe shortness of breath": ("shortness of breath", "difficulty breathing"),
    "chest pain": ("chest pain",),
    "fainting": ("fainting", "passed out", "loss of consciousness"),
    "confusion": ("confusion", "sudden confusion"),
}


def detect_red_flags(symptoms: list[str]) -> list[str]:
    normalized = [symptom.casefold() for symptom in symptoms]
    return sorted(
        label
        for label, terms in _RED_FLAG_TERMS.items()
        if any(term in symptom for symptom in normalized for term in terms)
    )
