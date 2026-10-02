import re


_VOLUME_PATTERN = re.compile(r"(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>ml|milliliters?|l|liters?)\b", re.I)


def parse_fluid_text(text: str) -> tuple[int | None, str]:
    """Extract an explicitly stated volume; do not guess when none is present."""
    match = _VOLUME_PATTERN.search(text)
    if match is None:
        return None, text.strip()
    amount = float(match.group("amount"))
    unit = match.group("unit").lower()
    volume_ml = round(amount * 1000) if unit.startswith("l") else round(amount)
    return volume_ml, text.strip()
