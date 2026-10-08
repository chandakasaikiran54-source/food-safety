from .config import QUALITY_HIGH_BROKEN_MAX, QUALITY_MEDIUM_BROKEN_MAX

def assess_rice_quality(morphology_result, color_result):
    """
    Evaluates visual quality of rice based on measurable optical and geometric criteria:
    - Grain uniformity
    - Broken grains percentage
    - Foreign material presence
    - Abnormal / chalky grains
    - Visible discoloration

    Returns:
    - indicator: "high", "medium", "low", or "insufficient_evidence"
    - broken_grains: percentage or null
    - foreign_material: bool
    - abnormal_grains: bool
    - reason: evidence-based scientific rationale
    """
    if not morphology_result or not morphology_result.get("success", False):
        return {
            "indicator": "insufficient_evidence",
            "broken_grains": None,
            "foreign_material": False,
            "abnormal_grains": False,
            "reason": "Unable to segment sufficient rice grains to assess physical quality."
        }

    metrics = morphology_result.get("metrics")
    if not metrics:
        return {
            "indicator": "insufficient_evidence",
            "broken_grains": None,
            "foreign_material": False,
            "abnormal_grains": False,
            "reason": "Grain morphology metrics not available."
        }

    broken_pct = metrics.get("broken_grain_percentage")
    uniformity = metrics.get("uniformity", "medium")
    has_discoloration = color_result.get("visible_discoloration", False) if color_result else False
    discoloration_details = color_result.get("discoloration_details", []) if color_result else []

    # Detect abnormal/foreign indicators
    foreign_material = False
    abnormal_grains = False

    if has_discoloration and any("dark speckles" in d.lower() for d in discoloration_details):
        foreign_material = True

    if uniformity == "low" or has_discoloration:
        abnormal_grains = True

    # If broken percentage could not be calculated (e.g. bulk cluster)
    if broken_pct is None:
        if has_discoloration:
            indicator = "medium"
            reason = "Bulk rice shows moderate visual discoloration or uneven coloration. Individual broken grain percentage could not be resolved."
        else:
            indicator = "medium"
            reason = "Bulk grain cluster shows acceptable visual appearance; single-grain broken ratio requires spread grain inspection."
        return {
            "indicator": indicator,
            "broken_grains": None,
            "foreign_material": foreign_material,
            "abnormal_grains": abnormal_grains,
            "reason": reason
        }

    # Grade determination based on broken percentage and uniformity
    if broken_pct <= QUALITY_HIGH_BROKEN_MAX and uniformity == "high" and not has_discoloration:
        indicator = "high"
        reason = f"Excellent quality. Low broken grain ratio ({broken_pct:.1f}% <= {QUALITY_HIGH_BROKEN_MAX}%), high size uniformity, and clean grain appearance."
    elif broken_pct <= QUALITY_MEDIUM_BROKEN_MAX and not foreign_material:
        indicator = "medium"
        reason = f"Acceptable commercial quality. Moderate broken grain ratio ({broken_pct:.1f}%) and standard grain uniformity."
    else:
        indicator = "low"
        issues = []
        if broken_pct > QUALITY_MEDIUM_BROKEN_MAX:
            issues.append(f"elevated broken grain percentage ({broken_pct:.1f}%)")
        if uniformity == "low":
            issues.append("irregular grain sizing")
        if has_discoloration:
            issues.append("visible surface discoloration")
        reason = f"Sub-optimal quality: {', '.join(issues)}."

    return {
        "indicator": indicator,
        "broken_grains": round(float(broken_pct), 1) if broken_pct is not None else None,
        "foreign_material": foreign_material,
        "abnormal_grains": abnormal_grains,
        "reason": reason
    }
