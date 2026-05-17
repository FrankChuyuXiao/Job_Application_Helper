from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from job_helper.ai_client import analyze_job_with_openai
from job_helper.config import load_settings
from job_helper.database import (
    init_db,
    save_analysis,
    list_jobs,
    get_job,
    update_status,
    export_csv,
)

console = Console()

def cmd_add(args) -> None:
    settings = load_settings()
    init_db(settings.database_path)

    company = input("Company: ").strip()
    title = input("Job Title: ").strip()
    url = input("Job URL (optional): ").strip() or None

    print("\nPaste job description below. When finished, press Ctrl+Z then Enter on Windows.\n")

    import sys
    job_description = sys.stdin.read().strip()

    if not company or not title or not job_description:
        console.print("[red]Company, title, and job description are required.[/red]")
        return

    full_description = f"""
Company: {company}
Job Title: {title}

Job Description:
{job_description}
"""

    analysis = analyze_job_with_openai(full_description, settings)
    job_id = save_analysis(settings.database_path, analysis, job_url=url)

    console.print(Panel.fit(
        f"[bold]{analysis.company} — {analysis.title}[/bold]\n"
        f"Technical Fit: [bold]{analysis.technical_fit_score}/100[/bold]\n"
        f"Hiring Competitiveness: [bold]{analysis.hiring_competitiveness_score}/100[/bold]\n"
        f"Apply Priority: [bold]{analysis.apply_priority}[/bold]\n"
        f"Sponsorship Risk: [bold]{analysis.sponsorship_risk}[/bold]\n"
        f"Saved Job ID: [bold]{job_id}[/bold]",
        title="Saved Job Analysis"
    ))

def cmd_init_db(args) -> None:
    settings = load_settings()
    init_db(settings.database_path)
    console.print(f"[green]Database initialized:[/green] {settings.database_path}")


def cmd_analyze(args) -> None:
    settings = load_settings()
    init_db(settings.database_path)

    job_path = Path(args.job_file)
    if not job_path.exists():
        raise FileNotFoundError(f"Job description file not found: {job_path}")

    job_description = job_path.read_text(encoding="utf-8")
    analysis = analyze_job_with_openai(job_description, settings)
    job_id = save_analysis(settings.database_path, analysis, job_url=args.url)

    console.print(Panel.fit(
        f"[bold]{analysis.company} — {analysis.title}[/bold]\n"
        f"Technical Fit: [bold]{analysis.technical_fit_score}/100[/bold]\n"
        f"Hiring Competitiveness: [bold]{analysis.hiring_competitiveness_score}/100[/bold]\n"
        f"Apply Priority: [bold]{analysis.apply_priority}[/bold]\n"
        f"Sponsorship Risk: [bold]{analysis.sponsorship_risk}[/bold]\n"
        f"Saved Job ID: [bold]{job_id}[/bold]",
        title="Job Fit Analysis"
    ))

    console.print("\n[bold]Best Fit Reasons[/bold]")
    for item in analysis.best_fit_reasons:
        console.print(f"  • {item}")

    console.print("\n[bold]Major Gaps[/bold]")
    for item in analysis.major_gaps:
        console.print(f"  • {item}")

    console.print("\n[bold]Recommended Resume Keywords[/bold]")
    console.print(", ".join(analysis.recommended_resume_keywords))

    console.print("\n[bold]Next Action[/bold]")
    console.print(analysis.next_action)


def cmd_list(args) -> None:
    settings = load_settings()
    init_db(settings.database_path)

    jobs = list_jobs(settings.database_path, limit=args.limit)

    table = Table(title="Tracked Jobs")
    table.add_column("ID", justify="right")
    table.add_column("Company")
    table.add_column("Title")
    table.add_column("Fit")
    table.add_column("Comp")
    table.add_column("Priority")
    table.add_column("Risk")
    table.add_column("Status")

    for job in jobs:
        table.add_row(
            str(job["id"]),
            job["company"],
            job["title"],
            str(job["technical_fit_score"]),
            str(job["hiring_competitiveness_score"]),
            job["apply_priority"],
            job["sponsorship_risk"],
            job["status"],
        )

    console.print(table)


def cmd_show(args) -> None:
    settings = load_settings()
    job = get_job(settings.database_path, args.job_id)
    if not job:
        console.print(f"[red]No job found with ID {args.job_id}[/red]")
        return

    analysis = json.loads(job["analysis_json"])
    console.print_json(json.dumps(analysis, indent=2))


def cmd_update_status(args) -> None:
    settings = load_settings()
    update_status(settings.database_path, args.job_id, args.status)
    console.print(f"[green]Updated job {args.job_id} status to:[/green] {args.status}")


def cmd_export(args) -> None:
    settings = load_settings()
    export_csv(settings.database_path, args.csv_file)
    console.print(f"[green]Exported jobs to:[/green] {args.csv_file}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Job Application Helper",
        description="AI-powered job fit analyzer and application tracker."
    )
    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser("init-db", help="Initialize the SQLite database.")
    p.set_defaults(func=cmd_init_db)

    p = subparsers.add_parser("analyze", help="Analyze a job description text file.")
    p.add_argument("job_file", help="Path to a text file containing the job description.")
    p.add_argument("--url", default=None, help="Optional job posting URL.")
    p.set_defaults(func=cmd_analyze)

    p = subparsers.add_parser("list", help="List tracked jobs.")
    p.add_argument("--limit", type=int, default=30)
    p.set_defaults(func=cmd_list)

    p = subparsers.add_parser("show", help="Show full JSON analysis for a job.")
    p.add_argument("job_id", type=int)
    p.set_defaults(func=cmd_show)

    p = subparsers.add_parser("update-status", help="Update application status.")
    p.add_argument("job_id", type=int)
    p.add_argument("status", help="New status, e.g. Applied, Interview, Rejected.")
    p.set_defaults(func=cmd_update_status)

    p = subparsers.add_parser("export", help="Export job tracker to CSV.")
    p.add_argument("csv_file", help="Output CSV path.")
    p.set_defaults(func=cmd_export)

    p = subparsers.add_parser("add", help="Manually input and analyze a job.")
    p.set_defaults(func=cmd_add)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
