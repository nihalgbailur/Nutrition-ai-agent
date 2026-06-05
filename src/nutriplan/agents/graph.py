from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from nutriplan.agents.nodes import (
    feedback_agent_node,
    inventory_agent_node,
    meal_planner_node,
    profile_manager_node,
    recipe_creator_node,
    safety_gate_node,
    shopping_list_optimizer_node,
)
from nutriplan.agents.state import NutriPlanState


def _route_after_safety(state: NutriPlanState) -> str:
    safety = state.get("safety_result")
    if safety and safety.action == "redirect":
        return "end"
    intent = state.get("intent", "")
    return {
        "save_profile": "profile",
        "sync_pantry": "inventory",
        "generate_recipes": "recipes_flow",
        "generate_weekly_plan": "plan_flow",
        "generate_shopping_list": "shopping",
        "feedback": "feedback",
    }.get(intent, "inventory")


def build_app():
    graph = StateGraph(NutriPlanState)
    graph.add_node("safety", safety_gate_node)
    graph.add_node("profile", profile_manager_node)
    graph.add_node("inventory", inventory_agent_node)
    graph.add_node("recipe_creator", recipe_creator_node)
    graph.add_node("meal_planner", meal_planner_node)
    graph.add_node("shopping", shopping_list_optimizer_node)
    graph.add_node("feedback", feedback_agent_node)

    def after_inventory(state: NutriPlanState) -> str:
        intent = state.get("intent", "")
        if intent in ("generate_recipes", "generate_weekly_plan"):
            return "recipe_creator"
        return "done"

    def after_recipes(state: NutriPlanState) -> str:
        if state.get("intent") == "generate_weekly_plan":
            return "meal_planner"
        return "done"

    graph.add_edge(START, "safety")
    graph.add_conditional_edges(
        "safety",
        _route_after_safety,
        {
            "profile": "profile",
            "inventory": "inventory",
            "recipes_flow": "inventory",
            "plan_flow": "inventory",
            "shopping": "shopping",
            "feedback": "feedback",
            "end": END,
        },
    )
    graph.add_edge("profile", END)
    graph.add_conditional_edges(
        "inventory",
        after_inventory,
        {"recipe_creator": "recipe_creator", "done": END},
    )
    graph.add_conditional_edges(
        "recipe_creator",
        after_recipes,
        {"meal_planner": "meal_planner", "done": END},
    )
    graph.add_edge("meal_planner", END)
    graph.add_edge("shopping", END)
    graph.add_edge("feedback", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def invoke_graph(
    intent: str,
    profile,
    pantry: list,
    *,
    user_text: str = "",
    weekly_plan=None,
    thread_id: str = "default",
    feedback_kwargs: dict | None = None,
):
    app = build_app()
    state: NutriPlanState = {
        "intent": intent,
        "user_profile": profile,
        "pantry": pantry,
        "user_text": user_text,
    }
    if weekly_plan:
        state["weekly_plan"] = weekly_plan
    if feedback_kwargs:
        state.update(feedback_kwargs)
    config = {"configurable": {"thread_id": thread_id}}
    return app.invoke(state, config=config)