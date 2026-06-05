can # NutriPlan AI — Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** June 05, 2026  
**Project Type:** Agentic AI Web Application (MVP)  
**Target Platform:** Local-first (FastAPI backend + premium Next.js frontend for delightful UX; easily deployable later)  
**Primary Goal:** Build a genuinely useful, agentic AI product that helps people with daily meal decisions using Grok Build.

---

## 1. Product Overview

**Product Name:** NutriPlan AI  
**Tagline:** Your intelligent kitchen companion that plans meals around what you already have.

**Problem Statement**  
Most people suffer from daily decision fatigue around "What should I cook today?". This leads to:
- Unhealthy food choices
- Food waste
- Overspending on groceries
- Repetitive boring meals
- Stress for home cooks and families

**Solution**  
An agentic AI system that:
- Understands the user’s dietary preferences, goals, allergies, and current pantry inventory
- Uses specialized AI agents to generate personalized recipes
- Creates realistic weekly meal plans
- Produces smart shopping lists
- Learns from user feedback over time

The system feels like having a personal nutritionist + chef who knows exactly what’s in your kitchen.

**Important Note on Health Scope**  
NutriPlan AI is a **meal ideation and planning tool**, not a medical, therapeutic, or clinical nutrition system. All nutrition estimates are approximations only. The product must include clear disclaimers and strict guardrails (detailed in Section 11).

---

## 11. Safety, Medical Boundaries & Edge Case Handling (Critical — Must Implement)

This section defines non-negotiable rules for agent behavior because the product touches health and nutrition.

### 11.1 Core Principle
NutriPlan AI helps with **everyday meal planning and reducing decision fatigue**. It does **not** provide:
- Medical nutrition therapy
- Treatment for any disease or condition
- Personalized advice for diagnosed medical conditions
- Exact macro/micronutrient calculations for clinical use
- Recommendations that could be harmful if followed without professional supervision

### 11.2 Mandatory Disclaimer (Must appear in UI)
Every recipe, meal plan, and shopping list must show this (or similar) disclaimer clearly:

> **Disclaimer**: This is general meal inspiration only. Nutrition information is approximate and for informational purposes. It is not a substitute for professional medical or dietary advice. If you have any medical condition, are pregnant, breastfeeding, or taking medication, please consult a qualified doctor or registered dietitian before making dietary changes.

### 11.3 Agent Behavior Rules for Risky Queries

**The agents must follow these rules strictly:**

**A. Medical Conditions (Diabetes, PCOS, Thyroid, Hypertension, Kidney, Heart, etc.)**
- Provide general, publicly known guidance only (e.g., “Many people with diabetes find lower glycemic meals helpful”).
- **Never** create “diabetic meal plans”, “PCOS reversal plans”, or “kidney-friendly therapeutic diets”.
- Always add strong disclaimer + recommend consulting their healthcare team.
- If user mentions serious conditions (kidney disease, cancer, eating disorders), politely redirect: “For conditions like this, I strongly recommend working with a registered dietitian who can create a plan tailored to your medical needs.”

**B. Pregnancy, Breastfeeding, Children under 12, Elderly (>70)**
- Give general safe suggestions only.
- Explicitly state: “This is not specialized prenatal or pediatric nutrition advice.”
- For pregnancy: Focus on common safe foods (iron-rich, easy to digest) but never claim benefits for specific pregnancy complications.
- For children: Keep suggestions family-friendly and note that growing children have different needs.

**C. Severe Allergies & Intolerances**
- **Hard rule**: Never suggest any recipe that contains a declared allergen (even in small amounts or “may contain”).
- When user declares severe allergy (nuts, dairy, gluten, shellfish, etc.), the InventoryAgent and RecipeCreator must filter strictly.
- If conflict arises (user wants something + has allergy to key ingredient), clearly explain the conflict and offer alternatives.

**D. Aggressive Weight Loss or Extreme Diets**
- Do not support plans promising rapid weight loss (>1 kg/week) or very low calorie diets (<1200 kcal/day for women, <1500 for men) without strong caution.
- For keto, carnivore, or OMAD-style requests: Provide options but clearly state potential risks and that these are not suitable for everyone.
- Never encourage disordered eating patterns.

**E. Medication Interactions**
- If user mentions medications (especially blood thinners, diabetes meds, thyroid meds, etc.), do **not** give specific food-medication advice.
- Response: “Certain foods can interact with medications. Please check with your doctor or pharmacist for personalized guidance.”

**F. Nutrition Numbers & “Is this healthy?” Questions**
- All calorie, protein, carb, fat numbers must be labeled as **“Approximate estimates only”**.
- Never present them as precise or suitable for clinical tracking (e.g., exact insulin dosing).
- For “Is X healthy?” questions: Give balanced, evidence-based general view + context that health is individual.

**G. Conflicting or Complex Family Requests**
- When multiple restrictions exist (e.g., diabetic father + nut-allergic child + weight loss goal for mother), the MealPlanner should create a practical compromise plan and clearly highlight compromises made.
- If too many conflicting constraints make planning impossible, the agent should say so honestly and suggest simplifying.

### 11.4 UI & System Safeguards (Must Build)
- Add a “Health Profile” section in onboarding with clear options: “I have a medical condition”, “I am pregnant/breastfeeding”, “I am cooking for children/elderly”.
- When these flags are set, show extra prominent disclaimers.
- Allow users to mark recipes as “Not suitable for me” with reason.
- Never auto-generate plans for users who have selected serious medical flags without extra confirmation step.
- In RecipeCreator and MealPlanner agents, implement rule-based filters + LLM instructions that enforce the above boundaries.

### 11.5 What the System Must Never Do
- Claim that any meal or plan can “treat”, “cure”, “reverse”, or “manage” any disease.
- Give exact personalized macro targets for medical conditions (e.g., “You need exactly 45g protein and 120g carbs daily”).
- Suggest raw meat, unpasteurized dairy, or any potentially unsafe food practices.
- Ignore declared allergies even if the user says “it’s okay in small amounts”.
- Generate content that promotes orthorexia or obsessive healthy eating.

### 11.6 Expected Agent Responses to Risky Queries (Examples)
See the separate analysis document for 50+ sample queries and correct agent behavior. The agents must be prompted/instructed to follow the patterns shown there.

---

## 12. Updated Scope & Non-Functional Requirements

### Updated In-Scope for MVP
- All previous features + the safety guardrails defined in Section 11.
- Prominent disclaimers in UI.
- Basic health profile flags during onboarding.
- Strict allergen filtering logic.

### Out of Scope (Reinforced)
- Any form of medical nutrition therapy or disease-specific therapeutic diets.
- Exact clinical nutrition calculations.
- Advice for eating disorders, cancer, advanced kidney/liver disease, or other serious conditions.

---

## 2. Target Users

**Primary Users**
- Busy working professionals (25-45)
- Home cooks responsible for family meals
- Fitness enthusiasts tracking macros/protein
- Health-conscious individuals
- Students living independently

**Secondary Users**
- Families with mixed dietary needs (veg + non-veg)
- People following specific diets (keto, high-protein, diabetic-friendly, etc.)

**User Personas**
- Priya, 32, software engineer in Bangalore — wants healthy meals but has limited time and often wastes vegetables.
- Rahul, 28, gym-goer in Mumbai — wants high-protein meals on a budget.
- Meera, 38, mother of two in Delhi — manages mixed family preferences and wants less decision stress.

---

## 3. Product Goals & Success Metrics (MVP)

**Business / User Goals**
- Dramatically reduce daily meal decision fatigue
- Help users eat healthier while using ingredients they already own
- Make meal planning feel effortless and even enjoyable

**MVP Success Metrics**
- User can go from profile setup → weekly plan in under 6 minutes
- Average recipe relevance rating ≥ 4.3/5
- Users report “this actually understands what I have at home”
- Core flow works reliably with zero crashes in happy path
- Clean, modern UI that feels premium (not toy-like)

---

## 4. MVP Scope (What to Build First)

### In Scope (MVP — Must Have)
1. **User Profile & Preferences**
   - Dietary style (Vegetarian, Vegan, Eggetarian, Non-Veg, Jain, etc.)
   - Health goals (Weight loss, Muscle gain, Maintenance, Energy, etc.)
   - Allergies & restrictions (free text + common chips)
   - Cuisine preferences (North Indian, South Indian, Continental, etc.)
   - Spice level, cooking time preference, budget level

2. **Pantry / Inventory Management**
   - Add, edit, delete ingredients
   - Categorize (Vegetables, Proteins, Grains, Spices, Dairy, etc.)
   - Simple quantity tracking (optional for MVP)
   - “What’s expiring soon” basic view (nice-to-have)

3. **Recipe Generation Agent**
   - Generate 3–5 personalized recipe suggestions based on current inventory + preferences
   - Each recipe includes: name, ingredients with quantities, step-by-step instructions, prep/cook time, servings, estimated nutrition (protein, calories — approximate), why it fits the user

4. **Weekly Meal Planner Agent**
   - Generate a 7-day meal plan (Breakfast + Lunch + Dinner or customizable)
   - Smartly reuse leftovers and ingredients across days
   - Balance nutrition and variety
   - Respect cooking time preferences

5. **Shopping List Generator**
   - Automatically create consolidated shopping list from the weekly plan
   - Remove items already in pantry
   - Group by category (Produce, Dairy, Pantry staples, etc.)
   - Allow manual editing before finalizing

6. **Feedback & Learning Loop (Basic)**
   - Rate recipes (thumbs up/down or 1-5 stars)
   - Simple “I made this” + “How was it?” feedback
   - System remembers preferences and avoids disliked recipes in future plans

7. **Dashboard / Home Screen**
   - Quick overview: Today’s suggested meals, pantry summary, quick actions
   - Beautiful, clean, modern UI with good visual hierarchy

### Out of Scope (MVP)
- Photo upload of fridge (vision)
- Real-time grocery price integration
- Multi-user accounts or family sharing
- Advanced macro/nutrition calculation engine
- Mobile app or PWA
- Voice input
- Recipe image generation
- Export to PDF/calendar integration
- Complex medical/disease-specific diets (keep general health goals)

---

## 5. Agentic Architecture (Core of the Product)

The product must feel **agentic** — not just a simple RAG or form-filling app.

**Recommended Multi-Agent Structure (LangGraph)**

1. **ProfileManager Agent**
   - Maintains and updates user preferences and long-term memory

2. **InventoryAgent**
   - Manages pantry state and suggests what to use first

3. **RecipeCreator Agent**
   - Creative + grounded recipe generation
   - Uses structured output (Pydantic)

4. **MealPlanner Agent**
   - Plans coherent weekly schedule with leftover awareness and variety
   - Calls RecipeCreator when needed

5. **ShoppingListOptimizer Agent**
   - Consolidates ingredients, removes pantry items, suggests smart substitutions

6. **FeedbackAgent (Reflection)**
   - Processes user ratings and updates user model/preferences

**Orchestration**
- Use **LangGraph** with a supervisor or clear state graph
- Clear separation of concerns between agents
- Human-in-the-loop possible later (approve plan before generating full week)

---

## 6. Technical Stack & Standards

**Recommended Stack (Modern & Clean)**
- **Language**: Python 3.11+
- **Backend API**: FastAPI (for clean separation + premium frontend)
- **Frontend**: Next.js 15 + Tailwind + shadcn/ui (premium, modern, consumer-grade feel — see migration plan)
- **Agent Framework**: LangGraph (strongly recommended for true agentic behavior)
- **Data**: SQLite + Pydantic models (or SQLModel)
- **LLM**: Grok API (primary) + support for LiteLLM so user can switch models easily
- **Dependency Management**: `uv` (modern, fast)
- **State Management**: LangGraph checkpointer (memory) + SQLite
- **Styling**: Premium modern frontend (Next.js + Tailwind + high-quality components); backend uses FastAPI. Legacy Streamlit + custom CSS still present during transition.

**Code Quality Requirements**
- Type hints everywhere (Pydantic v2)
- Clear separation: `agents/`, `tools/`, `ui/`, `models/`, `utils/`
- Comprehensive README with setup instructions
- `.env.example` for API keys
- Error handling with user-friendly messages
- Loading states and progress indicators in UI
- Modular code — easy to extend later

---

## 7. User Flow (Happy Path)

1. First-time user → Onboarding wizard (preferences + sample pantry)
2. Dashboard shows quick summary + “Plan this week” button
3. User reviews/edits pantry if needed
4. Clicks “Generate Weekly Plan”
5. System shows plan with option to regenerate specific days or recipes
6. User can rate recipes or mark “cooked”
7. One-click “Generate Shopping List”
8. User can edit shopping list and export (copy or simple download)

---

## 8. Non-Functional Requirements

- **Privacy**: All user data stored locally (SQLite file in user folder). No data sent to servers except LLM calls.
- **Performance**: Weekly plan generation should complete in < 45 seconds on average.
- **Reliability**: Graceful degradation if LLM fails (show partial results + retry option).
- **Extensibility**: Clear architecture so future features (vision, Telegram bot, advanced nutrition) can be added easily.
- **Documentation**: Excellent README + inline comments in key agent files.

---

## 9. Future Vision (Post-MVP — For Context Only)

- Vision: Upload photo of fridge → auto-detect ingredients
- WhatsApp / Telegram bot interface
- Family sharing + collaborative planning
- Integration with smart scales or grocery delivery apps
- Advanced nutrition tracking + weekly reports
- Recipe image generation
- Community recipe sharing (opt-in)

---

## 10. Build Instructions for Grok Build

**When building this project, follow these rules:**

1. Start by proposing a clear technical plan (use Plan Mode).
2. Build in phases: First core data models + profile + pantry, then agents, then UI, then integration.
3. Prioritize clean architecture over fancy features.
4. Make the agentic nature visible and impressive (show which agent is working when possible).
5. Use modern Python practices and excellent documentation.
6. Make the UI feel premium and delightful — not basic Streamlit default.
7. Include sample data so the app is immediately usable after setup.
8. Add a “How it works” section in the UI or README explaining the agents.

---

**End of PRD**

This document is the single source of truth for building NutriPlan AI v1.0 MVP.