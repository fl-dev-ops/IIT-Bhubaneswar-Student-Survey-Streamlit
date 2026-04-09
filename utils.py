from __future__ import annotations

import pandas as pd

DEPARTMENT_RENAMES = {
    "Computer Science": "CS",
    "Electronics and Communication": "EC",
    "Metallurgical and Materials": "Metallurgical",
}
PROGRAM_ORDER = ["BTech", "MTech", "MSc", "PhD"]
CHART_COLORS = [
    "#5470c6",
    "#91cc75",
    "#fac858",
    "#ee6666",
    "#73c0de",
    "#3ba272",
    "#fc8452",
    "#9a60b4",
    "#ea7ccc",
]

COMPANY_CLUSTERS = {
    "Google": ["Google", "Alphabet", "DeepMind", "YouTube"],
    "Microsoft": ["Microsoft", "Azure", "GitHub"],
    "Amazon": ["Amazon", "AWS", "Flipkart"],
    "Meta": ["Meta", "Facebook", "Instagram", "WhatsApp"],
    "ZS Associates": ["ZS Associates", "ZS"],
    "Goldman Sachs": ["Goldman Sachs", "GS"],
    "Morgan Stanley": ["Morgan Stanley", "MS"],
    " Deloitte ": ["Deloitte", "Deloitte"],
    "EY": ["EY", "Ernst & Young"],
    "TCS": ["TCS"],
    "Wipro": ["Wipro"],
    "Infosys": ["Infosys"],
    "ONGC": ["ONGC"],
}


def _extract_year(value: str) -> str:
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if "1" in value:
        return "Year 1"
    if "2" in value:
        return "Year 2"
    if "3" in value:
        return "Year 3"
    if "4" in value:
        return "Year 4"
    if "M Tech" in value or "M.Tech" in value or "Msc" in value:
        return value
    if "PhD" in value or "Ph.D" in value:
        return value
    return value


def _extract_program(value: str) -> str:
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if "1" in value:
        return "BTech"
    if "2" in value:
        return "BTech"
    if "3" in value:
        return "BTech"
    if "4" in value:
        return "BTech"
    if "M Tech" in value or "M.Tech" in value:
        return "MTech"
    if "Msc" in value or "M.Sc" in value:
        return "MSc"
    if "PhD" in value or "Ph.D" in value:
        return "PhD"
    return value


def _extract_interview_count(value: str) -> str:
    if pd.isna(value):
        return "No interviews yet"
    value = str(value).strip().lower()
    if value == "no" or value == "0" or value == "never":
        return "No interviews yet"
    if "1" in value or "2" in value or "3" in value:
        return "1-3 interviews"
    if "4" in value or "5" in value:
        return "3-5 interviews"
    if "more" in value or "6" in value or "7" in value or "8" in value or "9" in value:
        return "More than 5 interviews"
    return "Interviewed (count unknown)"


def _cluster_company(company: str) -> str:
    if pd.isna(company):
        return ""
    company = str(company).strip()
    for cluster_name, cluster_companies in COMPANY_CLUSTERS.items():
        for c in cluster_companies:
            if c.lower() in company.lower():
                return cluster_name.strip()
    return company


def _clean_text_field(value: str) -> str:
    if pd.isna(value):
        return ""
    items = str(value).split(",")
    return ",".join([item.strip() for item in items if item.strip()])


def _explode_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    exploded = df.dropna(subset=[column]).copy()
    exploded = exploded[exploded[column].str.strip() != ""]
    exploded[column] = exploded[column].apply(_clean_text_field)
    return exploded.explode(column)


def distribution_frame(data: pd.DataFrame, column: str) -> pd.DataFrame:
    return (
        data[column]
        .dropna()
        .value_counts()
        .reset_index()
        .rename(columns={column: "Category", 0: "Count"})
    )


def exploded_list_frame(
    data: pd.DataFrame, source_column: str, target_column: str
) -> pd.DataFrame:
    return _explode_column(data, source_column).rename(
        columns={source_column: target_column}
    )[[target_column]]


def relation_frame(
    data: pd.DataFrame,
    left_column: str,
    right_column: str,
    left_label: str,
    right_label: str,
) -> pd.DataFrame:
    left_exploded = _explode_column(data, left_column)
    right_exploded = _explode_column(data, right_column)
    left_exploded = left_exploded.rename(columns={left_column: left_label})
    right_exploded = right_exploded.rename(columns={right_column: right_label})
    combined = pd.merge(
        left_exploded, right_exploded, left_index=True, right_index=True
    )
    return combined[[left_label, right_label]]


def relation_heatmap_frame(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    x_label: str,
    y_label: str,
) -> pd.DataFrame:
    exploded_x = _explode_column(data, x_column)
    exploded_x = exploded_x.rename(columns={x_column: x_label})
    exploded_y = _explode_column(data, y_column)
    exploded_y = exploded_y.rename(columns={y_column: y_label})
    combined = pd.merge(exploded_x, exploded_y, left_index=True, right_index=True)
    return combined.groupby([x_label, y_label]).size().reset_index(name="Count")


def pie_chart_options(data: pd.DataFrame, column: str, title: str) -> dict:
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


def program_year_sunburst_options(data: pd.DataFrame, title: str) -> dict:
    program_data = data.copy()
    program_data["Program"] = program_data["Year"].apply(_extract_program)
    program_data["Year Label"] = program_data["Year"].apply(_extract_year)

    grouped = (
        program_data.groupby(["Program", "Year Label"]).size().reset_index(name="Count")
    )
    program_totals = grouped.groupby("Program")["Count"].transform("sum")
    grouped["Percent"] = (grouped["Count"] / program_totals * 100).round(1)

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
                        "name": program,
                        "children": [
                            {
                                "name": row["Year Label"],
                                "value": float(row["Percent"]),
                            }
                            for _, row in grouped[
                                grouped["Program"] == program
                            ].iterrows()
                        ],
                    }
                    for program in grouped["Program"].drop_duplicates().tolist()
                ],
            }
        ],
    }


def heatmap_options(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    value_column: str,
    title: str,
    x_order: list | None = None,
    y_order: list | None = None,
) -> dict:
    x_values = data[x_column].drop_duplicates().tolist()
    y_values = data[y_column].drop_duplicates().tolist()

    if x_order:
        x_values = [x for x in x_order if x in x_values] + [
            x for x in x_values if x not in x_order
        ]
    if y_order:
        y_values = [y for y in y_order if y in y_values] + [
            y for y in y_values if y not in y_order
        ]

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"position": "top"},
        "grid": {"height": "50%", "top": "10%"},
        "xAxis": {
            "type": "category",
            "data": x_values,
            "splitArea": {"show": True},
        },
        "yAxis": {
            "type": "category",
            "data": y_values,
            "splitArea": {"show": True},
        },
        "visualMap": {
            "min": 0,
            "max": int(data[value_column].max()),
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": "0%",
            "inRange": {"color": ["#f0f9ff", "#a5d8ff", "#3b82f6"]},
        },
        "series": [
            {
                "type": "heatmap",
                "data": [
                    [
                        x_values.index(row[x_column]),
                        y_values.index(row[y_column]),
                        row[value_column],
                    ]
                    for _, row in data.iterrows()
                ],
                "label": {"show": True},
                "emphasis": {
                    "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}
                },
            }
        ],
    }


def department_company_frame(data: pd.DataFrame) -> pd.DataFrame:
    exploded = _explode_column(data, "Placement Awareness")
    exploded = exploded.rename(columns={"Placement Awareness": "Company"})
    exploded["Company"] = exploded["Company"].apply(_cluster_company)
    exploded = exploded[exploded["Company"].str.strip() != ""]
    result = data[["Department"]].copy()
    result["Company"] = exploded["Company"].values
    return result.dropna()


def dream_attainability_frame(data: pd.DataFrame) -> pd.DataFrame:
    companies = department_company_frame(data)
    companies = companies[["Department"]].drop_duplicates().copy()
    companies["Company Set"] = companies["Department"].map(
        lambda dept: set(companies[companies["Department"] == dept]["Company"].tolist())
    )

    dream = _explode_column(data, "Dream Company")
    dream = dream.rename(columns={"Dream Company": "Dream Company"})
    dream = dream.merge(data[["Department"]], left_index=True, right_index=True)

    def check_match(row: str) -> str:
        company_cluster = _cluster_company(row)
        for _, dept_row in companies.iterrows():
            if company_cluster in dept_row["Company Set"]:
                return "Exact Match"
        for _, dept_row in companies.iterrows():
            for company in dept_row["Company Set"]:
                if company_cluster and company:
                    if (
                        company_cluster.lower() in company.lower()
                        or company.lower() in company_cluster.lower()
                    ):
                        return "Close Match"
        return "Gap"

    dream["Match Quality"] = dream["Dream Company"].apply(check_match)
    return dream[["Department", "Dream Company", "Match Quality"]]
