# ATS Resume Engine: Technical Specification & Setup Guide

This specification defines the architecture, data schemas, directory structure, and operational scripts for an automated, ATS-optimized CV tailoring engine powered by a Single Source of Truth (SSOT), an LLM extraction pipeline, and Typst.

## 1. System Architecture

```
┌─────────────────────────┐      ┌─────────────────────────┐
│ master_experience.yaml  │  +   │      inputs/jd.txt      │
│  (Complete Career SSOT) │      │  (Raw Target Job Post)  │
└────────────┬────────────┘      └────────────┬────────────┘
             │                                │
             └───────────────┬────────────────┘
                             │
                             ▼
               [ LLM Tailoring Engine ]
        (Strict Grounding, ATS Match, Schema Enforcement)
                             │
                             ▼
                 dist/tailored_cv.yaml
             (Filtered, Harmonized Subset)
                             │
                             ▼
               [ Typst Compilation Engine ]
                 (Reads dist/tailored_cv.yaml)
                             │
                             ▼
                      dist/resume.pdf
                  (ATS-Compliant Output)

```

## 2. Directory Structure

```
resume-engine/
├── .env.example              # Sample environment configuration
├── .env                      # Real credentials (ignored by git)
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── master_experience.yaml    # Master career database (SSOT)
├── template.typ              # Typst layout & typesetting template
├── generate.py               # Orchestrator script
├── inputs/
│   └── jd.txt                # Raw job description input
└── dist/                     # Build artifacts directory (ignored by git)
    ├── tailored_cv.yaml      # Intermediate structured data
    └── resume.pdf            # Compiled ATS-ready PDF

```

## 3. Environment & Prerequisites

* **Python:** 3.10+

* **Typst:** Managed via the Python `typst` wheel binding (no manual CLI binary required).

* **LLM Provider:** Google Gemini API (uses the `google-genai` SDK) or compatible OpenAI/Anthropic alternatives.

## 4. File Specifications

### 4.1. `requirements.txt`

```
google-genai>=0.1.1
python-dotenv>=1.0.0
pyyaml>=6.0.1
typst>=0.12.0

```

### 4.2. `.gitignore`

```
# Virtual environment
.venv/
env/
ENV/

# Secrets
.env

# Python cache
__pycache__/
*.pyc

# Build outputs
dist/
!dist/.gitkeep

# Local user inputs
inputs/jd.txt
!inputs/.gitkeep

```

### 4.3. `.env.example`

```
GEMINI_API_KEY="your_api_key_here"

```

### 4.4. `master_experience.yaml` (SSOT Schema)

This file represents the exhaustive superset of your professional history. Do not prune this file; the LLM selects from it.

```
basics:
  name: "Jane Doe"
  email: "jane.doe@example.com"
  phone: "+1 (555) 019-2834"
  location: "San Francisco, CA"
  linkedin: "linkedin.com/in/janedoe"
  github: "github.com/janedoe"

skills:
  languages:
    - "Python"
    - "Go"
    - "TypeScript"
    - "SQL"
    - "Bash"
  frameworks:
    - "FastAPI"
    - "Django"
    - "React"
    - "Node.js"
    - "Gin"
  cloud_and_devops:
    - "Docker"
    - "Kubernetes"
    - "Terraform"
    - "AWS (ECS, Lambda, RDS, S3)"
    - "CI/CD (GitHub Actions)"
  data_and_storage:
    - "PostgreSQL"
    - "Redis"
    - "Apache Kafka"
    - "ClickHouse"

experience:
  - company: "CloudScale Technologies"
    role: "Senior Backend Engineer"
    location: "San Francisco, CA"
    start_date: "2022-03"
    end_date: "Present"
    bullets:
      - id: "cs_perf_1"
        text: "Architected real-time ingestion pipeline in Go processing 40,000 events/sec, cutting ingestion latency by 55%."
        tags: ["go", "distributed-systems", "performance", "kafka", "scalability"]
      - id: "cs_cost_2"
        text: "Led database migration from monolithic Postgres to sharded ClickHouse cluster, reducing monthly AWS spend by $18,000."
        tags: ["postgresql", "clickhouse", "aws", "cost-optimization", "database"]
      - id: "cs_infra_3"
        text: "Engineered zero-downtime CI/CD deployment pipelines using GitHub Actions and Kubernetes, decreasing release cycle times from 2 days to 35 minutes."
        tags: ["kubernetes", "ci-cd", "devops", "docker"]
      - id: "cs_mentorship_4"
        text: "Mentored 4 junior and mid-level engineers through bi-weekly architectural reviews and pairing sessions."
        tags: ["leadership", "mentorship"]

  - company: "FinTech Infrastructure Lab"
    role: "Software Engineer"
    location: "New York, NY"
    start_date: "2019-08"
    end_date: "2022-02"
    bullets:
      - id: "ft_ledger_1"
        text: "Designed double-entry financial ledger service in Python/FastAPI handling $15M daily transaction volume with 99.999% consistency."
        tags: ["python", "fastapi", "finance", "postgresql", "acid"]
      - id: "ft_cache_2"
        text: "Implemented multi-tier caching strategy using Redis, reducing p99 API response latency from 240ms to 32ms."
        tags: ["redis", "caching", "performance", "api-design"]
      - id: "ft_security_3"
        text: "Conducted SOC2 Type II security audit compliance remediation across 12 microservices."
        tags: ["security", "soc2", "compliance"]

education:
  - institution: "University of California, Berkeley"
    degree: "B.S. in Computer Science"
    start_date: "2015"
    end_date: "2019"
    gpa: "3.8/4.0"

```

### 4.5. `template.typ` (Typst Layout Engine)

A single-column, high-parseability Typst template designed to import `dist/tailored_cv.yaml` and render without structural artifacts that confuse ATS scanners.

```
#let cv = yaml("dist/tailored_cv.yaml")

#set page(
  paper: "a4",
  margin: (top: 1.5cm, bottom: 1.5cm, left: 1.8cm, right: 1.8cm)
)

#set text(
  font: ("Liberation Sans", "DejaVu Sans", "Arial"),
  size: 9.5pt,
  fill: rgb("#111827")
)

#set par(
  justify: false,
  leading: 0.6em
)

// Header
#align(center)[
  #text(size: 16pt, weight: "bold")[#cv.basics.name] \
  #v(0.3em)
  #text(size: 8.5pt, fill: rgb("#4b5563"))[
    #cv.basics.location | #cv.basics.email | #cv.basics.phone \
    #link("https://" + cv.basics.linkedin)[#cv.basics.linkedin] | #link("https://" + cv.basics.github)[#cv.basics.github]
  ]
]

#v(0.8em)

// Section Macro
#let section-heading(title) = {
  v(0.6em)
  text(size: 11pt, weight: "bold", fill: rgb("#1f2937"))[#upper(title)]
  v(-0.4em)
  line(length: 100%, stroke: 0.5pt + rgb("#d1d5db"))
  v(0.2em)
}

// Technical Skills Section
#section-heading("Technical Skills")
#for (category, items) in cv.skills [
  #box(width: 100%)[
    *#upper(category.slice(0, 1))#category.slice(1).replace("_", " "):* #items.join(", ")
  ]
  #v(0.15em)
]

// Professional Experience Section
#section-heading("Professional Experience")
#for job in cv.experience [
  #grid(
    columns: (1fr, auto),
    [
      *#job.role* \
      #text(fill: rgb("#374151"), style: "italic")[#job.company] -- #text(fill: rgb("#6b7280"))[#job.location]
    ],
    [
      #align(right)[
        #text(fill: rgb("#4b5563"), weight: "medium")[#job.start_date -- #job.end_date]
      ]
    ]
  )
  #v(0.3em)
  #list(..job.selected_bullets)
  #v(0.4em)
]

// Education Section
#if "education" in cv [
  #section-heading("Education")
  #for edu in cv.education [
    #grid(
      columns: (1fr, auto),
      [
        *#edu.institution* \
        #edu.degree #if "gpa" in edu [ (GPA: #edu.gpa) ]
      ],
      [
        #align(right)[
          #text(fill: rgb("#4b5563"))[#edu.start_date -- #edu.end_date]
        ]
      ]
    )
    #v(0.3em)
  ]
]

```

### 4.6. `generate.py` (Automation Orchestrator)

Orchestrates reading inputs, prompting the LLM, extracting clean YAML, and invoking Typst.

````
#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
import yaml
import typst

# Load environment configuration
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MASTER_FILE = BASE_DIR / "master_experience.yaml"
JD_FILE = BASE_DIR / "inputs" / "jd.txt"
TEMPLATE_FILE = BASE_DIR / "template.typ"
DIST_DIR = BASE_DIR / "dist"
OUTPUT_YAML = DIST_DIR / "tailored_cv.yaml"
OUTPUT_PDF = DIST_DIR / "resume.pdf"

PROMPT_TEMPLATE = """
SYSTEM INSTRUCTION:
You are an expert Technical Recruiter and ATS Optimization Engine. Your task is to extract, select, and subtly harmonize experiences from `master_experience` against `target_job_description`.

CORE RULES:
1. STRICT GROUNDING: Never hallucinate, invent, or extrapolate skills, technologies, experiences, roles, or metrics not already substantiated in `master_experience`.
2. SELECTION: For each role, pick the top 3-4 most relevant bullets that demonstrate competence in areas required by the JD. Omit irrelevant bullets.
3. KEYWORD HARMONIZATION: Without altering the underlying truth or metrics, align terminology to match the job description (e.g., if JD specifies "relational databases" and master lists "PostgreSQL", you may specify "PostgreSQL relational databases").
4. SKILL PRIORITIZATION: Sort skill categories and individual skills so that technologies explicitly mentioned in the JD appear first. Drop skills completely irrelevant to the target role if space requires.
5. FORMAT GUARANTEE: Output strictly valid YAML conforming to the specified schema. Output NO markdown prose, explanations, or opening/closing commentary.

<master_experience>
{master_content}
</master_experience>

<target_job_description>
{jd_content}
</target_job_description>

REQUIRED SCHEMA:
```yaml
basics:
  name: "..."
  email: "..."
  phone: "..."
  location: "..."
  linkedin: "..."
  github: "..."
skills:
  languages: [...]
  frameworks: [...]
  cloud_and_devops: [...]
  data_and_storage: [...]
experience:
  - company: "..."
    role: "..."
    location: "..."
    start_date: "..."
    end_date: "..."
    selected_bullets:
      - "Accomplished [X] measured by [Y] by doing [Z]"
education:
  - institution: "..."
    degree: "..."
    start_date: "..."
    end_date: "..."
    gpa: "..."

````

"""

def extract_yaml_payload(raw_text: str) -> str:
"""Extracts raw YAML content from possible Markdown code block wrappers."""
match = re.search(r"`(?:yaml)?\s*(.*?)\s*`", raw_text, re.DOTALL)
if match:
return match.group(1).strip()
return raw_text.strip()

def validate_yaml(yaml_string: str) -> dict:
"""Validates that the output is syntactically correct YAML and contains critical keys."""
data = yaml.safe_load(yaml_string)
if not isinstance(data, dict):
raise ValueError("Root of generated YAML must be a dictionary/mapping.")
required_keys = \["basics", "skills", "experience"\]
for key in required_keys:
if key not in data:
raise KeyError(f"Missing required top-level key in YAML: '{key}'")
return data

def run_pipeline():
\# Verify environment
if not os.getenv("GEMINI_API_KEY"):
print("\[!\] Error: GEMINI_API_KEY is not set in environment or .env file.", file=sys.stderr)
sys.exit(1)

```
if not MASTER_FILE.exists():
    print(f"[!] Error: Master file not found at {MASTER_FILE}", file=sys.stderr)
    sys.exit(1)

if not JD_FILE.exists() or not JD_FILE.read_text(encoding="utf-8").strip():
    print(f"[!] Error: Job description empty or missing. Populate '{JD_FILE}' before running.", file=sys.stderr)
    sys.exit(1)

# Initialize output directory
DIST_DIR.mkdir(parents=True, exist_ok=True)

print("[*] Reading inputs...")
master_content = MASTER_FILE.read_text(encoding="utf-8")
jd_content = JD_FILE.read_text(encoding="utf-8")

print("[*] Requesting tailored alignment from LLM...")
from google import genai
client = genai.Client()

prompt = PROMPT_TEMPLATE.format(
    master_content=master_content,
    jd_content=jd_content
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print("[*] Validating structured output...")
clean_yaml = extract_yaml_payload(response.text)

try:
    validate_yaml(clean_yaml)
except Exception as e:
    print(f"[!] YAML validation failed: {e}", file=sys.stderr)
    print("Raw payload:\n", clean_yaml, file=sys.stderr)
    sys.exit(1)

OUTPUT_YAML.write_text(clean_yaml, encoding="utf-8")
print(f"    -> Intermediate data saved: {OUTPUT_YAML}")

print("[*] Compiling PDF with Typst...")
try:
    typst.compile(str(TEMPLATE_FILE), output=str(OUTPUT_PDF))
    print(f"[✓] Complete! Generated ATS Resume: {OUTPUT_PDF}")
except Exception as e:
    print(f"[!] Typst compilation failed: {e}", file=sys.stderr)
    sys.exit(1)

```

if **name** == "**main**":
run_pipeline()

````

---

## 5. Agent Instructions for Automated Setup

When commanding an AI Agent (e.g., Cursor, Claude Code, Cline) to initialize this repository, supply the following execution prompt:

```text
Follow the instructions in SETUP_GUIDE.md to initialize the project:
1. Create the project root directory and all required folders: `inputs/` and `dist/`.
2. Write `.gitignore`, `requirements.txt`, and `.env.example`.
3. Create `master_experience.yaml` using the schema defined in Section 4.4.
4. Create `template.typ` using the code in Section 4.5.
5. Create `generate.py` using the script in Section 4.6. Ensure the file has executable permissions (`chmod +x generate.py`).
6. Create an empty placeholder file `inputs/jd.txt`.
7. Initialize a Python virtual environment at `.venv`, activate it, and install `requirements.txt`.
8. Verify that `python -c "import typst; import yaml; import google.genai; print('Dependencies OK')"` runs cleanly.

````

## 6. Verification and ATS Parse Testing

To confirm that the output PDF is parseable by Applicant Tracking Systems without layout degradation or text fragmentation:

### 6.1. Raw Text Stream Verification

Run `pdftotext` (via Poppler) or a lightweight Python verification snippet:

```
python -c "
from pypdf import PdfReader
reader = PdfReader('dist/resume.pdf')
for page in reader.pages:
    print(page.extract_text())
"

```

### 6.2. Inspection Checklist

* \[ \] Text extracts top-to-bottom in natural reading order.

* \[ \] Job titles, employers, and dates remain on the same lines or logical blocks.

* \[ \] Bullet points are separated by clear linebreaks and are not glued together.

* \[ \] No ligature or font encoding corruptions (e.g., "fi", "fl" rendering as non-standard glyphs).

* \[ \] PDF size remains under 200 KB for optimal submission speed.