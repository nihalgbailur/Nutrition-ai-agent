CREATE TABLE IF NOT EXISTS user_profile (
    id TEXT PRIMARY KEY,
    data JSON NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pantry_items (
    id TEXT PRIMARY KEY,
    data JSON NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    data JSON NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meal_plans (
    id TEXT PRIMARY KEY,
    data JSON NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shopping_lists (
    id TEXT PRIMARY KEY,
    data JSON NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    data JSON NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kb_insights_cache (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data JSON NOT NULL,
    updated_at TEXT NOT NULL
);