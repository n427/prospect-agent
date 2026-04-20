import streamlit as st
import pandas as pd, time
from email_generator import generate_emails

st.set_page_config(
    page_title="GR0 Prospect Outreach",
    page_icon="📬",
    layout="centered",
)

st.markdown("""
<style>
    .block-container { padding-top: 2.5rem; max-width: 760px; }
    h1 { font-size: 1.9rem !important; font-weight: 700 !important; }
    .stTextArea textarea { font-size: 0.85rem; line-height: 1.6; }
    .stExpander { border: 1px solid #e2e8f0; border-radius: 8px; }
    .step-card {
        background: #f8fafc;
        border-left: 3px solid #6366f1;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        font-size: 0.82rem;
    }
    .step-card .tool-name {
        font-weight: 700;
        color: #6366f1;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.05em;
    }
    .step-card .tool-input { color: #334155; margin: 0.25rem 0; }
    .step-card .tool-output { color: #64748b; font-style: italic; }
    .email-card {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        background: #ffffff;
    }
    .variant-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
    }
    .badge-direct   { background:#ede9fe; color:#5b21b6; }
    .badge-curiosity{ background:#ecfdf5; color:#065f46; }
    .badge-pain     { background:#fff7ed; color:#92400e; }
    div.stFormSubmitButton > button[kind="primaryFormSubmit"] {
        background-color: #2563eb;
        border-color: #2563eb;
        color: #ffffff;
    }
    div.stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
        background-color: #1d4ed8;
        border-color: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📬 GR0 Prospect Outreach Agent")

st.divider()

with st.form("prospect_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        company = st.text_input("Company name", "Glossier")
        website = st.text_input("Website", "https://glossier.com")
    with col_b:
        contact = st.text_input("Contact name (optional)", "")
        sender  = st.text_input("Your name (signs the email)", "")

    submitted = st.form_submit_button("Generate emails", use_container_width=True, type="primary")

if submitted:
    start = time.time()
    with st.spinner("Researching company and drafting emails..."):
        result = generate_emails(
            company,
            website,
            contact_name=contact or "the founder",
            sender_name=sender or "the team",
        )
    elapsed = time.time() - start

    st.divider()

    m1, m2, m3 = st.columns(3)
    m1.metric("Time", f"{elapsed:.0f}s")
    m2.metric("Emails generated", "3")
    m3.metric("Agent steps", len(result.get("steps", [])))

    # Agent execution chain
    steps = result.get("steps", [])
    if steps:
        with st.expander("Agent execution chain", expanded=False):
            for i, step in enumerate(steps, 1):
                tool_input = step["input"]
                if isinstance(tool_input, dict):
                    display_input = next(iter(tool_input.values()), str(tool_input))
                else:
                    display_input = str(tool_input)
                output_preview = step["output"][:300] + ("..." if len(step["output"]) > 300 else "")
                st.markdown(f"""
<div class="step-card">
  <div class="tool-name">Step {i} &mdash; {step["tool"]}</div>
  <div class="tool-input"><strong>Input:</strong> {display_input}</div>
  <div class="tool-output"><strong>Result:</strong> {output_preview}</div>
</div>
""", unsafe_allow_html=True)

    # Research summary
    with st.expander("Research summary", expanded=False):
        st.write(result["research"])

    st.divider()
    st.markdown("### Generated emails")

    badge_class = {"direct": "badge-direct", "curiosity": "badge-curiosity", "pain": "badge-pain"}
    label       = {"direct": "Direct", "curiosity": "Curiosity", "pain": "Pain point"}

    for variant, content in result["emails"].items():
        body_html = content["body"].replace("\n", "<br>")
        st.markdown(f"""
<div class="email-card">
  <span class="variant-badge {badge_class[variant]}">{label[variant]}</span>
  <p style="margin:0.5rem 0 0.75rem;font-size:0.85rem;color:#334155;">
      <strong>Subject:</strong> {content["subject"]}
  </p>
  <hr style="border:none;border-top:1px solid #e2e8f0;margin:0.5rem 0 0.85rem;">
  <p style="font-size:0.88rem;line-height:1.75;color:#1e293b;margin:0;white-space:pre-wrap;">{body_html}</p>
</div>
""", unsafe_allow_html=True)

    # CSV download
    df = pd.DataFrame([{
        "company": company,
        "contact": contact,
        "sender": sender,
        "subject_direct":    result["emails"]["direct"]["subject"],
        "body_direct":       result["emails"]["direct"]["body"],
        "subject_curiosity": result["emails"]["curiosity"]["subject"],
        "body_curiosity":    result["emails"]["curiosity"]["body"],
        "subject_pain":      result["emails"]["pain"]["subject"],
        "body_pain":         result["emails"]["pain"]["body"],
    }])
    st.download_button(
        "Download all emails as CSV",
        df.to_csv(index=False),
        "outreach.csv",
        "text/csv",
        use_container_width=True,
    )
