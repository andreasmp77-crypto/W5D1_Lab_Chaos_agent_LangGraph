"""
W5D1_Lab_Chaos_agent_LangGraph
- Week 5 / Day 1
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-03
"""

# main.py
from workflow_langgraph import run_complaint


def main():
    # 1) Define some test complaints, including the invalid one
    test_complaints = [
        "The Downside Up portal opens at different times each day. How do I predict when?",
        "This is not a valid complaint about something random",  # Should be rejected
    ]

    # 2) Loop through each complaint and run the workflow
    for complaint in test_complaints:
        print("\n==============================")
        print(f"Complaint: {complaint}")

        final_state = run_complaint(complaint)

        # 3) Print key fields from the final state so you can inspect behavior
        print("\nFinal state:")
        print(f"  category:           {final_state.get('category')}")
        print(f"  status:             {final_state.get('status')}")
        print(f"  validation_passed:  {final_state.get('validation_passed')}")
        print(f"  workflow_path:      {final_state.get('workflow_path')}")
        print(f"  investigation_notes:{final_state.get('investigation_notes')}")
        print(f"  resolution:         {final_state.get('resolution')}")
        print(f"  closure_message:    {final_state.get('closure_message')}")


if __name__ == "__main__":
    main()