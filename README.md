# 🎯 ATS Resume & Cover Letter Engine

An automated, intelligent application engine that tailors your resume and generates a custom cover letter for **any job posting in under 30 seconds**.

It uses **Google Gemini AI** to match your actual experience against the job requirements, aligns keywords for **Applicant Tracking Systems (ATS)**, and renders pixel-perfect **1-page PDFs** using **Typst**.

> **No Made-Up Experience (Zero Hallucination)**: The AI is strictly restricted to your real career history in `master_experience.yaml`. It never invents skills, companies, or metrics you didn't provide.

---

## ⚡ How It Works in 3 Simple Steps

```
1. Paste Job Post          2. Run the Engine          3. Get Your Tailored Package
┌──────────────────┐       ┌─────────────────┐       ┌────────────────────────────────┐
│  inputs/jd.txt   │ ───►  │ python          │ ───►  │ dist/Company_Role/             │
│ (Any Job Notice) │       │ generate.py     │       │  ├── Aldo Rizkiawan resume.pdf │
└──────────────────┘       └─────────────────┘       │  ├── Aldo Rizkiawan cover.pdf  │
                                                     │  ├── cover_letter.md           │
                                                     │  ├── changes.md                │
                                                     │  └── tailored_cv.yaml          │
                                                     └────────────────────────────────┘
```

---

## 📦 What's Inside Each Application Folder?

Every time you run the engine, it detects the company and role, creating a dedicated folder inside `dist/` containing:

1. **`Your Name resume.pdf`** – A clean, single-column, 1-page PDF formatted to parse flawlessly through employer ATS scanners.
2. **`Your Name cover letter.pdf`** – A professional PDF cover letter with matching letterhead, colors, and typography.
3. **`cover_letter.md`** – A plain-text Markdown cover letter ready to copy-paste into online job portals (Greenhouse, Lever, LinkedIn, Workday).
4. **`changes.md`** – A transparent report showing which skills were prioritized, why specific bullets were chosen, and how your experience matches the job qualifications.
5. **`tailored_cv.yaml`** – The structured data extracted for this specific role.

---

## 🚀 Beginner Setup Guide (Do This Once)

You do **not** need to be a programmer to set this up. Just follow these steps:

### Step 1: Install Python
1. Download Python for Windows or Mac from [python.org](https://www.python.org/downloads/).
2. ⚠️ **VERY IMPORTANT ON WINDOWS**: When running the installer, make sure to check the box at the bottom that says **"Add Python to PATH"** before clicking Install.

### Step 2: Get a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with any Google account.
3. Click **"Create API key"** and copy the key (it starts with `AIza...`).

### Step 3: Configure Your API Key
1. In the project folder, locate the file named `.env.example`.
2. Make a copy of it and rename the copy to `.env` (just `.env`, with nothing in front of the dot).
3. Open `.env` in any text editor (Notepad, VS Code, etc.) and paste your key:
   ```env
   GEMINI_API_KEY="AIzaSyYourActualKeyHere..."
   ```
4. Save and close the file.

### Step 4: Configure Your Career History (Keep Your Real Data Private!)
Just like `.env`, this project uses a template file so your actual resume data stays private on your local machine:
1. Locate the file named `master_experience.example.yaml`.
2. Make a copy of it and rename the copy to `master_experience.yaml`.
3. Open `master_experience.yaml` and fill in your real contact info, skills, and work history.
4. `master_experience.yaml` is automatically ignored by Git, so your private career data will **never be pushed to GitHub**.

### Step 5: Install the Required Tools
Open your terminal (PowerShell on Windows, or Terminal on macOS/Linux) inside the project folder, and run:

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*(This takes about 30 seconds to download the tools. You only need to do this once!)*

---

## 🎯 How to Use It Daily (Takes 30 Seconds)

Whenever you find a job you want to apply to:

### 1. Copy the Job Description
Open `inputs/jd.txt`, select all (`Ctrl+A`), delete the old content, and paste the job description from LinkedIn, Indeed, or the company website. Save the file.

### 2. Run the Generator
In your terminal, run:

**On Windows:**
```powershell
.\.venv\Scripts\python .\generate.py
```

**On macOS / Linux:**
```bash
source .venv/bin/activate
python generate.py
```

### 3. Grab Your Files
Open the `dist/` folder. You will see a new folder named after the company and role (e.g., `dist/Anyday_Senior_Backend_Engineer/`). Inside are your ready-to-submit PDFs and cover letter text!

---

## 📝 How to Update Your Experience (`master_experience.yaml`)

`master_experience.yaml` is your **Single Source of Truth (SSOT)**. It holds your complete career history. You never need to delete anything from this file—the AI automatically picks the top 3–4 most relevant bullets for each job.

### 1. Contact Information (`basics`)
Open `master_experience.yaml` and update your details:
```yaml
basics:
  name: "Your Name"
  email: "your.email@example.com"
  phone: "+1 234 567 890"        # Optional, leave "" if you don't want it shown
  location: "City, Country"
  linkedin: "linkedin.com/in/yourprofile"
  github: "github.com/yourhandle"
  website: "yourwebsite.com"
```

### 2. Adding a New Skill
Add any skills to the appropriate category under `skills:`:
```yaml
skills:
  languages:
    - "Python"
    - "TypeScript"
    - "Go"
```

### 3. Adding a New Job or Achievement
Add a new job entry under `experience:`:
```yaml
experience:
  - company: "Company Name"
    role: "Job Title"
    location: "City, Country"
    start_date: "Jan 2024"
    end_date: "Present"
    bullets:
      - id: "unique_id_1"
        text: "What you achieved, measured with metrics (e.g. reduced latency by 40%)."
        tags: ["backend", "performance", "python"]
```

---

## 💡 Pro Tips

* **Always 1 Page**: The layout template is optimized so your resume fits neatly on a single page, adhering to international recruiting standards.
* **Smart Failover**: If Google's API experiences high traffic, the engine automatically tries alternative Flash models (`gemini-3.5-flash`, `gemini-3.1-flash-lite`, etc.) without crashing.
* **Privacy First**: Your personal `.env` file and virtual environment are strictly ignored by `.gitignore`. Nothing secret is ever pushed to GitHub.

---

## 🛠️ Frequently Asked Questions (FAQ)

<details>
<summary><b>Can I change the resume theme color or font?</b></summary>
<br>
Yes! Open <code>template.typ</code>. At the top you can customize:
<ul>
  <li><code>accent-color: "#26428b"</code> (Change to any HEX color, e.g. <code>#0f766e</code> for teal or <code>#1e3a8a</code> for navy).</li>
  <li><code>font: "Liberation Sans"</code> (Change to Arial, Roboto, Inter, etc.).</li>
</ul>
</details>

<details>
<summary><b>What if the job description doesn't mention the company name?</b></summary>
<br>
The AI will intelligently name the folder based on the industry or role (e.g. <code>AI_SaaS_Software_Engineer</code>), ensuring your files are always organized.
</details>

<details>
<summary><b>Do I need to pay for Gemini API?</b></summary>
<br>
No, Google AI Studio provides a generous free tier for personal use that allows multiple resume tailoring runs per day at no cost.
</details>

---

## 📜 License
MIT License. Built for job seekers who want to spend less time formatting documents and more time preparing for interviews.
