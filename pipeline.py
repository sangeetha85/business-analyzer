# =============================================================
# pipeline.py — 3-step NLP pipeline (100% offline, no API key)
# Uses rule-based text processing to demonstrate the pipeline
# =============================================================

import re
import json
import time


# ═══════════════════════════════════════════════════════════════
# STEP 1: Input Cleaning
# ═══════════════════════════════════════════════════════════════
def step1_clean(raw_text: str) -> str:
    """
    Clean and normalize raw business input text.
    - Fix whitespace and formatting issues
    - Normalize bullet points
    - Remove email headers noise
    - Standardize line spacing
    """
    if not raw_text.strip():
        raise ValueError("Input text cannot be empty.")

    text = raw_text

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive blank lines (keep max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize bullet points to consistent format
    text = re.sub(r"^\s*[-•●◦▪]\s*", "- ", text, flags=re.MULTILINE)

    # Remove trailing whitespace per line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # Normalize multiple spaces to single space
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Fix common abbreviations spacing
    text = re.sub(r"\bi\.e\b", "i.e.", text)
    text = re.sub(r"\be\.g\b", "e.g.", text)

    return text.strip()


# ═══════════════════════════════════════════════════════════════
# STEP 2: Requirement Extraction
# ═══════════════════════════════════════════════════════════════
def step2_extract(cleaned_text: str) -> dict:
    """
    Extract summary and user stories from cleaned text using
    keyword matching and pattern extraction.
    """
    lines = cleaned_text.split("\n")
    lower_text = cleaned_text.lower()

    # --- Build Summary ---
    summary_parts = []

    # Detect project type
    project_keywords = {
        "crm": "CRM system upgrade",
        "mobile app": "mobile application development",
        "banking": "banking application",
        "inventory": "inventory management system",
        "warehouse": "warehouse operations solution",
        "migration": "system migration",
        "dashboard": "analytics dashboard",
        "ecommerce": "e-commerce platform",
        "erp": "ERP integration",
    }
    project_type = "business initiative"
    for kw, desc in project_keywords.items():
        if kw in lower_text:
            project_type = desc
            break

    summary_parts.append(f"This initiative involves a {project_type}.")

    # Extract timeline
    timeline_match = re.search(
        r"(?:timeline|deadline|launch|complete|deliver)\s*[:\-]?\s*(\d+\s*(?:month|week|year|quarter)s?|(?:Q[1-4]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*\d{0,4})",
        cleaned_text,
        re.IGNORECASE,
    )
    if timeline_match:
        summary_parts.append(f"The target timeline is {timeline_match.group(1).strip()}.")

    # Extract budget
    budget_match = re.search(
        r"\$\s*[\d,.]+\s*[KkMmBb]?|\d+\s*(?:thousand|million|billion)?\s*(?:dollars|USD)",
        cleaned_text,
    )
    if budget_match:
        summary_parts.append(f"The allocated budget is {budget_match.group(0).strip()}.")

    # Extract key problem
    problem_patterns = [
        r"(?:issue|problem|challenge|pain point|causing)[s]?\s*[:\-]?\s*([^.\n]{15,80})",
        r"(?:currently|outdated|losing|lacking|no visibility)[^.\n]{10,80}",
    ]
    for pat in problem_patterns:
        m = re.search(pat, cleaned_text, re.IGNORECASE)
        if m:
            problem_text = m.group(0).strip().rstrip(".,")
            summary_parts.append(f"Key driver: {problem_text}.")
            break

    # Count requirements
    req_lines = [l for l in lines if re.match(r"^\s*[-•\d]+[.)]\s", l)]
    if req_lines:
        summary_parts.append(f"The scope includes {len(req_lines)} identified requirements.")

    summary = " ".join(summary_parts)

    # --- Build User Stories ---
    user_stories = []
    requirements = _extract_requirements(lines, lower_text)

    # Detect roles mentioned
    roles = _detect_roles(cleaned_text)
    if not roles:
        roles = ["End User", "System Administrator", "Manager"]

    for i, req in enumerate(requirements[:6]):
        role = roles[i % len(roles)]
        criteria = _generate_acceptance_criteria(req)
        user_stories.append(
            {
                "as": role,
                "iWant": req,
                "soThat": _generate_business_value(req, lower_text),
                "acceptanceCriteria": criteria,
            }
        )

    # Ensure at least 4 stories
    if len(user_stories) < 4:
        generic_stories = _generate_generic_stories(lower_text, roles)
        user_stories.extend(generic_stories[: 4 - len(user_stories)])

    return {"summary": summary, "userStories": user_stories}


# ═══════════════════════════════════════════════════════════════
# STEP 3: Insight Generation
# ═══════════════════════════════════════════════════════════════
def step3_insights(cleaned_text: str, user_stories: list) -> dict:
    """
    Generate risks and KPIs based on extracted context.
    """
    lower_text = cleaned_text.lower()

    # --- Generate Risks ---
    risks = []
    risk_patterns = _detect_risk_patterns(lower_text)
    for title, level, desc, mitigation in risk_patterns[:6]:
        risks.append(
            {
                "title": title,
                "level": level,
                "description": desc,
                "mitigation": mitigation,
            }
        )

    # Pad to at least 4
    if len(risks) < 4:
        generic_risks = _generic_risks(lower_text)
        risks.extend(generic_risks[: 4 - len(risks)])

    # --- Generate KPIs ---
    kpis = _generate_kpis(lower_text, user_stories)

    return {"risks": risks, "kpis": kpis}


# ═══════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════
def run_pipeline(raw_text: str, status_callback=None) -> dict:
    """
    Run the full 3-step pipeline. No API key needed.
    """

    def notify(step, msg):
        if status_callback:
            status_callback(step, msg)

    notify(1, "🧹 Step 1/3: Cleaning and normalizing input text...")
    time.sleep(0.8)
    cleaned = step1_clean(raw_text)

    notify(2, "🔍 Step 2/3: Extracting requirements and user stories...")
    time.sleep(1.0)
    extraction = step2_extract(cleaned)

    notify(3, "💡 Step 3/3: Generating risks and KPI recommendations...")
    time.sleep(0.8)
    insights = step3_insights(cleaned, extraction.get("userStories", []))

    return {
        "metadata": {
            "pipeline": ["Input Cleaning", "Requirement Extraction", "Insight Generation"],
            "engine": "Rule-based NLP (offline)",
        },
        "summary": extraction.get("summary", ""),
        "userStories": extraction.get("userStories", []),
        "risks": insights.get("risks", []),
        "kpis": insights.get("kpis", []),
    }


# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

def _extract_requirements(lines: list, lower_text: str) -> list:
    """Extract action items / requirements from text lines."""
    reqs = []
    for line in lines:
        stripped = line.strip()
        # Match bullet/numbered items with meaningful content
        if re.match(r"^[-•\d]+[.)]\s", stripped) and len(stripped) > 20:
            cleaned_req = re.sub(r"^[-•\d]+[.)]\s*", "", stripped).strip()
            if cleaned_req and len(cleaned_req) > 10:
                reqs.append(cleaned_req)
        # Match "Need to" / "Must" / "Should" patterns
        elif re.match(r"^\s*[-•]\s*", stripped):
            content = re.sub(r"^\s*[-•]\s*", "", stripped).strip()
            if content and len(content) > 15:
                reqs.append(content)
    return reqs


def _detect_roles(text: str) -> list:
    """Detect user roles mentioned in text."""
    role_patterns = [
        (r"sales\s*rep", "Sales Representative"),
        (r"vp\s*(?:of)?\s*(?:sales|operations|engineering)", "VP of Operations"),
        (r"developer|dev\s*team|engineer", "Developer"),
        (r"project\s*manager|pm\b", "Project Manager"),
        (r"customer|end.?user|user", "End User"),
        (r"warehouse\s*manager", "Warehouse Manager"),
        (r"admin|administrator", "System Administrator"),
        (r"manager", "Manager"),
        (r"analyst", "Business Analyst"),
        (r"stakeholder", "Stakeholder"),
        (r"qa|tester|quality", "QA Engineer"),
        (r"ux|designer", "UX Designer"),
    ]
    roles = []
    lower = text.lower()
    for pattern, role in role_patterns:
        if re.search(pattern, lower) and role not in roles:
            roles.append(role)
    return roles if roles else ["End User", "Manager", "Administrator"]


def _generate_business_value(requirement: str, context: str) -> str:
    """Generate a business value statement based on the requirement."""
    req_lower = requirement.lower()
    if any(w in req_lower for w in ["dashboard", "report", "visibility", "view"]):
        return "decision-makers have real-time data to make informed strategic choices"
    if any(w in req_lower for w in ["mobile", "app", "field"]):
        return "team members can work efficiently from any location"
    if any(w in req_lower for w in ["automate", "automatic", "auto-sync", "scoring"]):
        return "manual effort is reduced and accuracy is improved"
    if any(w in req_lower for w in ["integrate", "sync", "connect", "erp"]):
        return "data flows seamlessly between systems without manual intervention"
    if any(w in req_lower for w in ["migrate", "upgrade", "modernize"]):
        return "the team can leverage modern capabilities and improved performance"
    if any(w in req_lower for w in ["security", "compliance", "biometric", "auth"]):
        return "the system meets regulatory requirements and protects sensitive data"
    if any(w in req_lower for w in ["alert", "notification", "monitor"]):
        return "issues are detected early and addressed before they escalate"
    return "operational efficiency is improved and business objectives are met"


def _generate_acceptance_criteria(requirement: str) -> list:
    """Generate acceptance criteria from a requirement."""
    req_lower = requirement.lower()
    criteria = []

    if any(w in req_lower for w in ["real-time", "dashboard", "view"]):
        criteria.extend(["Data refreshes within 30 seconds", "Supports filtering by date range"])
    elif any(w in req_lower for w in ["mobile", "app"]):
        criteria.extend(["Works on iOS and Android", "Functions offline with sync on reconnect"])
    elif any(w in req_lower for w in ["integrate", "sync", "erp"]):
        criteria.extend(["Sync completes within 5 minutes", "Error notifications on sync failures"])
    elif any(w in req_lower for w in ["automate", "automatic", "scoring"]):
        criteria.extend(["Process runs without manual intervention", "Results are auditable"])
    elif any(w in req_lower for w in ["security", "biometric", "compliance"]):
        criteria.extend(["Passes security audit requirements", "Supports multi-factor authentication"])
    else:
        criteria.extend(["Feature meets documented specifications", "User acceptance testing passes"])

    criteria.append("Performance meets defined SLA thresholds")
    return criteria[:3]


def _generate_generic_stories(lower_text: str, roles: list) -> list:
    """Generate generic stories when not enough were extracted."""
    generics = [
        {"as": roles[0] if roles else "End User", "iWant": "a modern, intuitive interface for the system", "soThat": "I can complete my tasks efficiently with minimal training", "acceptanceCriteria": ["Interface is responsive", "Key actions require 3 clicks or fewer", "Supports accessibility standards"]},
        {"as": roles[1 % len(roles)] if roles else "Manager", "iWant": "comprehensive reporting and analytics", "soThat": "I can track progress and measure ROI", "acceptanceCriteria": ["Reports update in real-time", "Supports CSV/PDF export", "Custom date range filtering"]},
        {"as": roles[2 % len(roles)] if roles else "Administrator", "iWant": "role-based access control and audit logging", "soThat": "sensitive data is protected and all actions are traceable", "acceptanceCriteria": ["Minimum 3 role levels", "All changes logged with timestamp", "Compliant with security policies"]},
        {"as": "Stakeholder", "iWant": "the project delivered on time and within budget", "soThat": "we achieve the expected return on investment", "acceptanceCriteria": ["Milestones met per project plan", "Budget variance within 10%", "Post-launch review completed"]},
    ]
    return generics


def _detect_risk_patterns(lower_text: str) -> list:
    """Detect risks based on keyword patterns in text."""
    risks = []

    if any(w in lower_text for w in ["legacy", "old system", "outdated", "40+"]):
        risks.append(("Legacy System Integration", "High", "Integration with legacy systems poses significant technical challenges including API incompatibility, data format mismatches, and potential system instability.", "Dedicate integration specialists early, build adapter layers, and run parallel systems during transition."))

    if any(w in lower_text for w in ["migration", "migrate", "data migration"]):
        risks.append(("Data Migration Complexity", "High", "Migrating historical data risks data loss, corruption, or format incompatibility, especially with large or poorly documented datasets.", "Conduct data audit first, perform test migrations, maintain rollback capability, and validate data integrity post-migration."))

    if any(w in lower_text for w in ["timeline", "tight", "deadline", "6 month", "9 month"]):
        risks.append(("Timeline Pressure", "High", "Aggressive project timeline may lead to scope cuts, quality compromises, or team burnout.", "Prioritize features using MoSCoW method, build buffer into schedule, and plan phased releases."))

    if any(w in lower_text for w in ["compliance", "pci", "sox", "regulation", "security", "audit"]):
        risks.append(("Regulatory Compliance", "High", "Non-compliance with required regulations could delay launch or result in legal/financial penalties.", "Engage compliance team from project start, schedule audit checkpoints, and document all controls."))

    if any(w in lower_text for w in ["understaffed", "need more", "resource", "staffing"]):
        risks.append(("Resource Constraints", "Medium", "Insufficient staffing could slow delivery and overburden existing team members.", "Initiate hiring immediately, consider contractors for short-term needs, and re-prioritize scope."))

    if any(w in lower_text for w in ["training", "change management", "adoption", "200+", "reps"]):
        risks.append(("Change Management", "Medium", "Users may resist adopting new systems, undermining ROI and leading to shadow IT workarounds.", "Plan early stakeholder engagement, provide role-specific training, and identify internal champions."))

    if any(w in lower_text for w in ["budget", "$", "cost"]):
        risks.append(("Budget Overrun", "Medium", "Scope creep, unforeseen technical challenges, or vendor cost increases could exhaust the budget.", "Implement change control process, track budget weekly, and maintain 10-15% contingency reserve."))

    if any(w in lower_text for w in ["vendor", "third-party", "external", "supplier"]):
        risks.append(("Vendor Dependency", "Medium", "Reliance on third-party vendors introduces risks of delays, cost changes, or service quality issues.", "Establish clear SLAs, evaluate multiple vendors, and maintain internal capability for critical functions."))

    if any(w in lower_text for w in ["mobile", "app", "ios", "android"]):
        risks.append(("Cross-Platform Compatibility", "Low", "Supporting multiple platforms increases testing complexity and potential for platform-specific bugs.", "Use cross-platform framework, establish device testing matrix, and automate regression testing."))

    if any(w in lower_text for w in ["performance", "uptime", "sla", "load"]):
        risks.append(("Performance & Scalability", "Low", "System may not handle peak loads or meet performance SLAs under production conditions.", "Conduct load testing early, design for horizontal scaling, and establish monitoring/alerting."))

    return risks


def _generic_risks(lower_text: str) -> list:
    """Fallback generic risks."""
    return [
        {"title": "Scope Creep", "level": "Medium", "description": "Uncontrolled changes to project scope may delay delivery and exceed budget.", "mitigation": "Establish formal change request process with impact assessment before approval."},
        {"title": "Technical Debt", "level": "Medium", "description": "Pressure to deliver quickly may result in shortcuts that increase long-term maintenance costs.", "mitigation": "Allocate 20% of sprint capacity for refactoring and enforce code review standards."},
        {"title": "Knowledge Concentration", "level": "Low", "description": "Critical knowledge held by few team members creates single points of failure.", "mitigation": "Implement pair programming, maintain documentation, and cross-train team members."},
        {"title": "Stakeholder Alignment", "level": "Low", "description": "Misaligned expectations between stakeholders may cause rework or dissatisfaction.", "mitigation": "Hold bi-weekly stakeholder demos and maintain a shared requirements document."},
    ]


def _generate_kpis(lower_text: str, user_stories: list) -> list:
    """Generate KPIs based on context."""
    kpis = []

    if any(w in lower_text for w in ["time", "manual", "data entry", "hours"]):
        kpis.append({"name": "Manual Effort Reduction", "target": "50% reduction in manual tasks", "measurement": "Time tracking comparison: pre vs post implementation, measured monthly"})

    if any(w in lower_text for w in ["download", "user", "adoption", "active"]):
        kpis.append({"name": "User Adoption Rate", "target": "≥ 80% of target users active within 60 days", "measurement": "Active user logins / total licensed users, tracked weekly"})

    if any(w in lower_text for w in ["error", "accuracy", "quality", "defect"]):
        kpis.append({"name": "Error Rate Reduction", "target": "< 0.5% transaction error rate", "measurement": "Automated error monitoring with daily exception reports"})

    if any(w in lower_text for w in ["customer", "satisfaction", "support", "ticket"]):
        kpis.append({"name": "Customer Satisfaction", "target": "NPS score ≥ 40 or CSAT ≥ 4.0/5.0", "measurement": "Post-interaction surveys, tracked monthly"})

    if any(w in lower_text for w in ["budget", "$", "cost", "roi", "save"]):
        kpis.append({"name": "ROI & Cost Savings", "target": "Positive ROI within 12 months of launch", "measurement": "Quarterly financial review comparing costs vs. documented savings"})

    if any(w in lower_text for w in ["performance", "load", "speed", "uptime"]):
        kpis.append({"name": "System Performance", "target": "99.9% uptime, < 2s page load", "measurement": "Application performance monitoring (APM) dashboards"})

    if any(w in lower_text for w in ["timeline", "deadline", "milestone", "deliver"]):
        kpis.append({"name": "On-Time Delivery", "target": "100% of milestones delivered within ±1 week", "measurement": "Project management tool tracking against baseline schedule"})

    if any(w in lower_text for w in ["stockout", "inventory", "forecast"]):
        kpis.append({"name": "Forecast Accuracy", "target": "≥ 85% demand forecast accuracy", "measurement": "Monthly comparison of predicted vs actual demand per SKU"})

    # Ensure at least 4 KPIs
    generic_kpis = [
        {"name": "Project Delivery", "target": "Go-live on schedule, within approved budget", "measurement": "Weekly status reports tracking milestone completion and budget burn rate"},
        {"name": "Stakeholder Satisfaction", "target": "≥ 4/5 rating in stakeholder survey", "measurement": "Quarterly stakeholder feedback survey post-launch"},
        {"name": "Process Efficiency", "target": "30% improvement in key workflow completion time", "measurement": "Before/after time study on top 5 business-critical workflows"},
        {"name": "System Reliability", "target": "< 2 critical incidents per quarter", "measurement": "Incident management system tracking, reviewed in monthly ops review"},
    ]

    while len(kpis) < 5:
        for g in generic_kpis:
            if g["name"] not in [k["name"] for k in kpis]:
                kpis.append(g)
                break
        else:
            break

    return kpis[:6]
