// Lightweight TypeScript mirrors of backend Pydantic models (src/nutriplan/models/schemas.py)
// Keep in sync manually or later auto-generate from /api/openapi.json

export type DietStyle = "vegetarian" | "vegan" | "eggetarian" | "non_veg" | "jain";
export type HealthGoal = "weight_loss" | "muscle_gain" | "maintenance" | "energy" | "general_health";
export type SpiceLevel = "mild" | "medium" | "hot";
export type BudgetLevel = "low" | "medium" | "high";

export interface HealthFlags {
  has_medical_condition: boolean;
  medical_notes: string;
  is_pregnant_or_breastfeeding: boolean;
  cooking_for_children: boolean;
  cooking_for_elderly: boolean;
  requires_plan_confirmation?: boolean;
}

export interface UserProfile {
  id: string;
  name: string;
  diet_style: DietStyle;
  health_goal: HealthGoal;
  allergies: string[];
  cuisine_preferences: string[];
  spice_level: SpiceLevel;
  max_cook_minutes: number;
  budget_level: BudgetLevel;
  health_flags: HealthFlags;
  disliked_ingredients: string[];
  preferred_ingredients: string[];
  limit_packaged_snacks: boolean;
}

export interface PantryItem {
  id: string;
  name: string;
  category: string;
  quantity: string;
  expiry_date?: string | null;
  is_packaged: boolean;
}

export interface NutritionEstimate {
  calories?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  label: string;
}

export interface IngredientLine {
  name: string;
  quantity: string;
}

export interface Recipe {
  id: string;
  name: string;
  ingredients: IngredientLine[];
  steps: string[];
  prep_minutes: number;
  cook_minutes: number;
  servings: number;
  nutrition: NutritionEstimate;
  why_fits: string;
  kb_notes?: string;
  disclaimer: string;
  cuisine_tags: string[];
  contains_allergens: string[];
}

export interface MealSlot {
  slot: "breakfast" | "lunch" | "dinner" | "snack";
  recipe_name: string;
  recipe_id?: string | null;
  notes: string;
  uses_leftovers_from?: string | null;
}

export interface DayMeals {
  day_index: number;
  day_label: string;
  meals: MealSlot[];
}

export interface WeeklyMealPlan {
  id: string;
  days: DayMeals[];
  variety_notes: string;
  leftover_strategy: string;
  compromises: string;
  disclaimer: string;
}

export interface ShoppingListItem {
  name: string;
  category: string;
  quantity: string;
  in_pantry: boolean;
  suggested_swap?: string | null;
}

export interface ShoppingList {
  id: string;
  items: ShoppingListItem[];
  disclaimer: string;
}

export interface FeedbackRecord {
  id: string;
  recipe_id: string;
  recipe_name: string;
  rating: number;
  cooked: boolean;
  not_suitable: boolean;
  reason: string;
}

export interface KBInsight {
  pantry_item: string;
  concerns: string[];
  gentle_message: string;
  alternatives?: any[];
}

export interface SafetyResult {
  action: "allow" | "redirect" | "require_confirmation";
  message: string;
  category: string;
}

export interface SystemStatus {
  llm_available: boolean;
  provider: string;
  ollama_running: boolean;
  current_agent?: string;
}
