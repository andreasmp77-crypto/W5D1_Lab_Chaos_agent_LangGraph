"""
Streamlit chatbot UI for the Downside Up complaint workflow.

This file keeps the presentation layer separate from the LangGraph logic.
Run with:
    streamlit run streamlit_chatbot.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from workflow_langgraph import run_complaint


APP_TITLE = "Downside Up Complaint Desk"
APP_SUBTITLE = "A noir chatbot for routing strange incidents through intake, validation, investigation, resolution, and closure."
LOG_PATH = Path(__file__).with_name("conversation_records.jsonl")
HERO_IMAGE_PATH = Path(__file__).with_name("stranger_things___sketchers_of_will_by_godfathersky_dl703f8-pre.jpg")
STARTER_QUESTIONS = [
    "The Downside Up portal opens at different times each day. How do I predict when?",
    "Demogorgons sometimes work together and sometimes fight. What's their deal?",
    "El can move things with her mind but can't lift heavy rocks. Why?",
    "Why do creatures and power lines react so strangely together?",
    "This is not a valid complaint about something random",
]


def load_records() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []

    records: list[dict[str, Any]] = []
    for raw_line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def append_record(record: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = load_records()
    if "active_theme_note" not in st.session_state:
        st.session_state.active_theme_note = "Open a case, track the workflow, and keep a persistent log of every complaint."


def inject_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

            :root {
                --bg: #07090d;
                --panel: rgba(17, 20, 28, 0.86);
                --panel-2: rgba(28, 32, 42, 0.9);
                --border: rgba(255, 255, 255, 0.08);
                --text: #f4f7fb;
                --muted: #b8c0cc;
                --accent: #e50914;
                --accent-2: #ff8a5b;
                --accent-3: #ffd166;
                --glow: rgba(229, 9, 20, 0.26);
            }

            .stApp {
                background:
                    radial-gradient(circle at 15% 20%, rgba(229, 9, 20, 0.20), transparent 24%),
                    radial-gradient(circle at 85% 10%, rgba(255, 138, 91, 0.15), transparent 20%),
                    radial-gradient(circle at 50% 120%, rgba(255, 209, 102, 0.08), transparent 26%),
                    linear-gradient(180deg, #05070b 0%, #090c12 45%, #07090d 100%);
                color: var(--text);
                font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(9, 11, 16, 0.98), rgba(16, 19, 26, 0.96));
                border-right: 1px solid var(--border);
            }

            section[data-testid="stSidebar"] * {
                color: var(--text);
            }

            .hero-shell {
                display: grid;
                grid-template-columns: 1.3fr 0.9fr;
                gap: 1.25rem;
                align-items: stretch;
                margin: 0.25rem 0 1rem 0;
            }

            .hero-card, .glass-card {
                background: linear-gradient(180deg, var(--panel), rgba(13, 16, 22, 0.92));
                border: 1px solid var(--border);
                border-radius: 24px;
                box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
                overflow: hidden;
            }

            .hero-card {
                padding: 1.35rem 1.4rem 1.2rem 1.4rem;
                position: relative;
            }

            .hero-card::after {
                content: "";
                position: absolute;
                inset: auto -6% -40% auto;
                width: 220px;
                height: 220px;
                border-radius: 999px;
                background: radial-gradient(circle, rgba(229, 9, 20, 0.15), transparent 64%);
                pointer-events: none;
            }

            .eyebrow {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.78rem;
                letter-spacing: 0.2em;
                text-transform: uppercase;
                color: #ff8f8f;
                margin-bottom: 0.6rem;
            }

            .hero-title {
                font-size: clamp(2rem, 4vw, 3.6rem);
                line-height: 0.98;
                font-weight: 800;
                margin: 0;
                color: #fff;
            }

            .hero-copy {
                max-width: 62ch;
                color: var(--muted);
                font-size: 1rem;
                line-height: 1.6;
                margin: 0.9rem 0 0 0;
            }

            .banner-art {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100%;
                padding: 1rem;
            }

            .banner-art img {
                width: 100%;
                max-width: 360px;
                height: auto;
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.08);
                filter: drop-shadow(0 20px 40px rgba(229, 9, 20, 0.25));
            }

            .chat-surface {
                background: linear-gradient(180deg, rgba(17, 20, 28, 0.88), rgba(11, 14, 20, 0.95));
                border: 1px solid var(--border);
                border-radius: 26px;
                padding: 1.1rem 1.2rem 0.6rem 1.2rem;
                box-shadow: 0 18px 60px rgba(0, 0, 0, 0.32);
            }

            .section-title {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.18em;
                color: #ff9999;
                margin-bottom: 0.65rem;
            }

            .history-card {
                border: 1px solid rgba(255, 255, 255, 0.08);
                background: rgba(255, 255, 255, 0.03);
                border-radius: 16px;
                padding: 0.8rem 0.9rem;
                margin-bottom: 0.7rem;
            }

            .history-meta {
                display: flex;
                justify-content: space-between;
                gap: 0.8rem;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.72rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #ffb9b9;
                margin-bottom: 0.55rem;
            }

            .history-question {
                color: #eef2f7;
                font-size: 0.93rem;
                line-height: 1.45;
                margin-bottom: 0.55rem;
            }

            .history-answer {
                color: var(--muted);
                font-size: 0.9rem;
                line-height: 1.45;
            }

            .stChatMessage {
                border-radius: 18px;
                margin-bottom: 0.7rem;
            }

            [data-testid="stChatMessage"] {
                background: transparent;
            }

            [data-testid="stChatMessage"] > div {
                border-radius: 18px;
            }

            div[data-testid="stChatMessageContent"] {
                border: 1px solid rgba(255, 255, 255, 0.08);
                background: rgba(255, 255, 255, 0.04);
                color: var(--text);
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.16);
            }

            div[data-testid="stChatMessage"][aria-label="Chat message from assistant"] div[data-testid="stChatMessageContent"] {
                background: linear-gradient(180deg, rgba(229, 9, 20, 0.08), rgba(255, 255, 255, 0.03));
                border-color: rgba(229, 9, 20, 0.22);
            }

            div[data-testid="stChatMessage"][aria-label="Chat message from user"] div[data-testid="stChatMessageContent"] {
                background: rgba(255, 255, 255, 0.04);
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
            }

            .stTabs [data-baseweb="tab"] {
                background: rgba(255, 255, 255, 0.04);
                border-radius: 999px;
                color: #dfe6ee;
                padding: 0.55rem 0.9rem;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            .stTabs [aria-selected="true"] {
                background: rgba(229, 9, 20, 0.16) !important;
                color: #fff !important;
                border-color: rgba(229, 9, 20, 0.35) !important;
            }

            .stButton > button, .stDownloadButton > button {
                border-radius: 999px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: linear-gradient(180deg, rgba(229, 9, 20, 0.95), rgba(164, 5, 14, 0.95));
                color: #fff;
                font-weight: 700;
                letter-spacing: 0.01em;
                box-shadow: 0 12px 26px rgba(229, 9, 20, 0.22);
            }

            .stButton > button:hover, .stDownloadButton > button:hover {
                border-color: rgba(255, 255, 255, 0.18);
                transform: translateY(-1px);
            }

            textarea, input {
                border-radius: 18px !important;
            }

            @media (max-width: 1100px) {
                .hero-shell {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_banner() -> None:
    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown(
            f"""
            <div class="hero-card">
                <div class="eyebrow">Case Intake Console</div>
                <h1 class="hero-title">{APP_TITLE}</h1>
                <p class="hero-copy">{APP_SUBTITLE}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        if HERO_IMAGE_PATH.exists():
            st.image(
                str(HERO_IMAGE_PATH),
                caption="Stranger Things – Sketchers of Will",
                use_container_width=True,
            )
        else:
            st.markdown(
                '<div style="color:#b8c0cc;font-family:\'IBM Plex Mono\', monospace;text-align:center;max-width:18rem;">Missing hero image.</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            """
            <small>
            Artwork: <a href="https://www.deviantart.com/godfathersky/art/Stranger-Things-Sketchers-of-Will-1281551444" target="_blank">
            "Stranger Things – Sketchers of Will"</a> by godfathersky, used under Creative Commons.
            </small>
            """,
            unsafe_allow_html=True,
        )


def render_history_sidebar() -> None:
    st.sidebar.markdown("## Conversation Log")
    st.sidebar.caption("Saved locally as JSONL and reloaded on refresh.")
    st.sidebar.metric("Stored exchanges", len(st.session_state.history))

    if st.sidebar.button("Reset session", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    if st.session_state.history:
        exported = json.dumps(st.session_state.history, ensure_ascii=False, indent=2)
        st.sidebar.download_button(
            "Download history JSON",
            data=exported,
            file_name="conversation_records.json",
            mime="application/json",
            use_container_width=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Recent cases")
    for item in reversed(st.session_state.history[-8:]):
        with st.sidebar.container():
            st.markdown(
                f"""
                <div class="history-card">
                    <div class="history-meta">
                        <span>{item.get("timestamp", "")}</span>
                        <span>{item.get("status", "unknown")}</span>
                    </div>
                    <div class="history-question">{item.get("complaint", "")}</div>
                    <div class="history-answer">{item.get("closure_message", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def run_case(complaint_text: str, user_label: str) -> dict[str, Any]:
    final_state = run_complaint(complaint_text)

    record = {
        "timestamp": iso_now(),
        "user": user_label,
        "complaint": complaint_text,
        "category": final_state.get("category"),
        "status": final_state.get("status"),
        "validation_passed": final_state.get("validation_passed"),
        "workflow_path": final_state.get("workflow_path", []),
        "investigation_notes": final_state.get("investigation_notes"),
        "resolution": final_state.get("resolution"),
        "closure_message": final_state.get("closure_message"),
    }
    st.session_state.history.append(record)
    append_record(record)
    return final_state


def render_chat_log() -> None:
    for item in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(item.get("complaint", ""))

        assistant_message = item.get("closure_message", "Case processed.")
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
            with st.expander("Case details", expanded=False):
                st.write(f"Category: {item.get('category', 'unknown')}")
                st.write(f"Status: {item.get('status', 'unknown')}")
                st.write(f"Validation passed: {item.get('validation_passed', False)}")
                st.write(f"Workflow path: {' -> '.join(item.get('workflow_path', [])) or 'n/a'}")
                if item.get("investigation_notes"):
                    st.write("Investigation notes:")
                    st.write(item["investigation_notes"])
                if item.get("resolution"):
                    st.write("Resolution:")
                    st.write(item["resolution"])


def render_starter_questions(user_label: str) -> dict[str, Any] | None:
    st.markdown('<div class="section-title">Starter questions</div>', unsafe_allow_html=True)
    st.caption("Click a sample prompt to send it directly into the workflow.")

    chosen_prompt: str | None = None
    columns = st.columns(2)
    for index, question in enumerate(STARTER_QUESTIONS):
        with columns[index % 2]:
            if st.button(question, key=f"starter_question_{index}", use_container_width=True):
                chosen_prompt = question

    if not chosen_prompt:
        return None

    with st.chat_message("user"):
        st.markdown(chosen_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Routing complaint through the workflow..."):
            result = run_case(chosen_prompt, user_label)

        st.markdown(result.get("closure_message") or "Case processed.")

        with st.expander("Detailed output", expanded=False):
            st.write(f"Category: {result.get('category')}")
            st.write(f"Status: {result.get('status')}")
            st.write(f"Validation passed: {result.get('validation_passed')}")
            st.write(f"Workflow path: {' -> '.join(result.get('workflow_path', [])) or 'n/a'}")
            st.write("Investigation notes:")
            st.write(result.get("investigation_notes") or "None")
            st.write("Resolution:")
            st.write(result.get("resolution") or "None")

    return result


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=str(HERO_IMAGE_PATH), layout="wide", initial_sidebar_state="expanded")
    init_state()
    inject_css()
    render_banner()
    render_history_sidebar()

    st.markdown('<div class="section-title">Chat</div>', unsafe_allow_html=True)
    st.caption("Submit a complaint and the workflow will respond like a caseworker with a running log.")
    render_chat_log()
    user_label = st.text_input("Name", value="Visitor", help="Used only for the local record log.")
    render_starter_questions(user_label)

    with st.expander("Workflow reference", expanded=False):
        st.write("Intake -> Validate -> Investigate -> Resolve -> Close")
        st.write("Rejected cases stop after validation and record the closure message.")

    prompt = st.chat_input("Describe the problem you want processed...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Routing complaint through the workflow..."):
                result = run_case(prompt, user_label)

            st.markdown(result.get("closure_message") or "Case processed.")

            with st.expander("Detailed output", expanded=False):
                st.write(f"Category: {result.get('category')}")
                st.write(f"Status: {result.get('status')}")
                st.write(f"Validation passed: {result.get('validation_passed')}")
                st.write(f"Workflow path: {' -> '.join(result.get('workflow_path', [])) or 'n/a'}")
                st.write("Investigation notes:")
                st.write(result.get("investigation_notes") or "None")
                st.write("Resolution:")
                st.write(result.get("resolution") or "None")


if __name__ == "__main__":
    main()
