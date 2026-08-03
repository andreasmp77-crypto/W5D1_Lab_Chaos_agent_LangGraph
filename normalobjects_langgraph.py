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

# Allowed categories that intake_node can assign
ALLOWED_CATEGORIES = {"portal", "monster", "psychic", "environmental", "other"}

# Vaitation node
def validation_node(state: ComplaintState) -> ComplaintState:
    """
    Step 2: Validation - Check if complaint is coherent and on-topic.
    - Confirms the category is one of the allowed ones.
    - Optionally rejects obviously random / nonsense complaints.
    """
    print("\n[VALIDATION] Validating complaint...") # 1) Log that we entered the validation step
    category = state.get("category") # 2) Read the current category from the state
    category_ok = category in ALLOWED_CATEGORIES # 3) Basic category check: True if category is in the allowed list, False otherwise

    complaint_text = state["complaint"].lower() # 4) Simple "nonsense" filter: Here we just check for the word "random" as a toy rule.
    is_nonsense = "random" in complaint_text
   
    validation_passed = category_ok and not is_nonsense # 5) Combine checks into a single flag: validation_passed is True only if category_ok AND not nonsense


    # 6) Build the new state:
    #    - Keep everything from the old state (**state)
    #    - Update validation_passed
    #    - Append "validate" to workflow_path
    #    - Set status to "validated" or "rejected"
    new_state: ComplaintState = {
        **state,
        "validation_passed": validation_passed,
        "workflow_path": state.get("workflow_path", []) + ["validate"],
        "status": "validated" if validation_passed else "rejected",
    }

    
    print(f"[VALIDATION] Category OK: {category_ok}, Nonsense: {is_nonsense}") # 7) Log the result for debugging and traceability
    print(f"[VALIDATION] Passed: {validation_passed}")

    
    return new_state  # 8) Return the updated state so the next node can use it

# Investigation node (placeholder for now)
def investigation_node(state: ComplaintState) -> ComplaintState:
    """Step 3: Investigation - Gather findings based on category and complaint."""
    print("\n[INVESTIGATION] Investigating complaint...")

    complaint = state["complaint"]
    category = state.get("category", "other")

    investigation_prompt = f"""
    You are investigating a Downside Up complaint.

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

# resolution node
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
    - Explains the next steps in 2–3 sentences.
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

# closure node
def closure_node(state: ComplaintState) -> ComplaintState:
    """Step 5: Closure - Confirm completion and summarize actions."""
    print("\n[CLOSURE] Creating closure message...")

    complaint = state["complaint"]
    category = state.get("category", "other")
    notes = state.get("investigation_notes", "")
    resolution_text = state.get("resolution", "")

    closure_prompt = f"""
    You are closing a Downside Up complaint.

    Category: {category}
    Complaint: {complaint}
    Investigation notes: {notes}
    Resolution: {resolution_text}

    Write a short one line closure message that confirms the complaint has been processed.
    Uses a calm, professional tone.
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

# reject node
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
