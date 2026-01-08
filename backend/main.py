"""
FastAPI Backend for Call Center Insights Dashboard.
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from taxonomy import (
    LINES_OF_BUSINESS, CALL_REASONS, PRODUCTS, REGIONS,
    CHANNELS, CUSTOMER_SEGMENTS, TENURE_BANDS, COMPLAINT_CATEGORIES,
    COMPLAINT_SEVERITIES, TEAM_LEADERS
)
from data_generator import (
    get_all_agents, get_agent_lookup, get_all_interactions,
    get_interaction_by_id, get_interaction_index, AGENTS, AGENT_LOOKUP
)
from root_cause_engine import generate_ai_summary, analyze_root_causes
from ai_service import generate_executive_summary, generate_enhanced_root_cause

app = FastAPI(title="Call Center Insights API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class RootCauseRequest(BaseModel):
    interaction_ids: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class FiltersModel(BaseModel):
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    line_of_business: Optional[str] = None
    call_reason: Optional[str] = None
    product: Optional[str] = None
    region: Optional[str] = None
    team_leader: Optional[str] = None
    agent_id: Optional[str] = None
    complaints_only: bool = False
    channel: Optional[str] = None
    segment: Optional[str] = None


# Helper functions
def filter_interactions(
    interactions: List[Dict],
    from_date: str = None,
    to_date: str = None,
    line_of_business: str = None,
    call_reason: str = None,
    product: str = None,
    region: str = None,
    team_leader: str = None,
    agent_id: str = None,
    complaints_only: bool = False,
    channel: str = None,
    segment: str = None
) -> List[Dict]:
    """Apply filters to interaction list."""
    result = interactions

    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date.replace('Z', ''))
            result = [i for i in result if datetime.fromisoformat(i["timestamp"]) >= from_dt]
        except:
            pass

    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date.replace('Z', ''))
            result = [i for i in result if datetime.fromisoformat(i["timestamp"]) <= to_dt]
        except:
            pass

    if line_of_business:
        result = [i for i in result if i["line_of_business"] == line_of_business]

    if call_reason:
        result = [i for i in result if i["call_reason"] == call_reason]

    if product:
        result = [i for i in result if i["product"] == product]

    if region:
        result = [i for i in result if i["region"] == region]

    if team_leader:
        result = [i for i in result if i["team_leader"] == team_leader]

    if agent_id:
        result = [i for i in result if i["agent_id"] == agent_id]

    if complaints_only:
        result = [i for i in result if i["is_complaint"]]

    if channel:
        result = [i for i in result if i["channel"] == channel]

    if segment:
        result = [i for i in result if i["customer_segment"] == segment]

    return result


# API Endpoints

@app.get("/api/options")
def get_options():
    """Return all taxonomy lists, regions, leaders, agents."""
    # Get unique team leaders from actual data
    all_leaders = set()
    for region_leaders in TEAM_LEADERS.values():
        all_leaders.update(region_leaders)

    return {
        "lines_of_business": LINES_OF_BUSINESS,
        "call_reasons": CALL_REASONS,
        "products": PRODUCTS,
        "regions": REGIONS,
        "team_leaders": dict(TEAM_LEADERS),
        "all_team_leaders": sorted(list(all_leaders)),
        "channels": CHANNELS,
        "customer_segments": CUSTOMER_SEGMENTS,
        "tenure_bands": TENURE_BANDS,
        "complaint_categories": COMPLAINT_CATEGORIES,
        "complaint_severities": COMPLAINT_SEVERITIES,
        "agents": get_all_agents()
    }


@app.get("/api/interactions")
def get_interactions(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None,
    team_leader: Optional[str] = None,
    agent_id: Optional[str] = None,
    complaints_only: bool = False,
    channel: Optional[str] = None,
    segment: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "timestamp",
    sort_order: str = "desc"
):
    """Return paginated list of interactions with filters."""
    all_interactions = get_all_interactions()

    filtered = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        team_leader=team_leader,
        agent_id=agent_id,
        complaints_only=complaints_only,
        channel=channel,
        segment=segment
    )

    # Sort
    reverse = sort_order == "desc"
    if sort_by in ["timestamp", "handling_time_seconds", "estimated_cost_dollars"]:
        filtered.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)

    # Paginate
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = filtered[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        "data": page_data
    }


@app.get("/api/interactions/{interaction_id}")
def get_interaction_detail(interaction_id: str):
    """Return full interaction detail with AI summary."""
    interaction = get_interaction_by_id(interaction_id)

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    # Generate AI summary
    ai_summary = generate_ai_summary(interaction)

    # Determine concentration for this root cause
    all_interactions = get_all_interactions()
    same_root_cause = [
        i for i in all_interactions
        if i["root_cause_label"] == interaction["root_cause_label"] and i["is_complaint"]
    ]

    # Calculate agent concentration for this root cause
    agent_counts = defaultdict(int)
    for i in same_root_cause:
        agent_counts[i["agent_id"]] += 1

    total_for_cause = len(same_root_cause)
    top_3 = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_3_share = sum(c for _, c in top_3) / total_for_cause if total_for_cause > 0 else 0
    concentration = "Agent-Concentrated" if top_3_share >= 0.4 else "Systemic"

    return {
        **interaction,
        "ai_summary": ai_summary,
        "root_cause_concentration": concentration,
        "root_cause_total_count": total_for_cause,
        "root_cause_top_agents": [
            {
                "agent_id": aid,
                "agent_name": AGENT_LOOKUP.get(aid, {}).get("agent_name", aid),
                "count": cnt
            }
            for aid, cnt in top_3
        ]
    }


@app.get("/api/interactions/{interaction_id}/related")
def get_related_interactions(
    interaction_id: str,
    mode: str = Query("same_reason_product", regex="^(same_reason_product|same_agent|same_complaint_category)$"),
    limit: int = 20
):
    """Return related interactions based on mode."""
    interaction = get_interaction_by_id(interaction_id)

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    all_interactions = get_all_interactions()

    if mode == "same_reason_product":
        related = [
            i for i in all_interactions
            if i["call_reason"] == interaction["call_reason"]
            and i["product"] == interaction["product"]
            and i["interaction_id"] != interaction_id
        ]
    elif mode == "same_agent":
        related = [
            i for i in all_interactions
            if i["agent_id"] == interaction["agent_id"]
            and i["interaction_id"] != interaction_id
        ]
    elif mode == "same_complaint_category":
        if not interaction["is_complaint"]:
            return {"data": [], "total": 0, "mode": mode}
        related = [
            i for i in all_interactions
            if i.get("complaint_category") == interaction.get("complaint_category")
            and i["interaction_id"] != interaction_id
        ]
    else:
        related = []

    # Sort by timestamp desc and limit
    related.sort(key=lambda x: x["timestamp"], reverse=True)
    limited = related[:limit]

    return {
        "data": limited,
        "total": len(related),
        "mode": mode,
        "context": {
            "call_reason": interaction["call_reason"],
            "product": interaction["product"],
            "agent_id": interaction["agent_id"],
            "agent_name": interaction["agent_name"],
            "complaint_category": interaction.get("complaint_category")
        }
    }


@app.post("/api/root_cause")
def analyze_root_cause(request: RootCauseRequest):
    """Analyze interactions for root causes."""
    all_interactions = get_all_interactions()

    if request.interaction_ids:
        # Analyze specific interactions
        interactions = [
            i for i in all_interactions
            if i["interaction_id"] in request.interaction_ids
        ]
    elif request.filters:
        # Apply filters
        f = request.filters
        interactions = filter_interactions(
            all_interactions,
            from_date=f.get("from_date"),
            to_date=f.get("to_date"),
            line_of_business=f.get("line_of_business"),
            call_reason=f.get("call_reason"),
            product=f.get("product"),
            region=f.get("region"),
            team_leader=f.get("team_leader"),
            agent_id=f.get("agent_id"),
            complaints_only=f.get("complaints_only", True),
            channel=f.get("channel"),
            segment=f.get("segment")
        )
    else:
        # Default: all complaints
        interactions = [i for i in all_interactions if i["is_complaint"]]

    # Cap at 500 for analysis
    if len(interactions) > 500:
        interactions = interactions[:500]

    result = analyze_root_causes(interactions, get_agent_lookup())
    return result


@app.get("/api/root_cause/trends")
def get_root_cause_trends(
    root_cause: str = Query(..., description="Root cause category to get trends for"),
    weeks: int = Query(8, ge=4, le=16),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None
):
    """Return weekly trends for a specific root cause category."""
    all_interactions = get_all_interactions()

    # Calculate date range for the past N weeks
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)

    # Filter to complaints only and apply other filters
    filtered = filter_interactions(
        all_interactions,
        from_date=start_date.strftime("%Y-%m-%d"),
        to_date=end_date.strftime("%Y-%m-%d"),
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=True
    )

    # Group by week (ISO week number)
    weekly = defaultdict(lambda: {"total": 0, "root_cause_count": 0})

    for interaction in filtered:
        date = datetime.fromisoformat(interaction["timestamp"].replace("Z", ""))
        week_key = f"{date.isocalendar()[0]}-W{date.isocalendar()[1]:02d}"

        weekly[week_key]["total"] += 1
        # Check if this complaint matches the root cause
        if interaction.get("root_cause_label") == root_cause:
            weekly[week_key]["root_cause_count"] += 1

    # Build response sorted by week
    sorted_weeks = sorted(weekly.keys())

    labels = []
    values = []
    percentages = []

    for week_key in sorted_weeks:
        w = weekly[week_key]
        labels.append(week_key)
        values.append(w["root_cause_count"])
        percentages.append(round(w["root_cause_count"] / w["total"] * 100, 1) if w["total"] > 0 else 0)

    # Calculate WoW change
    wow_change = None
    if len(values) >= 2:
        current = values[-1]
        previous = values[-2]
        if previous != 0:
            wow_change = round((current - previous) / previous * 100, 1)

    return {
        "root_cause": root_cause,
        "labels": labels,
        "values": values,
        "percentages": percentages,
        "weeks": weeks,
        "wow_change": wow_change,
        "current_value": values[-1] if values else None,
        "previous_value": values[-2] if len(values) >= 2 else None,
        "total_count": sum(values)
    }


@app.get("/api/metrics")
def get_metrics(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None,
    team_leader: Optional[str] = None,
    agent_id: Optional[str] = None,
    complaints_only: bool = False
):
    """Return aggregated KPI metrics."""
    all_interactions = get_all_interactions()

    filtered = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        team_leader=team_leader,
        agent_id=agent_id,
        complaints_only=complaints_only
    )

    if not filtered:
        return {
            "total_interactions": 0,
            "total_complaints": 0,
            "complaint_rate": 0,
            "avg_handling_time_seconds": 0,
            "avg_handling_time_minutes": 0,
            "fcr_rate": 0,
            "escalation_rate": 0,
            "avg_transfers": 0,
            "digital_eligible_count": 0,
            "deflection_rate": 0,
            "total_cost": 0
        }

    total = len(filtered)
    complaints = sum(1 for i in filtered if i["is_complaint"])
    resolved = sum(1 for i in filtered if i["resolved_on_first_contact"])
    escalated = sum(1 for i in filtered if i["escalated"])
    transfers = sum(i["transfer_count"] for i in filtered)
    handling_time = sum(i["handling_time_seconds"] for i in filtered)
    digital_eligible = sum(1 for i in filtered if i["digital_eligible"])
    deflection_success = sum(1 for i in filtered if i["deflection_success"])
    total_cost = sum(i["estimated_cost_dollars"] for i in filtered)

    return {
        "total_interactions": total,
        "total_complaints": complaints,
        "complaint_rate": round(complaints / total * 100, 1) if total > 0 else 0,
        "avg_handling_time_seconds": round(handling_time / total) if total > 0 else 0,
        "avg_handling_time_minutes": round(handling_time / total / 60, 2) if total > 0 else 0,
        "fcr_rate": round(resolved / total * 100, 1) if total > 0 else 0,
        "escalation_rate": round(escalated / total * 100, 1) if total > 0 else 0,
        "avg_transfers": round(transfers / total, 2) if total > 0 else 0,
        "digital_eligible_count": digital_eligible,
        "deflection_rate": round(deflection_success / digital_eligible * 100, 1) if digital_eligible > 0 else 0,
        "total_cost": round(total_cost, 2)
    }


@app.get("/api/trends")
def get_trends(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None,
    complaints_only: bool = False,
    aggregation: str = "daily"
):
    """Return time series data for trends."""
    all_interactions = get_all_interactions()

    filtered = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=complaints_only
    )

    # Group by date
    daily = defaultdict(lambda: {"count": 0, "handling_time": 0, "resolved": 0, "complaints": 0})

    for interaction in filtered:
        dt = datetime.fromisoformat(interaction["timestamp"])
        if aggregation == "weekly":
            dt = dt - timedelta(days=dt.weekday())
        key = dt.date().isoformat()

        daily[key]["count"] += 1
        daily[key]["handling_time"] += interaction["handling_time_seconds"]
        if interaction["resolved_on_first_contact"]:
            daily[key]["resolved"] += 1
        if interaction["is_complaint"]:
            daily[key]["complaints"] += 1

    # Build response
    sorted_dates = sorted(daily.keys())

    labels = []
    volume = []
    aht = []
    fcr = []
    complaint_volume = []

    for date_key in sorted_dates:
        d = daily[date_key]
        labels.append(date_key)
        volume.append(d["count"])
        aht.append(round(d["handling_time"] / d["count"] / 60, 2) if d["count"] > 0 else 0)
        fcr.append(round(d["resolved"] / d["count"] * 100, 1) if d["count"] > 0 else 0)
        complaint_volume.append(d["complaints"])

    return {
        "labels": labels,
        "volume": volume,
        "avg_handling_time": aht,
        "fcr_rate": fcr,
        "complaint_volume": complaint_volume
    }


@app.get("/api/trends/weekly")
def get_weekly_trends(
    metric: str = Query("volume", regex="^(volume|complaint_rate|fcr_rate|avg_handling_time|escalation_rate|transfer_rate|complaint_volume_rate)$"),
    weeks: int = Query(8, ge=4, le=16),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None,
    complaints_only: bool = False
):
    """Return weekly aggregated trends for a specific metric."""
    all_interactions = get_all_interactions()

    # Calculate date range for the past N weeks
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)

    filtered = filter_interactions(
        all_interactions,
        from_date=start_date.strftime("%Y-%m-%d"),
        to_date=end_date.strftime("%Y-%m-%d"),
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=complaints_only
    )

    # Group by week (ISO week number)
    weekly = defaultdict(lambda: {
        "count": 0,
        "handling_time": 0,
        "resolved": 0,
        "complaints": 0,
        "escalated": 0,
        "transferred": 0
    })

    for interaction in filtered:
        date = datetime.fromisoformat(interaction["timestamp"].replace("Z", ""))
        # Get ISO week as "YYYY-WXX" format
        week_key = f"{date.isocalendar()[0]}-W{date.isocalendar()[1]:02d}"
        week_start = date - timedelta(days=date.weekday())

        weekly[week_key]["week_start"] = week_start.strftime("%Y-%m-%d")
        weekly[week_key]["count"] += 1
        weekly[week_key]["handling_time"] += interaction["handling_time_seconds"]
        if interaction["resolved_on_first_contact"]:
            weekly[week_key]["resolved"] += 1
        if interaction["is_complaint"]:
            weekly[week_key]["complaints"] += 1
        if interaction.get("escalated"):
            weekly[week_key]["escalated"] += 1
        if interaction.get("transfer_count", 0) > 0:
            weekly[week_key]["transferred"] += 1

    # Build response sorted by week
    sorted_weeks = sorted(weekly.keys())

    labels = []
    values = []
    rates = []  # For complaint_volume_rate metric - stores complaint rates as data labels

    for week_key in sorted_weeks:
        w = weekly[week_key]
        labels.append(week_key)

        if metric == "volume":
            values.append(w["count"])
        elif metric == "complaint_rate":
            values.append(round(w["complaints"] / w["count"] * 100, 1) if w["count"] > 0 else 0)
        elif metric == "fcr_rate":
            values.append(round(w["resolved"] / w["count"] * 100, 1) if w["count"] > 0 else 0)
        elif metric == "avg_handling_time":
            values.append(round(w["handling_time"] / w["count"] / 60, 1) if w["count"] > 0 else 0)
        elif metric == "escalation_rate":
            values.append(round(w["escalated"] / w["count"] * 100, 1) if w["count"] > 0 else 0)
        elif metric == "transfer_rate":
            values.append(round(w["transferred"] / w["count"] * 100, 1) if w["count"] > 0 else 0)
        elif metric == "complaint_volume_rate":
            # Bars show complaint volume, data labels show complaint rate %
            values.append(w["complaints"])
            rates.append(round(w["complaints"] / w["count"] * 100, 1) if w["count"] > 0 else 0)

    # Calculate WoW change
    wow_change = None
    if len(values) >= 2:
        current = values[-1]
        previous = values[-2]
        if previous != 0:
            wow_change = round((current - previous) / previous * 100, 1)

    response = {
        "metric": metric,
        "labels": labels,
        "values": values,
        "weeks": weeks,
        "wow_change": wow_change,
        "current_value": values[-1] if values else None,
        "previous_value": values[-2] if len(values) >= 2 else None
    }

    # Include rates array for complaint_volume_rate metric
    if metric == "complaint_volume_rate":
        response["rates"] = rates

    return response


@app.get("/api/breakdown")
def get_breakdown(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None,
    complaints_only: bool = False,
    group_by: str = "line_of_business"
):
    """Return breakdown by specified dimension."""
    all_interactions = get_all_interactions()

    filtered = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=complaints_only
    )

    # Group
    grouped = defaultdict(lambda: {
        "count": 0,
        "handling_time": 0,
        "resolved": 0,
        "complaints": 0,
        "cost": 0
    })

    for interaction in filtered:
        key = interaction.get(group_by, "Unknown")
        grouped[key]["count"] += 1
        grouped[key]["handling_time"] += interaction["handling_time_seconds"]
        grouped[key]["cost"] += interaction["estimated_cost_dollars"]
        if interaction["resolved_on_first_contact"]:
            grouped[key]["resolved"] += 1
        if interaction["is_complaint"]:
            grouped[key]["complaints"] += 1

    # Build response
    breakdown = []
    for label, data in grouped.items():
        count = data["count"]
        breakdown.append({
            "label": label,
            "count": count,
            "complaint_count": data["complaints"],
            "complaint_rate": round(data["complaints"] / count * 100, 1) if count > 0 else 0,
            "avg_handling_time_minutes": round(data["handling_time"] / count / 60, 2) if count > 0 else 0,
            "fcr_rate": round(data["resolved"] / count * 100, 1) if count > 0 else 0,
            "total_cost": round(data["cost"], 2)
        })

    breakdown.sort(key=lambda x: x["count"], reverse=True)

    return {
        "group_by": group_by,
        "data": breakdown
    }


@app.get("/api/agents/performance")
def get_agent_performance(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    region: Optional[str] = None,
    team_leader: Optional[str] = None
):
    """Return agent performance metrics."""
    all_interactions = get_all_interactions()

    filtered = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        region=region,
        team_leader=team_leader
    )

    # Group by agent
    agent_data = defaultdict(lambda: {
        "count": 0,
        "handling_time": 0,
        "resolved": 0,
        "complaints": 0,
        "escalated": 0
    })

    for interaction in filtered:
        agent_id = interaction["agent_id"]
        agent_data[agent_id]["count"] += 1
        agent_data[agent_id]["handling_time"] += interaction["handling_time_seconds"]
        if interaction["resolved_on_first_contact"]:
            agent_data[agent_id]["resolved"] += 1
        if interaction["is_complaint"]:
            agent_data[agent_id]["complaints"] += 1
        if interaction["escalated"]:
            agent_data[agent_id]["escalated"] += 1

    # Build response with agent details
    agent_lookup = get_agent_lookup()
    performance = []

    for agent_id, data in agent_data.items():
        agent_info = agent_lookup.get(agent_id, {})
        count = data["count"]

        performance.append({
            "agent_id": agent_id,
            "agent_name": agent_info.get("agent_name", agent_id),
            "team_leader": agent_info.get("team_leader", ""),
            "region": agent_info.get("region", ""),
            "tenure_band": agent_info.get("tenure_band", ""),
            "interaction_count": count,
            "complaint_count": data["complaints"],
            "complaint_rate": round(data["complaints"] / count * 100, 1) if count > 0 else 0,
            "avg_handling_time_minutes": round(data["handling_time"] / count / 60, 2) if count > 0 else 0,
            "fcr_rate": round(data["resolved"] / count * 100, 1) if count > 0 else 0,
            "escalation_rate": round(data["escalated"] / count * 100, 1) if count > 0 else 0
        })

    # Sort by complaint rate desc (worst performers first)
    performance.sort(key=lambda x: x["complaint_rate"], reverse=True)

    return {
        "data": performance,
        "total_agents": len(performance)
    }


@app.get("/api/metrics/comparison")
def get_metrics_comparison(
    current_from: str = Query(..., alias="currentFrom"),
    current_to: str = Query(..., alias="currentTo"),
    previous_from: Optional[str] = Query(None, alias="previousFrom"),
    previous_to: Optional[str] = Query(None, alias="previousTo"),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None,
    complaints_only: bool = False
):
    """Return metrics comparison between two periods (week-over-week, etc.)."""
    all_interactions = get_all_interactions()

    # If no previous period specified, calculate previous period of same length
    try:
        current_from_dt = datetime.fromisoformat(current_from.replace('Z', ''))
        current_to_dt = datetime.fromisoformat(current_to.replace('Z', ''))
        period_days = (current_to_dt - current_from_dt).days + 1

        if not previous_from or not previous_to:
            previous_to_dt = current_from_dt - timedelta(days=1)
            previous_from_dt = previous_to_dt - timedelta(days=period_days - 1)
            previous_from = previous_from_dt.isoformat()
            previous_to = previous_to_dt.isoformat()
    except:
        pass

    # Get current period metrics
    current_filtered = filter_interactions(
        all_interactions,
        from_date=current_from,
        to_date=current_to,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=complaints_only
    )

    # Get previous period metrics
    previous_filtered = filter_interactions(
        all_interactions,
        from_date=previous_from,
        to_date=previous_to,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=complaints_only
    )

    def calc_metrics(interactions):
        if not interactions:
            return {
                "total_interactions": 0, "total_complaints": 0, "complaint_rate": 0,
                "avg_handling_time_minutes": 0, "fcr_rate": 0, "escalation_rate": 0,
                "transfer_rate": 0, "digital_deflection_rate": 0, "cost_per_call": 0,
                "total_cost": 0, "high_severity_count": 0
            }

        total = len(interactions)
        complaints = [i for i in interactions if i["is_complaint"]]
        complaint_count = len(complaints)
        resolved = sum(1 for i in interactions if i["resolved_on_first_contact"])
        escalated = sum(1 for i in interactions if i["escalated"])
        transfers = sum(1 for i in interactions if i["transfer_count"] > 0)
        handling_time = sum(i["handling_time_seconds"] for i in interactions)
        digital_eligible = [i for i in interactions if i["digital_eligible"]]
        deflection_success = sum(1 for i in digital_eligible if i["deflection_success"])
        total_cost = sum(i["estimated_cost_dollars"] for i in interactions)
        high_severity = sum(1 for i in complaints if i.get("complaint_severity") == "High")

        return {
            "total_interactions": total,
            "total_complaints": complaint_count,
            "complaint_rate": round(complaint_count / total * 100, 1) if total > 0 else 0,
            "avg_handling_time_minutes": round(handling_time / total / 60, 2) if total > 0 else 0,
            "fcr_rate": round(resolved / total * 100, 1) if total > 0 else 0,
            "escalation_rate": round(escalated / total * 100, 1) if total > 0 else 0,
            "transfer_rate": round(transfers / total * 100, 1) if total > 0 else 0,
            "digital_deflection_rate": round(deflection_success / len(digital_eligible) * 100, 1) if digital_eligible else 0,
            "cost_per_call": round(total_cost / total, 2) if total > 0 else 0,
            "total_cost": round(total_cost, 2),
            "high_severity_count": high_severity
        }

    current = calc_metrics(current_filtered)
    previous = calc_metrics(previous_filtered)

    # Calculate deltas
    deltas = {}
    for key in current:
        curr_val = current[key]
        prev_val = previous[key]
        abs_delta = round(curr_val - prev_val, 2)
        pct_delta = round((curr_val - prev_val) / prev_val * 100, 1) if prev_val != 0 else 0
        # Determine if change is good or bad
        # For complaint_rate, escalation_rate, transfer_rate, cost - lower is better
        # For fcr_rate, digital_deflection_rate - higher is better
        bad_if_higher = key in ["complaint_rate", "escalation_rate", "transfer_rate", "cost_per_call", "total_cost", "high_severity_count", "avg_handling_time_minutes"]
        trend = "up" if abs_delta > 0 else ("down" if abs_delta < 0 else "flat")
        is_positive = (trend == "down" and bad_if_higher) or (trend == "up" and not bad_if_higher)

        deltas[key] = {
            "absolute": abs_delta,
            "percentage": pct_delta,
            "trend": trend,
            "is_positive": is_positive if abs_delta != 0 else None
        }

    return {
        "current_period": {"from": current_from, "to": current_to},
        "previous_period": {"from": previous_from, "to": previous_to},
        "current": current,
        "previous": previous,
        "deltas": deltas
    }


class AISummaryRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None


@app.post("/api/ai/summary")
def get_ai_summary(request: AISummaryRequest = None):
    """Generate AI executive summary for current data view."""
    all_interactions = get_all_interactions()

    # Apply filters if provided
    filters = request.filters if request else {}
    if filters:
        filtered = filter_interactions(
            all_interactions,
            from_date=filters.get("from_date"),
            to_date=filters.get("to_date"),
            line_of_business=filters.get("lineOfBusiness") or filters.get("line_of_business"),
            call_reason=filters.get("callReason") or filters.get("call_reason"),
            product=filters.get("product"),
            region=filters.get("region"),
            team_leader=filters.get("team_leader"),
            agent_id=filters.get("agent_id"),
            complaints_only=filters.get("complaints_only", False),
            channel=filters.get("channel"),
            segment=filters.get("segment")
        )
    else:
        filtered = all_interactions

    if not filtered:
        return {
            "success": False,
            "summary": {
                "key_finding": "No data available for the selected filters.",
                "details": [],
                "actions": [],
                "positive_trends": [],
                "anomalies": [],
                "generated_summary": "No data available for analysis.",
                "confidence": 0
            }
        }

    # Calculate current metrics
    total = len(filtered)
    complaints = [i for i in filtered if i["is_complaint"]]
    complaint_count = len(complaints)
    resolved = sum(1 for i in filtered if i["resolved_on_first_contact"])
    escalated = sum(1 for i in filtered if i["escalated"])
    handling_time = sum(i["handling_time_seconds"] for i in filtered)
    digital_eligible = [i for i in filtered if i["digital_eligible"]]
    deflection_success = sum(1 for i in digital_eligible if i["deflection_success"])
    total_cost = sum(i["estimated_cost_dollars"] for i in filtered)
    high_severity = sum(1 for i in complaints if i.get("complaint_severity") == "High")

    metrics = {
        "total_interactions": total,
        "total_complaints": complaint_count,
        "complaint_rate": round(complaint_count / total * 100, 1) if total > 0 else 0,
        "avg_handling_time_minutes": round(handling_time / total / 60, 2) if total > 0 else 0,
        "fcr_rate": round(resolved / total * 100, 1) if total > 0 else 0,
        "escalation_rate": round(escalated / total * 100, 1) if total > 0 else 0,
        "digital_deflection_rate": round(deflection_success / len(digital_eligible) * 100, 1) if digital_eligible else 0,
        "cost_per_call": round(total_cost / total, 2) if total > 0 else 0,
        "total_cost": round(total_cost, 2),
        "high_severity_count": high_severity
    }

    # Get root cause analysis
    root_cause_result = analyze_root_causes(complaints if complaints else filtered[:500], get_agent_lookup())
    root_causes = root_cause_result.get("root_causes", [])

    # Try to get comparison data (previous 7 days vs current 7 days)
    comparison = None
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        current_to = now
        current_from = now - timedelta(days=7)
        previous_to = current_from - timedelta(days=1)
        previous_from = previous_to - timedelta(days=6)

        current_filtered = filter_interactions(
            all_interactions,
            from_date=current_from.strftime("%Y-%m-%d"),
            to_date=current_to.strftime("%Y-%m-%d"),
            line_of_business=filters.get("lineOfBusiness") or filters.get("line_of_business") if filters else None,
            call_reason=filters.get("callReason") or filters.get("call_reason") if filters else None,
            product=filters.get("product") if filters else None,
            region=filters.get("region") if filters else None
        )

        previous_filtered = filter_interactions(
            all_interactions,
            from_date=previous_from.strftime("%Y-%m-%d"),
            to_date=previous_to.strftime("%Y-%m-%d"),
            line_of_business=filters.get("lineOfBusiness") or filters.get("line_of_business") if filters else None,
            call_reason=filters.get("callReason") or filters.get("call_reason") if filters else None,
            product=filters.get("product") if filters else None,
            region=filters.get("region") if filters else None
        )

        if current_filtered and previous_filtered:
            curr_complaints = sum(1 for i in current_filtered if i["is_complaint"])
            prev_complaints = sum(1 for i in previous_filtered if i["is_complaint"])
            curr_rate = curr_complaints / len(current_filtered) * 100 if current_filtered else 0
            prev_rate = prev_complaints / len(previous_filtered) * 100 if previous_filtered else 0

            curr_resolved = sum(1 for i in current_filtered if i["resolved_on_first_contact"])
            prev_resolved = sum(1 for i in previous_filtered if i["resolved_on_first_contact"])
            curr_fcr = curr_resolved / len(current_filtered) * 100 if current_filtered else 0
            prev_fcr = prev_resolved / len(previous_filtered) * 100 if previous_filtered else 0

            comparison = {
                "deltas": {
                    "complaint_rate": {
                        "absolute": round(curr_rate - prev_rate, 1),
                        "percentage": round((curr_rate - prev_rate) / prev_rate * 100, 1) if prev_rate else 0
                    },
                    "fcr_rate": {
                        "absolute": round(curr_fcr - prev_fcr, 1),
                        "percentage": round((curr_fcr - prev_fcr) / prev_fcr * 100, 1) if prev_fcr else 0
                    }
                }
            }
    except Exception:
        pass

    # Generate AI summary
    summary = generate_executive_summary(
        metrics=metrics,
        root_causes=root_causes,
        comparison=comparison,
        filters=filters
    )

    return {
        "success": True,
        "summary": summary,
        "metrics": metrics,
        "filter_context": filters
    }


@app.get("/api/ai/root-cause/{root_cause_label}")
def get_enhanced_root_cause(
    root_cause_label: str,
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None
):
    """Get AI-enhanced analysis for a specific root cause category."""
    all_interactions = get_all_interactions()

    # Filter to complaints with this root cause
    filtered = filter_interactions(
        all_interactions,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=True
    )

    # Get interactions matching this root cause
    rc_interactions = [i for i in filtered if i.get("root_cause_label") == root_cause_label]

    if not rc_interactions:
        raise HTTPException(status_code=404, detail="No data found for this root cause category")

    # Get base root cause analysis
    root_cause_result = analyze_root_causes(rc_interactions, get_agent_lookup())
    root_causes = root_cause_result.get("root_causes", [])

    # Find the matching root cause
    base_rc = next((rc for rc in root_causes if rc["root_cause_label"] == root_cause_label), None)

    if not base_rc:
        # Create minimal base if not found
        base_rc = {
            "root_cause_label": root_cause_label,
            "frequency": len(rc_interactions),
            "percentage": 100.0,
            "concentration": "Systemic",
            "top_agents": []
        }

    # Enhance with AI analysis
    enhanced = generate_enhanced_root_cause(base_rc, rc_interactions)

    return {
        "success": True,
        "root_cause": enhanced,
        "interaction_count": len(rc_interactions)
    }


@app.get("/api/metrics/severity-breakdown")
def get_severity_breakdown(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    call_reason: Optional[str] = None,
    product: Optional[str] = None,
    region: Optional[str] = None
):
    """Return complaint severity breakdown for pyramid visualization."""
    all_interactions = get_all_interactions()

    filtered = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        line_of_business=line_of_business,
        call_reason=call_reason,
        product=product,
        region=region,
        complaints_only=True
    )

    severity_counts = {"High": 0, "Medium": 0, "Low": 0}
    for interaction in filtered:
        severity = interaction.get("complaint_severity", "Low")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    total = sum(severity_counts.values())

    return {
        "high": severity_counts["High"],
        "medium": severity_counts["Medium"],
        "low": severity_counts["Low"],
        "total": total,
        "percentages": {
            "high": round(severity_counts["High"] / total * 100, 1) if total > 0 else 0,
            "medium": round(severity_counts["Medium"] / total * 100, 1) if total > 0 else 0,
            "low": round(severity_counts["Low"] / total * 100, 1) if total > 0 else 0
        }
    }


@app.get("/api/metrics/heatmap")
def get_complaint_heatmap(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    line_of_business: Optional[str] = Query(None, alias="lob"),
    region: Optional[str] = None
):
    """Return Product x Complaint Category heatmap data."""
    all_interactions = get_all_interactions()

    filtered = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        line_of_business=line_of_business,
        region=region,
        complaints_only=True
    )

    # Build matrix: product -> category -> count
    matrix = defaultdict(lambda: defaultdict(int))
    product_totals = defaultdict(int)
    category_totals = defaultdict(int)

    for interaction in filtered:
        product = interaction["product"]
        category = interaction.get("complaint_category", "Unknown")
        matrix[product][category] += 1
        product_totals[product] += 1
        category_totals[category] += 1

    # Sort products by total complaints (desc)
    sorted_products = sorted(product_totals.keys(), key=lambda p: product_totals[p], reverse=True)[:10]
    sorted_categories = sorted(category_totals.keys(), key=lambda c: category_totals[c], reverse=True)

    # Build heatmap data
    heatmap = []
    for product in sorted_products:
        row = {"product": product, "total": product_totals[product], "categories": {}}
        for category in sorted_categories:
            row["categories"][category] = matrix[product][category]
        heatmap.append(row)

    return {
        "products": sorted_products,
        "categories": sorted_categories,
        "data": heatmap,
        "category_totals": dict(category_totals),
        "product_totals": dict(product_totals)
    }


@app.get("/api/agents/{agent_id}/profile")
def get_agent_profile(
    agent_id: str,
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to")
):
    """Return detailed agent coaching profile."""
    all_interactions = get_all_interactions()
    agent_lookup = get_agent_lookup()

    agent_info = agent_lookup.get(agent_id)
    if not agent_info:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get agent's interactions
    agent_interactions = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        agent_id=agent_id
    )

    # Get team average for comparison
    team_interactions = filter_interactions(
        all_interactions,
        from_date=from_date,
        to_date=to_date,
        team_leader=agent_info["team_leader"]
    )

    def calc_stats(interactions):
        if not interactions:
            return {"count": 0, "complaint_rate": 0, "fcr_rate": 0, "aht": 0, "transfer_rate": 0}
        total = len(interactions)
        complaints = sum(1 for i in interactions if i["is_complaint"])
        resolved = sum(1 for i in interactions if i["resolved_on_first_contact"])
        transfers = sum(i["transfer_count"] for i in interactions)
        handling = sum(i["handling_time_seconds"] for i in interactions)
        return {
            "count": total,
            "complaint_rate": round(complaints / total * 100, 1),
            "fcr_rate": round(resolved / total * 100, 1),
            "aht": round(handling / total / 60, 1),
            "transfer_rate": round(transfers / total, 2)
        }

    agent_stats = calc_stats(agent_interactions)
    team_stats = calc_stats(team_interactions)

    # Calculate percentile among all agents
    all_agent_stats = []
    for aid in agent_lookup:
        agent_ints = [i for i in all_interactions if i["agent_id"] == aid]
        if agent_ints:
            comp_rate = sum(1 for i in agent_ints if i["is_complaint"]) / len(agent_ints) * 100
            all_agent_stats.append({"agent_id": aid, "complaint_rate": comp_rate})

    all_agent_stats.sort(key=lambda x: x["complaint_rate"])
    agent_rank = next((i for i, a in enumerate(all_agent_stats) if a["agent_id"] == agent_id), -1)
    percentile = round((1 - agent_rank / len(all_agent_stats)) * 100) if all_agent_stats else 0

    # Complaint category breakdown
    agent_complaints = [i for i in agent_interactions if i["is_complaint"]]
    category_breakdown = defaultdict(int)
    for complaint in agent_complaints:
        category_breakdown[complaint.get("complaint_category", "Unknown")] += 1

    sorted_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)

    # Sample complaint texts
    sample_complaints = [c.get("complaint_text", "") for c in agent_complaints[:5] if c.get("complaint_text")]

    # Generate coaching recommendations based on top complaint categories
    coaching_plan = []
    if sorted_categories:
        top_category = sorted_categories[0][0]
        coaching_plan.append({
            "priority": 1,
            "focus": f"{top_category} Training",
            "actions": [
                f"Schedule {top_category.lower()} handling workshop",
                f"Assign mentor from {top_category.lower()}-specialist team"
            ]
        })

    if agent_stats["fcr_rate"] < team_stats["fcr_rate"]:
        coaching_plan.append({
            "priority": 2,
            "focus": "Resolution Improvement",
            "actions": [
                "Review knowledge base articles",
                "Shadow top performer for call handling techniques"
            ]
        })

    if agent_stats["transfer_rate"] > team_stats["transfer_rate"] * 1.5:
        coaching_plan.append({
            "priority": 3,
            "focus": "Transfer Reduction",
            "actions": [
                "Review escalation decision tree",
                "Weekly 1:1 with team leader on complex cases"
            ]
        })

    return {
        "agent": agent_info,
        "stats": agent_stats,
        "team_average": team_stats,
        "gaps": {
            "complaint_rate": round(agent_stats["complaint_rate"] - team_stats["complaint_rate"], 1),
            "fcr_rate": round(agent_stats["fcr_rate"] - team_stats["fcr_rate"], 1),
            "aht": round(agent_stats["aht"] - team_stats["aht"], 1),
            "transfer_rate": round(agent_stats["transfer_rate"] - team_stats["transfer_rate"], 2)
        },
        "percentile": percentile,
        "category_breakdown": [{"category": c, "count": n, "percentage": round(n / len(agent_complaints) * 100, 1) if agent_complaints else 0} for c, n in sorted_categories],
        "sample_complaints": sample_complaints,
        "coaching_plan": coaching_plan
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    interactions = get_all_interactions()
    complaints = sum(1 for i in interactions if i["is_complaint"])

    return {
        "status": "healthy",
        "total_interactions": len(interactions),
        "total_complaints": complaints,
        "complaint_rate": round(complaints / len(interactions) * 100, 1) if interactions else 0,
        "total_agents": len(get_all_agents()),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
