from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from nutriplan.config import DB_PATH
from nutriplan.models.schemas import (
    FeedbackRecord,
    PantryItem,
    Recipe,
    ShoppingList,
    UserProfile,
    WeeklyMealPlan,
)
from nutriplan.models.schemas import KBInsight


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        schema_path = Path(__file__).parent / "schema.sql"
        with self._connect() as conn:
            conn.executescript(schema_path.read_text())

    def save_profile(self, profile: UserProfile) -> None:
        payload = profile.model_dump(mode="json")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_profile (id, data, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at
                """,
                (profile.id, json.dumps(payload), _utc_now()),
            )

    def get_profile(self) -> UserProfile | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data FROM user_profile ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
        if not row:
            return None
        return UserProfile.model_validate(json.loads(row["data"]))

    def clear_pantry(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM pantry_items")

    def reset_generated_data(self) -> None:
        """Clear recipes, plans, shopping, feedback (keep profile/pantry unless re-seeded)."""
        with self._connect() as conn:
            for table in ("recipes", "meal_plans", "shopping_lists", "feedback", "kb_insights_cache"):
                conn.execute(f"DELETE FROM {table}")

    def is_empty(self) -> bool:
        return self.get_profile() is None and not self.list_pantry()

    def save_pantry_item(self, item: PantryItem) -> None:
        payload = item.model_dump(mode="json")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO pantry_items (id, data, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at
                """,
                (item.id, json.dumps(payload), _utc_now()),
            )

    def delete_pantry_item(self, item_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM pantry_items WHERE id = ?", (item_id,))

    def list_pantry(self) -> list[PantryItem]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT data FROM pantry_items ORDER BY updated_at DESC"
            ).fetchall()
        return [PantryItem.model_validate(json.loads(r["data"])) for r in rows]

    def save_recipes(self, recipes: list[Recipe]) -> None:
        with self._connect() as conn:
            for recipe in recipes:
                conn.execute(
                    """
                    INSERT INTO recipes (id, data, created_at) VALUES (?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET data=excluded.data
                    """,
                    (recipe.id, json.dumps(recipe.model_dump(mode="json")), _utc_now()),
                )

    def list_recipes(self, limit: int = 20) -> list[Recipe]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT data FROM recipes ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [Recipe.model_validate(json.loads(r["data"])) for r in rows]

    def save_meal_plan(self, plan: WeeklyMealPlan) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO meal_plans (id, data, created_at) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET data=excluded.data
                """,
                (plan.id, json.dumps(plan.model_dump(mode="json")), _utc_now()),
            )

    def get_latest_meal_plan(self) -> WeeklyMealPlan | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data FROM meal_plans ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        if not row:
            return None
        return WeeklyMealPlan.model_validate(json.loads(row["data"]))

    def save_shopping_list(self, shopping: ShoppingList) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO shopping_lists (id, data, created_at) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET data=excluded.data
                """,
                (shopping.id, json.dumps(shopping.model_dump(mode="json")), _utc_now()),
            )

    def get_latest_shopping_list(self) -> ShoppingList | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data FROM shopping_lists ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        if not row:
            return None
        return ShoppingList.model_validate(json.loads(row["data"]))

    def save_feedback(self, record: FeedbackRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO feedback (id, data, created_at) VALUES (?, ?, ?)",
                (record.id, json.dumps(record.model_dump(mode="json")), _utc_now()),
            )

    def list_feedback(self, limit: int = 50) -> list[FeedbackRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT data FROM feedback ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [FeedbackRecord.model_validate(json.loads(r["data"])) for r in rows]

    def get_disliked_recipe_names(self) -> set[str]:
        names: set[str] = set()
        for fb in self.list_feedback():
            if fb.not_suitable or fb.rating <= 2:
                names.add(fb.recipe_name.lower())
        return names

    def save_kb_insights(self, insights: list[KBInsight]) -> None:
        payload = [i.model_dump(mode="json") for i in insights]
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO kb_insights_cache (id, data, updated_at) VALUES (1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at
                """,
                (json.dumps(payload), _utc_now()),
            )

    def get_kb_insights(self) -> list[KBInsight]:
        with self._connect() as conn:
            row = conn.execute("SELECT data FROM kb_insights_cache WHERE id = 1").fetchone()
        if not row:
            return []
        return [KBInsight.model_validate(x) for x in json.loads(row["data"])]