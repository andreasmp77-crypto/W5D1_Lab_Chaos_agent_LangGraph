"""
W5D1_Lab_Chaos_agent_LangGraph
- Week 5 / Day 1
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-03
"""

# test_visualize.py
from workflow_langgraph import build_workflow, run_complaint


# print representation of the workflow graph
def draw_graph_ascii():
    """Print an ASCII representation of the compiled workflow graph."""
    app = build_workflow()
    graph = app.get_graph()
    print("\n=== Workflow Graph (ASCII) ===")
    graph.print_ascii()

# run sample complaints through the workflow and show results
def test_sample_complaints():
    """Run sample complaints and show per-node results and execution trace."""
    test_complaints = [
        "The Downside Up portal opens at different times each day. How do I predict when?",
        "Demogorgons sometimes work together and sometimes fight. What's their deal?",
        "El can move things with her mind but can't lift heavy rocks. Why?",
        "Why do creatures and power lines react so strangely together?",
        "This is not a valid complaint about something random",  # Should be rejected
    ]

    for complaint in test_complaints:
        print("\n==============================")
        print(f"Complaint: {complaint}")

        final_state = run_complaint(complaint)

        # Extract key fields produced by each node
        category = final_state.get("category")                  # intake_node
        validation_passed = final_state.get("validation_passed")# validation_node
        investigation_notes = final_state.get("investigation_notes")  # investigation_node
        resolution_text = final_state.get("resolution")         # resolution_node
        closure_message = final_state.get("closure_message")    # closure_node / reject_node
        workflow_path = final_state.get("workflow_path", [])
        status = final_state.get("status")

        # Show execution path
        print(f"Execution path: {' -> '.join(workflow_path)}")

        # Show per-node outputs summarized
        print("\nNode outputs:")
        print(f"  [INTAKE]      category:           {category}")
        print(f"  [VALIDATION]  validation_passed:  {validation_passed}")
        print(f"  [INVESTIGATE] investigation_notes:\n{investigation_notes}")
        print(f"  [RESOLUTION]  resolution:\n{resolution_text}")
        print(f"  [CLOSURE/REJECT] status: {status}")
        print(f"  [CLOSURE/REJECT] closure_message:\n{closure_message}")


def main():
    draw_graph_ascii()
    test_sample_complaints()


if __name__ == "__main__":
    main()