"""
W5D1_Lab_Chaos_agent_LangGraph
- Week 5 / Day 1
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-03
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict, List, Optional

# This is the form that travels through all workflow stations
class ComplaintState(TypedDict):
    complaint: str                    # the original text from the user
    category: Optional[str]           # portal/monster/psychic/environmental/other
    status: str                       # current stage label, e.g. "intake", "validated"
    workflow_path: List[str]          # list of node names visited in order
    validation_passed: bool           # did validation accept or reject?
    investigation_notes: Optional[str]  # text gathered in investigation
    resolution: Optional[str]         # proposed fix
    closure_message: Optional[str]    # final message back to the user

# use a small model for lab
llm = ChatOpenAI(model="gpt-4o-mini")  # or the model your bootcamp uses

def intake_node(state: ComplaintState) -> ComplaintState:
    """Step 1: Intake - Parse and categorize the complaint"""
    print("\n[INTAKE] Processing complaint...")
    complaint = state["complaint"]

    categorization_prompt = f"""
    Categorize this Downside Up complaint into one of these categories:
    - portal: Issues with portal timing, location, or behavior
    - monster: Issues with creature behavior (demogorgons, etc.)
    - psychic: Issues with psychic abilities or limitations
    - environmental: Issues with electricity, weather, or physical environment
    - other: Anything else

    Complaint: {complaint}

    Respond with ONLY the category name (portal, monster, psychic, environmental, or other).
    """

    response = llm.invoke([HumanMessage(content=categorization_prompt)])
    category = response.content.strip().lower()

    new_state: ComplaintState = {
        **state,
        "category": category,
        "workflow_path": state.get("workflow_path", []) + ["intake"],
        "status": "intake",
    }

    print(f"[INTAKE] Categorized as: {category}")
    return new_state