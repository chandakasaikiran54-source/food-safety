def evaluate_culinary_profile(variety_result, morphology_result, quality_result):
    """
    Evaluates culinary suitability for Biryani and expected cooking / texture profile.
    
    IMPORTANT:
    Taste cannot be determined directly from image pixels.
    Output is strictly an 'Expected culinary profile' based on validated varietal science.
    """
    rice_type = variety_result.get("type", "unknown") if variety_result else "unknown"
    quality_indicator = quality_result.get("indicator", "medium") if quality_result else "medium"

    if rice_type == "basmati":
        rating = "high"
        reason = (
            "Extra-long slender grain morphology is the gold standard for traditional Biryani. "
            "Aged Basmati grains exhibit significant longitudinal elongation (up to 1.8-2.0x) upon cooking "
            "without expanding in girth, resulting in separate, elegant, non-sticky rice grains."
        )
        expected_texture = "Fluffy, tender yet firm grains that remain individually distinct."
        grain_separation = "high"
        aroma_potential = "High (Characteristic natural Basmati aroma attributed to 2-acetyl-1-pyrroline)."
        cooking_characteristics = (
            "Requires gentle parboiling (typically to 70-80% doneness) before dum layering. "
            "Exhibits superior steam absorption without bursting or releasing excess surface starch."
        )

    elif rice_type == "sona_masuri":
        rating = "moderate"
        reason = (
            "Medium-slender grain profile. Sona Masuri is highly valued in South Indian culinary tradition and "
            "absorbs spices and meat gravies effectively. However, it lacks the dramatic longitudinal elongation "
            "of Basmati, producing a denser, softer rice bed in Biryani."
        )
        expected_texture = "Soft, light, and tender with moderate cohesion."
        grain_separation = "moderate"
        aroma_potential = "Mild to pleasant natural cereal aroma; lacks the distinct floral note of Basmati."
        cooking_characteristics = (
            "Cooks more quickly than aged Basmati. Requires precise water-to-rice ratios to prevent excess softening "
            "during extended dum steaming."
        )

    elif rice_type == "other_rice":
        rating = "low"
        reason = (
            "Short or bold grain morphology typically contains higher surface amylopectin or starch leaching tendencies, "
            "causing grains to stick or clump together. Not recommended for traditional layered dum Biryani."
        )
        expected_texture = "Sticky, dense, or clumping texture unsuited for loose Biryani rice."
        grain_separation = "low"
        aroma_potential = "Neutral."
        cooking_characteristics = (
            "Tendency to absorb moisture rapidly and lose structural integrity under prolonged steam."
        )

    else:
        rating = "insufficient_evidence"
        reason = "Unable to determine Biryani culinary suitability due to inconclusive rice variety identification."
        expected_texture = "Unknown; requires verified rice variety classification."
        grain_separation = "undetermined"
        aroma_potential = "Undetermined."
        cooking_characteristics = "Cooking characteristics cannot be predicted from ambiguous grain evidence."

    return {
        "biryani_suitability": {
            "rating": rating,
            "reason": reason
        },
        "culinary_profile": {
            "expected_texture": expected_texture,
            "grain_separation": grain_separation,
            "aroma_potential": aroma_potential,
            "cooking_characteristics": cooking_characteristics,
            "taste_prediction": "Expected culinary profile only; taste cannot be determined from an image."
        }
    }
