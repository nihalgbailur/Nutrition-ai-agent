export function AgentPill({ name }: { name?: string }) {
  if (!name) return null;
  return <span className="agent-pill">{name.replace("Agent", "")}</span>;
}
