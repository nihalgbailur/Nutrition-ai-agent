from nutriplan.knowledge.packaged_foods import PackagedFoodsKB
from nutriplan.models.schemas import PantryItem, UserProfile


def test_matches_maggi_and_haldiram():
    kb = PackagedFoodsKB()
    pantry = [
        PantryItem(name="Maggi Masala Noodles", is_packaged=True),
        PantryItem(name="Haldiram Bhujia", is_packaged=True),
        PantryItem(name="Parle-G Biscuits", is_packaged=True),
    ]
    matches = kb.match_pantry_items(pantry, threshold=70)
    products = {m.kb_product for m in matches}
    assert any("Maggi" in p for p in products)
    assert any("Haldiram" in p for p in products)
    assert any("Parle" in p for p in products)


def test_alternatives_respect_allergy():
    kb = PackagedFoodsKB()
    profile = UserProfile(allergies=["dairy"])
    pantry = [PantryItem(name="Maggi 2-Minute", is_packaged=True)]
    matches = kb.match_pantry_items(pantry, threshold=65)
    assert matches
    alts = kb.get_alternatives_for_match(matches[0], profile)
    for alt in alts:
        blob = f"{alt.product} {alt.brand}".lower()
        assert "dairy" not in blob and "paneer" not in blob