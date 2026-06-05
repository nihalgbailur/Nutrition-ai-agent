"use client";

import React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "../../lib/api";

export default function FeedbackPage() {
  const qc = useQueryClient();
  const { data: recipes = [] } = useQuery({ queryKey: ["recipes"], queryFn: api.listRecipes });
  const { data: recent = [] } = useQuery({ queryKey: ["feedback"], queryFn: () => api.listFeedback(8) });

  const [selected, setSelected] = React.useState<any>(null);
  const [rating, setRating] = React.useState(4);
  const [cooked, setCooked] = React.useState(false);
  const [notSuitable, setNotSuitable] = React.useState(false);
  const [reason, setReason] = React.useState("");

  const submitMut = useMutation({
    mutationFn: () => api.submitFeedback({
      recipe_id: selected?.id || "",
      recipe_name: selected?.name || "",
      rating,
      cooked,
      not_suitable: notSuitable,
      reason,
    } as any),
    onSuccess: () => {
      toast.success("Thanks — future plans will learn from this.");
      setReason("");
      qc.invalidateQueries({ queryKey: ["feedback"] });
    },
  });

  if (recipes.length === 0) return <div className="text-sm">Generate some recipes first, then come back to leave feedback.</div>;

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="section-header">Feedback &amp; learning</h1>

      <div>
        <label className="text-sm font-medium block mb-1">Recipe</label>
        <select onChange={(e) => setSelected(recipes.find((r: any) => r.id === e.target.value) || recipes[0])} className="w-full">
          {recipes.map((r: any) => <option key={r.id} value={r.id}>{r.name}</option>)}
        </select>
      </div>

      <div>
        <label className="text-sm font-medium">Rating: {rating}/5</label>
        <input type="range" min={1} max={5} value={rating} onChange={(e) => setRating(parseInt(e.target.value))} className="w-full" />
      </div>

      <div className="flex gap-6 text-sm">
        <label><input type="checkbox" checked={cooked} onChange={e => setCooked(e.target.checked)} /> I made this</label>
        <label><input type="checkbox" checked={notSuitable} onChange={e => setNotSuitable(e.target.checked)} /> Not suitable for me</label>
      </div>

      <input value={reason} onChange={e => setReason(e.target.value)} placeholder="Reason (optional)" className="w-full" />

      <button onClick={() => submitMut.mutate()} disabled={!selected || submitMut.isPending} className="btn btn-primary">Submit feedback</button>

      {recent.length > 0 && (
        <div>
          <div className="font-medium mb-2">Recent feedback</div>
          {recent.map((fb: any, i: number) => (
            <div key={i} className="text-sm text-[#4a635c]">{fb.recipe_name}: {fb.rating}/5 {fb.cooked ? "cooked" : ""} {fb.not_suitable ? "not suitable" : ""}</div>
          ))}
        </div>
      )}
    </div>
  );
}
