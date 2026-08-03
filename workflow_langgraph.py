"""
W5D1_Lab_Chaos_agent_LangGraph
- Week 5 / Day 1
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-03
"""

from langgraph.graph import StateGraph, END

from langgraph.graph import StateGraph, END

from normalobjects_langgraph import (
    ComplaintState,
    intake_node,
    validation_node,
    investigation_node,
    resolution_node,
    closure_node,
    reject_node,
)

def validation_router(state: ComplaintState) -> str:
    """Conditional routing decision after validation."""
    # If validation_passed is True, go to investigation
    if state.get("validation_passed"):
        return "investigate"
    # Otherwise, go to rejection path
    return "reject"

def build_workflow():
    workflow = StateGraph(ComplaintState)

    # Nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("investigate", investigation_node)
    workflow.add_node("resolve", resolution_node)
    workflow.add_node("close", closure_node)
    workflow.add_node("reject", reject_node)

   
    workflow.set_entry_point("intake") # Entry point
    workflow.add_edge("intake", "validate") # Intake always goes to validate
    workflow.add_conditional_edges( # Conditional routing from validate, using add_conditional_edges
        "validate",          # node where the decision happens
        validation_router,   # function that inspects state and returns a key
        {
            "investigate": "investigate",  # if router returns "investigate", go to this node
            "reject": "reject",            # if router returns "reject", go to this node
        },
    )
    workflow.add_edge("investigate", "resolve")  # Valid complaint path: investigate -> resolve -> close -> END
    workflow.add_edge("resolve", "close")
    workflow.add_edge("close", END)

    # Reject path: reject -> END
    workflow.add_edge("reject", END)

    app = workflow.compile()
    return app


def run_complaint(complaint_text: str) -> ComplaintState:
    """Helper to run the workflow on a single complaint and return the final state."""
    initial_state: ComplaintState = {
        "complaint": complaint_text,
        "category": None,
        "status": "new",
        "workflow_path": [],
        "validation_passed": False,
        "investigation_notes": None,
        "resolution": None,
        "closure_message": None,
    }

    app = build_workflow()
    final_state = app.invoke(initial_state)
    return final_state