def score_symptoms(symptoms: list[str], red_flags: list[str]) -> int:
    return min(100, len(red_flags) * 40 + min(len(symptoms), 4) * 5)
