from __future__ import annotations

import re

from nutriplan.models.schemas import SafetyResult

MEDICAL_REDIRECT_PATTERNS = [
    r"\b(kidney\s+disease|renal\s+failure|dialysis)\b",
    r"\b(cancer|chemo|chemotherapy)\b",
    r"\b(eating\s+disorder|anorexia|bulimia)\b",
    r"\b(liver\s+cirrhosis|advanced\s+liver)\b",
]

MEDICAL_CAUTION_PATTERNS = [
    r"\b(diabetes|diabetic|pcos|thyroid|hypertension|blood\s+pressure)\b",
    r"\b(heart\s+disease|cardiac|cholesterol)\b",
]

PREGNANCY_PATTERNS = [r"\b(pregnant|pregnancy|breastfeeding|lactating)\b"]

MEDICATION_PATTERNS = [
    r"\b(medication|medicine|metformin|insulin|warfarin|blood\s+thinner)\b",
]

EXTREME_DIET_PATTERNS = [
    r"\b(\d{3,4})\s*(kcal|calories)\b",
    r"\b(lose\s+\d+\s*kg\s+per\s+week|rapid\s+weight\s+loss)\b",
    r"\b(omad|one\s+meal\s+a\s+day)\b",
]


def check_user_text(text: str) -> SafetyResult:
    lowered = text.lower().strip()
    if not lowered:
        return SafetyResult(action="allow")

    for pattern in MEDICAL_REDIRECT_PATTERNS:
        if re.search(pattern, lowered):
            return SafetyResult(
                action="redirect",
                category="serious_medical",
                message=(
                    "For conditions like this, I strongly recommend working with a registered "
                    "dietitian who can create a plan tailored to your medical needs. "
                    "NutriPlan AI can only offer general meal inspiration, not medical nutrition therapy."
                ),
            )

    for pattern in MEDICATION_PATTERNS:
        if re.search(pattern, lowered):
            return SafetyResult(
                action="redirect",
                category="medication",
                message=(
                    "Certain foods can interact with medications. Please check with your doctor "
                    "or pharmacist for personalized guidance."
                ),
            )

    for pattern in PREGNANCY_PATTERNS:
        if re.search(pattern, lowered):
            return SafetyResult(
                action="require_confirmation",
                category="pregnancy",
                message=(
                    "This is not specialized prenatal nutrition advice. Please consult your "
                    "healthcare provider for personalized guidance."
                ),
            )

    for pattern in EXTREME_DIET_PATTERNS:
        if re.search(pattern, lowered):
            m = re.search(r"\b(\d{3,4})\s*(kcal|calories)\b", lowered)
            if m and int(m.group(1)) < 1200:
                return SafetyResult(
                    action="redirect",
                    category="extreme_diet",
                    message=(
                        "Very low calorie plans can be unsafe without medical supervision. "
                        "NutriPlan AI won't generate extreme restriction plans."
                    ),
                )
            return SafetyResult(
                action="require_confirmation",
                category="extreme_diet",
                message="Aggressive or extreme diets may not be suitable for everyone. Proceed with caution.",
            )

    for pattern in MEDICAL_CAUTION_PATTERNS:
        if re.search(pattern, lowered):
            return SafetyResult(
                action="require_confirmation",
                category="medical_general",
                message=(
                    "Many people find certain meal patterns helpful, but this is not a disease-specific "
                    "therapeutic diet. Please consult your healthcare team for medical nutrition needs."
                ),
            )

    if re.search(r"\b(diabetic\s+meal\s+plan|pcos\s+reversal|kidney[\s-]?friendly\s+diet)\b", lowered):
        return SafetyResult(
            action="redirect",
            category="therapeutic_diet",
            message=(
                "NutriPlan AI cannot create disease-specific therapeutic meal plans. "
                "Please work with a qualified healthcare professional."
            ),
        )

    return SafetyResult(action="allow")


def profile_requires_confirmation(profile) -> bool:
    flags = profile.health_flags
    return bool(
        flags.has_medical_condition
        or flags.is_pregnant_or_breastfeeding
        or flags.cooking_for_children
        or flags.cooking_for_elderly
    )