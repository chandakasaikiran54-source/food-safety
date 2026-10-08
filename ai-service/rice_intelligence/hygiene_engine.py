def evaluate_visual_hygiene(morphology_result, color_result, quality_result):
    """
    Evaluates optical visible condition indicators of rice.

    IMPORTANT SCIENTIFIC LIMITATIONS:
    - Ordinary smartphone / RGB images CANNOT detect bacteria, fungal toxins (e.g. aflatoxin),
      chemical residues, or microbial pathogens (e.g. Bacillus cereus).
    - NEVER claims '100% hygienic', 'sterile', 'safe to eat', or 'no bacteria'.
    - Output is strictly an 'Image-based visual assessment only'.
    """
    if not morphology_result or not morphology_result.get("success", False):
        return {
            "rating": "Insufficient evidence",
            "visible_concerns": ["Unable to resolve rice grains with adequate optical clarity."],
            "limitations": "Image-based visual assessment only. Does not measure microbiological or chemical safety."
        }

    visible_concerns = []

    foreign_material = quality_result.get("foreign_material", False) if quality_result else False
    if foreign_material:
        visible_concerns.append("Visible foreign particulate or contrasting speckles detected on grain surface.")

    has_discoloration = color_result.get("visible_discoloration", False) if color_result else False
    if has_discoloration:
        details = color_result.get("discoloration_details", [])
        visible_concerns.extend(details if details else ["Visible surface discoloration observed."])

    quality_indicator = quality_result.get("indicator", "medium") if quality_result else "medium"
    if quality_indicator == "low":
        broken_pct = quality_result.get("broken_grains")
        if broken_pct and broken_pct > 20:
            visible_concerns.append(f"Elevated broken/fragmented grains ({broken_pct:.1f}%).")

    if not visible_concerns:
        rating = "Good visible condition"
    elif len(visible_concerns) == 1 and not foreign_material:
        rating = "Some visible concerns"
    else:
        rating = "Poor visible condition"

    return {
        "rating": rating,
        "visible_concerns": visible_concerns,
        "limitations": (
            "Image-based visual assessment only. An ordinary RGB image cannot verify bacterial absence, "
            "microbial load (e.g., Bacillus cereus spores), mycotoxins, pesticide residues, or laboratory food safety."
        )
    }
