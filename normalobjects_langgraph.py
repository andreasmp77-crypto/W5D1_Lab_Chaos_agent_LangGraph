"""
W5D1_Lab_Chaos_agent_LangGraph
- Week 5 / Day 1
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-03
"""
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict, List, Optional

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key,)


# This is the form that travels through all workflow stations
class ComplaintState(TypedDict):
    complaint: str
    category: Optional[str]
    status: str
    workflow_path: List[str]
    validation_passed: bool
    investigation_notes: Optional[str]
    resolution: Optional[str]
    closure_message: Optional[str]


# use a small model for lab
llm = ChatOpenAI(model="gpt-4o-mini")


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


# Allowed categories that intake_node can assign
ALLOWED_CATEGORIES = {"portal", "monster", "psychic", "environmental", "other"}


def validation_node(state: ComplaintState) -> ComplaintState:
    """
    Step 2: Validation - Check if complaint is coherent, on-topic, and related to Stranger Things.
    - Confirms the category is one of the allowed ones.
    - Rejects obviously random / nonsense complaints.
    - Uses the LLM to decide whether the request is actually Stranger Things-related.
    """
    print("\n[VALIDATION] Validating complaint...")
    category = state.get("category")
    category_ok = category in ALLOWED_CATEGORIES

    complaint_text = state["complaint"].lower()
    is_nonsense = "random" in complaint_text

    relevance_prompt = f"""
    Decide whether this request is clearly related to Stranger Things.

    Request: {state["complaint"]}

    Reply with ONLY YES if it is related to Stranger Things.
    Reply with ONLY NO if it is unrelated to Stranger Things.
    """
    relevance_response = llm.invoke([HumanMessage(content=relevance_prompt)])
    is_stranger_things_related = relevance_response.content.strip().upper().startswith("YES")

    validation_passed = category_ok and not is_nonsense and is_stranger_things_related

    new_state: ComplaintState = {
        **state,
        "validation_passed": validation_passed,
        "workflow_path": state.get("workflow_path", []) + ["validate"],
        "status": "validated" if validation_passed else "rejected",
    }

    print(
        f"[VALIDATION] Category OK: {category_ok}, Nonsense: {is_nonsense}, "
        f"Stranger Things related: {is_stranger_things_related}"
    )
    print(f"[VALIDATION] Passed: {validation_passed}")

    return new_state


def investigation_node(state: ComplaintState) -> ComplaintState:
    """Step 3: Investigation - Gather findings based on category and complaint."""
    print("\n[INVESTIGATION] Investigating complaint...")

    complaint = state["complaint"]
    category = state.get("category", "other")

    investigation_prompt = f"""
    You are investigating a Downside Up complaint related to Stranger Things TV series.

    Category: {category}
    Complaint: {complaint}

    Write a brief, factual investigation note that:
    - Describes what might be causing the issue.
    - Avoids wild speculation.
    - Stays consistent with the category.
    """

    response = llm.invoke([HumanMessage(content=investigation_prompt)])
    notes = response.content.strip()

    new_state: ComplaintState = {
        **state,
        "investigation_notes": notes,
        "workflow_path": state.get("workflow_path", []) + ["investigate"],
        "status": "investigating",
    }

    print("[INVESTIGATION] Notes recorded.")
    return new_state


def resolution_node(state: ComplaintState) -> ComplaintState:
    """Step 4: Resolution - Propose a fix based on investigation notes."""
    print("\n[RESOLUTION] Generating resolution...")

    complaint = state["complaint"]
    category = state.get("category", "other")
    notes = state.get("investigation_notes", "")

    resolution_prompt = f"""
    You are resolving a Downside Up complaint.

    Category: {category}
    Complaint: {complaint}
    Investigation notes: {notes}

    Propose a clear, practical resolution that:
    - Is consistent with the investigation notes.
    - Is safe and reasonable.
    - Explains the next steps in 2-3 sentences.
    """

    response = llm.invoke([HumanMessage(content=resolution_prompt)])
    resolution_text = response.content.strip()

    new_state: ComplaintState = {
        **state,
        "resolution": resolution_text,
        "workflow_path": state.get("workflow_path", []) + ["resolve"],
        "status": "resolved",
    }

    print("[RESOLUTION] Resolution generated.")
    return new_state


def closure_node(state: ComplaintState) -> ComplaintState:
    """Step 5: Closure - Confirm completion and summarize actions."""
    print("\n[CLOSURE] Creating closure message...")

    complaint = state["complaint"]
    category = state.get("category", "other")
    notes = state.get("investigation_notes", "")
    resolution_text = state.get("resolution", "")

    closure_prompt = f"""
    You are closing a Downside Up complaint related to Stranger Things TV series.

    Category: {category}
    Complaint: {complaint}
    Investigation notes: {notes}
    Resolution: {resolution_text}

    Write a short one line closure message that confirms the complaint has been processed.
    Use@ a calm tone.
    """

    response = llm.invoke([HumanMessage(content=closure_prompt)])
    closure_message = response.content.strip()

    new_state: ComplaintState = {
        **state,
        "closure_message": closure_message,
        "workflow_path": state.get("workflow_path", []) + ["close"],
        "status": "closed",
    }

    print("[CLOSURE] Closure message saved.")
    return new_state


def reject_node(state: ComplaintState) -> ComplaintState:
    """Rejection path for invalid complaints."""
    print("\n[REJECT] Complaint rejected by validation.")

    complaint = state["complaint"]

    closure_text = f"""
    Your Downside Up complaint could not be processed.

    Complaint: {complaint}

    Reason: The complaint did not meet validation rules
    (category or coherence). Please check the guidelines
    and submit a clearer, relevant complaint.
    """

    new_state: ComplaintState = {
        **state,
        "closure_message": closure_text.strip(),
        "workflow_path": state.get("workflow_path", []) + ["reject"],
        "status": "rejected",
    }

    print("[REJECT] Closure message recorded.")
    return new_state
