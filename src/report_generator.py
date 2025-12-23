"""
report_generator.py - Markdown Report Generator

Generates a comprehensive markdown report presenting internship opportunities
in Product Manager and Technical Sales roles with statistics and insights.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path


def generate_summary_stats(conn) -> dict:
    """
    Generate summary statistics from the database.

    Args:
        conn: Database connection

    Returns:
        Dictionary with summary statistics
    """
    stats = {}

    # Total jobs
    total = pd.read_sql_query("SELECT COUNT(*) as count FROM jobs", conn)
    stats['total_jobs'] = int(total['count'].iloc[0])

    # Internships count
    internships = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM jobs WHERE is_internship = 1", conn
    )
    stats['internship_count'] = int(internships['count'].iloc[0])

    # Remote jobs
    remote = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM jobs WHERE is_remote = 1", conn
    )
    stats['remote_count'] = int(remote['count'].iloc[0])

    # Unique companies
    companies = pd.read_sql_query(
        "SELECT COUNT(DISTINCT company) as count FROM jobs", conn
    )
    stats['unique_companies'] = int(companies['count'].iloc[0])

    # Unique countries
    countries = pd.read_sql_query(
        "SELECT COUNT(DISTINCT country) as count FROM jobs", conn
    )
    stats['unique_countries'] = int(countries['count'].iloc[0])

    # Average applicants
    avg_applicants = pd.read_sql_query(
        "SELECT AVG(applicant_count) as avg FROM jobs WHERE applicant_count IS NOT NULL", conn
    )
    stats['avg_applicants'] = round(avg_applicants['avg'].iloc[0] or 0, 1)

    return stats


def get_top_opportunities(conn, limit=20) -> pd.DataFrame:
    """
    Get the top job opportunities sorted by recent posting and lower competition.

    Args:
        conn: Database connection
        limit: Number of jobs to return

    Returns:
        DataFrame with top opportunities
    """
    query = f"""
        SELECT
            title,
            company,
            city,
            country,
            posted_date,
            is_internship,
            is_remote,
            applicant_count,
            url
        FROM jobs
        ORDER BY
            posted_date DESC,
            applicant_count ASC
        LIMIT {limit}
    """
    return pd.read_sql_query(query, conn)


def get_internships_only(conn) -> pd.DataFrame:
    """
    Get only internship positions.

    Args:
        conn: Database connection

    Returns:
        DataFrame with internship positions
    """
    query = """
        SELECT
            title,
            company,
            city,
            country,
            posted_date,
            is_remote,
            applicant_count,
            url
        FROM jobs
        WHERE is_internship = 1
        ORDER BY posted_date DESC
    """
    return pd.read_sql_query(query, conn)


def get_low_competition_jobs(conn, max_applicants=50) -> pd.DataFrame:
    """
    Get jobs with low applicant count (hidden gems).

    Args:
        conn: Database connection
        max_applicants: Maximum number of applicants

    Returns:
        DataFrame with low competition jobs
    """
    query = f"""
        SELECT
            title,
            company,
            city,
            country,
            posted_date,
            is_internship,
            is_remote,
            applicant_count,
            url
        FROM jobs
        WHERE applicant_count IS NOT NULL
          AND applicant_count <= {max_applicants}
        ORDER BY applicant_count ASC, posted_date DESC
        LIMIT 15
    """
    return pd.read_sql_query(query, conn)


def get_jobs_by_country_breakdown(conn) -> pd.DataFrame:
    """Get job count breakdown by country."""
    query = """
        SELECT
            country,
            COUNT(*) as job_count,
            SUM(CASE WHEN is_internship = 1 THEN 1 ELSE 0 END) as internships,
            SUM(CASE WHEN is_remote = 1 THEN 1 ELSE 0 END) as remote_jobs
        FROM jobs
        GROUP BY country
        ORDER BY job_count DESC
    """
    return pd.read_sql_query(query, conn)


def get_top_companies_breakdown(conn, limit=10) -> pd.DataFrame:
    """Get top hiring companies with details."""
    query = f"""
        SELECT
            company,
            COUNT(*) as job_count,
            GROUP_CONCAT(DISTINCT city) as locations
        FROM jobs
        GROUP BY company
        ORDER BY job_count DESC
        LIMIT {limit}
    """
    return pd.read_sql_query(query, conn)


def format_job_table(df: pd.DataFrame, include_url=True) -> str:
    """
    Format a DataFrame as a markdown table.

    Args:
        df: DataFrame with job data
        include_url: Whether to include clickable links

    Returns:
        Markdown table string
    """
    if df.empty:
        return "*No jobs found matching criteria*\n"

    lines = []

    # Header
    headers = ["Title", "Company", "Location", "Posted", "Applicants", "Remote"]
    if include_url:
        headers.append("Link")

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")

    # Rows
    for _, row in df.iterrows():
        location = f"{row.get('city', 'N/A')}, {row.get('country', 'N/A')}"

        # Format posted date
        posted = row.get('posted_date', '')
        if pd.notna(posted):
            try:
                posted = pd.to_datetime(posted).strftime('%Y-%m-%d')
            except:
                posted = str(posted)[:10]
        else:
            posted = "N/A"

        # Format applicants
        applicants = row.get('applicant_count', '')
        if pd.isna(applicants) or applicants == '' or applicants is None:
            applicants = "N/A"
        elif isinstance(applicants, (int, float)):
            applicants = str(int(applicants))
        else:
            # Handle strings like "over 100 applicants"
            applicants = str(applicants)

        # Remote badge
        is_remote = row.get('is_remote', False)
        remote = "Yes" if is_remote else "No"

        cells = [
            str(row.get('title', 'N/A'))[:50],
            str(row.get('company', 'N/A'))[:25],
            location[:30],
            posted,
            applicants,
            remote
        ]

        if include_url:
            url = row.get('url', '')
            if url:
                cells.append(f"[Apply]({url})")
            else:
                cells.append("N/A")

        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines) + "\n"


def generate_markdown_report(conn, output_path="outputs/INTERNSHIP_OPPORTUNITIES.md") -> str:
    """
    Generate a comprehensive markdown report with internship opportunities.

    Args:
        conn: Database connection
        output_path: Path to save the markdown file

    Returns:
        Path to the generated markdown file
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Gather all data
    stats = generate_summary_stats(conn)
    top_jobs = get_top_opportunities(conn, limit=20)
    internships = get_internships_only(conn)
    low_competition = get_low_competition_jobs(conn, max_applicants=50)
    country_breakdown = get_jobs_by_country_breakdown(conn)
    top_companies = get_top_companies_breakdown(conn, limit=10)

    # Build the report
    report = []

    # Header
    report.append("# Product Manager & Technical Sales Internship Opportunities")
    report.append("")
    report.append(f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    report.append("This report presents current internship and entry-level opportunities in Product Management and Technical Sales roles across Europe.")
    report.append("")

    # Quick Stats
    report.append("---")
    report.append("")
    report.append("## Quick Statistics")
    report.append("")
    report.append(f"| Metric | Count |")
    report.append("|--------|-------|")
    report.append(f"| **Total Positions** | {stats['total_jobs']} |")
    report.append(f"| **Internships** | {stats['internship_count']} |")
    report.append(f"| **Remote-Friendly** | {stats['remote_count']} |")
    report.append(f"| **Companies Hiring** | {stats['unique_companies']} |")
    report.append(f"| **Countries** | {stats['unique_countries']} |")
    report.append(f"| **Avg. Applicants** | {stats['avg_applicants']} |")
    report.append("")

    # Country breakdown
    report.append("---")
    report.append("")
    report.append("## Opportunities by Country")
    report.append("")
    if not country_breakdown.empty:
        report.append("| Country | Total Jobs | Internships | Remote |")
        report.append("|---------|------------|-------------|--------|")
        for _, row in country_breakdown.iterrows():
            report.append(f"| {row['country']} | {row['job_count']} | {row['internships']} | {row['remote_jobs']} |")
    report.append("")

    # Top Companies
    report.append("---")
    report.append("")
    report.append("## Top Hiring Companies")
    report.append("")
    if not top_companies.empty:
        report.append("| Company | Open Positions | Locations |")
        report.append("|---------|----------------|-----------|")
        for _, row in top_companies.iterrows():
            locations = str(row['locations'])[:40] if row['locations'] else "N/A"
            report.append(f"| **{row['company']}** | {row['job_count']} | {locations} |")
    report.append("")

    # Internships Section
    report.append("---")
    report.append("")
    report.append("## Internship Positions")
    report.append("")
    if internships.empty:
        report.append("*No explicit internship positions found. Check the 'All Recent Opportunities' section below.*")
    else:
        report.append(f"Found **{len(internships)} internship positions**:")
        report.append("")
        report.append(format_job_table(internships))
    report.append("")

    # Low Competition (Hidden Gems)
    report.append("---")
    report.append("")
    report.append("## Hidden Gems (Low Competition)")
    report.append("")
    report.append("These positions have fewer than 50 applicants - great opportunities to stand out!")
    report.append("")
    if low_competition.empty:
        report.append("*No low-competition jobs found at this time.*")
    else:
        report.append(format_job_table(low_competition))
    report.append("")

    # All Recent Opportunities
    report.append("---")
    report.append("")
    report.append("## All Recent Opportunities")
    report.append("")
    report.append("Most recent positions across all categories:")
    report.append("")
    report.append(format_job_table(top_jobs))
    report.append("")

    # Tips Section
    report.append("---")
    report.append("")
    report.append("## Tips for Applicants")
    report.append("")
    report.append("1. **Apply Early**: Positions with fewer applicants have higher response rates")
    report.append("2. **Tailor Your Resume**: Customize for each role, highlighting relevant PM/Sales skills")
    report.append("3. **Prepare for Case Interviews**: Many PM roles include product sense questions")
    report.append("4. **Network on LinkedIn**: Connect with hiring managers at target companies")
    report.append("5. **Show Side Projects**: Demonstrate initiative with personal projects or volunteer PM work")
    report.append("")

    # Footer
    report.append("---")
    report.append("")
    report.append("*Generated by PM Job Scraper*")
    report.append("")

    # Write to file
    content = "\n".join(report)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Markdown report saved: {output_path}")

    return output_path


if __name__ == "__main__":
    # Test with existing database
    import sqlite3

    conn = sqlite3.connect("database/jobs.db")
    generate_markdown_report(conn)
    conn.close()
