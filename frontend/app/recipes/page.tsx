"use client";

import React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { api } from "../../lib/api";
import { AgentPill } from "../../components/AgentPill";
import { Disclaimer } from "../../components/Disclaimer";

const dishImages = [
  "/images/palak-paneer.jpg",
  "/images/dal-makhani.jpg",
  "/images/samosas.jpg",
  "/images/aloo-paratha.jpg",
  "/images/veg-pulao.jpg",
  "/images/indian-thali.jpg",
  "/images/khichdi-bowl.jpg",
];

function getDishImage(name: string) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) | 0;
  return dishImages[Math.abs(hash) % dishImages.length];
}

export default function RecipesPage() {
  const qc = useQueryClient();
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });
  const { data: recipes = [] } = useQuery({ queryKey: ["recipes"], queryFn: api.listRecipes });

  const [query, setQuery] = React.useState("");
  const [expanded, setExpanded] = React.useState<string | null>(null);

  const genMut = useMutation({
    mutationFn: () => api.generateRecipes(query),
    onSuccess: (res) => {
      toast.success(`Generated ${res.recipes?.length || 0} recipes`);
      if (res.used_fallback) toast.warning("Using fallback templates (no LLM)");
      qc.invalidateQueries({ queryKey: ["recipes"] });
    },
    onError: (e: any) => toast.error(e.message || "Generation failed"),
  });

  if (!profile) return <div>Set up your profile first.</div>;

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="section-header">Recipe suggestions</h1>
        <p className="text-[#4a635c]">Personalized to your pantry, preferences, and safety rules.</p>
      </div>

      <div className="space-y-3">
        <div className="flex gap-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Optional: quick dinner, high protein, etc."
            className="flex-1"
          />
          <button onClick={() => genMut.mutate()} disabled={genMut.isPending} className="btn btn-primary min-w-[220px]">
            {genMut.isPending ? "Working with agents..." : "Generate recipes (RecipeCreator)"}
          </button>
        </div>

        {genMut.isPending && (
          <motion.div 
            initial={{ opacity: 0.6 }}
            animate={{ opacity: 1 }}
            className="card bg-white border-[#e2ebe6]"
          >
            <div className="text-sm font-medium mb-2 text-[#1a3c34]">Agent pipeline running…</div>
            <div className="space-y-1 text-sm">
              <div className="agent-step done">✓ InventoryAgent — scanning pantry + KB</div>
              <motion.div animate={{ scale: [1, 1.015, 1] }} transition={{ duration: 1.6, repeat: Infinity }} className="agent-step active">⟳ RecipeCreator — creating personalized recipes + safety filters</motion.div>
              <div className="agent-step">… Finalizing nutrition estimates + disclaimers</div>
            </div>
            <div className="text-[10px] text-[#4a635c] mt-2">First run with Ollama can take 20–60s while the model loads.</div>
          </motion.div>
        )}
      </div>

      <div className="grid gap-4">
        {recipes.length === 0 && <div className="text-sm text-[#4a635c]">No recipes yet. Generate some above.</div>}

        {recipes.map((r: any, idx: number) => {
          const open = expanded === r.id;
          const img = getDishImage(r.name);
          return (
            <motion.div 
              key={r.id} 
              className="card overflow-hidden p-0"
              whileHover={{ y: -2 }}
              transition={{ type: "spring", stiffness: 260, damping: 24 }}
            >
              <button className="w-full text-left p-5" onClick={() => setExpanded(open ? null : r.id)}>
                <div className="flex gap-4">
                  {/* Beautiful food image thumbnail */}
                  <div className="w-20 h-20 flex-shrink-0 overflow-hidden rounded-2xl border border-[#e2ebe6]">
                    <img src={img} alt={r.name} className="w-full h-full object-cover" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-semibold text-lg leading-tight pr-2">{r.name}</div>
                      <AgentPill name="RecipeCreator" />
                    </div>
                    <div className="text-sm text-[#4a635c] line-clamp-2 mt-1">{r.why_fits}</div>

                    <div className="mt-2.5 flex flex-wrap gap-2">
                      <span className="nutrition-tag">~{r.nutrition?.calories || "?"} kcal</span>
                      <span className="nutrition-tag">Protein ~{r.nutrition?.protein_g || "?"}g</span>
                      <span className="text-xs text-[#4a635c] self-center">{r.prep_minutes + r.cook_minutes} min • {r.servings} servings</span>
                    </div>
                  </div>
                </div>
              </button>

              <AnimatePresence>
                {open && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
                    className="overflow-hidden"
                  >
                    <div className="px-5 pb-5 pt-1 border-t border-[#e2ebe6] text-sm space-y-3 bg-[#f7faf8]">
                      <div className="pt-2">
                        <div className="font-medium mb-1">Ingredients</div>
                        <div className="text-[#4a635c]">{r.ingredients?.map((i: any) => `${i.name} (${i.quantity})`).join(" • ")}</div>
                      </div>
                      <div>
                        <div className="font-medium mb-1">Steps</div>
                        <ol className="list-decimal pl-5 space-y-1 text-[#4a635c]">
                          {r.steps?.map((s: string, i: number) => <li key={i}>{s}</li>)}
                        </ol>
                      </div>
                      {r.kb_notes && <div className="kb-badge inline-block">KB: {r.kb_notes}</div>}
                      <Disclaimer text={r.disclaimer} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
