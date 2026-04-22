from __future__ import annotations

import streamlit as st

from main import (
    column_legend_frame,
    ensure_program_year,
    load_dataset,
    relation_frame,
    relation_sunburst_options,
    render_department_company_section,
    render_department_dream_section,
    render_dream_company_preferences_section,
    render_department_section,
    render_dream_attainability_section,
    render_fear_factor_section,
    render_fear_support_section,
    render_info_sources_section,
    render_interview_exposure_section,
    render_program_exposure_relation_section,
    render_program_year_section,
    stacked_bar_options,
    st_echarts,
    render_support_needed_section,
    render_year_info_section,
)


def render_department_role_raw_section(data) -> None:
    relation = relation_frame(
        data,
        "Department",
        "Role Categories",
        "Department",
        "Role",
    )
    if relation.empty:
        return

    st.subheader("Department x Role Target")
    st_echarts(
        options=stacked_bar_options(
            relation,
            "Department",
            "Role",
            "Department x Role Target",
        ),
        height="520px",
        key="raw-department-role-bar",
    )

    left_column, right_column = st.columns(2)
    with left_column:
        st_echarts(
            options=relation_sunburst_options(
                relation,
                "Department",
                "Role",
                "Department to Role Sunburst",
            ),
            height="520px",
            key="raw-department-role-sunburst",
        )
    with right_column:
        st_echarts(
            options=relation_sunburst_options(
                relation,
                "Role",
                "Department",
                "Role to Department Sunburst",
            ),
            height="520px",
            key="raw-role-department-sunburst",
        )


def main() -> None:
    st.set_page_config(page_title="Raw Data", layout="wide")
    st.title("Raw Data")
    st.caption("Unfiltered survey table and column legend")

    data, source_name = load_dataset()
    if data is None:
        st.error("CSV not found")
        return

    data = ensure_program_year(data)

    st.caption(f"Loaded: {source_name}")
    st.dataframe(data, width="stretch", hide_index=True)
    st.subheader("Column Legend")
    st.dataframe(
        column_legend_frame(data.columns.tolist()), width="stretch", hide_index=True
    )
    st.divider()
    render_department_section(data)
    render_program_year_section(data)
    render_department_company_section(data)
    render_info_sources_section(data)
    render_fear_factor_section(data)
    render_support_needed_section(data)
    render_interview_exposure_section(data)
    render_fear_support_section(data)
    render_department_role_raw_section(data)
    render_program_exposure_relation_section(data)
    render_department_dream_section(data)
    render_dream_attainability_section(data)
    render_dream_company_preferences_section(data)
    render_year_info_section(data)


if __name__ == "__main__":
    main()
