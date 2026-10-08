"""
Verified Rice Nutrition and Glycemic Knowledge Layer.

SCIENTIFIC SOURCES:
1. ICMR - National Institute of Nutrition (NIN): Indian Food Composition Tables (IFCT, 2017)
2. USDA FoodData Central (Standard Reference Legacy / Foundation Foods)
3. University of Sydney International Tables of Glycemic Index and Glycemic Load Values (Atkinson et al., 2021)

DISCLAIMER:
Image pixels cannot measure protein, minerals, carbohydrates, or glycemic response.
All nutritional values are typical reference values per 100g raw milled rice for the identified variety.
"""

VERIFIED_RICE_NUTRITION_DATABASE = {
    "basmati": {
        "variety_name": "Milled Raw Basmati Rice",
        "serving_basis": "per 100g raw milled rice (reference data)",
        "energy_kcal": 356,
        "protein_g": 7.9,
        "carbohydrates_g": 78.2,
        "fat_g": 0.6,
        "dietary_fiber_g": 1.4,
        "minerals_mg": {
            "iron": 1.08,
            "zinc": 1.25,
            "magnesium": 23.0,
            "phosphorus": 108.0,
            "potassium": 115.0,
            "calcium": 9.0
        },
        "glycemic": {
            "gi": 54,
            "gi_category": "Low to Medium (Typically 50 - 58)",
            "glycemic_load_per_cooked_serving": "18 - 22 (per 150g cooked portion)",
            "amylose_content": "Intermediate to High (~20% - 24%)",
            "interpretation": (
                "Basmati rice is internationally recognized as having a lower glycemic index (50 - 58) "
                "than most standard white rices, attributed to its higher amylose-to-amylopectin ratio and intact grain structure."
            )
        }
    },
    "sona_masuri": {
        "variety_name": "Milled Raw Sona Masuri Rice (BPT 5204)",
        "serving_basis": "per 100g raw milled rice (reference data)",
        "energy_kcal": 350,
        "protein_g": 7.1,
        "carbohydrates_g": 79.0,
        "fat_g": 0.5,
        "dietary_fiber_g": 1.2,
        "minerals_mg": {
            "iron": 0.85,
            "zinc": 1.15,
            "magnesium": 21.0,
            "phosphorus": 96.0,
            "potassium": 105.0,
            "calcium": 8.0
        },
        "glycemic": {
            "gi": 68,
            "gi_category": "Medium to High (Typically 65 - 72)",
            "glycemic_load_per_cooked_serving": "24 - 28 (per 150g cooked portion)",
            "amylose_content": "Intermediate (~20% - 22%)",
            "interpretation": (
                "Sona Masuri has a medium to high glycemic index (65 - 72), reflecting its faster starch gelatinization "
                "and digestion rate compared to aged Basmati."
            )
        }
    },
    "other_rice": {
        "variety_name": "Standard Milled White Rice (Generic Medium/Short Grain)",
        "serving_basis": "per 100g raw milled rice (reference data)",
        "energy_kcal": 358,
        "protein_g": 6.8,
        "carbohydrates_g": 79.5,
        "fat_g": 0.5,
        "dietary_fiber_g": 1.0,
        "minerals_mg": {
            "iron": 0.80,
            "zinc": 1.10,
            "magnesium": 19.0,
            "phosphorus": 90.0,
            "potassium": 98.0,
            "calcium": 7.0
        },
        "glycemic": {
            "gi": 72,
            "gi_category": "High (Typically 70 - 78)",
            "glycemic_load_per_cooked_serving": "26 - 32 (per 150g cooked portion)",
            "amylose_content": "Lower amylose, higher amylopectin (~15% - 19%)",
            "interpretation": (
                "Standard short/medium grain white rice exhibits rapid enzymatic breakdown in the small intestine, "
                "leading to a higher glycemic response."
            )
        }
    }
}

COOKING_AND_METABOLIC_FACTORS = (
    "Factors modulating glycemic and digestive response in Biryani:\n"
    "1. Starch Retrogradation: Cooling and dum-holding of cooked rice promotes formation of Resistant Starch (Type 3 / RS3), "
    "which acts like dietary fiber and attenuates blood glucose spikes.\n"
    "2. Meal Matrix Effect: Biryani is co-ingested with protein (meat/eggs), dietary lipids (ghee/oil), and fiber (fried onions/herbs). "
    "This mixed food matrix significantly slows gastric emptying, blunting glycemic impact compared to eating plain white rice alone.\n"
    "3. Degree of Gelatinization: Extended boiling with excess water increases starch accessibility, whereas controlled dum steaming maintains grain integrity."
)

def get_rice_nutrition_profile(rice_type):
    """
    Returns verified reference nutrition and glycemic data for the identified rice variety.
    Returns null values if rice type is unknown.
    """
    data = VERIFIED_RICE_NUTRITION_DATABASE.get(rice_type.lower())
    if not data:
        return {
            "nutrition": {
                "protein": None,
                "carbohydrates": None,
                "fat": None,
                "fiber": None,
                "calories": None,
                "minerals": {},
                "reference_note": "Nutritional values cannot be determined for unknown or unverified rice variety."
            },
            "glycemic_information": {
                "gi": None,
                "gi_category": "Unknown",
                "interpretation": "GI cannot be reliably determined for this specific rice from the image.",
                "cooking_factors": COOKING_AND_METABOLIC_FACTORS,
                "limitations": "Individual glycemic response depends on variety, cooking method, cooling/reheating, and metabolic state."
            }
        }

    return {
        "nutrition": {
            "variety_referenced": data["variety_name"],
            "basis": data["serving_basis"],
            "calories_kcal": data["energy_kcal"],
            "protein_g": data["protein_g"],
            "carbohydrates_g": data["carbohydrates_g"],
            "fat_g": data["fat_g"],
            "fiber_g": data["dietary_fiber_g"],
            "minerals_mg": data["minerals_mg"],
            "reference_note": (
                "Typical reference values from ICMR-NIN IFCT / USDA databases. "
                "Values may vary by brand, degree of milling/polishing, agricultural soil, and portion size."
            )
        },
        "glycemic_information": {
            "gi": data["glycemic"]["gi"],
            "gi_category": data["glycemic"]["gi_category"],
            "glycemic_load": data["glycemic"]["glycemic_load_per_cooked_serving"],
            "amylose_context": data["glycemic"]["amylose_content"],
            "interpretation": data["glycemic"]["interpretation"],
            "cooking_factors": COOKING_AND_METABOLIC_FACTORS,
            "limitations": (
                "GI values are published reference benchmarks. Actual metabolic response varies by individual insulin sensitivity, "
                "preparation method, and co-consumed foods."
            )
        }
    }
