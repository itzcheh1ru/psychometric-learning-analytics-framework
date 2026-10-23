"""
app/services/sem_analysis/visualization_service.py

Interactive visualization generation using Plotly for Component 2:
Algorithmic Trust & Verification Analysis (CFA & SEM).

Generates:
- Standardized Factor Loadings Chart with λ = 0.70 threshold
- HTMT Discriminant Validity Heatmap
- Structural Path Diagram (Antecedents -> VB -> Outcomes)
- Direct vs. Indirect Effects Comparison Chart
- Indicator Distribution & Likert Boxplots
"""

from typing import Any, Dict, List
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def generate_loadings_chart(cfa_results: Dict[str, Any]) -> Dict[str, Any]:
    """Horizontal bar chart showing standardized factor loadings with threshold line."""
    indicators = []
    loadings = []
    colors = []
    constructs = []

    loadings_by_construct = cfa_results.get("loadings", {})
    palette = {
        "AT": "#2563eb",  # Blue
        "PU": "#059669",  # Green
        "VB": "#d97706",  # Amber
        "AD": "#dc2626",  # Red
        "LC": "#7c3aed",  # Purple
    }

    for c_code, items in loadings_by_construct.items():
        for it in items:
            ind = it["indicator"]
            std_l = it["std_loading"]
            indicators.append(ind)
            loadings.append(std_l)
            constructs.append(c_code)
            colors.append(palette.get(c_code, "#4b5563"))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=indicators,
        x=loadings,
        orientation="h",
        marker=dict(color=colors, line=dict(width=1, color="#1e293b")),
        text=[f"{v:.3f}" for v in loadings],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=11, family="sans-serif"),
        hoverinfo="text",
        hovertext=[f"Indicator: {ind}<br>Construct: {c}<br>Std Loading: {l:.3f}" for ind, c, l in zip(indicators, constructs, loadings)],
    ))

    # Add benchmark threshold line at λ = 0.70
    fig.add_shape(
        type="line",
        x0=0.70,
        y0=-0.5,
        x1=0.70,
        y1=len(indicators) - 0.5,
        line=dict(color="#b91c1c", width=2, dash="dash"),
    )

    fig.add_annotation(
        x=0.70,
        y=len(indicators) - 0.5,
        text="Target Threshold (λ ≥ 0.70)",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#b91c1c",
        font=dict(size=11, color="#b91c1c"),
        ax=40,
        ay=-20,
    )

    fig.update_layout(
        title=dict(text="<b>CFA Standardized Factor Loadings (λ) by Construct</b>", font=dict(size=14, color="#1e293b")),
        xaxis=dict(title="Standardized Loading (λ)", range=[0, 1.05], tickmode="linear", dtick=0.1, gridcolor="#e2e8f0"),
        yaxis=dict(title="Survey Indicator", autorange="reversed"),
        margin=dict(l=60, r=30, t=50, b=50),
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f8fafc",
    )

    return json.loads(fig.to_json())


def generate_htmt_heatmap(cfa_results: Dict[str, Any]) -> Dict[str, Any]:
    """Heatmap matrix visualizing Heterotrait-Monotrait (HTMT) ratios."""
    htmt_rows = cfa_results.get("htmt_matrix", [])
    if not htmt_rows:
        return {}

    labels = [row["construct"] for row in htmt_rows]
    z_values = []
    text_values = []

    for row in htmt_rows:
        z_row = []
        text_row = []
        for col_name in labels:
            val = row.get(col_name)
            if val == "-" or val is None:
                z_row.append(None)
                text_row.append("-")
            else:
                f_val = float(val)
                z_row.append(f_val)
                text_row.append(f"{f_val:.3f}")
        z_values.append(z_row)
        text_values.append(text_row)

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=labels,
        y=labels,
        text=text_values,
        texttemplate="%{text}",
        textfont=dict(size=12, color="#0f172a"),
        colorscale=[
            [0.0, "#dcfce7"],   # Soft Green (< 0.85)
            [0.85, "#fef08a"],  # Yellow (0.85 threshold)
            [0.90, "#fed7aa"],  # Orange (0.90 liberal threshold)
            [1.0, "#fca5a5"],   # Red (> 0.90)
        ],
        colorbar=dict(title="HTMT Ratio", tickvals=[0.5, 0.7, 0.85, 0.90, 1.0]),
        zmin=0.3,
        zmax=1.0,
    ))

    fig.update_layout(
        title=dict(text="<b>Heterotrait-Monotrait Ratio (HTMT) Matrix</b><br><span style='font-size:11px;color:#64748b;'>Threshold: HTMT < 0.85 indicates distinct construct discriminant validity</span>", font=dict(size=14, color="#1e293b")),
        xaxis=dict(title="Construct"),
        yaxis=dict(title="Construct", autorange="reversed"),
        margin=dict(l=60, r=40, t=60, b=50),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f8fafc",
    )

    return json.loads(fig.to_json())


def generate_path_diagram(sem_results: Dict[str, Any]) -> Dict[str, Any]:
    """Interactive visual representation of the structural path model."""
    direct_paths = sem_results.get("direct_paths", [])

    # Node positions (x, y)
    nodes = {
        "AT": {"x": 0.15, "y": 0.80, "label": "Algorithmic<br>Trust (AT)", "color": "#2563eb"},
        "PU": {"x": 0.15, "y": 0.20, "label": "Perceived<br>Usefulness (PU)", "color": "#059669"},
        "VB": {"x": 0.50, "y": 0.50, "label": "Verification<br>Behaviour (VB)<br><i>(Mediator)</i>", "color": "#d97706"},
        "AD": {"x": 0.85, "y": 0.80, "label": "AI<br>Dependence (AD)", "color": "#dc2626"},
        "LC": {"x": 0.85, "y": 0.20, "label": "Learning<br>Confidence (LC)", "color": "#7c3aed"},
    }

    fig = go.Figure()

    # Draw path arrows
    for p in direct_paths:
        pred = p["predictor"]
        out = p["outcome"]
        beta = p["std_beta"]
        sig = p["significant"]
        p_val = p["p_value"]

        if pred in nodes and out in nodes:
            x0, y0 = nodes[pred]["x"], nodes[pred]["y"]
            x1, y1 = nodes[out]["x"], nodes[out]["y"]

            star = "***" if p_val == "< 0.001" else ("**" if isinstance(p_val, (int, float)) and p_val < 0.01 else ("*" if sig else "(ns)"))
            path_label = f"β={beta:.2f}{star}"
            line_color = "#15803d" if sig else "#94a3b8"
            line_width = 3 if sig else 1.5

            # Midpoint for label
            mx = (x0 + x1) / 2.0
            my = (y0 + y1) / 2.0
            # Slight offset for direct paths skipping VB (AT->AD, AT->LC, PU->AD, PU->LC)
            if pred in ("AT", "PU") and out in ("AD", "LC"):
                my += 0.08 if out == "AD" else -0.08

            fig.add_annotation(
                x=x1,
                y=y1,
                ax=x0,
                ay=y0,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                text="",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.2,
                arrowwidth=line_width,
                arrowcolor=line_color,
            )

            fig.add_annotation(
                x=mx,
                y=my,
                text=path_label,
                showarrow=False,
                font=dict(size=11, color=line_color, family="monospace"),
                bgcolor="white",
                bordercolor=line_color,
                borderwidth=1,
                borderpad=2,
            )

    # Draw construct nodes
    for code, info in nodes.items():
        fig.add_trace(go.Scatter(
            x=[info["x"]],
            y=[info["y"]],
            mode="markers+text",
            marker=dict(size=55, color=info["color"], line=dict(color="#0f172a", width=2)),
            text=[f"<b>{code}</b>"],
            textposition="middle center",
            textfont=dict(color="white", size=13, family="sans-serif"),
            hoverinfo="text",
            hovertext=info["label"].replace("<br>", " "),
            showlegend=False,
        ))

        # Subtitle below node
        fig.add_annotation(
            x=info["x"],
            y=info["y"] - 0.10,
            text=f"<b>{info['label']}</b>",
            showarrow=False,
            font=dict(size=10, color="#1e293b"),
        )

    fig.update_layout(
        title=dict(text="<b>Structural Equation Model Path Diagram</b><br><span style='font-size:11px;color:#64748b;'>Arrows indicate standardized path estimates (β). *p < 0.05, **p < 0.01, ***p < 0.001, (ns) not significant.</span>", font=dict(size=14, color="#1e293b")),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.05, 0.95]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.02, 0.98]),
        margin=dict(l=30, r=30, t=70, b=40),
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f8fafc",
    )

    return json.loads(fig.to_json())


def generate_effects_comparison_chart(sem_results: Dict[str, Any]) -> Dict[str, Any]:
    """Grouped bar chart comparing direct vs. indirect effects on outcomes."""
    indirect_effects = sem_results.get("indirect_effects", [])

    paths = [it["path"] for it in indirect_effects]
    direct_betas = [it["direct_beta"] for it in indirect_effects]
    indirect_betas = [it["indirect_beta"] for it in indirect_effects]
    total_betas = [it["total_effect"] for it in indirect_effects]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Direct Effect (c')",
        x=paths,
        y=direct_betas,
        marker_color="#2563eb",
        text=[f"{v:.3f}" for v in direct_betas],
        textposition="auto",
    ))

    fig.add_trace(go.Bar(
        name="Indirect Effect (a*b)",
        x=paths,
        y=indirect_betas,
        marker_color="#d97706",
        text=[f"{v:.3f}" for v in indirect_betas],
        textposition="auto",
    ))

    fig.add_trace(go.Bar(
        name="Total Effect",
        x=paths,
        y=total_betas,
        marker_color="#059669",
        text=[f"{v:.3f}" for v in total_betas],
        textposition="auto",
    ))

    fig.update_layout(
        title=dict(text="<b>Mediation Effect Decomposition (Direct, Indirect, Total)</b>", font=dict(size=14, color="#1e293b")),
        barmode="group",
        xaxis=dict(title="Mediated Pathway"),
        yaxis=dict(title="Standardized Effect Size (β)", gridcolor="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=30, t=60, b=50),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f8fafc",
    )

    return json.loads(fig.to_json())
