#!/usr/bin/env python3
"""Load synthetic JSON data into data/nutriplan.db (no SQLite app required)."""

from nutriplan.db.repository import Repository
from nutriplan.utils.seed import load_demo_data, load_synthetic_database


def main() -> None:
    repo = Repository()
    counts = load_synthetic_database(repo)
    print(f"Database ready: {repo.db_path}")
    print(f"  Profile: {repo.get_profile().name}")
    print(f"  Pantry items: {len(repo.list_pantry())}")
    print(f"  Recipes: {len(repo.list_recipes())}")
    print(f"  Meal plan days: {len(repo.get_latest_meal_plan().days)}")
    print(f"  KB insights: {len(repo.get_kb_insights())}")
    print("Details:", counts)


if __name__ == "__main__":
    main()