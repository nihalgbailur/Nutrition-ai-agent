"use client";

import React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api } from "../../lib/api";
import type { PantryItem } from "../../lib/types";

export default function PantryPage() {
  const qc = useQueryClient();
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });
  const { data: pantry = [], isLoading } = useQuery({ queryKey: ["pantry"], queryFn: api.listPantry });
  const [insights, setInsights] = React.useState<any[]>([]);

  const [newItem, setNewItem] = React.useState({ name: "", category: "Vegetables", quantity: "", is_packaged: false });

  const addMut = useMutation({
    mutationFn: () => api.addPantry(newItem as any),
    onSuccess: () => {
      toast.success("Item added");
      setNewItem({ name: "", category: "Vegetables", quantity: "", is_packaged: false });
      qc.invalidateQueries({ queryKey: ["pantry"] });
    },
  });

  const delMut = useMutation({
    mutationFn: (id: string) => api.deletePantry(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pantry"] }),
  });

  const syncMut = useMutation({
    mutationFn: () => api.syncPantry(),
    onSuccess: (res) => {
      toast.success("Pantry synced with knowledge base");
      qc.invalidateQueries({ queryKey: ["pantry"] });
      setInsights(res.kb_insights || []);
    },
  });

  if (!profile) {
    return <div className="text-sm">Set up your <a href="/profile" className="underline">profile</a> first.</div>;
  }

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex gap-5 items-end">
        <div className="flex-1">
          <h1 className="section-header">Pantry / inventory</h1>
          <p className="text-[#4a635c]">Add what you have. Run the InventoryAgent to get smart insights on packaged items and usage priority.</p>
        </div>
        <img src="/images/spices-dark.jpg" alt="Rich spices for Indian pantry" className="w-36 h-24 object-cover rounded-2xl border border-[var(--np-border)] hidden md:block" />
      </div>

      <div className="card">
        <div className="font-medium mb-3">Add item</div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input placeholder="Ingredient name" value={newItem.name} onChange={e => setNewItem({ ...newItem, name: e.target.value })} />
          <select value={newItem.category} onChange={e => setNewItem({ ...newItem, category: e.target.value })}>
            {["Vegetables", "Proteins", "Grains", "Dairy", "Spices", "Packaged", "Pantry", "Other"].map(c => <option key={c}>{c}</option>)}
          </select>
          <input placeholder="Quantity e.g. 500g" value={newItem.quantity} onChange={e => setNewItem({ ...newItem, quantity: e.target.value })} />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={newItem.is_packaged} onChange={e => setNewItem({ ...newItem, is_packaged: e.target.checked })} /> Packaged
          </label>
        </div>
        <button onClick={() => addMut.mutate()} disabled={!newItem.name || addMut.isPending} className="btn btn-primary mt-3">Add to pantry</button>
      </div>

      <button onClick={() => syncMut.mutate()} disabled={syncMut.isPending} className="btn btn-secondary">Run InventoryAgent (scan + prioritize + KB insights)</button>

      <div className="space-y-3">
        {isLoading && <div className="text-sm">Loading pantry…</div>}
        {pantry.length === 0 && <div className="text-sm text-[#4a635c]">Your pantry is empty. Add items above or load demo data from Profile.</div>}

        {pantry.map((item: PantryItem, index: number) => (
          <motion.div 
            key={item.id} 
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(index * 0.025, 0.3) }}
            className="card flex items-center justify-between py-3"
          >
            <div>
              <span className="font-medium">{item.name}</span>
              <span className="text-xs text-[#4a635c] ml-2">• {item.category}</span>
              {item.quantity && <span className="ml-2 text-sm text-[#4a635c]">{item.quantity}</span>}
              {item.is_packaged && <span className="kb-badge ml-2">packaged</span>}
            </div>
            <button onClick={() => delMut.mutate(item.id)} className="text-xs text-red-600 hover:underline">Delete</button>
          </motion.div>
        ))}
      </div>

      {insights && insights.length > 0 && (
        <div>
          <div className="font-medium mb-2">Packaged food insights</div>
          {insights.slice(0, 6).map((ins: any, idx: number) => (
            <div key={idx} className="card text-sm mb-2">{ins.gentle_message}</div>
          ))}
        </div>
      )}

      <div className="disclaimer-box">Allergen filtering and safety rules are always applied by the agents. KB insights are gentle suggestions only.</div>
    </div>
  );
}
