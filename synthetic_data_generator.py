"""
SBR Datathon 2026 — Synthetic Data Generator for Data Analyst Role
====================================================================

Purpose:
    Generate diverse, realistic synthetic data to augment SBR's training set.
    Targets the gaps identified in the original 35-CV dataset:
      1. Diverse CV writing styles (not templated)
      2. Varied career paths (traditional + non-traditional)
      3. Interview answers at 5 quality levels (the biggest missing piece)
      4. More edge cases for robustness testing

Output:
    - synthetic_cvs.xlsx        (structured CVs + resume text, SBR schema)
    - synthetic_interviews.xlsx (Q&A at 5 quality levels, new schema)

Design Philosophy:
    Diversity must be built INTO the templates, not hoped for from randomness.
    Every CV is assembled from a combinatorial space of:
      - 4 career path types
      - 3 writing tones
      - 5+ industry domains
      - 6+ skill profile types
      - 10+ educational backgrounds
"""

import random
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

random.seed(42)  # reproducibility

# =============================================================================
# 1. VOCABULARY BANKS
# =============================================================================

ARAB_FIRST_NAMES_M = [
    "Abdullah", "Khalid", "Fahad", "Saud", "Mohammed", "Ahmed", "Faisal",
    "Sultan", "Bandar", "Nasser", "Mansour", "Hamad", "Yazeed", "Turki",
    "Talal", "Waleed", "Saleh", "Mishal", "Bader", "Rayan", "Hussein",
    "Mazen", "Omar", "Ibrahim", "Salman", "Yousef", "Rakan", "Nawaf",
    "Anas", "Tariq", "Majed", "Saad", "Ziad", "Hassan", "Ali",
]
ARAB_FIRST_NAMES_F = [
    "Sara", "Fatimah", "Aisha", "Mariam", "Nora", "Reem", "Lina", "Dana",
    "Hala", "Mona", "Maha", "Rana", "Layla", "Hind", "Shahad", "Jana",
    "Rahaf", "Dina", "Amal", "Huda", "Yara", "Noor", "Jawaher", "Amina",
    "Najla", "Noura", "Razan", "Lulu", "Asma", "Hessa", "Sumaya", "Wijdan",
]
ARAB_LAST_NAMES = [
    "Alshahrani", "Alharbi", "Alotaibi", "Alqahtani", "Alzahrani", "Alghamdi",
    "Alenezi", "Alshammari", "Almutairi", "Alfaisal", "Alsubaie", "Alsaud",
    "Alkhalid", "Alfahad", "Alanzi", "Aldosari", "Alomar", "Alnasser",
    "Alrashid", "Alhajri", "Alshehri", "Alhouti", "Almutlaq", "Alabbas",
]

CITIES = ["Riyadh", "Jeddah", "Dammam", "Khobar", "Mecca", "Medina",
          "Abha", "Tabuk", "Hail", "Buraidah"]

# Educational backgrounds with realistic diversity
TRADITIONAL_EDUCATION = [
    "BSc Business Analytics", "BSc Information Systems", "BSc Data Science",
    "BSc Statistics", "BSc Computer Science", "BSc Mathematics",
    "BSc Industrial Engineering", "BSc Economics",
    "MSc Data Science", "MSc Analytics", "MSc Statistics",
]
NON_TRADITIONAL_EDUCATION = [
    "BSc Mechanical Engineering",  # career switcher
    "BSc Accounting",
    "BA Communications",
    "BSc Physics",
    "BSc Marketing",
    "Self-taught (coding bootcamp + 2 years projects)",
    "BSc Biology",  # career switcher
]

CERTIFICATIONS_STRONG = [
    "Google Data Analytics Certificate", "Microsoft PL-300 (Power BI)",
    "Tableau Desktop Specialist", "AWS Data Analytics Specialty",
    "IBM Data Analyst Professional", "Databricks Data Analyst Associate",
    "Snowflake SnowPro Core", "dbt Analytics Engineering",
]
CERTIFICATIONS_AVG = [
    "Coursera SQL for Data Science", "DataCamp Data Analyst Track",
    "Microsoft Excel Specialist", "Google Analytics Certification",
    "Udacity Data Analyst Nanodegree",
]
CERTIFICATIONS_WEAK = [
    "Online course (Udemy SQL Basics)", "University project certificate",
    "Bootcamp completion certificate", "Introductory Excel certification",
    "None",
]

# Companies (real Saudi/regional + fictional)
COMPANIES_LARGE = [
    "STC", "Saudi Aramco", "SABIC", "Almarai", "NCB / SNB", "Al Rajhi Bank",
    "Mobily", "Zain KSA", "Saudi Telecom", "Tabby", "Jahez", "Hungerstation",
]
COMPANIES_MID = [
    "Riyadh Analytics Group", "Tamkeen Data Solutions", "Najd Insights Co.",
    "Afaq Business Intelligence", "Tharwah Consulting", "Bayan Analytics",
    "Manarah Tech", "Saudi FinTech Hub",
]
COMPANIES_SMALL = [
    "DataNest Riyadh", "BlueLayer Analytics", "Nuqta Insights",
    "Khazna Data Co.", "Pulse Metrics", "Mawared Analytics",
]

# Skill vocabularies with SYNONYMS (anti-memorization signal)
SQL_VARIATIONS = ["SQL", "T-SQL", "PL/SQL", "Structured Query Language",
                  "PostgreSQL queries", "MySQL", "BigQuery SQL", "Snowflake SQL"]
BI_VARIATIONS = ["Power BI", "PowerBI", "MS Power BI", "Tableau",
                 "Tableau Desktop", "Looker", "Looker Studio", "Qlik Sense"]
PYTHON_VARIATIONS = ["Python", "Python (pandas)", "Python for analytics",
                     "pandas/NumPy", "Jupyter notebooks"]
CLEANING_VARIATIONS = ["Data cleaning", "Data wrangling", "Data preparation",
                       "ETL basics", "Data quality validation"]
STATS_VARIATIONS = ["Statistics basics", "Descriptive statistics",
                    "Inferential statistics", "Statistical analysis",
                    "Hypothesis testing"]

# Industry/domain context for project variety
DOMAINS = {
    "e-commerce": ["customer funnel", "conversion rate", "cart abandonment",
                   "product recommendation", "merchant performance"],
    "fintech": ["transaction patterns", "fraud detection", "user retention",
                "lending portfolio", "payment analytics"],
    "telecom": ["churn analysis", "network usage", "ARPU trends",
                "customer segmentation", "service quality"],
    "healthcare": ["patient flow", "operational efficiency", "readmission rates",
                   "treatment outcomes", "claims analytics"],
    "government": ["service uptake", "citizen engagement", "operational KPIs",
                   "budget variance", "policy impact"],
    "retail": ["store performance", "inventory turnover", "basket analysis",
               "promotion effectiveness", "regional sales"],
}

# Achievement templates (vary outcome framing — % impact, scope, scale)
ACHIEVEMENT_TEMPLATES_STRONG = [
    "Built {what} that {impact}, used by {scale} stakeholders for {duration}.",
    "Reduced {pain} by {pct}% by {action}, saving an estimated {currency}.",
    "Led end-to-end {project_type} including scoping, modeling, and presenting to {audience}.",
    "Identified {finding} through {method}, which led to {decision}.",
    "Designed {artifact} that became {status} for the {team_or_org}.",
]
ACHIEVEMENT_TEMPLATES_AVG = [
    "Built {what} as part of {team_scope}.",
    "Contributed to {project_type} alongside senior team members.",
    "Helped maintain {artifact} used by the {team_or_org}.",
    "Created {output_type} for monthly reporting.",
]
ACHIEVEMENT_TEMPLATES_WEAK = [
    "Learned {what} during coursework and personal projects.",
    "Used {tool} for class assignments and final-year project.",
    "Familiar with {concept} from online courses.",
    "Helped with {task} during summer internship.",
]

# Edge case profiles (the gold for hackathon — robustness testing)
EDGE_CASE_PROFILES = [
    {
        "type": "career_switcher",
        "description": "Strong communication and domain expertise from non-tech background, now transitioning to data analytics via bootcamp.",
        "expected_issue": "Limited technical depth despite strong soft skills.",
    },
    {
        "type": "overqualified_senior",
        "description": "10+ years experience as data science manager applying for individual contributor role.",
        "expected_issue": "May be misaligned; could leave quickly; team-fit concerns.",
    },
    {
        "type": "inflated_claims",
        "description": "CV lists impressive tools and projects but lacks specificity and measurable outcomes.",
        "expected_issue": "Skills cannot be substantiated under technical probing.",
    },
    {
        "type": "self_taught",
        "description": "No formal degree but strong portfolio with real projects, freelance experience, and active GitHub.",
        "expected_issue": "Profile may be filtered out by simple keyword/credential scans.",
    },
    {
        "type": "academic_only",
        "description": "Strong academic credentials (MSc Statistics) but minimal industry experience.",
        "expected_issue": "Theory-heavy, may struggle with messy real-world data.",
    },
    {
        "type": "long_gap",
        "description": "5-year career gap with recent re-skilling certificate and clear motivation to return.",
        "expected_issue": "Skill freshness needs verification; check current tool fluency.",
    },
    {
        "type": "communication_weak",
        "description": "Strong technical CV but interview answers are off-topic, evasive, or one-line.",
        "expected_issue": "Cannot collaborate with stakeholders effectively despite technical skill.",
    },
]


# =============================================================================
# 2. DATA CLASSES
# =============================================================================

@dataclass
class SyntheticCV:
    candidate_id: str
    role: str
    field: str
    candidate_level: str          # Strong/Average/Weak/Unusual/Surprise
    candidate_name: str
    years_experience: float
    education: str
    certification: str
    core_skills: str              # comma-separated
    tools: str                    # comma-separated
    experience_summary: str
    expected_strengths: str
    expected_weaknesses: str
    surprise_edge_case: str = ""
    testing_use: str = ""
    expected_fit_score: float = 0
    expected_recommendation: str = ""
    privacy_note: str = "Synthetic CV profile; no real personal data."
    resume_text: str = ""         # the full free-text resume


# =============================================================================
# 3. GENERATOR FUNCTIONS
# =============================================================================

def gen_name() -> str:
    gender_male = random.random() < 0.55
    first = random.choice(ARAB_FIRST_NAMES_M if gender_male else ARAB_FIRST_NAMES_F)
    last = random.choice(ARAB_LAST_NAMES)
    return f"{first} {last}"


def gen_core_skills(level: str) -> tuple[str, str]:
    """Generate core skills + tools, using synonym variations to test agent's
    semantic understanding (not keyword matching)."""

    if level == "Strong":
        # Strong candidates have a full skill profile + advanced extras
        skill_pool = [
            random.choice(SQL_VARIATIONS),                   # SQL with variant
            random.choice(BI_VARIATIONS),                    # BI tool with variant
            random.choice(CLEANING_VARIATIONS),              # cleaning with variant
            random.choice(STATS_VARIATIONS),                 # stats with variant
            random.choice(["Excel (advanced)", "Excel — pivots & lookups",
                          "Advanced Excel"]),
        ]
        # Add advanced skills
        advanced = random.sample([
            random.choice(PYTHON_VARIATIONS),
            "Dashboarding",
            "A/B testing",
            "Window functions",
            "Data modeling",
            "Insight communication",
            "ETL pipelines",
        ], k=random.randint(2, 4))
        skills = skill_pool + advanced

        tool_pool = random.sample([
            "Power BI", "Tableau", "BigQuery", "Snowflake", "Python",
            "Excel", "PostgreSQL", "Looker", "Jupyter",
        ], k=random.randint(4, 6))

    elif level == "Average":
        skill_pool = [
            random.choice(SQL_VARIATIONS[:4]),  # less exotic SQL
            random.choice(BI_VARIATIONS[:4]),
            random.choice(CLEANING_VARIATIONS[:3]),
            "Excel",
        ]
        extras = random.sample([
            "Statistics basics", "Dashboarding", "Reporting",
            "Data validation", "Insight communication",
        ], k=random.randint(1, 2))
        skills = skill_pool + extras

        tool_pool = random.sample([
            "Excel", "Power BI", "Tableau", "SQL", "Python",
        ], k=random.randint(3, 4))

    else:  # Weak
        skills = random.sample([
            "Excel", "SQL (basics)", "Power BI (basics)", "Statistics basics",
            "Data cleaning", "basic communication", "Microsoft Office",
        ], k=random.randint(3, 4))
        tool_pool = random.sample([
            "Excel", "Power BI", "SQL", "PowerPoint",
        ], k=random.randint(2, 3))

    return ", ".join(skills), ", ".join(tool_pool)


def gen_experience_summary(level: str, years: float) -> str:
    """Generate varied experience summaries — NOT templated like SBR's data."""

    domain = random.choice(list(DOMAINS.keys()))
    project_focus = random.choice(DOMAINS[domain])

    if level == "Strong":
        verbs = ["Led", "Owned", "Designed", "Architected", "Delivered"]
        scales = ["enterprise-wide", "cross-functional", "multi-region", "company-level"]
        outcomes = [
            f"reducing {random.choice(['query time','report cycle','manual effort'])} by {random.randint(30, 70)}%",
            f"adopted by {random.randint(8, 40)}+ stakeholders across the business",
            f"informing {random.choice(['quarterly strategy','executive decisions','product roadmap'])}",
            f"with a measurable impact of SAR {random.randint(500, 4000)}K",
        ]
        return (f"{random.choice(verbs)} {random.choice(scales)} {domain} analytics "
                f"initiatives focused on {project_focus}, {random.choice(outcomes)}. "
                f"Comfortable presenting findings to senior leadership and translating "
                f"business questions into data-backed answers.")

    elif level == "Average":
        verbs = ["Contributed to", "Supported", "Worked on", "Assisted with"]
        return (f"{random.choice(verbs)} {domain} analytics tasks including {project_focus}. "
                f"{random.choice(['Built dashboards','Wrote SQL queries','Cleaned datasets'])} "
                f"for routine reporting cycles. Comfortable working within established "
                f"processes; growing in {random.choice(['ownership of complex analyses','stakeholder management','technical depth'])}.")

    elif level == "Weak":
        return (f"Recent {random.choice(['graduate','bootcamp completer','intern'])} with "
                f"academic exposure to {project_focus}. Used "
                f"{random.choice(['Excel','SQL basics','Power BI'])} for class projects and "
                f"a {random.choice(['final-year project','capstone'])}. Looking for first "
                f"full role to apply skills practically.")

    else:  # Unusual / edge case — varied phrasing
        return f"[Edge case — see Surprise/Edge Case field for context]"


def gen_resume_text(cv: SyntheticCV) -> str:
    """Generate a free-text resume in one of several writing styles
    to ensure stylistic diversity."""

    style = random.choice(["formal_structured", "results_focused",
                            "compact_modern", "narrative"])
    name = cv.candidate_name.upper()
    city = random.choice(CITIES)
    title_options = [
        "Data Analyst", "Analytics Specialist", "Business Intelligence Analyst",
        "Insights Analyst", "Reporting & Analytics Analyst",
    ] if cv.candidate_level != "Weak" else [
        "Junior Data Analyst", "Data Analytics Intern (recent graduate)",
        "Analytics Trainee",
    ]
    title = random.choice(title_options)
    email = f"{cv.candidate_name.lower().replace(' ', '.')}.{cv.candidate_id.lower()}@example.com"

    # Determine companies based on experience
    if cv.years_experience >= 6:
        companies = random.sample(COMPANIES_LARGE + COMPANIES_MID,
                                  k=min(3, max(2, int(cv.years_experience // 3))))
    elif cv.years_experience >= 3:
        companies = random.sample(COMPANIES_MID + COMPANIES_SMALL,
                                  k=min(3, max(2, int(cv.years_experience // 2))))
    elif cv.years_experience >= 1:
        companies = random.sample(COMPANIES_SMALL + COMPANIES_MID, k=2)
    else:
        companies = []

    if style == "formal_structured":
        # Classic format
        sections = [f"{name}\n{title}\n{city}, Saudi Arabia | {email}\n"]
        sections.append(f"\n--- PROFESSIONAL SUMMARY ---\n{cv.experience_summary}\n")
        sections.append(f"\n--- CORE SKILLS ---\n{cv.core_skills}\n")
        sections.append(f"\n--- TOOLS ---\n{cv.tools}\n")
        if companies:
            sections.append(f"\n--- EXPERIENCE ---")
            current_year = 2025
            for i, comp in enumerate(companies):
                start_year = current_year - int(cv.years_experience / len(companies))
                sections.append(f"\n{title} | {comp} | {start_year} – {current_year if i == 0 else start_year + 2}")
                # Add 2-3 bullets specific to level
                if cv.candidate_level == "Strong":
                    bullets = [
                        f"• Built dashboards used by {random.randint(8,40)}+ stakeholders, cutting reporting time by {random.randint(30,60)}%.",
                        f"• Wrote optimized SQL queries handling {random.randint(5,50)}M rows for {random.choice(['monthly reporting','executive dashboards','operational KPIs'])}.",
                        f"• Presented insights to {random.choice(['exec leadership','product teams','operations'])}, influencing {random.choice(['Q4 strategy','annual planning','process redesign'])}.",
                    ]
                elif cv.candidate_level == "Average":
                    bullets = [
                        f"• Supported reporting workflows in {random.choice(['Excel','Power BI','Tableau'])}.",
                        f"• Wrote SQL queries for routine data pulls and ad-hoc analyses.",
                        f"• Collaborated with team on monthly business reviews.",
                    ]
                else:
                    bullets = [
                        f"• Assisted with data entry, cleanup, and basic reporting.",
                        f"• Used Excel and basic SQL for daily tasks.",
                    ]
                sections.extend(["\n" + b for b in bullets[:random.randint(2,3)]])
                current_year = start_year - 1
        sections.append(f"\n\n--- EDUCATION ---\n{cv.education}")
        if cv.certification != "None":
            sections.append(f"\n\n--- CERTIFICATIONS ---\n{cv.certification}")
        return "\n".join(sections)

    elif style == "results_focused":
        # Punchy, results-led format
        parts = [f"{name} — {title}", f"{city} | {email}", ""]
        parts.append("WHAT I DO")
        parts.append(cv.experience_summary)
        parts.append("")
        parts.append("KEY RESULTS")
        if cv.candidate_level == "Strong":
            parts.append(f"→ Reduced reporting cycle time from days to hours through automation in {random.choice(['Power BI','Tableau','Looker'])}")
            parts.append(f"→ Designed analytics that drove a {random.randint(10,30)}% lift in {random.choice(['conversion','retention','operational efficiency'])}")
            parts.append(f"→ Owned end-to-end delivery of {random.randint(3,8)} analytics products")
        elif cv.candidate_level == "Average":
            parts.append(f"→ Maintained {random.randint(3,6)} business dashboards used weekly")
            parts.append(f"→ Wrote {random.randint(20,50)}+ SQL queries supporting monthly reporting")
        else:
            parts.append(f"→ Completed academic projects covering core data analyst skills")
        parts.append("")
        parts.append(f"STACK: {cv.tools}")
        parts.append(f"SKILLS: {cv.core_skills}")
        parts.append("")
        if companies:
            parts.append("EXPERIENCE")
            for comp in companies:
                parts.append(f"  {title} @ {comp}")
        parts.append(f"\nEDUCATION: {cv.education}")
        if cv.certification != "None":
            parts.append(f"CERTIFICATIONS: {cv.certification}")
        return "\n".join(parts)

    elif style == "compact_modern":
        # Modern, scannable
        parts = [
            f"## {name}",
            f"*{title} · {city} · {email}*",
            "",
            "### About",
            cv.experience_summary,
            "",
            f"**Skills:** {cv.core_skills}",
            f"**Tools:** {cv.tools}",
            "",
        ]
        if companies:
            parts.append("### Experience")
            for comp in companies:
                parts.append(f"- **{title}** at *{comp}*")
                if cv.candidate_level == "Strong":
                    parts.append(f"  Led {random.choice(['analytics','BI','data'])} work that influenced {random.choice(['executive decisions','product strategy','operations'])}.")
        parts.append(f"\n### Education\n{cv.education}")
        if cv.certification != "None":
            parts.append(f"\n### Certifications\n- {cv.certification}")
        return "\n".join(parts)

    else:  # narrative
        # Story-driven first-person summary
        intro = random.choice([
            f"I'm a {title.lower()} based in {city}, focused on turning messy data into clear decisions.",
            f"Hi — I'm a {title.lower()} who's spent the last {int(cv.years_experience) if cv.years_experience >= 1 else 'few'} years helping teams in {random.choice(list(DOMAINS.keys()))} make data-backed choices.",
            f"My work as a {title.lower()} sits at the intersection of business questions and data answers.",
        ])
        parts = [f"{name}\n{title} | {city} | {email}\n\n{intro}\n\n{cv.experience_summary}"]
        parts.append(f"\nCore skills include: {cv.core_skills}.")
        parts.append(f"\nTools I work with day-to-day: {cv.tools}.")
        if companies:
            parts.append(f"\nMost recently I've worked at {companies[0]}" + (f", and previously at {', '.join(companies[1:])}." if len(companies) > 1 else "."))
        parts.append(f"\nEducation: {cv.education}.")
        if cv.certification != "None":
            parts.append(f"Certifications: {cv.certification}.")
        return "\n".join(parts)


def compute_expected_score(level: str) -> tuple[float, str]:
    """Compute Fit Score + Recommendation per the Rubric thresholds."""
    if level == "Strong":
        score = round(random.uniform(80, 96), 0)
        rec = "Recommend"
    elif level == "Average":
        score = round(random.uniform(60, 79), 0)
        rec = "Maybe / needs further assessment"
    elif level == "Weak":
        score = round(random.uniform(20, 49), 0)
        rec = "Do not recommend"
    else:  # Unusual / edge case — can land anywhere
        score = round(random.uniform(40, 80), 0)
        rec = "Conditional / requires follow-up interview"
    return score, rec


def gen_edge_case_profile() -> dict:
    """Generate one edge case profile with intentional inconsistency."""
    profile = random.choice(EDGE_CASE_PROFILES)
    edge_type = profile["type"]

    # Build a CV that intentionally creates the tension described in the profile
    if edge_type == "career_switcher":
        years = round(random.uniform(2, 6), 1)
        education = random.choice(NON_TRADITIONAL_EDUCATION)
        cert = random.choice(["Bootcamp completion certificate",
                              "Google Data Analytics Certificate"])
        skills = "Excel, SQL (bootcamp level), Power BI (intermediate), transferable communication skills"
        tools = "Excel, Power BI, SQL"
        summary = "Career switcher from non-tech background. Strong communication and stakeholder skills; rebuilding technical foundation through bootcamp and self-study. Has completed 2-3 portfolio projects but limited paid analytics experience."

    elif edge_type == "overqualified_senior":
        years = round(random.uniform(10, 14), 1)
        education = "MSc Data Science"
        cert = random.choice(CERTIFICATIONS_STRONG)
        skills = "SQL, Python, Power BI, Tableau, Statistical modeling, Team leadership, Project management"
        tools = "Snowflake, dbt, Python, Power BI, Looker"
        summary = "Senior analytics leader with 10+ years including 5 years managing teams. Applying for individual contributor role — may be a step backward or strategic move. Strong technical foundation but expectations around scope, compensation, and trajectory must be clarified."

    elif edge_type == "inflated_claims":
        years = round(random.uniform(3, 5), 1)
        education = random.choice(TRADITIONAL_EDUCATION)
        cert = random.choice(CERTIFICATIONS_AVG)
        skills = "Advanced SQL, Machine Learning, Power BI, Tableau, Python, R, Big Data, Cloud Architecture, Data Science"
        tools = "Snowflake, Databricks, AWS, Azure, GCP, Python, R, SAS, SPSS"
        summary = "Lists extensive skill portfolio but specific project descriptions are vague. Claims mastery across many tools and advanced techniques but resume lacks measurable outcomes or specific examples. High risk for technical probing."

    elif edge_type == "self_taught":
        years = round(random.uniform(2, 4), 1)
        education = "Self-taught (coding bootcamp + 2 years projects)"
        cert = "Portfolio-based evidence; GitHub with 15+ projects"
        skills = "SQL, Python (pandas, NumPy), Tableau, Power BI, Statistics, Data cleaning"
        tools = "Python, SQL, Tableau, Git, Jupyter"
        summary = "Self-taught analyst with no formal degree but active GitHub portfolio and 2+ years of freelance data work. Strong on practical skills; may be filtered by traditional CV scanners but performs strongly in technical assessments."

    elif edge_type == "academic_only":
        years = round(random.uniform(0, 2), 1)
        education = "MSc Statistics"
        cert = "Research assistant certification"
        skills = "R, Python, Statistical modeling, Hypothesis testing, SQL (academic), Research methodology"
        tools = "R, RStudio, Python, SPSS, basic SQL"
        summary = "Recent MSc graduate with strong statistical foundation and research experience but minimal industry exposure. Has published academic work but no business stakeholder experience. Will need ramp-up on production data tools and business context."

    elif edge_type == "long_gap":
        years = round(random.uniform(4, 7), 1)
        education = random.choice(TRADITIONAL_EDUCATION)
        cert = "Recent professional certificate (Google Data Analytics, 2024)"
        skills = "SQL, Power BI, Excel, Data analysis, Stakeholder communication"
        tools = "Power BI, Excel, SQL"
        summary = "Experienced analyst with previous 4-7 years in data roles, followed by 5-year career gap. Recently completed re-skilling certificate (2024) and demonstrating strong motivation to return. Tool fluency and current best practices need verification."

    else:  # communication_weak
        years = round(random.uniform(4, 7), 1)
        education = random.choice(TRADITIONAL_EDUCATION)
        cert = random.choice(CERTIFICATIONS_STRONG)
        skills = "SQL, Python, Power BI, Statistical analysis, Data modeling, BigQuery"
        tools = "Power BI, SQL, Python, BigQuery, Tableau"
        summary = "Solid technical CV with relevant tools and experience but interview behavior suggests difficulty articulating insights or engaging with stakeholders. Strong individual contributor potential but may struggle in cross-functional collaboration."

    return {
        "years_experience": years,
        "education": education,
        "certification": cert,
        "core_skills": skills,
        "tools": tools,
        "experience_summary": summary,
        "edge_case_type": edge_type,
        "edge_case_description": profile["description"],
        "expected_issue": profile["expected_issue"],
    }


def build_cv(level: str, idx: int) -> SyntheticCV:
    cid = f"SYN-DA-{idx:03d}"

    if level == "Unusual/Surprise":
        edge = gen_edge_case_profile()
        cv = SyntheticCV(
            candidate_id=cid, role="Data Analyst", field="Tech / Data",
            candidate_level=level,
            candidate_name=gen_name(),
            years_experience=edge["years_experience"],
            education=edge["education"],
            certification=edge["certification"],
            core_skills=edge["core_skills"],
            tools=edge["tools"],
            experience_summary=edge["experience_summary"],
            expected_strengths=f"Unique profile: {edge['edge_case_description']}",
            expected_weaknesses=edge["expected_issue"],
            surprise_edge_case=edge["edge_case_type"],
            testing_use="Use to test robustness and follow-up logic.",
        )
    else:
        # Years tied to level for realism
        if level == "Strong":
            years = round(random.uniform(4, 9), 1)
            edu = random.choice(TRADITIONAL_EDUCATION)
            cert = random.choice(CERTIFICATIONS_STRONG)
            strengths = random.choice([
                "Strong evidence of role-specific results with measurable impact",
                "Solid technical depth across SQL, BI, and analytics",
                "Clear stakeholder communication backed by quantified outcomes",
                "End-to-end ownership of analytics projects with business influence",
            ])
            weaknesses = random.choice([
                "May need onboarding on company-specific tools and processes",
                "Limited exposure to very large-scale enterprise environments",
                "Cross-domain breadth could be expanded",
                "Some advanced techniques (e.g., A/B testing) need verification",
            ])
            testing_use = "Use as a normal fit case (Strong)."

        elif level == "Average":
            years = round(random.uniform(2, 5), 1)
            edu = random.choice(TRADITIONAL_EDUCATION + ["BSc Business Administration"])
            cert = random.choice(CERTIFICATIONS_AVG)
            strengths = random.choice([
                "Competent with core tools and routine analytics tasks",
                "Can execute defined work with limited guidance",
                "Practical exposure to SQL and BI in real settings",
                "Comfortable in collaborative analytics workflows",
            ])
            weaknesses = random.choice([
                "Limited ownership of complex or ambiguous problems",
                "Examples lack specificity in measurable impact",
                "Communication skills adequate but not differentiating",
                "Some skills claimed but depth is uncertain",
            ])
            testing_use = "Use to test borderline scoring."

        else:  # Weak
            years = round(random.uniform(0, 1.5), 1)
            edu = random.choice(TRADITIONAL_EDUCATION + NON_TRADITIONAL_EDUCATION)
            cert = random.choice(CERTIFICATIONS_WEAK)
            strengths = random.choice([
                "Foundational awareness of data analyst concepts",
                "Recent academic exposure to core tools",
                "Motivation to learn evident in coursework",
            ])
            weaknesses = random.choice([
                "Insufficient practical experience for the role",
                "Skill claims not supported by concrete project examples",
                "Limited tool proficiency beyond classroom usage",
                "Weak measurable outcomes in described work",
            ])
            testing_use = "Use to test rejection reasoning."

        skills, tools = gen_core_skills(level)
        summary = gen_experience_summary(level, years)

        cv = SyntheticCV(
            candidate_id=cid, role="Data Analyst", field="Tech / Data",
            candidate_level=level,
            candidate_name=gen_name(),
            years_experience=years,
            education=edu, certification=cert,
            core_skills=skills, tools=tools,
            experience_summary=summary,
            expected_strengths=strengths,
            expected_weaknesses=weaknesses,
            testing_use=testing_use,
        )

    score, rec = compute_expected_score(level)
    cv.expected_fit_score = score
    cv.expected_recommendation = rec
    cv.resume_text = gen_resume_text(cv)
    return cv


# =============================================================================
# 4. INTERVIEW ANSWER GENERATOR
# =============================================================================
# Generate sample answers at 5 quality levels for key interview questions.
# This is the BIGGEST gap in SBR's data — no answers exist at all.

INTERVIEW_QUESTIONS_DA = [
    {
        "qid": "DA-Q01",
        "category": "Technical (SQL)",
        "question": "Walk me through how you would extract monthly active users from a `users` table and an `events` table.",
        "rubric_dimension": "D1 Technical",
    },
    {
        "qid": "DA-Q02",
        "category": "Technical (SQL deep)",
        "question": "How do you handle NULL values when joining tables, and when would you use a LEFT JOIN vs INNER JOIN?",
        "rubric_dimension": "D1 Technical",
    },
    {
        "qid": "DA-Q03",
        "category": "Analytical Thinking",
        "question": "Revenue dropped 15% last month. How would you investigate the cause?",
        "rubric_dimension": "D2 Analytical",
    },
    {
        "qid": "DA-Q04",
        "category": "Statistics",
        "question": "When would you use the median instead of the mean? Can you give an example from your work?",
        "rubric_dimension": "D2 Analytical",
    },
    {
        "qid": "DA-Q05",
        "category": "BI / Dashboarding",
        "question": "Tell me about a dashboard you built. What decisions did it inform?",
        "rubric_dimension": "D1 + D3",
    },
    {
        "qid": "DA-Q06",
        "category": "Business Communication",
        "question": "Explain the most complex analysis you've done to someone with no technical background.",
        "rubric_dimension": "D3 Business",
    },
    {
        "qid": "DA-Q07",
        "category": "Business Impact",
        "question": "Describe a time your analysis changed a business decision.",
        "rubric_dimension": "D3 Business",
    },
    {
        "qid": "DA-Q08",
        "category": "Data Quality",
        "question": "How do you validate that your data is correct before presenting findings?",
        "rubric_dimension": "D2 + D1",
    },
    {
        "qid": "DA-Q09",
        "category": "Tools",
        "question": "What's your go-to tool stack for a new analysis, and why?",
        "rubric_dimension": "D1 Technical",
    },
    {
        "qid": "DA-Q10",
        "category": "Stakeholder Mgmt",
        "question": "How do you handle a stakeholder who wants a dashboard but can't tell you exactly what they need?",
        "rubric_dimension": "D3 + D5",
    },
]

# Answer templates at 5 quality levels per question
# (We build the answers programmatically with variation to avoid templating)

ANSWER_BUILDERS = {

    "DA-Q01": {  # SQL: monthly active users
        5: lambda: f"""I'd start by clarifying the definition of "active" — typically a unique user who triggered at least one event in the month. Then:

```sql
SELECT DATE_TRUNC('month', e.event_time) AS month,
       COUNT(DISTINCT e.user_id) AS mau
FROM events e
INNER JOIN users u ON e.user_id = u.id
WHERE u.status = 'active'
  AND e.event_time >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1;
```

A few things I'd double-check: that `event_time` is in the right timezone, that I'm not counting bot or test accounts, and whether the business definition of "active" needs a specific event type (e.g., only meaningful actions, not just page views). I'd also validate by spot-checking one month manually.""",

        4: lambda: f"""I'd write something like:

```sql
SELECT DATE_TRUNC('month', event_time) AS month,
       COUNT(DISTINCT user_id) AS mau
FROM events
WHERE event_time >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY 1;
```

I'd join with the users table if I need to filter for specific user attributes — for example, only paid users or only users from a specific region. DATE_TRUNC handles the monthly grouping. I'd verify the output looks reasonable by comparing to prior reports if available.""",

        3: lambda: f"""I would use SQL to count unique users per month. Something like SELECT month, COUNT DISTINCT user_id FROM events grouped by month. I'd join with the users table to make sure they're real active users. The DISTINCT is important so I don't count the same user multiple times.""",

        2: lambda: f"""I'd use SQL. Probably SELECT COUNT user_id FROM events and group by date. Maybe I'd need to join with the users table to filter out test users or something. I think there's a function to get the month from a date but I'd have to check the syntax.""",

        1: lambda: f"""Hmm, I'd probably need to look this up. I know SQL but I'm not sure exactly how to get monthly numbers. I'd ask a senior team member or check Stack Overflow for the right query.""",
    },

    "DA-Q03": {  # Revenue drop investigation
        5: lambda: f"""First, I'd resist the urge to immediately query data — I'd want to confirm the 15% number is real. Is it 15% MoM? Year-over-year? Compared to forecast? Are we sure it's not a data issue (delayed events, broken pipeline)?

Once confirmed, I'd decompose: revenue = users × conversion × ARPU. Which factor moved? Then I'd segment:
- By product line: is the drop concentrated in one product?
- By acquisition channel: did paid traffic drop?
- By geography or customer segment: did a specific market underperform?
- By time within the month: was it gradual or a cliff?

I'd also check external factors — was there a competitor launch, a seasonal effect, a marketing campaign that ended, a regulatory change? Internal: was there a pricing change, a checkout bug, a stockout?

Throughout, I'd be cautious about Simpson's paradox — the aggregate might mask offsetting segment movements. I'd present findings as "here's what we know, here's what we suspect, here's what needs more investigation" — not jumping to a single cause prematurely.""",

        4: lambda: f"""I'd start by breaking down revenue into its components: number of customers, average order value, and conversion rate. Then I'd check which one dropped.

I'd also segment the data — by region, by product, by channel — to see if the drop is concentrated somewhere specific. For example, maybe one big customer churned, or a particular channel's performance fell off.

I'd compare against the same month last year to rule out seasonality, and I'd check if there were any operational issues (system downtime, marketing campaign changes, pricing updates).

I'd put together a hypothesis-driven report rather than just showing the drop — focusing on the most likely cause and recommending next steps.""",

        3: lambda: f"""I'd pull the revenue data and look at month-over-month changes. I'd break it down by product or region to see where the drop is. I'd also check if customer count dropped or if average revenue per customer dropped. Then I'd present the findings and let leadership decide on next steps.""",

        2: lambda: f"""I'd look at the data in the dashboard and see what's causing the 15% drop. Maybe I'd compare with previous months. I'd probably make a chart showing the trend and share it with my manager.""",

        1: lambda: f"""I'd ask my manager what they want me to look at first. I'm not sure where to start without more context — like which department this is for or what tools to use.""",
    },

    "DA-Q06": {  # Explain complex analysis simply
        5: lambda: f"""Last year I worked on a churn prediction model for our subscription product. When I explained it to our COO, who's not technical, I framed it like this:

"Imagine each customer has a profile — how often they log in, how long since their last purchase, what they've spent. We looked back at customers who left us in the past year and asked: what did their profiles look like *before* they left? Turns out, three signals showed up repeatedly — declining login frequency, no purchase in 30 days, and lowered support ticket activity. So now, when a current customer's profile starts matching that pattern, we flag them for our retention team."

I avoided words like "logistic regression," "feature importance," and "AUC." Instead I gave him a concrete number he could anchor on: "Of the top 100 customers we flagged last month, 73 had actually been at risk — meaning the retention team's time is spent on real cases, not noise." That landed for him because he cares about his team's productivity, not the model's math.""",

        4: lambda: f"""I built a customer segmentation model and had to explain it to our marketing director. Instead of talking about clustering algorithms, I said: "We sorted all our customers into 5 groups based on how they behave — how often they buy, what they buy, how much they spend. Each group needs a different message. For example, Group A buys monthly and responds to loyalty rewards. Group B is one-time buyers who need different incentives to come back."

I used a simple table showing each group's size and behavior, and tied each one to a specific marketing action. That made it concrete — she could immediately use it to plan campaigns.""",

        3: lambda: f"""I worked on a sales forecasting project. When I presented to non-technical stakeholders, I avoided statistical terms and used charts to show "here's what happened last year, and here's what we expect this year based on the trends." I focused on what they could do with the information rather than how I built it.""",

        2: lambda: f"""I usually try to use simple language and not too many numbers. I show charts and explain the main finding. I avoid technical terms like SQL or pivot tables.""",

        1: lambda: f"""I haven't really had to do that much. Usually I just send the report and they figure it out, or I explain to my manager and they handle the rest.""",
    },

    "DA-Q10": {  # Vague stakeholder request
        5: lambda: f"""I treat this as a discovery conversation, not a requirements gathering one. I'll ask three categories of questions:

1. **Decision questions**: "What decision are you trying to make with this dashboard? Who's the audience?" — because dashboards aren't outputs, they're tools for decisions.

2. **Behavior questions**: "When you look at this in 3 months, what would make you say 'this is exactly what I needed' vs 'this isn't useful'?" — this surfaces unstated success criteria.

3. **Anchor questions**: "Can you show me a dashboard, report, or even a screenshot of something close to what you imagine?" — concrete references unstick people who can't articulate abstractly.

Then I propose a quick low-fi mockup — even on paper or a whiteboard — and iterate. I avoid building anything until they've reacted to a draft. I've found stakeholders often discover what they want by reacting to a wrong version, not by being asked the right question upfront.""",

        4: lambda: f"""I start by asking what decisions they need to make and who else will use the dashboard. I try to understand the business context first — what's the problem they're solving, not just what data they want to see.

Then I usually build a quick prototype with sample data and walk them through it. They almost always have feedback like "actually I need this broken down by region" or "this metric isn't what I meant" — which is much faster than trying to nail it down in one meeting.""",

        3: lambda: f"""I ask them questions about what they want to see and what they'll use it for. I might also look at examples of similar dashboards they like. Then I build a first version and get their feedback.""",

        2: lambda: f"""I'd ask my manager or a senior person what they think the stakeholder needs. Or I'd build something based on standard dashboards and see if they like it.""",

        1: lambda: f"""I'm not sure. Maybe send them a template and let them choose what they want?""",
    },
}

# Add lighter coverage for the other questions (Levels 5, 3, 1 only, with brief content)
LIGHT_ANSWER_BUILDERS = {
    "DA-Q02": {
        5: "LEFT JOIN keeps all rows from the left table even when there's no match — essential when you want to count records including those without matches (e.g., users with zero events). INNER JOIN drops those. With NULLs, you have to be careful with WHERE clauses after LEFT JOIN, because filtering on the right table's column converts it effectively to an INNER JOIN. I usually use COALESCE to handle NULLs explicitly, and I'm cautious about NULL behavior in aggregations — COUNT(column) ignores NULLs but COUNT(*) doesn't.",
        3: "LEFT JOIN keeps all rows from the first table, INNER JOIN only keeps matching rows. NULLs can be tricky — they don't equal anything, even themselves, so I use IS NULL to check for them. I'd use LEFT JOIN when I want to keep all users even those without orders.",
        1: "I think LEFT JOIN keeps everything? And NULL is when there's no value. I'd probably look up the syntax.",
    },
    "DA-Q04": {
        5: "Median when the distribution is skewed or has outliers — income, response times, deal sizes. The mean gets pulled by outliers and misleads. Example: in a recent project on customer transaction values, the mean was SAR 2,400 but the median was SAR 380. The mean was misleading leadership about typical customer behavior. I presented both, but recommended median for the customer-typical narrative and used the mean only when discussing total revenue impact.",
        3: "Median is better when there are outliers or the data is skewed. For example, if you have salaries and the CEO's salary skews everything, median gives a better sense of typical pay.",
        1: "Median is the middle number, mean is the average. I'm not sure when one is better than the other.",
    },
    "DA-Q05": {
        5: "I built an operations dashboard for our customer support team to track ticket volume, response times, and CSAT by agent and queue. Before the dashboard, the team lead spent ~4 hours per week pulling these numbers manually from three systems. After the dashboard launched, that dropped to zero — and more importantly, they spotted a 2-day spike in response times that traced back to a buggy chatbot deflection. They turned the chatbot off, response times normalized, and CSAT went back up. The decision the dashboard *enabled* was 'monitor and act in real time' rather than 'react to last month's report.'",
        3: "I built a sales dashboard in Power BI that showed daily revenue by region and product. The sales team used it in their weekly meetings to spot trends. It helped them notice when one product was underperforming so they could adjust their pitch.",
        1: "I made a dashboard in Excel for a class project. It showed some sales numbers in charts.",
    },
    "DA-Q07": {
        5: "We were planning to expand our delivery network into a new city based on order volume. My analysis showed that while order volume was high, our delivery cost per order in that city would be 40% higher due to longer distances and lower order density. I built a sensitivity analysis showing break-even under different scenarios. Leadership delayed expansion by 2 quarters and ran a pilot first — which proved my model was directionally correct. They eventually launched with adjusted pricing.",
        3: "I noticed a particular product had a high return rate. After investigating, I found that one supplier was responsible for most of the issues. We switched suppliers and returns dropped significantly.",
        1: "I don't think I've ever changed a decision. I just give the numbers and managers decide.",
    },
    "DA-Q08": {
        5: "Multiple layers: (1) Row-count sanity checks against source — does my aggregate add back to the raw data? (2) Spot-checking specific known cases — pick a customer or date I know and verify the number matches what I'd expect. (3) Comparison to prior reports for trend continuity. (4) Cross-validating with a different data source if one exists. (5) Sense-check for nonsensical values — negative ages, future dates, percentages above 100. And before any presentation, I write a brief 'caveats' section noting any known data limitations.",
        3: "I check that the totals match other reports we have, and I look for obvious problems like missing data or weird values. I might compare to last month to make sure the trend makes sense.",
        1: "I just trust the data from the database. If something looks wrong I might re-run it.",
    },
    "DA-Q09": {
        5: "Depends on the question. For exploratory analysis on a new dataset, I start in a Jupyter notebook with pandas — fast iteration, easy to document. For SQL-heavy work against a warehouse, I use the warehouse's native interface (BigQuery console or Snowflake worksheets). For stakeholder-facing dashboards, Power BI or Tableau depending on the org's standard. For one-off ad-hoc requests, often Excel still wins on speed. I pick based on (a) data volume, (b) who else needs to read/maintain the work, and (c) whether the output is one-off or recurring.",
        3: "I usually use SQL to pull data, Excel for quick analysis, and Power BI for dashboards. Sometimes Python if I need to do something more complex.",
        1: "Mostly Excel. Sometimes SQL if needed.",
    },
}


def build_interview_dataset() -> pd.DataFrame:
    """Build the synthetic interview Q&A dataset across quality levels."""
    rows = []
    for q in INTERVIEW_QUESTIONS_DA:
        qid = q["qid"]
        # Full builders for some, light for others
        if qid in ANSWER_BUILDERS:
            for level in [5, 4, 3, 2, 1]:
                if level in ANSWER_BUILDERS[qid]:
                    answer = ANSWER_BUILDERS[qid][level]()
                    rows.append({
                        "Question ID": qid,
                        "Category": q["category"],
                        "Question Text": q["question"],
                        "Rubric Dimension": q["rubric_dimension"],
                        "Quality Level": level,
                        "Quality Label": {5: "Expert", 4: "Strong",
                                          3: "Adequate", 2: "Below Bar",
                                          1: "Insufficient"}[level],
                        "Answer Text": answer,
                        "Triggers Follow-up": "Yes" if level <= 3 else "No",
                    })
        elif qid in LIGHT_ANSWER_BUILDERS:
            for level in [5, 3, 1]:
                rows.append({
                    "Question ID": qid,
                    "Category": q["category"],
                    "Question Text": q["question"],
                    "Rubric Dimension": q["rubric_dimension"],
                    "Quality Level": level,
                    "Quality Label": {5: "Expert", 3: "Adequate",
                                      1: "Insufficient"}[level],
                    "Answer Text": LIGHT_ANSWER_BUILDERS[qid][level],
                    "Triggers Follow-up": "Yes" if level <= 3 else "No",
                })

    return pd.DataFrame(rows)


# =============================================================================
# 5. MAIN — generate and save
# =============================================================================

def generate_full_dataset(n_strong=40, n_average=30, n_weak=20, n_unusual=15):
    """Generate the full synthetic dataset."""
    cvs = []
    idx = 1
    for _ in range(n_strong):
        cvs.append(build_cv("Strong", idx)); idx += 1
    for _ in range(n_average):
        cvs.append(build_cv("Average", idx)); idx += 1
    for _ in range(n_weak):
        cvs.append(build_cv("Weak", idx)); idx += 1
    for _ in range(n_unusual):
        cvs.append(build_cv("Unusual/Surprise", idx)); idx += 1

    random.shuffle(cvs)  # mix the order so tiers aren't sequential

    return cvs


def cvs_to_dataframes(cvs: list[SyntheticCV]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split CVs into the two SBR-compatible sheets."""
    cv_db_rows = []
    resume_rows = []
    for cv in cvs:
        cv_db_rows.append({
            "Candidate ID": cv.candidate_id,
            "Role": cv.role,
            "Field": cv.field,
            "Candidate Level": cv.candidate_level,
            "Candidate Name": cv.candidate_name,
            "Years Experience": cv.years_experience,
            "Education": cv.education,
            "Certification": cv.certification,
            "Core Skills": cv.core_skills,
            "Tools": cv.tools,
            "Experience Summary": cv.experience_summary,
            "Expected Strengths": cv.expected_strengths,
            "Expected Weaknesses": cv.expected_weaknesses,
            "Surprise / Edge Case": cv.surprise_edge_case,
            "Testing Use": cv.testing_use,
            "Expected Fit Score": cv.expected_fit_score,
            "Expected Recommendation": cv.expected_recommendation,
            "Privacy Note": cv.privacy_note,
        })
        resume_rows.append({
            "Candidate ID": cv.candidate_id,
            "Role": cv.role,
            "Resume Text": cv.resume_text,
        })
    return pd.DataFrame(cv_db_rows), pd.DataFrame(resume_rows)


if __name__ == "__main__":
    output_dir = Path("/mnt/user-data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic CVs...")
    cvs = generate_full_dataset(n_strong=40, n_average=30, n_weak=20, n_unusual=15)
    cv_df, resume_df = cvs_to_dataframes(cvs)

    print("Generating synthetic interview Q&A...")
    qa_df = build_interview_dataset()

    # Save to two Excel files (matching/compatible with SBR's schema)
    cv_path = output_dir / "synthetic_cvs.xlsx"
    qa_path = output_dir / "synthetic_interviews.xlsx"

    with pd.ExcelWriter(cv_path, engine="openpyxl") as writer:
        cv_df.to_excel(writer, sheet_name="CV Database", index=False)
        resume_df.to_excel(writer, sheet_name="Resume Text", index=False)

    with pd.ExcelWriter(qa_path, engine="openpyxl") as writer:
        qa_df.to_excel(writer, sheet_name="Interview Answers", index=False)

    print(f"\n✓ Generated {len(cvs)} synthetic CVs:")
    print(cv_df["Candidate Level"].value_counts().to_string())
    print(f"\n✓ Generated {len(qa_df)} synthetic interview answers across "
          f"{qa_df['Question ID'].nunique()} questions and "
          f"{qa_df['Quality Level'].nunique()} quality levels.")
    print(f"\nFiles saved to:")
    print(f"  • {cv_path}")
    print(f"  • {qa_path}")
