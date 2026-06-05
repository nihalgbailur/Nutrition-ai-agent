from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache

from rapidfuzz import fuzz, process

from nutriplan.config import KB_EXTRA_PATHS, KB_PATH
from nutriplan.models.schemas import (
    AlternativeSuggestion,
    KBInsight,
    PantryItem,
    PantryKBMatch,
    UserProfile,
)

ALIASES: dict[str, str] = {
    "maggi": "Maggi 2-Minute Noodles (Masala)",
    "parle g": "Parle-G Original",
    "parle-g": "Parle-G Original",
    "haldiram": "Haldiram's All in One / Bhujia / Sev",
    "bhujia": "Haldiram's All in One / Bhujia / Sev",
    "kurkure": "Kurkure / Lay's / Bingo Chips",
    "lays": "Kurkure / Lay's / Bingo Chips",
    "lay's": "Kurkure / Lay's / Bingo Chips",
    "good day": "Britannia Good Day",
    "marie gold": "Britannia Marie Gold",
    "chocos": "Many Corn Flakes / Rice Flakes with added sugar",
    "coke": "Soft Drinks (Coca-Cola, Pepsi, Sprite, etc.)",
    "coca cola": "Soft Drinks (Coca-Cola, Pepsi, Sprite, etc.)",
    "ching": "Ching's Schezwan Noodles",
    "knorr": "Knorr Soupy Noodles",
    "yippee": "Top Ramen / Yippee Noodles",
}


@dataclass
class KBRecord:
    category: str
    kind: str  # poor_choices | better_alternatives
    product: str
    brand: str
    concerns: list[str]
    narrative: str


def _load_categories_from_file(path) -> dict:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("categories", {})


class PackagedFoodsKB:
    def __init__(self, path=KB_PATH, extra_paths: list | None = None) -> None:
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.guidelines: dict[str, str] = dict(raw.get("general_guidelines_for_agents", {}))
        merged_categories: dict = dict(raw.get("categories", {}))
        for extra in extra_paths or KB_EXTRA_PATHS:
            for cat, block in _load_categories_from_file(extra).items():
                if cat not in merged_categories:
                    merged_categories[cat] = block
                else:
                    for kind in ("poor_choices", "better_alternatives"):
                        merged_categories[cat].setdefault(kind, [])
                        merged_categories[cat][kind].extend(block.get(kind, []))

        self.records: list[KBRecord] = []
        for category, block in merged_categories.items():
            for kind in ("poor_choices", "better_alternatives"):
                for item in block.get(kind, []):
                    narrative = item.get("why_problematic") or item.get("why_better", "")
                    self.records.append(
                        KBRecord(
                            category=category,
                            kind=kind,
                            product=item["product"],
                            brand=item.get("brand", ""),
                            concerns=item.get("concerns", []),
                            narrative=narrative,
                        )
                    )
        self._poor = [r for r in self.records if r.kind == "poor_choices"]
        self._better = [r for r in self.records if r.kind == "better_alternatives"]
        self._product_choices = [r.product for r in self._poor]

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()

    def _resolve_alias(self, name: str) -> str | None:
        key = self._normalize(name)
        for alias, product in ALIASES.items():
            if alias in key:
                return product
        return None

    def match_pantry_items(
        self, pantry: list[PantryItem], threshold: float = 78.0
    ) -> list[PantryKBMatch]:
        matches: list[PantryKBMatch] = []
        for item in pantry:
            alias_product = self._resolve_alias(item.name)
            candidates = self._poor
            query = alias_product or item.name
            result = process.extractOne(
                query,
                [r.product for r in candidates],
                scorer=fuzz.token_set_ratio,
            )
            if not result:
                continue
            product_name, score, idx = result
            if alias_product:
                score = max(score, 90.0)
            if score < threshold and not item.is_packaged:
                continue
            record = self._poor[idx]
            matches.append(
                PantryKBMatch(
                    pantry_item_name=item.name,
                    kb_product=record.product,
                    kb_brand=record.brand,
                    category=record.category,
                    concerns=record.concerns,
                    why_problematic=record.narrative,
                    score=float(score),
                )
            )
        return matches

    def get_alternatives_for_match(
        self, match: PantryKBMatch, profile: UserProfile
    ) -> list[AlternativeSuggestion]:
        alts: list[AlternativeSuggestion] = []
        allergy_tokens = [a.lower() for a in profile.allergies]
        for record in self._better:
            if record.category != match.category:
                continue
            blob = f"{record.product} {record.brand}".lower()
            if any(a in blob for a in allergy_tokens):
                continue
            if profile.diet_style.value == "vegan" and any(
                x in blob for x in ("paneer", "dairy", "ghee", "curd", "milk", "chaas")
            ):
                continue
            if profile.diet_style.value == "jain" and any(
                x in blob for x in ("onion", "garlic", "egg")
            ):
                continue
            alts.append(
                AlternativeSuggestion(
                    product=record.product,
                    brand=record.brand,
                    why_better=record.narrative,
                    concerns=record.concerns,
                )
            )
            if len(alts) >= 2:
                break
        return alts

    def build_insights(
        self, pantry: list[PantryItem], profile: UserProfile
    ) -> list[KBInsight]:
        insights: list[KBInsight] = []
        matches = self.match_pantry_items(pantry)
        for match in matches[:5]:
            alts = self.get_alternatives_for_match(match, profile)
            alt_text = ""
            if alts:
                alt_text = " Consider: " + "; ".join(a.product for a in alts[:2]) + "."
            gentle = (
                f"'{match.pantry_item_name}' matches a commonly used packaged item "
                f"({match.kb_product}) — concerns include {', '.join(match.concerns[:3])}. "
                f"{match.why_problematic}{alt_text}"
            )
            insights.append(
                KBInsight(
                    pantry_item=match.pantry_item_name,
                    concerns=match.concerns,
                    gentle_message=gentle,
                    alternatives=alts,
                )
            )
        return insights

    def build_agent_context(self, insights: list[KBInsight]) -> str:
        if not insights:
            return "No high-concern packaged food matches in pantry."
        lines = ["Indian packaged foods context (informational, not medical advice):"]
        for ins in insights[:4]:
            lines.append(f"- {ins.gentle_message}")
        for key, value in self.guidelines.items():
            lines.append(f"Guideline ({key}): {value}")
        return "\n".join(lines)

    def shopping_swap_hint(self, item_name: str, profile: UserProfile) -> str | None:
        fake = PantryItem(name=item_name, is_packaged=True)
        matches = self.match_pantry_items([fake], threshold=72.0)
        if not matches:
            return None
        alts = self.get_alternatives_for_match(matches[0], profile)
        if not alts:
            return None
        return f"Optional swap idea: {alts[0].product} ({alts[0].why_better[:120]}...)"


@lru_cache(maxsize=1)
def get_kb() -> PackagedFoodsKB:
    return PackagedFoodsKB()