from __future__ import annotations

import pandas as pd
import streamlit as st

from main import (
    CHART_COLORS,
    DEPARTMENT_RENAMES,
    DEFAULT_CSV,
    PROGRAM_ORDER,
    department_company_frame,
    dream_attainability_frame,
    distribution_frame,
    exploded_list_frame,
    heatmap_options,
    load_csv_from_path,
    pie_chart_options,
    program_year_sunburst_options,
    relation_frame,
    relation_heatmap_frame,
    relation_sunburst_options,
    st_echarts,
)


def metric_rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0%"
    return f"{(numerator / denominator) * 100:.1f}%"


def normalize_departments(data: pd.DataFrame) -> pd.DataFrame:
    normalized = data.copy()
    if "Department" in normalized.columns:
        normalized["Department"] = normalized["Department"].replace(DEPARTMENT_RENAMES)
    return normalized


def render_centered_chart(options: dict, *, height: str, width: str, key: str) -> None:
    left, center, right = st.columns([1, 2, 1])
    with center:
        st_echarts(options=options, height=height, width=width, key=key)


def normalized_doughnut_options(data: pd.DataFrame, column: str, title: str) -> dict:
    total = int(data["Count"].sum()) if not data.empty else 0
    chart_data = data.copy()
    chart_data["Percent"] = (chart_data["Count"] / total * 100).round(1) if total else 0

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c}%"},
        "legend": {"right": "0%", "top": "35%", "orient": "vertical"},
        "series": [
            {
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["40%", "55%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2,
                },
                "label": {"show": False, "position": "center"},
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 28,
                        "fontWeight": "bold",
                        "formatter": "{b}\n{c}%",
                    }
                },
                "labelLine": {"show": False},
                "data": [
                    {"name": row[column], "value": float(row["Percent"])}
                    for _, row in chart_data.iterrows()
                ],
            }
        ],
    }


def normalized_relation_sunburst_options(
    data: pd.DataFrame,
    parent_column: str,
    child_column: str,
    title: str,
) -> dict:
    grouped = (
        data.groupby([parent_column, child_column]).size().reset_index(name="Count")
    )
    parent_totals = grouped.groupby(parent_column)["Count"].transform("sum")
    grouped["Percent"] = (grouped["Count"] / parent_totals * 100).round(1)

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c}%"},
        "series": [
            {
                "type": "sunburst",
                "radius": ["18%", "88%"],
                "sort": None,
                "itemStyle": {
                    "borderRadius": 4,
                    "borderWidth": 2,
                    "borderColor": "#fff",
                },
                "label": {"rotate": "radial"},
                "data": [
                    {
                        "name": parent,
                        "children": [
                            {
                                "name": row[child_column],
                                "value": float(row["Percent"]),
                            }
                            for _, row in grouped[
                                grouped[parent_column] == parent
                            ].iterrows()
                        ],
                    }
                    for parent in grouped[parent_column].drop_duplicates().tolist()
                ],
            }
        ],
    }


def render_header(data: pd.DataFrame) -> None:
    total = len(data)
    no_interviews = int(data["Interview Exposure Detail"].eq("No interviews yet").sum())
    pilot_yes = int(data["Pilot Interest"].eq("Yes — Interested").sum())
    need_self_assess = int(data["Self Assessment"].eq("Yes").sum())

    st.title("Survey Insights")
    st.caption("A storytelling view of the cleaned IIT Bhubaneswar survey data.")

    cards = st.columns(4)
    cards[0].metric("Responses", f"{total}")
    cards[1].metric("No interviews yet", metric_rate(no_interviews, total))
    cards[2].metric("Interested in pilot", metric_rate(pilot_yes, total))
    cards[3].metric("Want self-assessment", metric_rate(need_self_assess, total))

    st.info(
        "The strongest signal is a readiness gap: most students want help now, many have never faced interviews yet, and mock interviews emerge as the central requested intervention."
    )


def render_cohort_section(data: pd.DataFrame) -> None:
    st.header("Who Responded")
    st.write(
        "The sample is dominated by Mechanical and CS students, with UG students forming the bulk of the population."
    )

    left, right = st.columns(2)
    with left:
        dept_data = distribution_frame(data, "Department")
        st_echarts(
            options=pie_chart_options(dept_data, "Department", "Department"),
            height="520px",
            key="insights-department-donut",
        )
    with right:
        st_echarts(
            options=program_year_sunburst_options(data, "Program and Year"),
            height="520px",
            key="insights-program-year-sunburst",
        )


def render_readiness_section(data: pd.DataFrame) -> None:
    st.header("Readiness Gap")
    st.write(
        "UG students appear to be the group most hungry for interview exposure: they make up the largest pool of students who have not yet faced interviews, which makes them the clearest audience for structured mock-interview support."
    )

    relation = (
        data[["Program", "Interview Exposure Detail"]]
        .dropna()
        .groupby(["Program", "Interview Exposure Detail"])
        .size()
        .reset_index(name="Count")
    )

    st_echarts(
        options=heatmap_options(
            relation,
            "Program",
            "Interview Exposure Detail",
            "Count",
            "",
            x_order=PROGRAM_ORDER,
            y_order=[
                "No interviews yet",
                "1-3 interviews",
                "3-5 interviews",
                "More than 5 interviews",
                "Interviewed (count unknown)",
            ],
        ),
        height="540px",
        key="insights-program-exposure-heatmap",
    )


def render_barrier_section(data: pd.DataFrame) -> None:
    st.header("Barriers and Help")
    st.write(
        "The survey points to a tight loop: fear about interviews, placement outcomes, and communication maps directly to a request for mock interviews, guidance, and communication support."
    )

    left, right = st.columns(2)
    with left:
        fear_data = distribution_frame(
            exploded_list_frame(data, "Fear Factor", "Fear Item"),
            "Fear Item",
        )
        st_echarts(
            options=normalized_doughnut_options(
                fear_data,
                "Fear Item",
                "Fear Factor",
            ),
            height="520px",
            key="insights-fear-donut",
        )
    with right:
        support_data = distribution_frame(
            exploded_list_frame(data, "Support Needed", "Support Item"),
            "Support Item",
        )
        st_echarts(
            options=normalized_doughnut_options(
                support_data,
                "Support Item",
                "Help Students Are Asking For",
            ),
            height="520px",
            key="insights-support-donut",
        )

    fear_support = relation_frame(
        data, "Fear Factor", "Support Needed", "Fear", "Support"
    )
    fear_support_heatmap = (
        fear_support.groupby(["Fear", "Support"]).size().reset_index(name="Count")
    )
    fear_totals = fear_support_heatmap.groupby("Fear")["Count"].transform("sum")
    fear_support_heatmap["Percent"] = (
        fear_support_heatmap["Count"] / fear_totals * 100
    ).round(1)

    st_echarts(
        options=heatmap_options(
            fear_support_heatmap,
            "Support",
            "Fear",
            "Percent",
            "Fear to Support Heatmap",
        ),
        height="560px",
        key="insights-fear-support-heatmap",
    )

    normalized_pathways = []
    for fear in fear_support_heatmap["Fear"].drop_duplicates().tolist():
        fear_rows = fear_support_heatmap[fear_support_heatmap["Fear"] == fear]
        normalized_pathways.append(
            {
                "name": fear,
                "children": [
                    {
                        "name": row["Support"],
                        "value": float(row["Percent"]),
                    }
                    for _, row in fear_rows.iterrows()
                ],
            }
        )

    render_centered_chart(
        {
            "color": CHART_COLORS,
            "title": {"text": "Fear to Support Pathways", "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c}%"},
            "series": [
                {
                    "type": "sunburst",
                    "radius": ["18%", "88%"],
                    "sort": None,
                    "itemStyle": {
                        "borderRadius": 4,
                        "borderWidth": 2,
                        "borderColor": "#fff",
                    },
                    "label": {"rotate": "radial"},
                    "data": normalized_pathways,
                }
            ],
        },
        height="900px",
        width="900px",
        key="insights-fear-support-sunburst",
    )


def render_information_section(data: pd.DataFrame) -> None:
    st.header("Information Pathways")
    st.write(
        "LinkedIn and seniors dominate across years, while the Career Development Cell (CDC) appears as one of several information sources rather than the only trusted channel."
    )

    relation = relation_heatmap_frame(data, "Year", "Info Sources", "Year", "Source")
    relation["Year Label"] = relation["Year"].map(
        lambda value: f"Year {int(float(value))}"
    )
    st_echarts(
        options=heatmap_options(
            relation,
            "Year Label",
            "Source",
            "Count",
            "Year x Info Sources",
            x_order=["Year 1", "Year 2", "Year 3", "Year 4"],
        ),
        height="540px",
        key="insights-year-info-heatmap",
    )


def render_attainability_section(data: pd.DataFrame) -> None:
    st.header("Dream Companies & Accessibility")
    st.write(
        "This view estimates whether students seem to have realistic access to their dream companies through their department's visible placement ecosystem. An exact match means the same company is already showing up in department-level placement mentions, a close match means similar companies from the same hiring cluster are visible, and a gap means that access signal is weak or missing."
    )

    dream_relation = relation_frame(
        data, "Department", "Dream Role", "Department", "Dream Company"
    )
    placement_relation = department_company_frame(data)
    attainability = dream_attainability_frame(data)
    summary = (
        attainability.groupby(["Department", "Match Quality"])
        .size()
        .reset_index(name="Count")
    )
    department_totals = summary.groupby("Department")["Count"].transform("sum")
    summary["Percent"] = (summary["Count"] / department_totals * 100).round(1)

    left, right = st.columns(2)
    with left:
        st_echarts(
            options=normalized_relation_sunburst_options(
                dream_relation,
                "Department",
                "Dream Company",
                "Dream Companies by Department",
            ),
            height="560px",
            key="insights-dream-companies-sunburst",
        )
    with right:
        st_echarts(
            options=normalized_relation_sunburst_options(
                placement_relation,
                "Department",
                "Company",
                "Placement Company Access by Department",
            ),
            height="560px",
            key="insights-placement-companies-sunburst",
        )

    left, right = st.columns(2)
    with left:
        st_echarts(
            options=heatmap_options(
                summary,
                "Match Quality",
                "Department",
                "Percent",
                "Dream Company Access by Department",
                x_order=["Exact Match", "Close Match", "Gap"],
            ),
            height="540px",
            key="insights-attainability-heatmap",
        )
    with right:
        normalized_attainability = attainability.merge(
            attainability.groupby("Department").size().rename("Department Total"),
            on="Department",
        )
        normalized_attainability = (
            normalized_attainability.groupby(
                ["Department", "Match Quality", "Department Total"]
            )
            .size()
            .reset_index(name="Count")
        )
        normalized_attainability["Percent Label"] = (
            normalized_attainability["Count"]
            / normalized_attainability["Department Total"]
            * 100
        ).round(1)
        st_echarts(
            options={
                "color": CHART_COLORS,
                "title": {
                    "text": "Department to Dream Company Access",
                    "left": "center",
                },
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}%"},
                "series": [
                    {
                        "type": "sunburst",
                        "radius": ["18%", "88%"],
                        "sort": None,
                        "itemStyle": {
                            "borderRadius": 4,
                            "borderWidth": 2,
                            "borderColor": "#fff",
                        },
                        "label": {"rotate": "radial"},
                        "data": [
                            {
                                "name": department,
                                "children": [
                                    {
                                        "name": row["Match Quality"],
                                        "value": float(row["Percent Label"]),
                                    }
                                    for _, row in normalized_attainability[
                                        normalized_attainability["Department"]
                                        == department
                                    ].iterrows()
                                ],
                            }
                            for department in normalized_attainability["Department"]
                            .drop_duplicates()
                            .tolist()
                        ],
                    }
                ],
            },
            height="540px",
            key="insights-attainability-sunburst",
        )

    access_summary = (
        attainability.groupby("Match Quality").size().reset_index(name="Count")
    )
    total_access = int(access_summary["Count"].sum())
    access_summary["Percent"] = (
        (access_summary["Count"] / total_access * 100).round(1) if total_access else 0
    )
    render_centered_chart(
        {
            "color": CHART_COLORS,
            "title": {"text": "Overall Dream Company Access", "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c}%"},
            "legend": {"right": "0%", "top": "35%", "orient": "vertical"},
            "series": [
                {
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "center": ["40%", "55%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {
                        "borderRadius": 10,
                        "borderColor": "#fff",
                        "borderWidth": 2,
                    },
                    "label": {"show": False, "position": "center"},
                    "emphasis": {
                        "label": {
                            "show": True,
                            "fontSize": 28,
                            "fontWeight": "bold",
                            "formatter": "{b}\n{c}%",
                        }
                    },
                    "labelLine": {"show": False},
                    "data": [
                        {
                            "name": row["Match Quality"],
                            "value": float(row["Percent"]),
                        }
                        for _, row in access_summary.iterrows()
                    ],
                }
            ],
        },
        height="640px",
        width="640px",
        key="insights-attainability-donut",
    )


def main() -> None:
    st.set_page_config(page_title="IIT Bhubaneswar Student Survey", layout="wide")
    st.title("IIT Bhubaneswar Student Survey")

    if not DEFAULT_CSV.exists():
        st.error(f"CSV not found: {DEFAULT_CSV.name}")
        return

    data = normalize_departments(load_csv_from_path(str(DEFAULT_CSV)))
    render_header(data)
    st.markdown("---")
    render_cohort_section(data)
    st.markdown("---")
    render_attainability_section(data)
    st.markdown("---")
    render_information_section(data)
    st.markdown("---")
    render_readiness_section(data)
    st.markdown("---")
    render_barrier_section(data)


if __name__ == "__main__":
    main()
