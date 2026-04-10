from __future__ import annotations

import importlib.metadata
import re
from pathlib import Path

import pandas as pd
import streamlit as st

DEFAULT_CSV = Path(__file__).with_name("IIT_Bhubaneswar_109_Student_Responses.csv")
PROGRAM_ORDER = ["UG", "PG", "PhD"]
CHART_COLORS = [
    "#2563eb",
    "#0f766e",
    "#f59e0b",
    "#7c3aed",
    "#dc2626",
    "#0891b2",
    "#65a30d",
]

DEPARTMENT_RENAMES = {
    "Metallurgical and Materials": "Metallurgical",
    "Electronics and Communication": "EC",
    "Computer Science": "CS",
}

COMPANY_CLUSTERS = {
    "Software / Product": {
        "Google",
        "Microsoft",
        "Amazon",
        "Flipkart",
        "Zomato",
        "Media.net",
        "Rippling",
        "Oracle",
        "Walmart",
        "Samsung",
        "Adobe",
        "Netflix",
        "Meta",
        "TCS",
        "Infosys",
        "DE Shaw",
    },
    "Consulting / Analytics": {
        "ZS Associates",
        "Tiger Analytics",
        "EXL",
        "FactSet",
        "Visa",
        "Lenskart",
    },
    "Core / Industrial": {
        "Tata Steel",
        "Jindal Steel",
        "BPCL",
        "HPCL",
        "Caterpillar",
        "Applied Materials",
        "GE",
        "Schneider Electric",
        "Hitachi",
        "Reliance",
        "Vedanta",
        "Skyroot",
        "TVS",
        "GMDC",
        "Godrej",
        "Maruti Suzuki",
        "BEL",
        "L&T",
    },
    "Semiconductor / Electronics": {
        "NVIDIA",
        "Texas Instruments",
        "Synopsys",
        "Micron",
        "AMD",
        "Cadence",
        "MathWorks",
    },
    "Open Source / Research": {"Red Hat", "Mozilla"},
}

SHORT_HEADERS = {
    "Timestamp": "Timestamp",
    "Department": "Department",
    "Which year are you in?": "Study Stage",
    "Your current CGPA": "CGPA",
    "How much do you know about placements in your department? Name some companies that usually come, job roles your seniors have got, anything you know.": "Placement Awareness",
    "Which companies are you aiming for, and what is your dream job?": "Dream Role",
    "What type of role are you targeting?": "Role Target",
    "What do you think is a realistic salary you can aim for in your first job?": "Salary Expectation",
    "Where do you get information about jobs and careers?": "Info Sources",
    "When you imagine yourself five years from now in your ideal role, what does that look like?": "Five-Year Goal",
    "What is your biggest fear about placements?": "Fear Factor",
    "If you do not get placed on campus, what is your backup plan?": "Backup Plan",
    "What kind of help would give you more confidence going into an actual interview?": "Support Needed",
    "Do you think your English communication skills will affect your placement chances?": "English Impact",
    "How will you rate yourself in English?": "English Level",
    "How confident are you facing a VIDEO interview fully in English?": "Video Confidence",
    "Which are the languages are you comfortable speaking?": "Languages",
    "Have you attended any mock or real interviews so far?": "Interview Exposure",
    "If yes, how many interviews have you attended?": "Interview Count",
    "How soon are you aiming to sit for placement interviews?": "Placement Timeline",
    "Do you want to self-assess yourself on where you currently stand with respect to interviews?": "Self Assessment",
    "When do you want to start preparing for interview training?": "Prep Start",
    "We are planning to pilot intervoo.ai for improving interview-practice & communication skills for IIT BHU students, to improve their placement performance. Would you be interested in participating?": "Pilot Interest",
    "Which is the device will you prefer using for a regular interview preparation as of today?": "Device",
    "Can you share your experience about using any other interview prep app? (Name of the app, what did you like, what other features you would have preferred having, etc.)": "App Experience",
}

DERIVED_HEADERS = {
    "Program": "Derived from 'Which year are you in?'",
    "Year": "Derived from 'Which year are you in?'",
    "Program Year": "Derived from 'Which year are you in?'",
    "Interview Exposure Detail": "Derived from 'Have you attended any mock or real interviews so far?' and 'If yes, how many interviews have you attended?'",
    "Placement Companies": "Parsed from 'Placement Awareness'",
    "Dream Companies": "Parsed from 'Dream Role'",
    "Role Categories": "Parsed from 'Role Target'",
    "Info Source Categories": "Parsed from 'Info Sources'",
    "Fear Categories": "Parsed from 'Fear Factor'",
    "Support Categories": "Parsed from 'Support Needed'",
}

PLACEMENT_COMPANY_PATTERNS = [
    ("Allen", [r"\ballen\b"]),
    ("FIITJEE", [r"\bfitjee\b", r"\bfiitjee\b"]),
    ("EXL", [r"\bexl\b"]),
    ("ZS Associates", [r"\bzs\b", r"zs associates"]),
    ("Applied Materials", [r"applied materials"]),
    ("L&T", [r"\bl\s*&\s*t\b", r"\blandt\b"]),
    ("Accenture", [r"\baccenture\b"]),
    ("Tata Steel", [r"tata steel", r"tatasteel"]),
    ("Jindal Steel", [r"jindal steel", r"\bjindal\b", r"\bjsl\b", r"\bjspl\b"]),
    ("Reliance", [r"\breliance\b", r"\bril\b"]),
    ("Skyroot", [r"\bskyroot\b"]),
    ("Vedanta", [r"\bvedanta\b"]),
    ("TVS", [r"\btvs\b"]),
    ("BPCL", [r"\bbpcl\b"]),
    ("HPCL", [r"\bhpcl\b"]),
    ("BEL", [r"\bbel\b"]),
    ("Maruti Suzuki", [r"maruti suzuki"]),
    ("Infosys", [r"\binfosys\b"]),
    ("Caterpillar", [r"\bcaterpillar\b"]),
    ("NVIDIA", [r"nvidia", r"nvdia"]),
    ("Texas Instruments", [r"texas instruments"]),
    ("Synopsys", [r"\bsynopsys\b"]),
    ("Tredence", [r"\btredence\b"]),
    ("GE", [r"\bge\b"]),
    ("Schneider Electric", [r"schinder", r"schneider"]),
    ("Hitachi", [r"\bhitachi\b"]),
    ("Google", [r"gooogle", r"\bgoogle\b"]),
    ("Amazon", [r"\bamazon\b"]),
    ("Flipkart", [r"\bflipkart\b"]),
    ("Goldman Sachs", [r"goldman sacchs", r"goldman sachs"]),
    ("Media.net", [r"media\.\s*net", r"media\.net"]),
    ("Oracle", [r"\boracle\b"]),
    ("DE Shaw", [r"de shaw", r"de\s*shaw"]),
    ("Microsoft", [r"\bmicrosoft\b"]),
    ("Zscaler", [r"z scaler", r"zscaler"]),
    ("Rippling", [r"\brippling\b"]),
    ("Walmart", [r"\bwalmart\b"]),
    ("Samsung", [r"\bsamsung\b"]),
    ("TCS", [r"\btcs\b"]),
    ("Tiger Analytics", [r"tiger analytics", r"tigers analytics"]),
    ("Visa", [r"\bvisa\b"]),
    ("MathWorks", [r"mathworks"]),
    ("Lenskart", [r"\blenskart\b"]),
    ("GMDC", [r"\bgmdc\b"]),
    ("Godrej", [r"\bgodrej\b"]),
    ("Zomato", [r"\bzomato\b"]),
    ("Adobe", [r"\badobe\b"]),
    ("Netflix", [r"\bnetflix\b"]),
    ("Meta", [r"\bmeta\b"]),
    ("FactSet", [r"factset"]),
    ("Red Hat", [r"red hat"]),
    ("Mozilla", [r"mozilla"]),
    ("Micron", [r"\bmicron\b"]),
    ("AMD", [r"\bamd\b"]),
    ("Cadence", [r"\bcadence\b"]),
    ("BNY Mellon", [r"bny mellon"]),
]

ROLE_TARGET_PATTERNS = [
    ("Core Engineering", [r"core"]),
    ("Software & IT", [r"software", r"\bit\b", r"sde", r"swe"]),
    ("Consulting", [r"consult"]),
    ("Finance", [r"finance", r"quant", r"trader"]),
    ("Open to anything", [r"open to anything"]),
    ("Not sure yet", [r"not sure"]),
    (
        "Data Science / AI",
        [r"data scientist", r"data science", r"\bai\b", r"ai/ml", r"ml"],
    ),
    ("Research", [r"research", r"r&d", r"develoment"]),
    ("Academia", [r"faculty", r"assistant professor", r"professor"]),
    ("Design", [r"design"]),
    ("Geologist", [r"geologist"]),
    ("Physics", [r"physics"]),
]

INFO_SOURCE_PATTERNS = [
    ("LinkedIn", [r"linkedin", r"linkdln", r"linkedln", r"linked in"]),
    (
        "CDC / Placement Cell",
        [
            r"\bcdc\b",
            r"placement cell",
            r"placement handbook",
            r"placement brochure",
        ],
    ),
    ("Seniors / Alumni", [r"\bseniors?\b", r"alumni"]),
    (
        "Friends / Peers",
        [r"\bfriends?\b", r"\bpeers?\b", r"classmates?", r"colleagues?"],
    ),
    ("Family / Relatives", [r"\brelatives?\b", r"\bsiblings?\b"]),
    ("Job Platforms", [r"glassdoor", r"unstop", r"indeed"]),
    (
        "Search / Internet",
        [r"\bgoogle\b", r"\binternet\b", r"research", r"online", r"websites?"],
    ),
    ("Social Media", [r"social media", r"youtube"]),
    (
        "Institute / College",
        [r"institute website", r"\bcollege\b", r"society", r"seminars?"],
    ),
    ("Email / Mail", [r"\bmail\b"]),
    ("Messaging Groups", [r"whatsapp", r"telegram"]),
    ("Newspaper", [r"newspaper"]),
]

FEAR_FACTOR_PATTERNS = [
    (
        "Not Getting Placed",
        [
            r"unplaced",
            r"not get placed",
            r"won'?t be placed",
            r"go unplaced",
            r"not getting placed",
            r"not cracking",
            r"rejection",
            r"rejected",
            r"don'?t get selected",
            r"not get selected",
            r"not get any company",
        ],
    ),
    (
        "Interview Performance",
        [
            r"\binterview\b",
            r"hr round",
            r"fumbling",
            r"stress",
            r"convey",
            r"explain",
            r"perform well",
            r"talking in",
        ],
    ),
    (
        "Communication / English",
        [
            r"communication",
            r"english",
            r"speaking",
            r"confidently",
            r"express my thoughts",
            r"words",
        ],
    ),
    (
        "CGPA / Eligibility",
        [
            r"cgpa",
            r"\bcg\b",
            r"criterion",
            r"criteria",
            r"cutoff",
            r"qualifications",
            r"oa",
            r"resume , cg",
        ],
    ),
    (
        "Package / Role Quality",
        [
            r"underpaid",
            r"less package",
            r"low package",
            r"salary",
            r"salry",
            r"good lpa",
            r"ctc",
            r"bad job role",
            r"role which i don't like",
            r"employment bond",
            r"package",
        ],
    ),
    (
        "Lack of Companies / Opportunities",
        [
            r"companies will come",
            r"good companies don'?t come",
            r"limited number",
            r"no major companies",
            r"no company",
            r"fewer .* roles",
            r"enough opportunities",
            r"less no'? of company",
            r"showcase my skills",
            r"vacancies",
            r"updates about the vacancies",
            r"opportunity",
        ],
    ),
    (
        "Branch / Domain Constraints",
        [
            r"non circuital",
            r"non-core",
            r"non core",
            r"dual degree",
            r"civil roles",
            r"core role",
            r"conventional standards",
            r"limited to",
        ],
    ),
    (
        "Preparation / Technical Skills",
        [
            r"coding",
            r"technical",
            r"dsa",
            r"problem solving",
            r"how to prepare",
            r"lack of preparation",
            r"core knowledge",
            r"not good enough",
        ],
    ),
    ("Resume / Profile", [r"resume", r"profile"]),
    (
        "Guidance / Exposure",
        [
            r"mock or demo interviews",
            r"guidance",
            r"exposure to learning",
            r"updates about the vacancies from the placement cell",
        ],
    ),
]

SUPPORT_NEEDED_PATTERNS = [
    (
        "Mock Interviews",
        [
            r"mock interview",
            r"practice interviews?",
            r"realistic interview",
            r"demo interview",
            r"interview practice",
        ],
    ),
    ("Feedback", [r"feedback", r"analysis of", r"correct feedback"]),
    (
        "Communication / English",
        [
            r"communication",
            r"english",
            r"fluency",
            r"presentation skills",
            r"soft skills",
        ],
    ),
    (
        "Technical Prep",
        [
            r"technical",
            r"core subjects?",
            r"dsa",
            r"coding",
            r"concepts",
            r"subject",
            r"problem-solving",
            r"problem solving",
        ],
    ),
    (
        "Company / Role-specific Prep",
        [
            r"company",
            r"role-based",
            r"company-wise",
            r"recruiters expect",
            r"dream role",
            r"questions they usually ask",
            r"specific company",
        ],
    ),
    (
        "Guidance / Mentorship",
        [
            r"guidance",
            r"alumni",
            r"seniors",
            r"how to prepare",
            r"placement assistance",
            r"placements work",
            r"work culture",
            r"psychology of reading the room",
        ],
    ),
    (
        "Interview Questions / PYQs",
        [
            r"real questions",
            r"past",
            r"pyq",
            r"most asked questions",
            r"questions that they might actually ask",
        ],
    ),
    ("Resume / Projects", [r"resume", r"projects should i make"]),
    (
        "OA / Test Prep",
        [
            r"\boa\b",
            r"online test",
            r"online assessments?",
            r"coding contests",
            r"\bot\b",
        ],
    ),
    (
        "Confidence / Motivation",
        [r"confidence", r"moral support", r"not demotivating", r"positive affirmation"],
    ),
    (
        "More Opportunities / Companies",
        [
            r"bring in more companies",
            r"bringing more companies",
            r"having options",
            r"more companies to college",
        ],
    ),
]


def split_study_stage(value: object) -> tuple[str | None, int | None]:
    if not isinstance(value, str) or not value.strip():
        return None, None

    text = value.strip()
    lowered = text.lower()

    if lowered.startswith("ug"):
        program = "UG"
    elif "phd" in lowered:
        program = "PhD"
    elif any(token in lowered for token in ("m.tech", "m.sc", "pg")):
        program = "PG"
    else:
        program = None

    if "final year" in lowered:
        year = 4
    else:
        match = re.search(r"(\d+)", lowered)
        year = int(match.group(1)) if match else None

    return program, year


def extract_placement_companies(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""

    text = value.lower()
    companies = []
    for company, patterns in PLACEMENT_COMPANY_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            companies.append(company)

    seen = set()
    ordered = []
    for company in companies:
        if company in seen:
            continue
        seen.add(company)
        ordered.append(company)

    return ", ".join(ordered)


def extract_companies(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""

    text = value.lower()
    companies = []
    for company, patterns in PLACEMENT_COMPANY_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            companies.append(company)

    seen = set()
    ordered = []
    for company in companies:
        if company in seen:
            continue
        seen.add(company)
        ordered.append(company)

    return ", ".join(ordered)


def extract_role_targets(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""

    text = value.lower()
    roles = []
    for role, patterns in ROLE_TARGET_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            roles.append(role)

    seen = set()
    ordered = []
    for role in roles:
        if role in seen:
            continue
        seen.add(role)
        ordered.append(role)

    return ", ".join(ordered)


def extract_info_sources(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""

    text = value.lower()
    sources = []
    for source, patterns in INFO_SOURCE_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            sources.append(source)

    seen = set()
    ordered = []
    for source in sources:
        if source in seen:
            continue
        seen.add(source)
        ordered.append(source)

    return ", ".join(ordered)


def extract_fear_factors(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""

    text = value.lower()
    fears = []
    for fear, patterns in FEAR_FACTOR_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            fears.append(fear)

    seen = set()
    ordered = []
    for fear in fears:
        if fear in seen:
            continue
        seen.add(fear)
        ordered.append(fear)

    return ", ".join(ordered)


def extract_support_needed(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""

    text = value.lower()
    supports = []
    for support, patterns in SUPPORT_NEEDED_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            supports.append(support)

    seen = set()
    ordered = []
    for support in supports:
        if support in seen:
            continue
        seen.add(support)
        ordered.append(support)

    return ", ".join(ordered)


def combine_program_year(program: object, year: object) -> str | None:
    if not isinstance(program, str) or not program:
        return None

    if pd.isna(year):
        return program

    return f"{program} {int(year)}"


def combine_interview_exposure(exposure: object, count: object) -> str:
    exposure_text = str(exposure).strip().lower() if exposure is not None else ""
    count_text = str(count).strip() if count is not None else ""

    if exposure_text == "no":
        return "No interviews yet"
    if count_text == "1-3":
        return "1-3 interviews"
    if count_text == "3-5":
        return "3-5 interviews"
    if count_text == "More than 5":
        return "More than 5 interviews"
    if exposure_text == "yes":
        return "Interviewed (count unknown)"
    return "Unknown"


def program_year_sort_key(value: str) -> tuple[int, int, str]:
    if value == "PhD":
        return (2, 99, value)

    match = re.match(r"^(UG|PG)\s+(\d+)$", value)
    if match:
        program, year = match.groups()
        return (PROGRAM_ORDER.index(program), int(year), value)

    if value in PROGRAM_ORDER:
        return (PROGRAM_ORDER.index(value), 99, value)

    return (99, 99, value)


def transform_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    transformed = data.rename(columns=SHORT_HEADERS).copy()

    if "Department" in transformed.columns:
        transformed["Department"] = transformed["Department"].replace(
            DEPARTMENT_RENAMES
        )

    if "Placement Awareness" in transformed.columns:
        transformed["Placement Companies"] = transformed["Placement Awareness"].map(
            extract_placement_companies
        )

    if "Dream Role" in transformed.columns:
        transformed["Dream Companies"] = transformed["Dream Role"].map(
            extract_companies
        )

    if "Role Target" in transformed.columns:
        transformed["Role Categories"] = transformed["Role Target"].map(
            extract_role_targets
        )

    if "Info Sources" in transformed.columns:
        transformed["Info Source Categories"] = transformed["Info Sources"].map(
            extract_info_sources
        )

    if "Fear Factor" in transformed.columns:
        transformed["Fear Categories"] = transformed["Fear Factor"].map(
            extract_fear_factors
        )

    if "Support Needed" in transformed.columns:
        transformed["Support Categories"] = transformed["Support Needed"].map(
            extract_support_needed
        )

    if {"Interview Exposure", "Interview Count"}.issubset(transformed.columns):
        transformed["Interview Exposure Detail"] = [
            combine_interview_exposure(exposure, count)
            for exposure, count in zip(
                transformed["Interview Exposure"], transformed["Interview Count"]
            )
        ]

    if "Study Stage" in transformed.columns:
        expanded = transformed["Study Stage"].apply(split_study_stage)
        insert_at = transformed.columns.get_loc("Study Stage")
        expanded_df = pd.DataFrame(
            expanded.tolist(), columns=["Program", "Year"], index=transformed.index
        )
        expanded_df["Year"] = expanded_df["Year"].astype("Int64")
        expanded_df["Program Year"] = [
            combine_program_year(program, year)
            for program, year in zip(expanded_df["Program"], expanded_df["Year"])
        ]
        transformed = pd.concat(
            [
                transformed.iloc[:, :insert_at],
                expanded_df,
                transformed.iloc[:, insert_at + 1 :],
            ],
            axis=1,
        )

    return transformed


def load_csv_from_path(path: str) -> pd.DataFrame:
    data = pd.read_csv(path, low_memory=False)
    return transform_dataframe(data)


def load_dataset() -> tuple[pd.DataFrame | None, str | None]:
    if DEFAULT_CSV.exists():
        return load_csv_from_path(str(DEFAULT_CSV)), DEFAULT_CSV.name

    return None, None


def column_legend_frame(columns: list[str]) -> pd.DataFrame:
    reverse_headers = {
        short_name: original for original, short_name in SHORT_HEADERS.items()
    }
    legend_rows = []

    for column in columns:
        original_title = DERIVED_HEADERS.get(
            column, reverse_headers.get(column, column)
        )
        legend_rows.append(
            {
                "Column Name": column,
                "Original Title": original_title,
            }
        )

    return pd.DataFrame(legend_rows)


def ensure_program_year(data: pd.DataFrame) -> pd.DataFrame:
    if "Program Year" in data.columns:
        return data

    repaired = data.copy()
    if {"Program", "Year"}.issubset(repaired.columns):
        repaired["Program Year"] = [
            combine_program_year(program, year)
            for program, year in zip(repaired["Program"], repaired["Year"])
        ]

    return repaired


@st.cache_resource(show_spinner=False)
def echarts_component():
    dist = importlib.metadata.distribution("streamlit-echarts")
    build_dir = Path(dist.locate_file("streamlit_echarts/frontend/build"))
    bundle_paths = sorted(build_dir.glob("index-*.js"))
    if not bundle_paths:
        raise FileNotFoundError("streamlit-echarts bundle not found")

    js_bundle = bundle_paths[0].read_text(encoding="utf-8")
    return st.components.v2.component(
        "iitbbs-streamlit-echarts",
        html='<div class="echarts-container"></div>',
        js=js_bundle,
        isolate_styles=False,
    )


def st_echarts(
    options: dict,
    *,
    height: str = "300px",
    width: str = "100%",
    theme: str | dict = "streamlit",
    key: str | None = None,
) -> None:
    component = echarts_component()
    component(
        data={
            "options": options,
            "theme": theme,
            "onEvents": {},
            "height": height,
            "width": width,
            "renderer": "canvas",
            "replaceMerge": None,
            "map": None,
            "selectionActive": False,
            "selectionMode": [],
        },
        key=key,
        default={},
        width="stretch",
        height="content",
        on_chart_event_change=lambda: None,
    )


def distribution_frame(
    data: pd.DataFrame, column: str, order: list[str] | None = None
) -> pd.DataFrame:
    counts = (
        data[column]
        .dropna()
        .astype(str)
        .value_counts()
        .rename_axis(column)
        .reset_index(name="Count")
    )

    if order:
        rank = {label: index for index, label in enumerate(order)}
        counts["sort_key"] = counts[column].map(lambda value: rank.get(value, 999))
        counts = counts.sort_values(
            ["sort_key", "Count"], ascending=[True, False]
        ).drop(columns="sort_key")

    return counts


def department_company_frame(data: pd.DataFrame) -> pd.DataFrame:
    if not {"Department", "Placement Companies"}.issubset(data.columns):
        return pd.DataFrame(columns=["Department", "Company"])

    rows = []
    for _, row in data[["Department", "Placement Companies"]].dropna().iterrows():
        department = str(row["Department"]).strip()
        companies = [
            company.strip()
            for company in str(row["Placement Companies"]).split(",")
            if company.strip()
        ]
        for company in companies:
            rows.append({"Department": department, "Company": company})

    return pd.DataFrame(rows)


def exploded_list_frame(
    data: pd.DataFrame, source_column: str, item_column: str
) -> pd.DataFrame:
    if source_column not in data.columns:
        return pd.DataFrame(columns=[item_column])

    rows = []
    for value in data[source_column].fillna(""):
        items = [item.strip() for item in str(value).split(",") if item.strip()]
        for item in items:
            rows.append({item_column: item})

    return pd.DataFrame(rows)


def bar_chart_options(data: pd.DataFrame, column: str, title: str) -> dict:
    labels = data[column].tolist()
    counts = data["Count"].tolist()

    return {
        "color": [CHART_COLORS[0]],
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {
            "left": 40,
            "right": 20,
            "top": 60,
            "bottom": 80,
            "containLabel": True,
        },
        "xAxis": {
            "type": "category",
            "data": labels,
            "axisLabel": {"interval": 0, "rotate": 25},
        },
        "yAxis": {"type": "value", "name": "Count"},
        "series": [
            {
                "type": "bar",
                "data": counts,
                "barWidth": "55%",
                "label": {"show": True, "position": "top"},
                "itemStyle": {"borderRadius": [8, 8, 0, 0]},
            }
        ],
    }


def sunburst_options(data: pd.DataFrame, column: str, title: str) -> dict:
    children = [
        {"name": row[column], "value": int(row["Count"])} for _, row in data.iterrows()
    ]

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [
            {
                "type": "sunburst",
                "center": ["50%", "55%"],
                "radius": ["14%", "72%"],
                "sort": None,
                "itemStyle": {
                    "borderRadius": 4,
                    "borderWidth": 2,
                    "borderColor": "#fff",
                },
                "label": {"rotate": "radial"},
                "data": [
                    {"name": title.replace(" Sunburst", ""), "children": children}
                ],
            }
        ],
    }


def pie_chart_options(data: pd.DataFrame, column: str, title: str) -> dict:
    series_data = [
        {"name": row[column], "value": int(row["Count"])} for _, row in data.iterrows()
    ]

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
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
                        "formatter": "{b}\n{c}",
                    }
                },
                "labelLine": {"show": False},
                "data": series_data,
            }
        ],
    }


def program_year_dataset(data: pd.DataFrame) -> list[list[object]]:
    year_columns = [1, 2, 3, 4]
    header = ["Program", "Year 1", "Year 2", "Year 3", "Year 4", "PhD"]
    rows = [header]

    for program in ["UG", "PG"]:
        program_rows = data[data["Program"] == program]
        row = [program]
        for year in year_columns:
            row.append(int(program_rows[program_rows["Year"] == year].shape[0]))
        row.append(0)
        rows.append(row)

    phd_count = int(data[data["Program"] == "PhD"].shape[0])
    rows.append(["PhD", 0, 0, 0, 0, phd_count])
    return rows


def program_year_bar_options(data: pd.DataFrame, title: str) -> dict:
    source = program_year_dataset(data)
    series_names = source[0][1:]

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"top": 28},
        "dataset": {"source": source},
        "grid": {
            "left": 40,
            "right": 20,
            "top": 80,
            "bottom": 40,
            "containLabel": True,
        },
        "xAxis": {"type": "category"},
        "yAxis": {"type": "value", "name": "Count"},
        "series": [
            {
                "type": "bar",
                "seriesLayoutBy": "row",
                "emphasis": {"focus": "series"},
                "label": {"show": True, "position": "top"},
            }
            for _ in series_names
        ],
    }


def program_year_sunburst_options(data: pd.DataFrame, title: str) -> dict:
    tree = []
    for program in PROGRAM_ORDER:
        program_rows = data[data["Program"] == program]
        if program_rows.empty:
            continue

        if program == "PhD":
            tree.append({"name": "PhD", "value": int(program_rows.shape[0])})
            continue

        children = []
        for year in sorted(program_rows["Year"].dropna().unique()):
            year_count = int(program_rows[program_rows["Year"] == year].shape[0])
            children.append({"name": f"Year {int(year)}", "value": year_count})

        tree.append({"name": program, "children": children})

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [
            {
                "type": "sunburst",
                "center": ["50%", "55%"],
                "radius": ["14%", "72%"],
                "sort": None,
                "itemStyle": {
                    "borderRadius": 4,
                    "borderWidth": 2,
                    "borderColor": "#fff",
                },
                "label": {"rotate": "radial"},
                "data": tree,
            }
        ],
    }


def department_company_bar_options(data: pd.DataFrame, title: str) -> dict:
    grouped = data.groupby(["Company", "Department"]).size().reset_index(name="Count")
    top_companies = (
        grouped.groupby("Company")["Count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index
    )
    grouped = grouped[grouped["Company"].isin(top_companies)]
    companies = top_companies.tolist()
    departments = sorted(grouped["Department"].unique().tolist())

    series = []
    for index, department in enumerate(departments):
        counts_by_company = []
        dept_data = grouped[grouped["Department"] == department].set_index("Company")
        for company in companies:
            counts_by_company.append(int(dept_data["Count"].get(company, 0)))
        series.append(
            {
                "name": department,
                "type": "bar",
                "stack": "total",
                "emphasis": {"focus": "series"},
                "data": counts_by_company,
            }
        )

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"top": 28},
        "grid": {
            "left": 40,
            "right": 20,
            "top": 80,
            "bottom": 90,
            "containLabel": True,
        },
        "xAxis": {
            "type": "category",
            "data": companies,
            "axisLabel": {"rotate": 25, "interval": 0},
        },
        "yAxis": {"type": "value", "name": "Mentions"},
        "series": series,
    }


def department_company_sunburst_options(data: pd.DataFrame, title: str) -> dict:
    tree = []
    grouped = data.groupby(["Department", "Company"]).size().reset_index(name="Count")
    for department in sorted(grouped["Department"].unique().tolist()):
        dept_rows = grouped[grouped["Department"] == department].sort_values(
            "Count", ascending=False
        )
        children = [
            {"name": row["Company"], "value": int(row["Count"])}
            for _, row in dept_rows.iterrows()
        ]
        tree.append({"name": department, "children": children})

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [
            {
                "type": "sunburst",
                "center": ["50%", "55%"],
                "radius": ["14%", "72%"],
                "sort": None,
                "itemStyle": {
                    "borderRadius": 4,
                    "borderWidth": 2,
                    "borderColor": "#fff",
                },
                "label": {"rotate": "radial"},
                "data": tree,
            }
        ],
    }


def relation_frame(
    data: pd.DataFrame,
    left_column: str,
    right_column: str,
    left_label: str,
    right_label: str,
) -> pd.DataFrame:
    if not {left_column, right_column}.issubset(data.columns):
        return pd.DataFrame(columns=[left_label, right_label])

    rows = []
    for _, row in data[[left_column, right_column]].iterrows():
        left_value = row[left_column]
        right_value = row[right_column]
        if pd.isna(left_value) or not str(left_value).strip():
            continue
        if pd.isna(right_value) or not str(right_value).strip():
            continue

        left_items = [
            item.strip() for item in str(left_value).split(",") if item.strip()
        ]
        right_items = [
            item.strip() for item in str(right_value).split(",") if item.strip()
        ]
        for left_item in left_items:
            for right_item in right_items:
                rows.append({left_label: left_item, right_label: right_item})

    return pd.DataFrame(rows)


def crosstab_counts(
    data: pd.DataFrame,
    x_column: str,
    series_column: str,
    x_order: list[str] | None = None,
    series_order: list[str] | None = None,
) -> pd.DataFrame:
    grouped = data.groupby([x_column, series_column]).size().reset_index(name="Count")
    if grouped.empty:
        return grouped

    if x_order:
        x_rank = {value: index for index, value in enumerate(x_order)}
        grouped["x_rank"] = grouped[x_column].map(lambda value: x_rank.get(value, 999))
    else:
        grouped["x_rank"] = grouped[x_column]

    if series_order:
        s_rank = {value: index for index, value in enumerate(series_order)}
        grouped["s_rank"] = grouped[series_column].map(
            lambda value: s_rank.get(value, 999)
        )
    else:
        grouped["s_rank"] = grouped[series_column]

    return grouped.sort_values(
        ["x_rank", "s_rank", "Count"], ascending=[True, True, False]
    ).drop(columns=["x_rank", "s_rank"])


def stacked_bar_options(
    data: pd.DataFrame,
    x_column: str,
    series_column: str,
    title: str,
    x_order: list[str] | None = None,
    series_order: list[str] | None = None,
) -> dict:
    grouped = crosstab_counts(data, x_column, series_column, x_order, series_order)
    if grouped.empty:
        return {}

    x_values = x_order or grouped[x_column].drop_duplicates().tolist()
    series_values = series_order or grouped[series_column].drop_duplicates().tolist()
    series = []
    for series_value in series_values:
        series_slice = grouped[grouped[series_column] == series_value].set_index(
            x_column
        )
        series.append(
            {
                "name": series_value,
                "type": "bar",
                "stack": "total",
                "emphasis": {"focus": "series"},
                "data": [
                    int(series_slice["Count"].get(x_value, 0)) for x_value in x_values
                ],
            }
        )

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"top": 28},
        "grid": {
            "left": 40,
            "right": 20,
            "top": 80,
            "bottom": 90,
            "containLabel": True,
        },
        "xAxis": {
            "type": "category",
            "data": x_values,
            "axisLabel": {"rotate": 25, "interval": 0},
        },
        "yAxis": {"type": "value", "name": "Count"},
        "series": series,
    }


def hierarchy_from_relations(
    data: pd.DataFrame, parent_column: str, child_column: str
) -> list[dict]:
    tree = []
    grouped = (
        data.groupby([parent_column, child_column]).size().reset_index(name="Count")
    )
    for parent in grouped[parent_column].drop_duplicates().tolist():
        parent_rows = grouped[grouped[parent_column] == parent].sort_values(
            "Count", ascending=False
        )
        children = [
            {"name": row[child_column], "value": int(row["Count"])}
            for _, row in parent_rows.iterrows()
        ]
        tree.append({"name": parent, "children": children})
    return tree


def relation_sunburst_options(
    data: pd.DataFrame,
    parent_column: str,
    child_column: str,
    title: str,
    *,
    center: tuple[str, str] = ("50%", "55%"),
    radius: tuple[str, str] = ("14%", "72%"),
) -> dict:
    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [
            {
                "type": "sunburst",
                "center": list(center),
                "radius": list(radius),
                "sort": None,
                "itemStyle": {
                    "borderRadius": 4,
                    "borderWidth": 2,
                    "borderColor": "#fff",
                },
                "label": {"rotate": "radial"},
                "data": hierarchy_from_relations(data, parent_column, child_column),
            }
        ],
    }


def relation_treemap_options(
    data: pd.DataFrame,
    parent_column: str,
    child_column: str,
    title: str,
) -> dict:
    tree = []
    grouped = (
        data.groupby([parent_column, child_column]).size().reset_index(name="Count")
    )
    for parent in grouped[parent_column].drop_duplicates().tolist():
        parent_rows = grouped[grouped[parent_column] == parent].sort_values(
            "Count", ascending=False
        )
        children = [
            {"name": row[child_column], "value": int(row["Count"])}
            for _, row in parent_rows.iterrows()
        ]
        tree.append({"name": parent, "children": children})

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [
            {
                "type": "treemap",
                "top": 60,
                "left": 20,
                "right": 20,
                "bottom": 20,
                "breadcrumb": {"show": False},
                "roam": False,
                "nodeClick": False,
                "label": {"show": True, "formatter": "{b}"},
                "upperLabel": {"show": True, "height": 28},
                "itemStyle": {
                    "borderColor": "#ffffff",
                    "borderWidth": 1,
                    "borderRadius": 10,
                    "gapWidth": 1,
                },
                "levels": [
                    {
                        "itemStyle": {
                            "borderColor": "#ffffff",
                            "borderWidth": 1,
                            "borderRadius": 10,
                            "gapWidth": 1,
                        },
                        "upperLabel": {"show": True, "height": 30},
                    },
                    {
                        "itemStyle": {
                            "borderColor": "#ffffff",
                            "borderWidth": 1,
                            "borderRadius": 10,
                            "gapWidth": 1,
                        }
                    },
                ],
                "data": tree,
            }
        ],
    }


def relation_sankey_options(
    data: pd.DataFrame,
    source_column: str,
    target_column: str,
    value_column: str,
    title: str,
) -> dict:
    sources = data[source_column].dropna().astype(str).unique().tolist()
    targets = data[target_column].dropna().astype(str).unique().tolist()
    nodes = [
        {"name": f"source::{name}", "label": {"formatter": name}} for name in sources
    ] + [{"name": f"target::{name}", "label": {"formatter": name}} for name in targets]
    links = [
        {
            "source": f"source::{str(row[source_column])}",
            "target": f"target::{str(row[target_column])}",
            "value": float(row[value_column]),
        }
        for _, row in data.iterrows()
    ]

    return {
        "color": CHART_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [
            {
                "type": "sankey",
                "top": 60,
                "bottom": 20,
                "left": "12%",
                "right": "12%",
                "nodeWidth": 18,
                "nodeGap": 14,
                "nodeAlign": "justify",
                "emphasis": {"focus": "adjacency"},
                "data": nodes,
                "links": links,
                "lineStyle": {"color": "source", "curveness": 0.5, "opacity": 0.35},
                "label": {"color": "inherit", "fontSize": 13, "distance": 8},
            }
        ],
    }


def heatmap_options(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    value_column: str,
    title: str,
    x_order: list[str] | None = None,
    y_order: list[str] | None = None,
) -> dict:
    x_values = x_order or data[x_column].drop_duplicates().tolist()
    y_values = y_order or data[y_column].drop_duplicates().tolist()
    heatmap_data = []
    for _, row in data.iterrows():
        try:
            x_index = x_values.index(row[x_column])
            y_index = y_values.index(row[y_column])
        except ValueError:
            continue
        heatmap_data.append([x_index, y_index, int(row[value_column])])

    max_value = int(data[value_column].max()) if not data.empty else 0
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"position": "top"},
        "grid": {
            "left": 80,
            "right": 40,
            "top": 70,
            "bottom": 80,
            "containLabel": True,
        },
        "xAxis": {
            "type": "category",
            "data": x_values,
            "axisLabel": {"interval": 0, "rotate": 25},
        },
        "yAxis": {"type": "category", "data": y_values},
        "visualMap": {
            "min": 0,
            "max": max_value,
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": 20,
        },
        "series": [
            {
                "name": value_column,
                "type": "heatmap",
                "data": heatmap_data,
                "label": {"show": True},
                "itemStyle": {
                    "borderColor": "#ffffff",
                    "borderWidth": 6,
                    "borderRadius": 10,
                },
                "emphasis": {
                    "itemStyle": {
                        "borderColor": "#ffffff",
                        "borderWidth": 6,
                        "borderRadius": 10,
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.25)",
                    }
                },
            }
        ],
    }


def relation_heatmap_frame(
    data: pd.DataFrame,
    left_column: str,
    right_column: str,
    left_label: str,
    right_label: str,
) -> pd.DataFrame:
    relation = relation_frame(data, left_column, right_column, left_label, right_label)
    if relation.empty:
        return relation
    return relation.groupby([left_label, right_label]).size().reset_index(name="Count")


def company_cluster(company: str) -> str | None:
    for cluster_name, companies in COMPANY_CLUSTERS.items():
        if company in companies:
            return cluster_name
    return None


def dream_attainability_frame(data: pd.DataFrame) -> pd.DataFrame:
    placement = department_company_frame(data)
    dreams = relation_frame(
        data, "Department", "Dream Companies", "Department", "Dream Company"
    )
    if placement.empty or dreams.empty:
        return pd.DataFrame(columns=["Department", "Match Quality", "Dream Company"])

    placement_by_department = {
        department: set(group["Company"].tolist())
        for department, group in placement.groupby("Department")
    }
    rows = []
    for _, row in dreams.iterrows():
        department = row["Department"]
        dream_company = row["Dream Company"]
        placement_companies = placement_by_department.get(department, set())

        if dream_company in placement_companies:
            match_quality = "Exact Match"
        else:
            dream_cluster = company_cluster(dream_company)
            placement_clusters = {
                company_cluster(company)
                for company in placement_companies
                if company_cluster(company) is not None
            }
            if dream_cluster is not None and dream_cluster in placement_clusters:
                match_quality = "Close Match"
            else:
                match_quality = "Gap"

        rows.append(
            {
                "Department": department,
                "Dream Company": dream_company,
                "Match Quality": match_quality,
            }
        )

    return pd.DataFrame(rows)


def render_department_section(data: pd.DataFrame) -> None:
    column = "Department"
    if column not in data.columns:
        return

    chart_data = distribution_frame(data, column)
    if chart_data.empty:
        return

    st.subheader("By Department")
    left_column, right_column = st.columns(2)
    with left_column:
        st_echarts(
            options=bar_chart_options(chart_data, column, "By Department Bar Chart"),
            height="420px",
            key="department-bar",
        )
    with right_column:
        st_echarts(
            options=pie_chart_options(chart_data, column, "By Department Donut Chart"),
            height="420px",
            key="department-donut",
        )


def render_distribution_section(
    data: pd.DataFrame, heading: str, column: str, order: list[str] | None = None
) -> None:
    if column not in data.columns:
        return

    chart_data = distribution_frame(data, column, order)
    if chart_data.empty:
        return

    st.subheader(heading)
    left_column, right_column = st.columns(2)
    with left_column:
        st_echarts(
            options=bar_chart_options(chart_data, column, f"{heading} Bar Chart"),
            height="420px",
            key=f"{column}-bar",
        )
    with right_column:
        st_echarts(
            options=sunburst_options(chart_data, column, f"{heading} Sunburst"),
            height="360px",
            key=f"{column}-sunburst",
        )


def render_program_year_section(data: pd.DataFrame) -> None:
    if not {"Program", "Year"}.issubset(data.columns):
        return

    st.subheader("By Program and Year")
    left_column, right_column = st.columns(2)
    with left_column:
        program_data = distribution_frame(data, "Program", PROGRAM_ORDER)
        st_echarts(
            options=bar_chart_options(program_data, "Program", "By Program Bar Chart"),
            height="320px",
            key="program-bar",
        )
        if "Program Year" in data.columns:
            program_year_order = sorted(
                data["Program Year"].dropna().astype(str).unique(),
                key=program_year_sort_key,
            )
            program_year_data = distribution_frame(
                data, "Program Year", program_year_order
            )
            st_echarts(
                options=bar_chart_options(
                    program_year_data,
                    "Program Year",
                    "By Program and Year Bar Chart",
                ),
                height="360px",
                key="program-year-bar",
            )
    with right_column:
        st_echarts(
            options=program_year_sunburst_options(data, "By Program and Year Sunburst"),
            height="700px",
            key="program-year-sunburst",
        )


def render_department_company_section(data: pd.DataFrame) -> None:
    company_data = department_company_frame(data)
    if company_data.empty:
        return

    st.subheader("Department and Placement Companies")
    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st_echarts(
            options=department_company_sunburst_options(
                company_data,
                "Department to Company Sunburst",
            ),
            height="800px",
            width="100%",
            key="department-company-sunburst",
        )


def render_info_sources_section(data: pd.DataFrame) -> None:
    exploded = exploded_list_frame(data, "Info Source Categories", "Source")
    if exploded.empty:
        return

    chart_data = distribution_frame(exploded, "Source")
    if chart_data.empty:
        return

    st.subheader("Info Sources")
    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st_echarts(
            options=pie_chart_options(
                chart_data,
                "Source",
                "Info Sources Doughnut Chart",
            ),
            height="800px",
            width="800px",
            key="info-sources-doughnut",
        )


def render_fear_factor_section(data: pd.DataFrame) -> None:
    exploded = exploded_list_frame(data, "Fear Categories", "Fear")
    if exploded.empty:
        return

    chart_data = distribution_frame(exploded, "Fear")
    if chart_data.empty:
        return

    st.subheader("Fear Factor")
    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st_echarts(
            options=pie_chart_options(
                chart_data,
                "Fear",
                "Fear Factor Doughnut Chart",
            ),
            height="800px",
            width="800px",
            key="fear-factor-doughnut",
        )


def render_support_needed_section(data: pd.DataFrame) -> None:
    exploded = exploded_list_frame(data, "Support Categories", "Support")
    if exploded.empty:
        return

    chart_data = distribution_frame(exploded, "Support")
    if chart_data.empty:
        return

    st.subheader("Support Needed")
    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st_echarts(
            options=pie_chart_options(
                chart_data,
                "Support",
                "Support Needed Doughnut Chart",
            ),
            height="800px",
            width="800px",
            key="support-needed-doughnut",
        )


def render_interview_exposure_section(data: pd.DataFrame) -> None:
    column = "Interview Exposure Detail"
    if column not in data.columns:
        return

    chart_data = distribution_frame(data, column)
    if chart_data.empty:
        return

    st.subheader("Interview Exposure")
    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st_echarts(
            options=pie_chart_options(
                chart_data,
                column,
                "Interview Exposure Doughnut Chart",
            ),
            height="800px",
            width="800px",
            key="interview-exposure-doughnut",
        )


def render_fear_support_section(data: pd.DataFrame) -> None:
    relation = relation_frame(
        data,
        "Fear Categories",
        "Support Categories",
        "Fear",
        "Support",
    )
    if relation.empty:
        return

    st.subheader("Fear Factor x Support Needed")
    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st_echarts(
            options=relation_sunburst_options(
                relation,
                "Fear",
                "Support",
                "Fear to Support Sunburst",
            ),
            height="900px",
            width="100%",
            key="fear-support-sunburst",
        )


def render_department_role_section(data: pd.DataFrame) -> None:
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
    left_column, right_column = st.columns(2)
    with left_column:
        st_echarts(
            options=stacked_bar_options(
                relation,
                "Department",
                "Role",
                "Department x Role Target",
            ),
            height="520px",
            key="department-role-bar",
        )
    with right_column:
        st_echarts(
            options=relation_sunburst_options(
                relation,
                "Department",
                "Role",
                "Department to Role Sunburst",
            ),
            height="520px",
            key="department-role-sunburst",
        )


def render_program_exposure_relation_section(data: pd.DataFrame) -> None:
    if not {"Program", "Interview Exposure Detail"}.issubset(data.columns):
        return

    relation = (
        data[["Program", "Interview Exposure Detail"]]
        .dropna()
        .groupby(["Program", "Interview Exposure Detail"])
        .size()
        .reset_index(name="Count")
    )
    st.subheader("Program x Interview Exposure")
    st_echarts(
        options=heatmap_options(
            relation,
            "Program",
            "Interview Exposure Detail",
            "Count",
            "Program x Interview Exposure",
            x_order=PROGRAM_ORDER,
            y_order=[
                "No interviews yet",
                "1-3 interviews",
                "3-5 interviews",
                "More than 5 interviews",
                "Interviewed (count unknown)",
            ],
        ),
        height="520px",
        key="program-exposure-heatmap",
    )


def render_department_dream_section(data: pd.DataFrame) -> None:
    relation = relation_frame(
        data,
        "Department",
        "Dream Companies",
        "Department",
        "Company",
    )
    if relation.empty:
        return

    # Keep the chart readable by limiting to the most-mentioned dream companies.
    top_companies = relation["Company"].value_counts().head(15).index.tolist()
    relation = relation[relation["Company"].isin(top_companies)]

    st.subheader("Department x Dream Companies")
    st_echarts(
        options=relation_sunburst_options(
            relation,
            "Department",
            "Company",
            "Department to Dream Companies",
            center=("50%", "55%"),
            radius=("14%", "72%"),
        ),
        height="900px",
        width="100%",
        key="department-dream-sunburst",
    )


def render_dream_attainability_section(data: pd.DataFrame) -> None:
    attainability = dream_attainability_frame(data)
    if attainability.empty:
        return

    summary = (
        attainability.groupby(["Department", "Match Quality"])
        .size()
        .reset_index(name="Count")
    )
    st.subheader("Department x Dream Attainability")
    left_column, right_column = st.columns(2)
    with left_column:
        st_echarts(
            options=heatmap_options(
                summary,
                "Match Quality",
                "Department",
                "Count",
                "Dream Company Match Quality by Department",
                x_order=["Exact Match", "Close Match", "Gap"],
            ),
            height="520px",
            key="dream-attainability-heatmap",
        )
    with right_column:
        st_echarts(
            options=relation_sunburst_options(
                attainability,
                "Department",
                "Match Quality",
                "Department to Match Quality",
            ),
            height="520px",
            key="dream-attainability-sunburst",
        )


def render_year_info_section(data: pd.DataFrame) -> None:
    relation = relation_heatmap_frame(
        data,
        "Year",
        "Info Source Categories",
        "Year",
        "Source",
    )
    if relation.empty:
        return

    relation["Year Label"] = relation["Year"].map(
        lambda value: f"Year {int(float(value))}"
    )
    st.subheader("Year x Info Sources")
    st_echarts(
        options=heatmap_options(
            relation,
            "Year Label",
            "Source",
            "Count",
            "Year x Info Sources",
            x_order=["Year 1", "Year 2", "Year 3", "Year 4"],
        ),
        height="520px",
        key="year-info-heatmap",
    )


def metric_value(data: pd.DataFrame, column: str, value: str) -> int:
    if column not in data.columns:
        return 0
    return int((data[column].astype(str) == value).sum())


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
            exploded_list_frame(data, "Fear Categories", "Fear Item"),
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
            exploded_list_frame(data, "Support Categories", "Support Item"),
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
        data, "Fear Categories", "Support Categories", "Fear", "Support"
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
        height="720px",
        key="insights-fear-support-heatmap",
    )

    st_echarts(
        options=relation_sankey_options(
            fear_support_heatmap,
            "Fear",
            "Support",
            "Percent",
            "Fear to Support Sankey",
        ),
        height="760px",
        width="100%",
        key="insights-fear-support-sankey",
    )


def render_information_section(data: pd.DataFrame) -> None:
    st.header("Information Pathways")
    st.write(
        "LinkedIn and seniors dominate across years, while the Career Development Cell (CDC) appears as one of several information sources rather than the only trusted channel."
    )

    relation = relation_heatmap_frame(
        data, "Year", "Info Source Categories", "Year", "Source"
    )
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
        height="680px",
        key="insights-year-info-heatmap",
    )


def render_attainability_section(data: pd.DataFrame) -> None:
    st.header("Dream Companies & Accessibility")
    st.write(
        "This view estimates whether students seem to have realistic access to their dream companies through their department's visible placement ecosystem. An exact match means the same company is already showing up in department-level placement mentions, a close match means similar companies from the same hiring cluster are visible, and a gap means that access signal is weak or missing."
    )

    dream_relation = relation_frame(
        data, "Department", "Dream Companies", "Department", "Dream Company"
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

    data, source_name = load_dataset()
    if data is None:
        st.error(f"CSV not found: {DEFAULT_CSV.name}")
        return

    data = normalize_departments(ensure_program_year(data))
    st.caption(f"Loaded: {source_name}")
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
