"""
Simulated AI Service for Executive Summary Generation.
Uses template-based generation with actual metrics - no external API calls.
"""
from typing import Dict, Any, List, Optional
from collections import defaultdict
import random

# Severity thresholds for anomaly detection
ANOMALY_THRESHOLDS = {
    "complaint_rate_high": 25.0,  # % considered high
    "complaint_rate_change": 10.0,  # % WoW change considered significant
    "fcr_rate_low": 65.0,  # % considered low
    "aht_high": 12.0,  # minutes considered high
    "escalation_high": 15.0,  # % considered high
}

# Templates for executive summary generation
SUMMARY_TEMPLATES = {
    "opening": [
        "Analysis of {total_interactions:,} interactions ({complaint_count:,} complaints) reveals {key_finding}.",
        "Review of {total_interactions:,} call center interactions shows {key_finding}.",
        "Current period data ({total_interactions:,} interactions) indicates {key_finding}.",
    ],
    "complaint_trend_up": [
        "Complaint rate increased {change:.1f}% week-over-week to {current:.1f}%, driven primarily by {top_driver}.",
        "Complaints rose {change:.1f}% WoW, reaching {current:.1f}%. Primary contributor: {top_driver}.",
    ],
    "complaint_trend_down": [
        "Complaint rate improved by {change:.1f}% week-over-week, now at {current:.1f}%.",
        "Positive trend: complaints decreased {change:.1f}% WoW to {current:.1f}%.",
    ],
    "complaint_trend_stable": [
        "Complaint rate remains stable at {current:.1f}% (±{change:.1f}% WoW).",
    ],
    "fcr_concern": [
        "First Contact Resolution at {fcr:.1f}% is below target, contributing to repeat contacts.",
        "FCR rate of {fcr:.1f}% indicates resolution challenges requiring attention.",
    ],
    "agent_concentration": [
        "{count} root cause categories show agent concentration - targeted coaching recommended.",
        "Agent-specific patterns detected in {count} categories, suggesting training gaps.",
    ],
    "action_intro": [
        "**Recommended Priority Actions:**",
        "**Immediate Actions Required:**",
    ],
}

# Action templates by root cause category
ACTION_TEMPLATES = {
    "Policy/Fees Confusion": [
        {"text": "Review fee disclosure clarity on statements and online", "impact": "Medium", "effort": "Low"},
        {"text": "Implement proactive balance/fee alerts before charges", "impact": "High", "effort": "Medium"},
        {"text": "Update agent fee waiver authority matrix", "impact": "Medium", "effort": "Low"},
    ],
    "Digital/App Experience": [
        {"text": "Prioritize critical bug fixes in mobile app backlog", "impact": "High", "effort": "High"},
        {"text": "Add fallback authentication for OTP delivery failures", "impact": "High", "effort": "Medium"},
        {"text": "Improve error messaging with actionable guidance", "impact": "Medium", "effort": "Low"},
    ],
    "Processing Delays": [
        {"text": "Review and streamline approval workflows", "impact": "High", "effort": "High"},
        {"text": "Implement real-time transaction status notifications", "impact": "High", "effort": "Medium"},
        {"text": "Set and communicate clear SLAs to customers", "impact": "Medium", "effort": "Low"},
    ],
    "Incorrect Info / Agent Knowledge Gap": [
        {"text": "Deploy updated knowledge base with decision trees", "impact": "High", "effort": "Medium"},
        {"text": "Schedule mandatory policy refresh training", "impact": "Medium", "effort": "Medium"},
        {"text": "Implement QA monitoring with coaching feedback", "impact": "High", "effort": "High"},
    ],
    "Fraud & Disputes": [
        {"text": "Streamline fraud claim submission and tracking", "impact": "High", "effort": "Medium"},
        {"text": "Accelerate provisional credit for verified customers", "impact": "High", "effort": "Medium"},
        {"text": "Enhance fraud detection to reduce false positives", "impact": "Medium", "effort": "High"},
    ],
    "Documentation / KYC Friction": [
        {"text": "Implement OCR for improved document acceptance", "impact": "High", "effort": "High"},
        {"text": "Reduce re-verification frequency for established customers", "impact": "Medium", "effort": "Low"},
        {"text": "Provide clearer guidance on acceptable document formats", "impact": "Medium", "effort": "Low"},
    ],
    "Service Experience": [
        {"text": "Implement callback options to reduce hold times", "impact": "High", "effort": "Medium"},
        {"text": "Enhance soft skills training for agents", "impact": "Medium", "effort": "Medium"},
        {"text": "Create escalation paths that minimize transfers", "impact": "High", "effort": "Medium"},
    ],
}


def generate_executive_summary(
    metrics: Dict[str, Any],
    root_causes: List[Dict[str, Any]],
    comparison: Optional[Dict[str, Any]] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate an AI executive summary from metrics and root cause data.

    Args:
        metrics: Current period metrics (total_interactions, complaint_rate, fcr_rate, etc.)
        root_causes: List of root cause analysis results
        comparison: Optional comparison data with previous period
        filters: Optional filters applied (for context)

    Returns:
        Dict with summary sections: key_finding, details, actions, positive_trends, raw_analysis
    """
    result = {
        "key_finding": "",
        "details": [],
        "actions": [],
        "positive_trends": [],
        "anomalies": [],
        "generated_summary": "",
        "confidence": 0.85,  # Simulated confidence score
    }

    # Extract key metrics
    total = metrics.get("total_interactions", 0)
    complaints = metrics.get("total_complaints", 0)
    complaint_rate = metrics.get("complaint_rate", 0)
    fcr_rate = metrics.get("fcr_rate", 0)
    aht = metrics.get("avg_handling_time_minutes", 0)
    escalation_rate = metrics.get("escalation_rate", 0)

    if total == 0:
        result["key_finding"] = "No data available for the selected period and filters."
        result["generated_summary"] = result["key_finding"]
        return result

    # Detect anomalies
    anomalies = []

    if complaint_rate > ANOMALY_THRESHOLDS["complaint_rate_high"]:
        anomalies.append({
            "type": "high_complaint_rate",
            "severity": "high",
            "message": f"Complaint rate ({complaint_rate:.1f}%) exceeds threshold ({ANOMALY_THRESHOLDS['complaint_rate_high']}%)"
        })

    if fcr_rate < ANOMALY_THRESHOLDS["fcr_rate_low"]:
        anomalies.append({
            "type": "low_fcr",
            "severity": "medium",
            "message": f"FCR rate ({fcr_rate:.1f}%) below target ({ANOMALY_THRESHOLDS['fcr_rate_low']}%)"
        })

    if aht > ANOMALY_THRESHOLDS["aht_high"]:
        anomalies.append({
            "type": "high_aht",
            "severity": "medium",
            "message": f"AHT ({aht:.1f} min) exceeds benchmark ({ANOMALY_THRESHOLDS['aht_high']} min)"
        })

    if escalation_rate > ANOMALY_THRESHOLDS["escalation_high"]:
        anomalies.append({
            "type": "high_escalation",
            "severity": "medium",
            "message": f"Escalation rate ({escalation_rate:.1f}%) above normal ({ANOMALY_THRESHOLDS['escalation_high']}%)"
        })

    result["anomalies"] = anomalies

    # Determine key finding based on data patterns
    top_root_cause = root_causes[0] if root_causes else None
    key_finding = _determine_key_finding(complaint_rate, fcr_rate, top_root_cause, comparison)
    result["key_finding"] = key_finding

    # Generate details based on trends
    details = []

    if comparison and comparison.get("deltas"):
        deltas = comparison["deltas"]
        complaint_delta = deltas.get("complaint_rate", {})

        if complaint_delta.get("absolute", 0) > 0:
            top_driver = top_root_cause["root_cause_label"] if top_root_cause else "multiple factors"
            template = random.choice(SUMMARY_TEMPLATES["complaint_trend_up"])
            details.append(template.format(
                change=abs(complaint_delta.get("absolute", 0)),
                current=complaint_rate,
                top_driver=top_driver
            ))
        elif complaint_delta.get("absolute", 0) < -2:
            template = random.choice(SUMMARY_TEMPLATES["complaint_trend_down"])
            details.append(template.format(
                change=abs(complaint_delta.get("absolute", 0)),
                current=complaint_rate
            ))
        else:
            template = random.choice(SUMMARY_TEMPLATES["complaint_trend_stable"])
            details.append(template.format(
                current=complaint_rate,
                change=abs(complaint_delta.get("absolute", 0))
            ))

    # Add FCR concern if applicable
    if fcr_rate < ANOMALY_THRESHOLDS["fcr_rate_low"]:
        template = random.choice(SUMMARY_TEMPLATES["fcr_concern"])
        details.append(template.format(fcr=fcr_rate))

    # Add agent concentration insight
    concentrated = [rc for rc in root_causes if rc.get("concentration") == "Agent-Concentrated"]
    if concentrated:
        template = random.choice(SUMMARY_TEMPLATES["agent_concentration"])
        details.append(template.format(count=len(concentrated)))

    result["details"] = details

    # Generate prioritized actions
    actions = _generate_prioritized_actions(root_causes, anomalies, metrics)
    result["actions"] = actions

    # Identify positive trends
    positive_trends = []
    if comparison and comparison.get("deltas"):
        deltas = comparison["deltas"]

        if deltas.get("fcr_rate", {}).get("absolute", 0) > 2:
            positive_trends.append(f"FCR improved {deltas['fcr_rate']['absolute']:.1f}% WoW")

        if deltas.get("avg_handling_time_minutes", {}).get("absolute", 0) < -0.5:
            positive_trends.append(f"AHT reduced by {abs(deltas['avg_handling_time_minutes']['absolute']):.1f} minutes WoW")

        if deltas.get("escalation_rate", {}).get("absolute", 0) < -2:
            positive_trends.append(f"Escalation rate down {abs(deltas['escalation_rate']['absolute']):.1f}% WoW")

    result["positive_trends"] = positive_trends

    # Build the full generated summary
    summary_parts = []

    # Opening
    template = random.choice(SUMMARY_TEMPLATES["opening"])
    summary_parts.append(template.format(
        total_interactions=total,
        complaint_count=complaints,
        key_finding=key_finding.lower()
    ))

    # Details
    for detail in details[:3]:  # Limit to 3 details
        summary_parts.append(detail)

    # Actions
    if actions:
        summary_parts.append("")
        summary_parts.append(random.choice(SUMMARY_TEMPLATES["action_intro"]))
        for i, action in enumerate(actions[:3], 1):
            impact_str = f" (est. impact: {action.get('estimated_impact', 'TBD')})" if action.get("estimated_impact") else ""
            summary_parts.append(f"{i}. {action['text']}{impact_str}")

    # Positive trends
    if positive_trends:
        summary_parts.append("")
        summary_parts.append("**Positive Developments:** " + "; ".join(positive_trends))

    result["generated_summary"] = "\n".join(summary_parts)

    return result


def _determine_key_finding(
    complaint_rate: float,
    fcr_rate: float,
    top_root_cause: Optional[Dict],
    comparison: Optional[Dict]
) -> str:
    """Determine the most important finding to highlight."""

    # Check for significant WoW change
    if comparison and comparison.get("deltas"):
        complaint_change = comparison["deltas"].get("complaint_rate", {}).get("absolute", 0)

        if complaint_change > ANOMALY_THRESHOLDS["complaint_rate_change"]:
            if top_root_cause:
                return f"significant complaint increase ({complaint_change:+.1f}% WoW) driven by {top_root_cause['root_cause_label']}"
            return f"significant complaint rate increase of {complaint_change:+.1f}% week-over-week"

        if complaint_change < -ANOMALY_THRESHOLDS["complaint_rate_change"]:
            return f"notable improvement in complaint rate ({complaint_change:.1f}% WoW)"

    # Check absolute levels
    if complaint_rate > ANOMALY_THRESHOLDS["complaint_rate_high"]:
        if top_root_cause:
            return f"elevated complaint rate ({complaint_rate:.1f}%) with {top_root_cause['root_cause_label']} as primary driver"
        return f"elevated complaint rate at {complaint_rate:.1f}%"

    if fcr_rate < ANOMALY_THRESHOLDS["fcr_rate_low"]:
        return f"FCR challenges with {fcr_rate:.1f}% resolution rate"

    # Stable state
    if top_root_cause:
        return f"stable operations with {top_root_cause['root_cause_label']} as top focus area"

    return "stable performance across key metrics"


def _generate_prioritized_actions(
    root_causes: List[Dict],
    anomalies: List[Dict],
    metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate prioritized action recommendations."""

    actions = []
    action_set = set()  # Track unique actions

    # Add actions based on top root causes
    for rc in root_causes[:3]:
        rc_label = rc.get("root_cause_label", "")
        rc_templates = ACTION_TEMPLATES.get(rc_label, [])

        for template in rc_templates[:2]:
            if template["text"] not in action_set:
                action_set.add(template["text"])

                # Estimate impact based on root cause frequency
                frequency = rc.get("frequency", 0)
                percentage = rc.get("percentage", 0)

                if percentage > 20:
                    estimated_impact = f"-{int(percentage * 0.3)}-{int(percentage * 0.5)}% complaints"
                elif percentage > 10:
                    estimated_impact = f"-{int(percentage * 0.2)}-{int(percentage * 0.3)}% complaints"
                else:
                    estimated_impact = "Incremental improvement"

                actions.append({
                    "text": template["text"],
                    "impact": template["impact"],
                    "effort": template["effort"],
                    "root_cause": rc_label,
                    "estimated_impact": estimated_impact,
                    "priority": len(actions) + 1
                })

    # Add actions based on anomalies
    if any(a["type"] == "low_fcr" for a in anomalies):
        action_text = "Review resolution workflows and knowledge base coverage"
        if action_text not in action_set:
            action_set.add(action_text)
            actions.append({
                "text": action_text,
                "impact": "High",
                "effort": "Medium",
                "root_cause": "FCR Gap",
                "estimated_impact": f"+{int((70 - metrics.get('fcr_rate', 60)) * 0.5)}% FCR improvement",
                "priority": len(actions) + 1
            })

    if any(a["type"] == "high_escalation" for a in anomalies):
        action_text = "Review escalation criteria and agent authorization levels"
        if action_text not in action_set:
            action_set.add(action_text)
            actions.append({
                "text": action_text,
                "impact": "Medium",
                "effort": "Low",
                "root_cause": "Escalation Rate",
                "estimated_impact": f"-{int(metrics.get('escalation_rate', 10) * 0.2)}% escalations",
                "priority": len(actions) + 1
            })

    # Sort by priority
    actions.sort(key=lambda x: x["priority"])

    return actions[:5]  # Return top 5 actions


def generate_enhanced_root_cause(
    root_cause: Dict[str, Any],
    interactions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Enhance a root cause category with deeper AI analysis.

    Args:
        root_cause: Base root cause data from analyze_root_causes
        interactions: List of interactions for this root cause

    Returns:
        Enhanced root cause with sub-issues, correlations, and personalized actions
    """
    rc_label = root_cause.get("root_cause_label", "")

    # Simulate sub-issue detection
    sub_issues = _detect_sub_issues(rc_label, interactions)

    # Detect correlations
    correlations = _detect_correlations(interactions)

    # Generate personalized actions
    personalized_actions = _generate_personalized_actions(
        rc_label,
        sub_issues,
        correlations,
        root_cause
    )

    # Calculate predicted impact
    frequency = root_cause.get("frequency", 0)
    predicted_impact = _calculate_predicted_impact(frequency, sub_issues)

    return {
        **root_cause,
        "ai_analysis": {
            "sub_issues": sub_issues,
            "correlations": correlations,
            "personalized_actions": personalized_actions,
            "predicted_impact": predicted_impact,
            "confidence": 0.78 + random.random() * 0.15,  # 0.78-0.93
            "analysis_summary": _generate_analysis_summary(rc_label, sub_issues, correlations)
        }
    }


def _detect_sub_issues(rc_label: str, interactions: List[Dict]) -> List[Dict[str, Any]]:
    """Simulate sub-issue detection within a root cause category."""

    # Pre-defined sub-issue patterns by root cause
    sub_issue_patterns = {
        "Policy/Fees Confusion": [
            {"name": "Overdraft fees", "keywords": ["overdraft", "nsf", "insufficient"]},
            {"name": "Monthly maintenance fees", "keywords": ["monthly", "maintenance", "service charge"]},
            {"name": "Wire transfer fees", "keywords": ["wire", "transfer", "international"]},
        ],
        "Digital/App Experience": [
            {"name": "Login failures", "keywords": ["login", "password", "sign in", "access"]},
            {"name": "Transfer timeouts", "keywords": ["timeout", "slow", "transfer", "pending"]},
            {"name": "UI/Navigation issues", "keywords": ["find", "confusing", "navigate", "where"]},
        ],
        "Processing Delays": [
            {"name": "Application processing", "keywords": ["application", "approval", "waiting"]},
            {"name": "Transaction posting", "keywords": ["post", "clear", "pending", "available"]},
            {"name": "Document verification", "keywords": ["document", "verify", "review"]},
        ],
        "Incorrect Info / Agent Knowledge Gap": [
            {"name": "Policy misinformation", "keywords": ["policy", "told", "different", "wrong"]},
            {"name": "Product feature confusion", "keywords": ["feature", "how to", "supposed"]},
            {"name": "Process guidance errors", "keywords": ["process", "steps", "said"]},
        ],
        "Fraud & Disputes": [
            {"name": "Unauthorized transactions", "keywords": ["unauthorized", "fraud", "didn't"]},
            {"name": "Merchant disputes", "keywords": ["merchant", "refund", "return"]},
            {"name": "Identity theft", "keywords": ["identity", "account opened", "not me"]},
        ],
        "Documentation / KYC Friction": [
            {"name": "Document rejection", "keywords": ["rejected", "not accepted", "blurry"]},
            {"name": "Repeated verification requests", "keywords": ["again", "already", "sent"]},
            {"name": "Format/specification issues", "keywords": ["format", "type", "size"]},
        ],
        "Service Experience": [
            {"name": "Long wait times", "keywords": ["wait", "hold", "long"]},
            {"name": "Multiple transfers", "keywords": ["transfer", "department", "again"]},
            {"name": "Agent attitude", "keywords": ["rude", "attitude", "unprofessional"]},
        ],
    }

    patterns = sub_issue_patterns.get(rc_label, [])

    # Count matches for each sub-issue
    sub_issues = []
    total_matched = 0

    for pattern in patterns:
        count = 0
        for interaction in interactions:
            text = (interaction.get("complaint_text", "") + " " +
                   interaction.get("agent_notes", "")).lower()
            if any(kw in text for kw in pattern["keywords"]):
                count += 1

        if count > 0:
            total_matched += count
            sub_issues.append({
                "name": pattern["name"],
                "count": count,
                "percentage": 0  # Will calculate after
            })

    # Calculate percentages
    for sub in sub_issues:
        sub["percentage"] = round(sub["count"] / max(total_matched, 1) * 100, 1)

    # Sort by count descending
    sub_issues.sort(key=lambda x: x["count"], reverse=True)

    # If no sub-issues detected, generate some based on frequency distribution
    if not sub_issues and interactions:
        total = len(interactions)
        sub_issues = [
            {"name": "Primary pattern", "count": int(total * 0.45), "percentage": 45.0},
            {"name": "Secondary pattern", "count": int(total * 0.30), "percentage": 30.0},
            {"name": "Other", "count": int(total * 0.25), "percentage": 25.0},
        ]

    return sub_issues[:5]


def _detect_correlations(interactions: List[Dict]) -> List[Dict[str, Any]]:
    """Detect correlations in the interaction data."""

    if not interactions:
        return []

    correlations = []

    # Channel correlation
    channel_counts = defaultdict(int)
    for i in interactions:
        channel_counts[i.get("channel", "Unknown")] += 1

    top_channel = max(channel_counts.items(), key=lambda x: x[1], default=("Unknown", 0))
    if top_channel[1] / max(len(interactions), 1) > 0.5:
        correlations.append({
            "factor": "Channel",
            "value": top_channel[0],
            "percentage": round(top_channel[1] / len(interactions) * 100, 1),
            "insight": f"{top_channel[1] / len(interactions) * 100:.0f}% of issues occur via {top_channel[0]} channel"
        })

    # Customer segment correlation
    segment_counts = defaultdict(int)
    for i in interactions:
        segment_counts[i.get("customer_segment", "Unknown")] += 1

    top_segment = max(segment_counts.items(), key=lambda x: x[1], default=("Unknown", 0))
    if top_segment[1] / max(len(interactions), 1) > 0.4:
        correlations.append({
            "factor": "Customer Segment",
            "value": top_segment[0],
            "percentage": round(top_segment[1] / len(interactions) * 100, 1),
            "insight": f"{top_segment[0]} customers disproportionately affected"
        })

    # Region correlation
    region_counts = defaultdict(int)
    for i in interactions:
        region_counts[i.get("region", "Unknown")] += 1

    top_region = max(region_counts.items(), key=lambda x: x[1], default=("Unknown", 0))
    if top_region[1] / max(len(interactions), 1) > 0.35:
        correlations.append({
            "factor": "Region",
            "value": top_region[0],
            "percentage": round(top_region[1] / len(interactions) * 100, 1),
            "insight": f"Higher concentration in {top_region[0]} region"
        })

    # Product correlation
    product_counts = defaultdict(int)
    for i in interactions:
        product_counts[i.get("product", "Unknown")] += 1

    top_product = max(product_counts.items(), key=lambda x: x[1], default=("Unknown", 0))
    if top_product[1] / max(len(interactions), 1) > 0.3:
        correlations.append({
            "factor": "Product",
            "value": top_product[0],
            "percentage": round(top_product[1] / len(interactions) * 100, 1),
            "insight": f"{top_product[0]} accounts for majority of issues"
        })

    return correlations[:4]


def _generate_personalized_actions(
    rc_label: str,
    sub_issues: List[Dict],
    correlations: List[Dict],
    root_cause: Dict
) -> List[Dict[str, Any]]:
    """Generate personalized actions based on specific patterns detected."""

    actions = []
    concentration = root_cause.get("concentration", "Systemic")

    # Sub-issue specific actions
    if sub_issues:
        top_sub = sub_issues[0]

        if rc_label == "Digital/App Experience":
            if "Login" in top_sub["name"]:
                actions.append({
                    "text": "Investigate login authentication flow and add fallback mechanisms",
                    "priority": "Critical",
                    "type": "Technical"
                })
            elif "timeout" in top_sub["name"].lower():
                actions.append({
                    "text": "Review backend API latency and increase timeout thresholds",
                    "priority": "High",
                    "type": "Technical"
                })

        elif rc_label == "Policy/Fees Confusion":
            if "Overdraft" in top_sub["name"]:
                actions.append({
                    "text": "Implement low balance alerts and overdraft protection enrollment",
                    "priority": "High",
                    "type": "Product"
                })

    # Concentration-based actions
    if concentration == "Agent-Concentrated":
        top_agents = root_cause.get("top_agents", [])
        if top_agents:
            agent_names = [a.get("agent_name", a.get("agent_id")) for a in top_agents[:3]]
            actions.append({
                "text": f"Schedule focused coaching sessions for agents: {', '.join(agent_names)}",
                "priority": "High",
                "type": "Training"
            })

    # Correlation-based actions
    for corr in correlations:
        if corr["factor"] == "Channel" and corr["percentage"] > 60:
            actions.append({
                "text": f"Investigate {corr['value']} channel-specific issues and processes",
                "priority": "Medium",
                "type": "Process"
            })
        elif corr["factor"] == "Region" and corr["percentage"] > 40:
            actions.append({
                "text": f"Review {corr['value']} region operational practices and resources",
                "priority": "Medium",
                "type": "Operations"
            })

    # Default actions from templates
    templates = ACTION_TEMPLATES.get(rc_label, [])
    for template in templates[:2]:
        if template["text"] not in [a["text"] for a in actions]:
            actions.append({
                "text": template["text"],
                "priority": template["impact"],
                "type": "Standard"
            })

    return actions[:5]


def _calculate_predicted_impact(frequency: int, sub_issues: List[Dict]) -> Dict[str, Any]:
    """Calculate predicted impact if actions are implemented."""

    # Estimate based on frequency and sub-issue concentration
    if not sub_issues:
        reduction_rate = 0.15
    else:
        # Higher concentration in top sub-issue = more targeted fix possible
        top_concentration = sub_issues[0].get("percentage", 0) / 100
        reduction_rate = 0.1 + (top_concentration * 0.25)  # 10-35% reduction

    complaints_reduced = int(frequency * reduction_rate)

    return {
        "estimated_reduction": complaints_reduced,
        "reduction_percentage": round(reduction_rate * 100, 0),
        "confidence": "Medium" if reduction_rate < 0.25 else "High",
        "timeframe": "4-6 weeks",
        "message": f"{complaints_reduced} fewer complaints/week if primary actions implemented"
    }


def _generate_analysis_summary(
    rc_label: str,
    sub_issues: List[Dict],
    correlations: List[Dict]
) -> str:
    """Generate a natural language summary of the AI analysis."""

    parts = []

    # Sub-issue summary
    if sub_issues and len(sub_issues) > 1:
        parts.append(f"This category shows {len(sub_issues)} distinct sub-patterns:")
        for sub in sub_issues[:3]:
            parts.append(f"  • {sub['name']} ({sub['percentage']:.0f}%)")

    # Correlation summary
    if correlations:
        corr_strs = [f"{c['factor']}: {c['value']}" for c in correlations[:2]]
        parts.append(f"\nKey correlations identified: {'; '.join(corr_strs)}.")

    # Root cause specific insight
    insights = {
        "Digital/App Experience": "Consider prioritizing technical fixes as these issues often have cascading impact on customer trust.",
        "Policy/Fees Confusion": "Fee transparency improvements typically show quick ROI in complaint reduction.",
        "Processing Delays": "SLA visibility and proactive communication can reduce complaint severity even before fixing root delays.",
        "Incorrect Info / Agent Knowledge Gap": "Knowledge base and training investments show compounding returns over time.",
        "Fraud & Disputes": "Speed of resolution is critical for fraud cases - customers are highly anxious.",
        "Documentation / KYC Friction": "Digital document solutions can dramatically reduce this category if implemented well.",
        "Service Experience": "Agent empowerment and reduced transfers address multiple pain points simultaneously.",
    }

    if rc_label in insights:
        parts.append(f"\n{insights[rc_label]}")

    return "\n".join(parts) if parts else "Analysis complete. Review sub-issues and correlations for detailed insights."
