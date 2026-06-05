"use client";

import React from "react";
import { motion } from "framer-motion";
import { Disclaimer } from "../../components/Disclaimer";

const agents = [
  { name: "SafetyGate", role: "First filter for risky/medical queries. Enforces hard boundaries." },
  { name: "ProfileManager", role: "Stores & updates your diet style, goals, allergies, health flags." },
  { name: "InventoryAgent", role: "Scans pantry, prioritizes items, matches against Indian packaged foods KB for insights & swaps." },
  { name: "RecipeCreator", role: "Generates 4+ personalized recipes using only what you have. Applies strict allergen & safety filters." },
  { name: "MealPlanner", role: "Builds coherent 7-day B/L/D plan with leftover reuse, variety, and practical compromises." },
  { name: "ShoppingListOptimizer", role: "Consolidates missing items from the plan, removes pantry stock, suggests smart KB swaps." },
  { name: "FeedbackAgent", role: "Learns from your ratings & 'not suitable' feedback to update future preferences." },
];

export default function HowItWorks() {
  return (
    <div className="max-w-4xl space-y-8 text-sm">
      <div>
        <h1 className="section-header">How NutriPlan AI is an Agentic App</h1>
        <p className="text-[#4a635c] text-base mt-2">
          It is <strong>agentic</strong> because it doesn’t just call one LLM prompt. Instead, it uses a team of specialized AI agents that collaborate, reason step-by-step, use tools (the KB), enforce safety, and learn — all orchestrated by <strong>LangGraph</strong>.
        </p>
      </div>

      {/* Visual flow - richer with animation and imagery */}
      <div className="card overflow-hidden">
        <div className="font-medium mb-3 text-[var(--np-green)]">Typical Agent Flow (e.g. “Generate Weekly Plan”)</div>
        <div className="flex flex-wrap gap-2 text-xs mb-4">
          {["SafetyGate", "InventoryAgent", "RecipeCreator", "MealPlanner"].map((step, i) => (
            <motion.div
              key={i}
              whileHover={{ scale: 1.05, y: -1 }}
              whileTap={{ scale: 0.98 }}
              className="px-3 py-1.5 rounded-full bg-[rgba(74,143,122,0.12)] text-[var(--np-green)] border border-[var(--np-green)]/20 flex items-center gap-2"
            >
              <span className="font-mono text-[10px] opacity-60">0{i+1}</span>
              {step}
              {i < 3 && <span className="text-[var(--np-green)]/40">→</span>}
            </motion.div>
          ))}
        </div>
        <div className="relative rounded-xl overflow-hidden border border-[var(--np-border)]">
          <video 
            src="/videos/spices-pour.mp4" 
            poster="/images/spices-dark.jpg"
            className="w-full h-48 object-cover"
            autoPlay 
            loop 
            muted 
            playsInline 
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-4">
            <div className="text-white text-sm">
              The agents draw on a real Indian Packaged Foods knowledge base for smart, safe suggestions.
            </div>
          </div>
        </div>
        <div className="mt-3 text-xs text-[var(--np-text-muted)]">
          Each step can call the LLM (with structured output) or fall back to smart templates. Results are validated and persisted.
        </div>
      </div>

      {/* Agents table */}
      <div>
        <div className="font-medium mb-2">The Specialized Agents</div>
        <div className="grid gap-3">
          {agents.map((a, i) => (
            <div key={i} className="card py-3 flex gap-4 items-start">
              <div className="font-mono text-xs w-28 shrink-0 text-[#1a3c34] pt-0.5">{a.name}</div>
              <div className="text-[#4a635c]">{a.role}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <strong>Why this is more than “just an LLM”:</strong>
          <ul className="list-disc pl-5 mt-2 text-[#4a635c] space-y-1">
            <li><strong>Multi-agent collaboration</strong> — InventoryAgent’s insights directly influence what RecipeCreator and MealPlanner produce.</li>
            <li><strong>Tools &amp; Knowledge</strong> — Indian Packaged Foods KB gives agents real data on Maggi, Haldiram, etc. so they can give gentle, specific swap suggestions.</li>
            <li><strong>Deterministic safety</strong> — Allergies are filtered in code (not left to the model). SafetyGate runs before any creative work.</li>
            <li><strong>Structured + validated output</strong> — Every agent returns Pydantic models. Post-processing validators catch issues.</li>
            <li><strong>Learning loop</strong> — FeedbackAgent actually mutates your profile preferences for future runs.</li>
            <li><strong>Transparency</strong> — The UI shows exactly which agent is working (“MealPlanner building schedule…”) and the full pipeline.</li>
          </ul>
        </div>

        <div className="font-mono text-xs bg-white p-4 rounded-xl border border-[#e2ebe6]">
          Frontend (beautiful Next.js) → FastAPI → invoke_graph("generate_weekly_plan") → LangGraph StateGraph → [Safety → Inventory → RecipeCreator → MealPlanner] → DB
        </div>
      </div>

      <p className="text-[#4a635c]">
        The new premium UI makes the agentic nature <em>visible and delightful</em> — you see the agents thinking, get rich cards with real food photography, and experience smooth animations while the graph runs.
      </p>

      <Disclaimer />
    </div>
  );
}
