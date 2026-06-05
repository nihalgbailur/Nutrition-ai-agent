from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
KB_PATH = DATA_DIR / "indian_packaged_foods_knowledge_base.json"
DB_PATH = DATA_DIR / "nutriplan.db"
SAMPLE_DIR = DATA_DIR / "sample"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
KB_EXTRA_PATHS = [
    SYNTHETIC_DIR / "packaged_foods_synthetic.json",
]
TXT_CORPUS_DIR = SYNTHETIC_DIR / "txt"

NUTRITION_LABEL = "Approximate estimates only"

DISCLAIMER = (
    "**Disclaimer**: This is general meal inspiration only. Nutrition information is "
    "approximate and for informational purposes. It is not a substitute for professional "
    "medical or dietary advice. If you have any medical condition, are pregnant, "
    "breastfeeding, or taking medication, please consult a qualified doctor or registered "
    "dietitian before making dietary changes."
)

MEDICAL_EXTRA_BANNER = (
    "You indicated a health-sensitive situation. NutriPlan AI provides general meal ideas "
    "only — not medical or specialized nutrition advice. Please confirm you understand "
    "before generating plans."
)

SAFETY_SYSTEM_APPENDIX = """
SAFETY RULES (non-negotiable):
- You are a meal ideation assistant, NOT a doctor or dietitian.
- Never claim to treat, cure, reverse, or manage any disease.
- Never create "diabetic meal plans", "PCOS reversal", or therapeutic diets.
- All nutrition numbers are approximate estimates only — never precise clinical values.
- Never suggest ingredients that match the user's declared allergens (including traces).
- If user has serious medical needs, recommend consulting a registered dietitian.
- For medications, never give food-drug advice — refer to doctor/pharmacist.
- Do not support extreme diets (<1200 kcal women, <1500 men) without strong caution.
- For packaged food swaps: be gentle, no shame, max 1-2 suggestions, moderation framing.
- Prioritize home-cooked whole foods over ultra-processed items when relevant.
"""

DEFAULT_LLM_MODEL = "xai/grok-beta"
DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"

# Chat speed (local Ollama is slow on first token — keep prompts/tokens small)
CHAT_MAX_TOKENS = 280
CHAT_TIMEOUT_SECONDS = 50
AGENT_MAX_TOKENS = 1200

CHAT_SAFETY_APPENDIX = """
Rules: meal ideas only, not medical advice. Allergies are strict. Nutrition is approximate only. Be brief.
"""