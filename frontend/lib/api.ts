import type {
  FeedbackRecord,
  PantryItem,
  Recipe,
  ShoppingList,
  SystemStatus,
  UserProfile,
  WeeklyMealPlan,
} from "./types";

// When running with next dev + rewrites, use relative /api so it proxies to backend automatically.
// Override with NEXT_PUBLIC_API_URL only if you run the frontend against a remote/deployed API.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    // credentials not needed for local
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail?.message || err?.message || `API error ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Profile
  getProfile: () => fetchJSON<UserProfile | null>("/api/profile"),
  saveProfile: (profile: UserProfile) =>
    fetchJSON<UserProfile>("/api/profile", { method: "POST", body: JSON.stringify(profile) }),

  // Pantry
  listPantry: () => fetchJSON<PantryItem[]>("/api/pantry"),
  addPantry: (item: Omit<PantryItem, "id">) =>
    fetchJSON<PantryItem>("/api/pantry", { method: "POST", body: JSON.stringify(item) }),
  deletePantry: (id: string) => fetchJSON<{ ok: boolean }>(`/api/pantry/${id}`, { method: "DELETE" }),
  syncPantry: () => fetchJSON<{ pantry: PantryItem[]; kb_insights: any[] }>("/api/pantry/sync", { method: "POST" }),

  // Recipes
  listRecipes: () => fetchJSON<Recipe[]>("/api/recipes"),
  generateRecipes: (query: string = "") =>
    fetchJSON<{ recipes: Recipe[]; used_fallback?: boolean; active_agent?: string }>(
      "/api/recipes/generate",
      { method: "POST", body: JSON.stringify({ query }) }
    ),

  // Plan
  getPlan: () => fetchJSON<WeeklyMealPlan | null>("/api/plan"),
  generatePlan: (confirmed: boolean = false) =>
    fetchJSON<any>("/api/plan/generate", {
      method: "POST",
      body: JSON.stringify({ confirmed }),
    }),

  // Shopping
  getShopping: () => fetchJSON<ShoppingList | null>("/api/shopping"),
  generateShopping: () => fetchJSON<any>("/api/shopping/generate", { method: "POST" }),

  // Feedback
  listFeedback: (limit = 20) => fetchJSON<FeedbackRecord[]>(`/api/feedback?limit=${limit}`),
  submitFeedback: (record: Omit<FeedbackRecord, "id">) =>
    fetchJSON<any>("/api/feedback", { method: "POST", body: JSON.stringify(record) }),

  // System
  getStatus: () => fetchJSON<SystemStatus>("/api/system/status"),
  seedDemo: () => fetchJSON<any>("/api/system/seed/demo", { method: "POST" }),
  seedFull: () => fetchJSON<any>("/api/system/seed/full", { method: "POST" }),

  // Chat streaming uses EventSource (see useChat hook or components)
  chatOnce: (message: string, fast_mode = false) =>
    fetchJSON<{ agent: string; text: string }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, fast_mode }),
    }),
};

export { API_BASE };
