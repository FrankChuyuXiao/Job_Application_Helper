# Job Application Helper

A Python-based AI job tracking assistant for Chuyu Xiao.

This project helps you:
- paste a job description
- extract company, role, requirements, and risks
- score technical fit and hiring competitiveness
- detect sponsorship / work authorization risk
- recommend whether to apply
- save jobs into a local SQLite tracker
- export tracked jobs to CSV

## Setup

### 1. Create virtual environment

```bash
cd "Job Application Helper"
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add API key

Copy `.env.example` to `.env`, then edit it:

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.2
```

### 4. Initialize database

```bash
python main.py init-db
```

### 5. Analyze a job description

```bash
python main.py analyze samples/job_description_example.txt
```

Optional with URL:

```bash
python main.py analyze samples/job_description_example.txt --url "https://example.com/job"
```

### 6. List saved jobs

```bash
python main.py list
```

### 7. Update application status

```bash
python main.py update-status 1 Applied
```

### 8. Export tracked jobs

```bash
python main.py export jobs.csv
```

## Project Structure

```text
Job Application Helper/
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
├── samples/
│   └── job_description_example.txt
└── job_helper/
    ├── __init__.py
    ├── ai_client.py
    ├── config.py
    ├── database.py
    ├── profile.py
    ├── prompts.py
    └── schemas.py
```

## Notes

This MVP uses OpenAI structured JSON output so every job receives a consistent scoring format.

The scoring is an estimate. It does not guarantee interviews, recruiter review, or ATS passage.
