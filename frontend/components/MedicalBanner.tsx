"use client";
import type { UserProfile } from "../lib/types";

export function MedicalBanner({ profile }: { profile?: UserProfile | null }) {
  if (!profile) return null;
  const f = profile.health_flags;
  const needs = f?.has_medical_condition || f?.is_pregnant_or_breastfeeding || f?.cooking_for_children || f?.cooking_for_elderly;
  if (!needs) return null;
  return (
    <div className="mb-4 rounded-xl border-l-4 border-[#e6a817] bg-[#fff8e6] p-3 text-sm text-[#5c4a1a]">
      You indicated a health-sensitive situation. NutriPlan AI provides general meal ideas only — not medical or specialized nutrition advice.
    </div>
  );
}
