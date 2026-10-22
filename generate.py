#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
import yaml
import typst
import shutil
import time

# Ensure UTF-8 output in Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Load environment configuration
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MASTER_FILE = BASE_DIR / "master_experience.yaml"
JD_FILE = BASE_DIR / "inputs" / "jd.txt"
TEMPLATE_FILE = BASE_DIR / "template.typ"
COVER_LETTER_TEMPLATE_FILE = BASE_DIR / "cover_letter.typ"
DIST_DIR = BASE_DIR / "dist"
OUTPUT_YAML = DIST_DIR / "tailored_cv.yaml"
OUTPUT_PDF = DIST_DIR / "resume.pdf"
OUTPUT_CHANGES = DIST_DIR / "changes.md"

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
meta:
  company: "Target company name (e.g. AI SaaS, or extracted from JD)"
  role: "Target role title (e.g. FDE or Forward Deployed Engineer)"
basics:
  name: "..."
  email: "..."
  phone: "..."
  location: "..."
  linkedin: "..."
  github: "..."
  website: "..."
skills:
  languages: [...]
  architecture_and_concepts: [...]
  cloud_devops_and_infra: [...]
  databases_and_messaging: [...]
  frameworks_and_libraries: [...]
experience:
  - company: "..."
    role: "..."
    location: "..."
    start_date: "..."
    end_date: "..."
    selected_bullets:
      - "Accomplished [X] measured by [Y] by doing [Z]"
projects:
  - name: "..."
    role: "..."
    url: "..."
    selected_bullets:
      - "..."
education:
  - institution: "..."
    location: "..."
    degree: "..."
    start_date: "..."
    end_date: "..."
```
"""


def extract_yaml_payload(raw_text: str) -> str:
    """Extracts raw YAML content from possible Markdown code block wrappers."""
    match = re.search(r"```(?:yaml)?\s*(.*?)\s*```", raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()


def validate_yaml(yaml_string: str) -> dict:
    """Validates that the output is syntactically correct YAML and contains critical keys."""
    data = yaml.safe_load(yaml_string)
    if not isinstance(data, dict):
        raise ValueError("Root of generated YAML must be a dictionary/mapping.")
    required_keys = ["basics", "skills", "experience"]
    for key in required_keys:
        if key not in data:
            raise KeyError(f"Missing required top-level key in YAML: '{key}'")
    return data


def generate_change_report(client, candidate_models, master_content: str, jd_content: str, tailored_content: str) -> str:
    prompt = f"""
SYSTEM INSTRUCTION:
You are an expert Technical Recruiter and Career Coach. 
Analyze the changes made between `master_experience` and `tailored_cv` to align with `target_job_description`.

Produce a concise, well-structured Markdown report explaining:
1. **Executive Summary**: Core strategy and focus areas for this tailoring.
2. **Key Skill Prioritizations**: Which skills were promoted or emphasized and why.
3. **Experience & Bullet Harmonizations**: Specific phrasing alignments and dropped bullets per company with rationales.
4. **ATS Alignment Table**: How the tailored CV directly satisfies key qualifications from the job description.

<target_job_description>
{jd_content}
</target_job_description>

<master_experience>
{master_content}
</master_experience>

<tailored_cv>
{tailored_content}
</tailored_cv>
"""
def call_gemini_with_fallback(client, candidate_models, prompt, task_desc="content"):
    for attempt in range(2):
        for model_name in candidate_models:
            try:
                print(f"[*] Calling Gemini ({model_name}) for {task_desc}...")
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if res and res.text:
                    print(f"[+] Received response using {model_name}")
                    return res
            except Exception as e:
                print(f"[!] Warning: {model_name} failed ({e}). Trying next...", file=sys.stderr)
        if attempt == 0:
            print("[*] Temporary API capacity busy, waiting 2 seconds before retry...", file=sys.stderr)
            time.sleep(2)
    return None


def generate_change_report(client, candidate_models, master_content: str, jd_content: str, tailored_content: str) -> str:
    prompt = f"""
SYSTEM INSTRUCTION:
You are an expert Technical Recruiter and Career Coach. 
Analyze the changes made between `master_experience` and `tailored_cv` to align with `target_job_description`.

Produce a concise, well-structured Markdown report explaining:
1. **Executive Summary**: Core strategy and focus areas for this tailoring.
2. **Key Skill Prioritizations**: Which skills were promoted or emphasized and why.
3. **Experience & Bullet Harmonizations**: Specific phrasing alignments and dropped bullets per company with rationales.
4. **ATS Alignment Table**: How the tailored CV directly satisfies key qualifications from the job description.

<target_job_description>
{jd_content}
</target_job_description>

<master_experience>
{master_content}
</master_experience>

<tailored_cv>
{tailored_content}
</tailored_cv>
"""
    res = call_gemini_with_fallback(client, candidate_models, prompt, task_desc="change report")
    if res and res.text:
        return res.text.strip()
    return "# ATS Tailoring Report\n\nTailoring completed successfully."


def generate_cover_letter(client, candidate_models, master_content: str, jd_content: str, tailored_content: str, meta: dict) -> str:
    company = meta.get("company", "the Hiring Team")
    role = meta.get("role", "Software Engineer")
    prompt = f"""
SYSTEM INSTRUCTION:
You are an expert Executive Career Coach and Technical Recruiter.
Write a concise, compelling, and professional short cover letter (3 short paragraphs, under 250 words) tailored specifically to the `target_job_description` at {company} for the {role} position.
Use facts strictly grounded in `master_experience` and `tailored_cv`.

GUIDELINES:
1. TONE: Confident, engaging, authentic, and direct. Avoid cliché openings like "I am writing to express my enthusiastic interest in...".
2. HOOK: Open by connecting the candidate's core background (e.g., 5+ years building distributed backend services and full-stack platforms across Grab and Tokopedia) to {company}'s specific product, mission, and tech stack in the JD.
3. VALUE & EVIDENCE: Spotlight 2 concrete achievements from past roles that map directly to the technical challenges and stack in the JD (e.g. APIs, databases, scaling, product collaboration).
4. CLOSING: Brief, high-confidence closing looking forward to discussing the role.
5. FORMAT: Standard clean Markdown with a salutation ("Dear {company} Hiring Team,"), 3 focused paragraphs, and sign-off ("Best regards,", name). Do NOT include placeholders like [Your Phone Number] if empty; use only actual data from basics.

<target_job_description>
{jd_content}
</target_job_description>

<master_experience>
{master_content}
</master_experience>

<tailored_cv>
{tailored_content}
</tailored_cv>
"""
    res = call_gemini_with_fallback(client, candidate_models, prompt, task_desc="cover letter")
    if res and res.text:
        return res.text.strip()
    return f"Dear {company} Hiring Team,\n\nI am excited to apply for the {role} position.\n\nBest regards,\nAldo Rizkiawan"


def run_pipeline():
    # Verify environment
    if not os.getenv("GEMINI_API_KEY"):
        print("[!] Error: GEMINI_API_KEY is not set in environment or .env file.", file=sys.stderr)
        sys.exit(1)

    if not MASTER_FILE.exists():
        print(f"[!] Error: Master file not found at {MASTER_FILE}", file=sys.stderr)
        print("    -> Copy 'master_experience.example.yaml' to 'master_experience.yaml' and add your career history.", file=sys.stderr)
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

    preferred_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    candidate_models = [preferred_model]
    for fallback in ["gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-pro-preview"]:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    response = call_gemini_with_fallback(client, candidate_models, prompt, task_desc="tailored CV")

    if response is None or not response.text:
        print("[!] Error: All candidate models failed to generate content.", file=sys.stderr)
        sys.exit(1)

    print("[*] Validating structured output...")
    clean_yaml = extract_yaml_payload(response.text)

    try:
        validated_data = validate_yaml(clean_yaml)
    except Exception as e:
        print(f"[!] YAML validation failed: {e}", file=sys.stderr)
        print("Raw payload:\n", clean_yaml, file=sys.stderr)
        sys.exit(1)

    # Determine job-specific folder name from company and role
    meta = validated_data.get("meta", {})
    company = meta.get("company", "Company")
    role = meta.get("role", "Role")
    clean_company = re.sub(r"[^\w\-]+", "_", company).strip("_")
    clean_role = re.sub(r"[^\w\-]+", "_", role).strip("_")
    folder_name = f"{clean_company}_{clean_role}".strip("_")
    if not folder_name:
        folder_name = "tailored_job"

    job_dir = DIST_DIR / folder_name
    job_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ensure .gitkeep exists inside the job folder
    (job_dir / ".gitkeep").touch(exist_ok=True)

    # 2. Save tailored_cv.yaml
    job_yaml = job_dir / "tailored_cv.yaml"
    job_yaml.write_text(clean_yaml, encoding="utf-8")
    print(f"    -> Saved YAML: {job_yaml}")

    # 3. Generate and save changes.md
    print("[*] Generating tailoring changes explanation...")
    report_md = generate_change_report(client, candidate_models, master_content, jd_content, clean_yaml)
    job_changes = job_dir / "changes.md"
    job_changes.write_text(report_md, encoding="utf-8")
    print(f"    -> Saved Change Report: {job_changes}")

    # 4. Generate and save short cover letter
    print("[*] Generating tailored short cover letter...")
    cover_letter_md = generate_cover_letter(client, candidate_models, master_content, jd_content, clean_yaml, meta)
    job_cover_letter = job_dir / "cover_letter.md"
    job_cover_letter.write_text(cover_letter_md, encoding="utf-8")
    print(f"    -> Saved Cover Letter: {job_cover_letter}")

    # 5. Compile PDF named "{Candidate Name} resume.pdf"
    candidate_name = validated_data.get("basics", {}).get("name", "Aldo Rizkiawan")
    pdf_filename = f"{candidate_name} resume.pdf"
    job_pdf = job_dir / pdf_filename

    print("[*] Compiling PDF with Typst...")
    rel_yaml_path = job_yaml.relative_to(BASE_DIR).as_posix()
    try:
        typst.compile(
            str(TEMPLATE_FILE),
            output=str(job_pdf),
            sys_inputs={"cv_path": rel_yaml_path}
        )
        print(f"[+] Complete! Generated ATS Resume: {job_pdf}")
    except Exception as e:
        print(f"[!] Typst compilation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 6. Compile Cover Letter PDF if template exists
    if COVER_LETTER_TEMPLATE_FILE.exists():
        cl_pdf_filename = f"{candidate_name} cover letter.pdf"
        job_cl_pdf = job_dir / cl_pdf_filename
        rel_letter_path = job_cover_letter.relative_to(BASE_DIR).as_posix()
        try:
            typst.compile(
                str(COVER_LETTER_TEMPLATE_FILE),
                output=str(job_cl_pdf),
                sys_inputs={
                    "cv_path": rel_yaml_path,
                    "letter_path": rel_letter_path
                }
            )
            print(f"[+] Complete! Generated Cover Letter PDF: {job_cl_pdf}")
        except Exception as e:
            print(f"[!] Warning: Cover letter PDF compilation failed: {e}", file=sys.stderr)

    # Maintain root dist/ copies for quick access
    OUTPUT_YAML.write_text(clean_yaml, encoding="utf-8")
    OUTPUT_CHANGES.write_text(report_md, encoding="utf-8")
    try:
        shutil.copyfile(job_pdf, OUTPUT_PDF)
    except Exception:
        pass


if __name__ == "__main__":
    run_pipeline()
