"use client";

import React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "../../lib/api";
import { Disclaimer } from "../../components/Disclaimer";

export default function ShoppingPage() {
  const qc = useQueryClient();
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });
  const { data: plan } = useQuery({ queryKey: ["plan"], queryFn: api.getPlan });
  const { data: shopping } = useQuery({ queryKey: ["shopping"], queryFn: api.getShopping });

  const genMut = useMutation({
    mutationFn: () => api.generateShopping(),
    onSuccess: () => {
      toast.success("Shopping list generated");
      qc.invalidateQueries({ queryKey: ["shopping"] });
    },
  });

  if (!profile) return <div>Profile required.</div>;
  if (!plan) return <div>Generate a weekly plan first on the Weekly Plan page.</div>;

  const byCat: Record<string, any[]> = {};
  shopping?.items?.forEach((it: any) => {
    (byCat[it.category] ||= []).push(it);
  });

  const copyList = () => {
    if (!shopping) return;
    const lines = shopping.items.map((i: any) => `${i.name}\t${i.quantity}\t${i.category}${i.suggested_swap ? ` — swap: ${i.suggested_swap}` : ""}`).join("\n");
    navigator.clipboard.writeText(lines);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="section-header">Shopping list</h1>
        <p className="text-[#4a635c]">Consolidated from your plan, with pantry items removed and smart KB swaps suggested.</p>
      </div>

      <button onClick={() => genMut.mutate()} disabled={genMut.isPending} className="btn btn-primary">Generate shopping list (ShoppingListOptimizer)</button>
      {genMut.isPending && <div className="text-sm text-[#4a635c]">ShoppingListOptimizer consolidating missing items + suggesting swaps…</div>}

      {!shopping && <div className="text-sm">No shopping list yet.</div>}

      {shopping && Object.keys(byCat).length > 0 && (
        <div className="space-y-6">
          {Object.entries(byCat).sort().map(([cat, items]) => (
            <div key={cat}>
              <div className="font-semibold text-sm tracking-wider text-[#4a635c] mb-2">{cat.toUpperCase()}</div>
              <div className="space-y-1.5">
                {items.map((item: any, idx: number) => (
                  <div key={idx} className="flex justify-between text-sm card py-2">
                    <div>{item.name} <span className="text-[#4a635c]">({item.quantity})</span></div>
                    {item.suggested_swap && <div className="text-xs text-[#9a3b20]">Swap idea: {item.suggested_swap}</div>}
                  </div>
                ))}
              </div>
            </div>
          ))}
          <button onClick={copyList} className="btn btn-secondary">Copy list to clipboard</button>
          <Disclaimer text={shopping.disclaimer} />
        </div>
      )}
    </div>
  );
}
