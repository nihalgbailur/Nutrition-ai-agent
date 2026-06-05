"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Home,
  User,
  Package,
  UtensilsCrossed,
  Calendar,
  ShoppingCart,
  MessageCircle,
  Star,
  Info,
  Leaf,
} from "lucide-react";
import { cn } from "../lib/utils";
import { api } from "../lib/api";
import { ThemeToggle } from "./ThemeToggle";

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/pantry", label: "Pantry", icon: Package },
  { href: "/recipes", label: "Recipes", icon: UtensilsCrossed },
  { href: "/planner", label: "Weekly Plan", icon: Calendar },
  { href: "/shopping", label: "Shopping List", icon: ShoppingCart },
  { href: "/chat", label: "Chat", icon: MessageCircle },
  { href: "/feedback", label: "Feedback", icon: Star },
  { href: "/how-it-works", label: "How it works", icon: Info },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Premium sidebar */}
      <aside className="w-64 border-r border-[var(--np-border)] bg-[var(--np-card-bg)] flex flex-col">
        <div className="p-6 border-b border-[var(--np-border)]">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-[var(--np-green)] flex items-center justify-center">
              <Leaf className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="font-semibold text-xl tracking-[-0.02em] text-[var(--np-green)]">NutriPlan AI</div>
              <div className="text-[10px] text-[var(--np-text-muted)] -mt-0.5">Premium kitchen companion</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn("nav-link relative", active && "active")}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
                {active && (
                  <motion.div 
                    layoutId="activeNav" 
                    className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full" 
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-[var(--np-border)] text-xs text-[var(--np-text-muted)]">
          <LLMStatus />
          <div className="mt-2">Local-first • LangGraph agents<br />Data in <code className="font-mono">data/nutriplan.db</code></div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 border-b border-[var(--np-border)] bg-[var(--np-card-bg)]/80 backdrop-blur flex items-center px-6 text-sm text-[var(--np-text-muted)] justify-between">
          <span>Agentic meal planning for Indian households — beautiful, private, and smart.</span>
          <div className="flex items-center gap-3">
            <LLMStatus compact />
            <ThemeToggle />
          </div>
        </header>
        <main className="flex-1 overflow-auto p-8 bg-[#f7faf8]">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
}

function LLMStatus({ compact = false }: { compact?: boolean }) {
  const { data: status } = useQuery({
    queryKey: ["status"],
    queryFn: api.getStatus,
    refetchInterval: 45000,
  });

  if (!status) return null;

  const label = status.provider?.replace(" (", "\n(").split("\n")[0] || "LLM";
  const pill = (
    <span className="inline-flex items-center gap-1 rounded-full bg-[#e8f4ef] text-[#1a5c45] px-2 py-0.5 text-[10px] font-medium">
      {status.llm_available ? "●" : "○"} {label}
    </span>
  );

  if (compact) return pill;

  return <div className="text-[10px]">{pill}</div>;
}
