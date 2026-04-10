from __future__ import annotations

import streamlit as st

from main import (
    column_legend_frame,
    ensure_program_year,
    load_dataset,
    render_department_company_section,
    render_department_dream_section,
    render_department_role_section,
    render_department_section,
    render_dream_attainability_section,
    render_fear_factor_section,
    render_fear_support_section,
    render_info_sources_section,
    render_interview_exposure_section,
    render_program_exposure_relation_section,
    render_program_year_section,
    render_support_needed_section,
    render_year_info_section,
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
    render_department_role_section(data)
    render_program_exposure_relation_section(data)
    render_department_dream_section(data)
    render_dream_attainability_section(data)
    render_year_info_section(data)


if __name__ == "__main__":
    main()
