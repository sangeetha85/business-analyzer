# =============================================================
# app.py — Business Input Analyzer (100% Offline, No API Key)
# Run: python -m streamlit run app.py
# =============================================================

import json
import streamlit as st
from pipeline import run_pipeline

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Business Input Analyzer",
    page_icon="📋",
    layout="wide",
)

# ── Presets ───────────────────────────────────────────────────
PRESETS = {
    "📧 Email": """Subject: Urgent - CRM Upgrade Project Kickoff

Hi Team,

Following our exec review last week, we've been given the green light to proceed with the CRM system upgrade. The current system (Salesforce Classic) is outdated — our sales reps are spending 40% of their time on manual data entry, leads are falling through the cracks, and we have zero visibility into pipeline health.

Key things we need:
- Migrate to Salesforce Lightning before Q3
- Integrate with our existing ERP (SAP) so orders auto-sync
- Build a mobile app so field reps can update deals on-the-go
- Set up automated lead scoring to prioritize high-value prospects
- Create dashboards for VP Sales to get real-time pipeline view

Timeline: 6 months. Budget: $450K.
Risks: data migration (15 years of legacy data), SAP integration complexity, change management for 200+ sales reps.

- James Chen, VP of Operations""",

    "📝 Meeting Notes": """PROJECT KICKOFF MEETING NOTES
Date: March 15, 2026 | Attendees: Sarah (PM), Dev Team (4), UX Lead, QA, Mark (Stakeholder)

1. Product: New customer-facing mobile banking app
   - Target: existing bank customers aged 25-55
   - Launch deadline: Sept 2026

2. Must-have features:
   - Real-time account balance and transaction history
   - Fund transfers (internal + external)
   - Bill payments with reminders
   - Biometric login (Face ID / fingerprint)
   - Card freeze/unfreeze

3. Technical risks:
   - Legacy core banking system (40+ yrs old) — HIGH RISK integration
   - PCI-DSS compliance required before launch
   - Team understaffed — need 2 more backend devs

4. Success metrics:
   - 50,000 app downloads in first 3 months
   - App store rating 4.5+ stars
   - Transaction error rate below 0.1%
   - Customer support tickets reduced by 30%""",

    "📋 Requirements": """Feature Request: AI-Powered Inventory Management System

Our warehouse ops team needs to replace spreadsheet-based inventory tracking.
We lose ~$2M annually due to stockouts and overstocking.

Key requirements:
1. Demand forecasting with 90%+ accuracy for top 500 SKUs
2. Automated PO generation with supplier EDI communication
3. Multi-warehouse visibility across 8 locations
4. Exception alerts for demand spikes and supplier delays
5. ROI reporting to track waste reduction

Non-functional: <2s page loads, 99.9% uptime, 500 concurrent users, SOX audit trail.
Goals: reduce stockouts 70%, reduce excess inventory 40%, save 20 hrs/week.
Timeline: 9 months. Budget: ~$800K.""",
}

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ About")
    st.markdown("---")

    st.success("✅ No API key needed!")
    st.caption("This app runs 100% offline using rule-based NLP processing.")

    st.markdown("---")
    st.markdown("#### 📌 3-Step Pipeline")
    st.markdown(
        "1. 🧹 **Input Cleaning**  \n   Normalize & clean text\n"
        "2. 🔍 **Requirement Extraction**  \n   Summary + User Stories\n"
        "3. 💡 **Insight Generation**  \n   Risks + KPIs"
    )
    st.markdown("---")
    st.markdown("#### 📥 Input Types")
    st.markdown("- Emails\n- Meeting notes\n- Requirement docs\n- Feature requests")
    st.markdown("---")
    st.markdown("#### 📤 Output")
    st.markdown("- Executive Summary\n- User Stories\n- Risk Register\n- KPI Targets\n- JSON Download")
    st.markdown("---")
    st.caption("Built with Streamlit · 100% Offline · No API Key")

# ── Header ────────────────────────────────────────────────────
st.title("📋 Business Input Analyzer")
st.markdown(
    "Convert unstructured business text into **structured outputs** — "
    "summary, user stories, risks, and KPIs.  \n"
    "**🔓 100% free · No API key · Runs offline**"
)
st.markdown("---")

# ── Presets ───────────────────────────────────────────────────
st.markdown("#### Load Sample Input")
cols = st.columns(len(PRESETS))
for i, (label, content) in enumerate(PRESETS.items()):
    if cols[i].button(label, use_container_width=True):
        st.session_state["input_text"] = content

# ── Text Area ─────────────────────────────────────────────────
st.markdown("#### Business Input")
input_text = st.text_area(
    label="input",
    value=st.session_state.get("input_text", ""),
    height=250,
    placeholder="Paste your email, meeting notes, or requirement description here...",
    key="input_text",
    label_visibility="collapsed",
)
st.caption(f"{len(input_text):,} characters")

# ── Analyze ───────────────────────────────────────────────────
st.markdown("---")
analyze = st.button(
    "⚡ Analyze Now",
    type="primary",
    use_container_width=True,
    disabled=not input_text.strip(),
)

if not input_text.strip():
    st.info("⬆️ Paste or load a sample above to start.")

# ── Pipeline ──────────────────────────────────────────────────
if analyze and input_text.strip():
    st.markdown("---")
    st.markdown("#### ⚙️ Processing Pipeline")

    progress = st.progress(0, text="Starting...")
    status = st.empty()
    result = None

    def on_status(step, msg):
        progress.progress(int((step / 3) * 90), text=msg)
        status.info(msg)

    try:
        result = run_pipeline(raw_text=input_text, status_callback=on_status)
        progress.progress(100, text="✅ Pipeline complete!")
        status.success("✅ Analysis complete! Scroll down for results.")
    except ValueError as e:
        progress.empty()
        status.empty()
        st.error(f"❌ {e}")
    except Exception as e:
        progress.empty()
        status.empty()
        st.error(f"❌ Unexpected error: {e}")

    # ── Results ────────────────────────────────────────────────
    if result:
        st.markdown("---")
        st.markdown("#### 📊 Structured Output")

        t1, t2, t3, t4, t5 = st.tabs(
            ["📝 Summary", "👤 User Stories", "⚠️ Risks", "📊 KPIs", "🔧 JSON"]
        )

        with t1:
            st.markdown("### Executive Summary")
            st.info(result.get("summary", "No summary generated."))

        with t2:
            st.markdown("### User Stories")
            for i, s in enumerate(result.get("userStories", []), 1):
                with st.expander(
                    f"Story {i}: As a {s.get('as', '?')}, I want {s.get('iWant', '?')}",
                    expanded=(i == 1),
                ):
                    st.markdown(f"**Role:** {s.get('as', '')}")
                    st.markdown(f"**I want:** {s.get('iWant', '')}")
                    st.markdown(f"**So that:** {s.get('soThat', '')}")
                    for c in s.get("acceptanceCriteria", []):
                        st.markdown(f"  ✅ {c}")

        with t3:
            st.markdown("### Risk Register")
            icons = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            for r in result.get("risks", []):
                lv = r.get("level", "Medium")
                with st.expander(f"{icons.get(lv, '⚪')} {r.get('title', '')} — {lv}"):
                    st.markdown(f"**Impact:** {r.get('description', '')}")
                    st.markdown(f"**Mitigation:** {r.get('mitigation', '')}")

        with t4:
            st.markdown("### Key Performance Indicators")
            for i, k in enumerate(result.get("kpis", []), 1):
                c1, c2 = st.columns([2, 1])
                c1.markdown(f"**{i}. {k.get('name', '')}**")
                c1.caption(f"📏 {k.get('measurement', '')}")
                c2.metric("Target", k.get("target", "—"))
                if i < len(result.get("kpis", [])):
                    st.divider()

        with t5:
            st.markdown("### Raw JSON Output")
            j = json.dumps(result, indent=2)
            st.code(j, language="json")
            st.download_button("⬇️ Download JSON", j, "business-analysis.json", "application/json")
