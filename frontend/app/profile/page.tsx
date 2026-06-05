"use client";

import React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "../../lib/api";
import type { UserProfile } from "../../lib/types";

const dietOptions = ["vegetarian", "vegan", "eggetarian", "non_veg", "jain"] as const;
const goalOptions = ["weight_loss", "muscle_gain", "maintenance", "energy", "general_health"] as const;
const spiceOptions = ["mild", "medium", "hot"] as const;
const budgetOptions = ["low", "medium", "high"] as const;

export default function ProfilePage() {
  const qc = useQueryClient();
  const { data: profile, isLoading } = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });

  const [form, setForm] = React.useState<Partial<UserProfile>>({});

  React.useEffect(() => {
    if (profile) setForm(profile);
  }, [profile]);

  const saveMut = useMutation({
    mutationFn: (p: UserProfile) => api.saveProfile(p),
    onSuccess: (p) => {
      toast.success("Profile saved. Agents will use your preferences.");
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: (e: any) => {
      if (e.message?.includes("safety")) toast.error("Safety redirect: " + (e.message || "Check medical notes"));
      else toast.error("Save failed: " + (e.message || "Unknown"));
    },
  });

  const seedDemo = useMutation({
    mutationFn: () => api.seedDemo(),
    onSuccess: () => {
      toast.success("Demo loaded");
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["pantry"] });
    },
  });
  const seedFull = useMutation({
    mutationFn: () => api.seedFull(),
    onSuccess: (d) => {
      toast.success("Full synthetic loaded");
      qc.invalidateQueries();
    },
  });

  if (isLoading) return <div className="text-sm text-[#4a635c]">Loading profile…</div>;

  const p = { ...(profile || {}), ...form } as UserProfile;

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Build a complete profile from form state (simplified for demo)
    const toSave: UserProfile = {
      id: p.id || crypto.randomUUID(),
      name: p.name || "User",
      diet_style: (p.diet_style as any) || "vegetarian",
      health_goal: (p.health_goal as any) || "maintenance",
      allergies: (p.allergies || []).filter(Boolean),
      cuisine_preferences: (p.cuisine_preferences || ["North Indian", "South Indian"]).filter(Boolean),
      spice_level: (p.spice_level as any) || "medium",
      max_cook_minutes: p.max_cook_minutes || 30,
      budget_level: (p.budget_level as any) || "medium",
      health_flags: p.health_flags || {
        has_medical_condition: false,
        medical_notes: "",
        is_pregnant_or_breastfeeding: false,
        cooking_for_children: false,
        cooking_for_elderly: false,
      },
      disliked_ingredients: p.disliked_ingredients || [],
      preferred_ingredients: p.preferred_ingredients || [],
      limit_packaged_snacks: !!p.limit_packaged_snacks,
    };
    saveMut.mutate(toSave);
  };

  const hf = p.health_flags || ({} as any);

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="section-header">Profile &amp; onboarding</h1>
        <p className="text-[#4a635c]">Tell NutriPlan about your diet, goals, allergies and household so the agents can plan perfectly for you.</p>
      </div>

      <div className="flex gap-3">
        <button onClick={() => seedDemo.mutate()} className="btn btn-secondary" disabled={seedDemo.isPending}>
          Load demo data (small)
        </button>
        <button onClick={() => seedFull.mutate()} className="btn btn-secondary" disabled={seedFull.isPending}>
          Load full synthetic database
        </button>
      </div>

      <form onSubmit={onSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium block mb-1">Name</label>
            <input value={p.name || ""} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Diet style</label>
            <select value={p.diet_style} onChange={(e) => setForm({ ...form, diet_style: e.target.value as any })} className="w-full">
              {dietOptions.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Health goal</label>
            <select value={p.health_goal} onChange={(e) => setForm({ ...form, health_goal: e.target.value as any })} className="w-full">
              {goalOptions.map((g) => <option key={g} value={g}>{g.replace("_", " ")}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Spice level</label>
            <select value={p.spice_level} onChange={(e) => setForm({ ...form, spice_level: e.target.value as any })} className="w-full">
              {spiceOptions.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium block mb-1">Allergies (comma separated)</label>
          <input value={(p.allergies || []).join(", ")} onChange={(e) => setForm({ ...form, allergies: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })} className="w-full" />
        </div>
        <div>
          <label className="text-sm font-medium block mb-1">Cuisine preferences</label>
          <input value={(p.cuisine_preferences || []).join(", ")} onChange={(e) => setForm({ ...form, cuisine_preferences: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })} className="w-full" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium block mb-1">Max cook time (min)</label>
            <input type="number" value={p.max_cook_minutes || 30} onChange={(e) => setForm({ ...form, max_cook_minutes: parseInt(e.target.value) || 30 })} className="w-full" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Budget</label>
            <select value={p.budget_level} onChange={(e) => setForm({ ...form, budget_level: e.target.value as any })} className="w-full">
              {budgetOptions.map((b) => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>
        </div>

        <div>
          <div className="font-medium mb-2">Health profile (important for safety)</div>
          <div className="space-y-2 text-sm">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={hf.has_medical_condition} onChange={(e) => setForm({ ...form, health_flags: { ...(hf as any), has_medical_condition: e.target.checked } })} />
              I have a medical condition
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={hf.is_pregnant_or_breastfeeding} onChange={(e) => setForm({ ...form, health_flags: { ...(hf as any), is_pregnant_or_breastfeeding: e.target.checked } })} />
              Pregnant / breastfeeding
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={hf.cooking_for_children} onChange={(e) => setForm({ ...form, health_flags: { ...(hf as any), cooking_for_children: e.target.checked } })} />
              Cooking for children under 12
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={hf.cooking_for_elderly} onChange={(e) => setForm({ ...form, health_flags: { ...(hf as any), cooking_for_elderly: e.target.checked } })} />
              Cooking for elderly (70+)
            </label>
            <textarea placeholder="Medical notes (not used for therapy)" value={hf.medical_notes || ""} onChange={(e) => setForm({ ...form, health_flags: { ...(hf as any), medical_notes: e.target.value } })} className="w-full mt-1" rows={2} />
          </div>
          { (hf.has_medical_condition || hf.is_pregnant_or_breastfeeding || hf.cooking_for_children || hf.cooking_for_elderly) && (
            <div className="disclaimer-box mt-3">You indicated a health-sensitive situation. NutriPlan provides general meal ideas only — not medical advice.</div>
          )}
        </div>

        <button type="submit" className="btn btn-primary" disabled={saveMut.isPending}>
          {saveMut.isPending ? "Saving..." : "Save profile"}
        </button>
      </form>

      <div className="disclaimer-box">This is general meal inspiration only. Nutrition information is approximate and for informational purposes. It is not a substitute for professional medical or dietary advice.</div>
    </div>
  );
}
