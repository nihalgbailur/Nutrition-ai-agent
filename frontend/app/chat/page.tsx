"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { api, API_BASE } from "../../lib/api";
import { AgentPill } from "../../components/AgentPill";

type ChatTurn = { user: string; assistant: string; agent?: string };

export default function ChatPage() {
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });
  const [history, setHistory] = React.useState<ChatTurn[]>([]);
  const [input, setInput] = React.useState("");
  const [fastMode, setFastMode] = React.useState(true);
  const [streaming, setStreaming] = React.useState(false);
  const [currentAgent, setCurrentAgent] = React.useState("");

  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: 99999, behavior: "smooth" });
  }, [history]);

  async function send() {
    if (!input.trim() || streaming) return;
    const prompt = input.trim();
    setInput("");
    setHistory((h) => [...h, { user: prompt, assistant: "", agent: "" }]);
    setStreaming(true);
    setCurrentAgent("");

    try {
      const res = await fetch(`${API_BASE}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: prompt, fast_mode: fastMode }),
      });

      if (!res.body) throw new Error("No stream");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = "";
      let agent = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter(Boolean);
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = JSON.parse(line.slice(6));
          if (data.type === "agent") {
            agent = data.agent;
            setCurrentAgent(agent);
            setHistory((h) => {
              const copy = [...h];
              copy[copy.length - 1].agent = agent;
              return copy;
            });
          } else if (data.type === "token") {
            assistantText += data.text;
            setHistory((h) => {
              const copy = [...h];
              copy[copy.length - 1].assistant = assistantText;
              return copy;
            });
          } else if (data.type === "done") {
            // final
          }
        }
      }
    } catch (e: any) {
      setHistory((h) => {
        const copy = [...h];
        copy[copy.length - 1].assistant = "Sorry, chat failed. " + (e.message || "");
        return copy;
      });
    } finally {
      setStreaming(false);
      setCurrentAgent("");
    }
  }

  function clearChat() {
    setHistory([]);
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="section-header">Chat with NutriPlan</h1>
          <div className="text-xs text-[#4a635c]">Ask about recipes, pantry, swaps, or planning. Streaming enabled.</div>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={fastMode} onChange={(e) => setFastMode(e.target.checked)} />
          Fast mode (instant templates)
        </label>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-auto space-y-4 pr-2 pb-4">
        {history.length === 0 && (
          <div className="text-sm text-[#4a635c]">
            Try: “quick veg dinner”, “swaps for Maggi”, “what can I make with dal and rice this week?”
          </div>
        )}
        <AnimatePresence>
          {history.map((turn, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-2"
            >
              <div className="chat-bubble-user ml-auto">{turn.user}</div>
              <div className="chat-bubble-assistant">
                {turn.agent && <div className="mb-1"><AgentPill name={turn.agent} /></div>}
                {turn.assistant || (streaming && i === history.length - 1 ? "..." : "")}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {currentAgent && <div className="text-xs text-[#1a3c34] pl-1">Thinking with {currentAgent}…</div>}
      </div>

      <div className="pt-3 border-t flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") send(); }}
          placeholder="Ask anything about meals, pantry, or planning…"
          className="flex-1"
          disabled={streaming}
        />
        <button onClick={send} disabled={streaming || !input.trim()} className="btn btn-primary">Send</button>
        <button onClick={clearChat} className="btn btn-ghost">Clear</button>
      </div>

      {!profile && <div className="text-xs mt-2 text-[#4a635c]">Chatting as guest. Save a Profile for full personalization.</div>}
    </div>
  );
}
