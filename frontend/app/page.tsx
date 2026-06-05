"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { Leaf, ArrowRight, Play } from "lucide-react";

export default function HomePage() {
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });
  const { data: pantry } = useQuery({ queryKey: ["pantry"], queryFn: api.listPantry });
  const { data: recipes } = useQuery({ queryKey: ["recipes"], queryFn: api.listRecipes });
  const { data: plan } = useQuery({ queryKey: ["plan"], queryFn: api.getPlan });
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: api.getStatus, refetchInterval: 30000 });

  const pantryCount = pantry?.length ?? 0;
  const recipeCount = recipes?.length ?? 0;
  const planDays = plan?.days?.length ?? 0;

  // Simple rich animated counters
  const [displayPantry, setDisplayPantry] = React.useState(0);
  const [displayRecipes, setDisplayRecipes] = React.useState(0);

  React.useEffect(() => {
    const animate = (target: number, setter: (n: number) => void) => {
      let start = 0;
      const step = Math.max(1, Math.floor(target / 20));
      const iv = setInterval(() => {
        start += step;
        if (start >= target) {
          setter(target);
          clearInterval(iv);
        } else {
          setter(start);
        }
      }, 60);
    };
    if (pantryCount > 0) animate(pantryCount, setDisplayPantry);
    if (recipeCount > 0) animate(recipeCount, setDisplayRecipes);
  }, [pantryCount, recipeCount]);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Beautiful premium hero with video + image */}
      <div className="relative overflow-hidden rounded-3xl border border-[#e2ebe6] bg-white shadow-sm">
        <div className="grid md:grid-cols-5 gap-0">
          {/* Left: Text + CTAs (animated) */}
          <div className="md:col-span-3 p-8 md:p-10 flex flex-col justify-center">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-9 w-9 rounded-2xl bg-[#1a3c34] flex items-center justify-center">
                <Leaf className="h-5 w-5 text-white" />
              </div>
              <div className="uppercase tracking-[3px] text-xs text-[#1a3c34]/70 font-medium">NutriPlan AI</div>
            </div>

            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="text-5xl md:text-6xl font-semibold tracking-[-0.04em] text-[#1a3c34] leading-[0.95] mb-4"
            >
              Plans meals<br />around what<br />you already have.
            </motion.h1>

            <motion.p 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.6 }}
              className="text-xl text-[#4a635c] max-w-md mb-8"
            >
              Your intelligent kitchen companion. Personalized. Safe. Delicious. Powered by specialized agents.
            </motion.p>

            <div className="flex flex-wrap gap-3">
              <a href="/profile" className="btn btn-primary group flex items-center gap-2 px-7">
                Get started <ArrowRight className="group-hover:translate-x-0.5 transition" />
              </a>
              <a href="/chat" className="btn btn-secondary flex items-center gap-2">
                <Play className="h-4 w-4" /> Try the chat
              </a>
            </div>

            <div className="mt-6 text-xs text-[#4a635c]/80">
              100% local • No medical advice • Strict allergen filtering
            </div>
          </div>

          {/* Right: Video + beautiful image overlay */}
          <div className="md:col-span-2 relative bg-[#1a3c34] min-h-[320px] md:min-h-[420px] flex items-center justify-center overflow-hidden rounded-r-3xl md:rounded-l-none rounded-l-3xl">
            <video
              className="absolute inset-0 w-full h-full object-cover opacity-90"
              src="/videos/hero-dal-steam.mp4"
              poster="/images/hero-kitchen.jpg"
              autoPlay
              loop
              muted
              playsInline
            />
            
            {/* Subtle gradient + image accent */}
            <div className="absolute inset-0 bg-gradient-to-r from-[#1a3c34]/70 via-[#1a3c34]/30 to-transparent" />
            
            <div className="relative z-10 p-6 text-right text-white/95 max-w-[210px] ml-auto mr-4">
              <div className="uppercase text-[10px] tracking-[2px] mb-1 opacity-75">Fresh from your kitchen</div>
              <div className="text-2xl font-semibold leading-tight tracking-tight">Real ingredients.<br />Real flavor.<br />Zero waste.</div>
            </div>

            {/* Small beautiful still as decorative corner accent */}
            <img 
              src="/images/dal-makhani.jpg" 
              alt="Rich Dal Makhani" 
              className="absolute bottom-4 right-4 w-24 h-24 object-cover rounded-2xl border-2 border-white/70 shadow-xl hidden lg:block" 
            />
          </div>
        </div>
      </div>

      {/* Metrics row - with subtle entrance animation */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Pantry items", value: displayPantry },
          { label: "Saved recipes", value: displayRecipes },
          { label: "Current plan", value: planDays ? `${planDays}-day` : "—" },
          { label: "LLM", value: status?.provider || "Checking...", sub: status?.ollama_running ? "Ollama local" : status?.llm_available ? "Cloud" : "Fallback mode" },
        ].map((m, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 * idx, duration: 0.4 }}
            className="metric hover:-translate-y-px transition-transform"
          >
            <div className="text-xs uppercase tracking-widest text-[#4a635c]">{m.label}</div>
            <div className="text-4xl font-semibold text-[#1a3c34] mt-1 tracking-tight">{m.value}</div>
            {m.sub && <div className="text-[10px] text-[#4a635c] mt-0.5">{m.sub}</div>}
          </motion.div>
        ))}
      </div>

      {/* Today's preview */}
      {plan?.days?.[0] && (
        <div className="card">
          <div className="text-sm font-medium text-[#4a635c] mb-3">TODAY'S PLAN PREVIEW</div>
          <div className="space-y-2">
            {plan.days[0].meals.map((m, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="font-medium capitalize">{m.slot}</span>
                <span>{m.recipe_name}</span>
                {m.uses_leftovers_from && <span className="text-xs text-[#4a635c]">leftovers</span>}
              </div>
            ))}
          </div>
          <div className="mt-4 text-xs text-[#4a635c]">
            Go to <span className="font-medium text-[#1a3c34]">Weekly Plan</span> for the full schedule.
          </div>
        </div>
      )}

      <div className="card bg-white">
        <div className="font-medium mb-2">Quick start</div>
        <ol className="text-sm space-y-1 text-[#4a635c] list-decimal pl-5">
          <li>Visit <strong>Profile</strong> and load demo data (or full synthetic).</li>
          <li>Review &amp; enrich your <strong>Pantry</strong> — run InventoryAgent for KB insights.</li>
          <li>Generate <strong>Recipes</strong> or a full <strong>Weekly Plan</strong>.</li>
          <li>Use <strong>Chat</strong> for quick ideas and packaged food swaps.</li>
        </ol>
        <div className="mt-3 text-xs">
          All data stays on your machine in <code>data/nutriplan.db</code>. Only LLM calls leave when configured.
        </div>
      </div>

      {/* Visual inspiration strip using our beautiful generated food imagery */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="text-sm font-medium text-[#1a3c34]">Inspiration from real Indian kitchens</div>
          <a href="/recipes" className="text-xs text-[#1a3c34] hover:underline flex items-center gap-1">Browse recipes <ArrowRight size={14} /></a>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { src: "/images/palak-paneer.jpg", label: "Palak Paneer" },
            { src: "/images/dal-makhani.jpg", label: "Dal Makhani" },
            { src: "/images/samosas.jpg", label: "Crispy Samosas" },
            { src: "/images/aloo-paratha.jpg", label: "Aloo Paratha" },
            { src: "/images/veg-pulao.jpg", label: "Vegetable Pulao" },
            { src: "/images/indian-thali.jpg", label: "Home Thali" },
          ].map((item, i) => (
            <motion.a 
              key={i} 
              href="/recipes" 
              whileHover={{ scale: 1.01 }} 
              className="group block overflow-hidden rounded-2xl border border-[#e2ebe6] bg-white"
            >
              <div className="relative aspect-[4/3] overflow-hidden">
                <img 
                  src={item.src} 
                  alt={item.label} 
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.06]" 
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
                  <div className="text-white text-sm font-medium tracking-tight">{item.label}</div>
                </div>
              </div>
            </motion.a>
          ))}
        </div>
      </div>

      <div className="text-xs text-[#4a635c] text-center pt-2">
        Premium frontend • {status?.provider ? `Connected to ${status.provider}` : "Local mode"} • Safety guardrails always on.
      </div>
    </div>
  );
}
