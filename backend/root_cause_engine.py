"""
Deterministic LLM Simulation for Root Cause Analysis.
Uses keyword-based classification - no external API calls.
"""
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Root cause definitions with keywords and suggested actions
ROOT_CAUSE_DEFINITIONS = {
    "Policy/Fees Confusion": {
        "keywords": ["fee", "charge", "overdraft", "rate", "interest", "cost", "penalty", "price", "billing", "statement"],
        "description": "Customers confused about fees, charges, and account policies leading to dissatisfaction.",
        "actions": [
            {"text": "Update fee disclosure documents with clearer language", "type": "Policy"},
            {"text": "Implement proactive fee alerts before charges apply", "type": "Digital"},
            {"text": "Train agents on fee waiver authority and escalation", "type": "Training"}
        ]
    },
    "Digital/App Experience": {
        "keywords": ["app", "login", "error", "crash", "password", "otp", "mobile", "online", "website", "frozen", "stuck", "load"],
        "description": "Technical issues with digital banking platforms preventing transactions.",
        "actions": [
            {"text": "Prioritize critical bug fixes in mobile app backlog", "type": "Digital"},
            {"text": "Implement better error messaging with actionable guidance", "type": "Digital"},
            {"text": "Add redundant authentication methods for OTP failures", "type": "Process"}
        ]
    },
    "Processing Delays": {
        "keywords": ["pending", "waiting", "approval", "slow", "days", "weeks", "delay", "status", "long", "taking"],
        "description": "Extended processing times causing customer frustration and business impact.",
        "actions": [
            {"text": "Review and streamline approval workflows", "type": "Process"},
            {"text": "Implement real-time status tracking notifications", "type": "Digital"},
            {"text": "Set and communicate clear SLAs for transaction types", "type": "Policy"}
        ]
    },
    "Incorrect Info / Agent Knowledge Gap": {
        "keywords": ["told me", "different answer", "inconsistent", "agent said", "wrong", "misinformed", "confused", "didn't know"],
        "description": "Agents providing inconsistent or incorrect information requiring multiple contacts.",
        "actions": [
            {"text": "Enhance knowledge base with decision trees", "type": "Training"},
            {"text": "Implement mandatory refresher training on policy updates", "type": "Training"},
            {"text": "Create quality monitoring program with coaching feedback", "type": "Process"}
        ]
    },
    "Fraud & Disputes": {
        "keywords": ["fraud", "dispute", "unauthorized", "chargeback", "stolen", "identity", "theft", "suspicious", "scam"],
        "description": "Fraud incidents and dispute resolution creating anxiety and delays.",
        "actions": [
            {"text": "Streamline fraud claim submission process", "type": "Process"},
            {"text": "Reduce provisional credit timeline for verified customers", "type": "Policy"},
            {"text": "Enhance fraud detection to reduce false positives", "type": "Digital"}
        ]
    },
    "Documentation / KYC Friction": {
        "keywords": ["document", "id", "verification", "kyc", "upload", "proof", "identity", "verify", "rejected", "submit"],
        "description": "Document requirements creating barriers to account access and onboarding.",
        "actions": [
            {"text": "Implement OCR to improve document acceptance rates", "type": "Digital"},
            {"text": "Reduce re-verification frequency for established customers", "type": "Policy"},
            {"text": "Provide clearer guidance on acceptable document formats", "type": "Process"}
        ]
    },
    "Service Experience": {
        "keywords": ["wait", "transfer", "rude", "callback", "hold", "disconnected", "hung up", "attitude", "unprofessional"],
        "description": "Poor service interactions affecting customer satisfaction and loyalty.",
        "actions": [
            {"text": "Implement callback options to reduce hold times", "type": "Process"},
            {"text": "Enhance soft skills training for agents", "type": "Training"},
            {"text": "Create escalation paths that don't require transfers", "type": "Process"}
        ]
    }
}


def classify_interaction(
    complaint_text: str = None,
    call_reason: str = None,
    product: str = None,
    is_complaint: bool = False
) -> Dict[str, Any]:
    """
    Classify an interaction into a root cause category.
    Returns root_cause_label, confidence, and recommended actions.
    """
    if not complaint_text and not is_complaint:
        # Non-complaint interactions get generic classification based on call reason
        return _classify_by_context(call_reason, product)

    text_to_analyze = (complaint_text or "").lower()
    scores = {}

    for category, definition in ROOT_CAUSE_DEFINITIONS.items():
        score = 0
        for keyword in definition["keywords"]:
            if keyword.lower() in text_to_analyze:
                score += 1
        scores[category] = score

    # Find best match
    max_score = max(scores.values()) if scores else 0

    if max_score > 0:
        best_category = max(scores, key=scores.get)
        # Confidence based on keyword matches (more matches = higher confidence)
        confidence = min(0.6 + (max_score * 0.07), 0.95)
    else:
        # Fallback classification based on context
        return _classify_by_context(call_reason, product)

    definition = ROOT_CAUSE_DEFINITIONS[best_category]

    return {
        "root_cause_label": best_category,
        "root_cause_confidence": round(confidence, 2),
        "root_cause_description": definition["description"],
        "recommended_actions": definition["actions"]
    }


def _classify_by_context(call_reason: str, product: str) -> Dict[str, Any]:
    """Fallback classification based on call reason and product."""
    # Default mappings
    reason_to_cause = {
        "Digital Access": "Digital/App Experience",
        "Disputes & Issues": "Fraud & Disputes",
        "Payments & Transactions": "Processing Delays",
        "Account Maintenance": "Documentation / KYC Friction",
        "New Business": "Policy/Fees Confusion",
        "Existing Business": "Service Experience",
        "Information Request": "Incorrect Info / Agent Knowledge Gap"
    }

    category = reason_to_cause.get(call_reason, "Service Experience")
    definition = ROOT_CAUSE_DEFINITIONS[category]

    return {
        "root_cause_label": category,
        "root_cause_confidence": round(0.6 + (hash(f"{call_reason}{product}") % 20) / 100, 2),
        "root_cause_description": definition["description"],
        "recommended_actions": definition["actions"]
    }


def generate_ai_summary(interaction: Dict[str, Any]) -> List[str]:
    """Generate a deterministic AI summary (3-5 bullets) from interaction fields."""
    bullets = []

    # Opening context
    channel = interaction.get("channel", "Phone")
    segment = interaction.get("customer_segment", "Mass")
    bullets.append(f"{segment} customer contacted via {channel} channel.")

    # Call reason and product
    call_reason = interaction.get("call_reason", "")
    product = interaction.get("product", "")
    bullets.append(f"Inquiry related to {call_reason} for {product}.")

    # Complaint specific
    if interaction.get("is_complaint"):
        category = interaction.get("complaint_category", "")
        severity = interaction.get("complaint_severity", "")
        bullets.append(f"Customer filed {severity.lower()} severity complaint regarding {category}.")

    # Resolution status
    resolved = interaction.get("resolved_on_first_contact", False)
    disposition = interaction.get("disposition", "")
    if resolved:
        bullets.append(f"Issue was resolved on first contact. Disposition: {disposition}.")
    else:
        transfers = interaction.get("transfer_count", 0)
        if transfers > 0:
            bullets.append(f"Required {transfers} transfer(s) before resolution. Disposition: {disposition}.")
        else:
            bullets.append(f"Issue not fully resolved on first contact. Disposition: {disposition}.")

    # Digital opportunity
    if interaction.get("digital_eligible"):
        if interaction.get("deflection_success"):
            bullets.append("Customer successfully used self-service option.")
        elif interaction.get("deflection_attempted"):
            reason = interaction.get("digital_failure_reason", "Unknown")
            bullets.append(f"Self-service attempted but failed: {reason}.")

    return bullets[:5]


def analyze_root_causes(
    interactions: List[Dict[str, Any]],
    agent_data: Dict[str, Dict] = None
) -> Dict[str, Any]:
    """
    Analyze a set of interactions for root causes.
    Returns ranked root causes with impact scores and concentration analysis.
    """
    if not interactions:
        return {
            "root_causes": [],
            "executive_summary": "No interactions to analyze.",
            "total_analyzed": 0
        }

    # Group by root cause
    categorized = defaultdict(list)
    for interaction in interactions:
        label = interaction.get("root_cause_label", "Service Experience")
        categorized[label].append(interaction)

    # Calculate metrics for each root cause
    root_causes = []
    total_complaints = sum(1 for i in interactions if i.get("is_complaint"))

    for category, items in categorized.items():
        complaint_items = [i for i in items if i.get("is_complaint")]
        frequency = len(complaint_items) if complaint_items else len(items)

        if frequency == 0:
            continue

        # Calculate metrics
        total_ht = sum(i.get("handling_time_seconds", 0) for i in items)
        avg_ht = total_ht / len(items) if items else 0

        resolved = sum(1 for i in items if i.get("resolved_on_first_contact"))
        fcr_rate = (resolved / len(items) * 100) if items else 0

        # Impact score = frequency * avg handling time (in minutes)
        impact_score = frequency * (avg_ht / 60)

        # Agent concentration analysis
        agent_counts = defaultdict(int)
        for item in complaint_items or items:
            agent_id = item.get("agent_id", "unknown")
            agent_counts[agent_id] += 1

        top_3_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_3_share = sum(count for _, count in top_3_agents) / frequency if frequency > 0 else 0
        is_concentrated = top_3_share >= 0.4

        # Get example complaints
        examples = []
        for item in (complaint_items or items)[:3]:
            text = item.get("complaint_text") or item.get("agent_notes") or ""
            if text:
                examples.append(text[:150] + "..." if len(text) > 150 else text)

        definition = ROOT_CAUSE_DEFINITIONS.get(category, {})

        root_causes.append({
            "root_cause_label": category,
            "description": definition.get("description", ""),
            "frequency": frequency,
            "percentage": round(frequency / max(total_complaints, 1) * 100, 1),
            "avg_handling_time_minutes": round(avg_ht / 60, 1),
            "fcr_rate": round(fcr_rate, 1),
            "impact_score": round(impact_score, 1),
            "concentration": "Agent-Concentrated" if is_concentrated else "Systemic",
            "top_agents": [
                {"agent_id": aid, "count": cnt, "agent_name": agent_data.get(aid, {}).get("agent_name", aid) if agent_data else aid}
                for aid, cnt in top_3_agents
            ],
            "top_agent_share": round(top_3_share * 100, 1),
            "example_complaints": examples,
            "suggested_actions": definition.get("actions", [])
        })

    # Sort by impact score
    root_causes.sort(key=lambda x: x["impact_score"], reverse=True)

    # Generate executive summary
    summary = _generate_executive_summary(root_causes, len(interactions), total_complaints)

    return {
        "root_causes": root_causes,
        "executive_summary": summary,
        "total_analyzed": len(interactions),
        "total_complaints": total_complaints
    }


def _generate_executive_summary(root_causes: List[Dict], total: int, complaints: int) -> str:
    """Generate executive summary paragraph."""
    if not root_causes:
        return "No significant patterns identified in the analyzed interactions."

    parts = [f"Analysis of {total} interactions ({complaints} complaints) identified {len(root_causes)} root cause categories. "]

    if root_causes:
        top = root_causes[0]
        parts.append(
            f"The primary driver is **{top['root_cause_label']}** ({top['percentage']}% of complaints), "
            f"which is **{top['concentration']}** with avg handling time of {top['avg_handling_time_minutes']} min. "
        )

    if len(root_causes) >= 2:
        second = root_causes[1]
        parts.append(f"**{second['root_cause_label']}** ({second['percentage']}%) is the second priority. ")

    # Recommendations
    concentrated = [rc for rc in root_causes if rc["concentration"] == "Agent-Concentrated"]
    if concentrated:
        parts.append(f"\n\n**Immediate Action:** {len(concentrated)} categories show agent concentration - recommend targeted coaching. ")

    if root_causes:
        parts.append(f"**Top Priority:** {root_causes[0]['suggested_actions'][0]['text']}.")

    return "".join(parts)
