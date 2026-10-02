def lookup_barcode(barcode: str) -> dict[str, str | int | None]:
    """Placeholder lookup: no external product catalog is configured."""
    return {"barcode": barcode, "product_name": None, "volume_ml": None}
