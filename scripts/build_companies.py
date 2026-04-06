# scripts/build_companies.py
# Company pages generator: /companies/ index + /companies/{slug}/ detail pages.
# Reads jobs.json data and generates pages for companies with 2+ listings.

import os
import sys
import json
import re
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav_config import *
from templates import (get_page_wrapper, write_page, get_breadcrumb_schema,
                       breadcrumb_html, newsletter_cta_html)

ROLE_NAME = "Sales Enablement"
CURRENT_YEAR = 2026


def slugify(text):
    """Convert text to URL slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def fmt_salary_range(job):
    """Format salary range from job data, or return empty string."""
    min_amt = job.get("min_amount")
    max_amt = job.get("max_amount")
    if min_amt and max_amt and min_amt > 0 and max_amt > 0:
        return f"${min_amt // 1000}K - ${max_amt // 1000}K"
    elif min_amt and min_amt > 0:
        return f"${min_amt // 1000}K+"
    elif max_amt and max_amt > 0:
        return f"Up to ${max_amt // 1000}K"
    return ""


def load_jobs(project_dir):
    """Load jobs.json and return list of job dicts."""
    path = os.path.join(project_dir, "data", "jobs.json")
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("jobs", [])


def get_company_data(jobs):
    """Group jobs by company. Returns dict of company_name -> list of jobs."""
    companies = defaultdict(list)
    for job in jobs:
        company = (job.get("company") or "").strip()
        if company:
            companies[company].append(job)
    return companies


def get_company_locations(jobs):
    """Extract unique locations from a company's jobs."""
    locations = set()
    for job in jobs:
        loc = (job.get("location") or "").strip()
        if loc:
            locations.add(loc)
    return sorted(locations)


def build_company_page(company_name, jobs, all_companies):
    """Generate a single company detail page."""
    slug = slugify(company_name)
    canonical = f"/companies/{slug}/"
    n_jobs = len(jobs)
    locations = get_company_locations(jobs)
    location_str = ", ".join(locations[:5])
    if len(locations) > 5:
        location_str += f" and {len(locations) - 5} more"

    title = f"{company_name} {ROLE_NAME} Jobs"
    meta_title = f"{company_name} {ROLE_NAME} Jobs & Salary ({CURRENT_YEAR})"
    description = (
        f"{company_name} has {n_jobs} open {ROLE_NAME.lower()} "
        f"{'position' if n_jobs == 1 else 'positions'}. "
        f"View salary ranges, locations, and seniority levels."
    )

    crumbs = [("Home", "/"), ("Companies", "/companies/"), (company_name, None)]

    # Job listings table
    rows = ""
    for job in sorted(jobs, key=lambda j: j.get("title", "")):
        job_title = job.get("title", "Untitled")
        job_loc = job.get("location", "Not specified")
        salary = fmt_salary_range(job)
        seniority = job.get("seniority", "")
        source_url = job.get("source_url", "")

        title_cell = f'<a href="{source_url}" target="_blank" rel="noopener">{job_title}</a>' if source_url else job_title
        rows += f"""<tr>
    <td>{title_cell}</td>
    <td>{job_loc}</td>
    <td>{salary if salary else '<span class="text-muted">Not disclosed</span>'}</td>
    <td>{seniority if seniority else '<span class="text-muted">--</span>'}</td>
</tr>
"""

    # Related companies (3-5 others with most jobs)
    related_html = ""
    related = []
    for c_name, c_jobs in sorted(all_companies.items(), key=lambda x: -len(x[1])):
        if c_name != company_name and len(c_jobs) >= 2:
            related.append((c_name, len(c_jobs)))
        if len(related) >= 5:
            break

    if related:
        related_items = ""
        for r_name, r_count in related:
            r_slug = slugify(r_name)
            related_items += f'<li><a href="/companies/{r_slug}/">{r_name}</a> ({r_count} jobs)</li>\n'
        related_html = f"""<section class="related-companies" style="margin-top: 2rem;">
    <h2>Other Companies Hiring {ROLE_NAME} Professionals</h2>
    <ul class="company-related-list">
        {related_items}
    </ul>
</section>
"""

    body = f"""<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>{company_name} | {ROLE_NAME} Jobs</h1>
        <p class="page-subtitle">{location_str}</p>
    </div>

    <div class="salary-content">
        <section class="company-overview" style="margin-bottom: 2rem;">
            <h2>Company Overview</h2>
            <p>{company_name} is actively hiring {ROLE_NAME.lower()} professionals. Based on our database, they have {n_jobs} open {'position' if n_jobs == 1 else 'positions'}.</p>
        </section>

        <section class="company-jobs">
            <h2>Open Positions ({n_jobs})</h2>
            <div class="table-wrapper" style="overflow-x: auto;">
                <table class="data-table" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Location</th>
                            <th>Salary Range</th>
                            <th>Seniority</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </section>

        {related_html}
    </div>
</div>
"""
    body += newsletter_cta_html(f"Get {ROLE_NAME.lower()} job alerts in your inbox.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(
        title=meta_title, description=description,
        canonical_path=canonical, body_content=body,
        active_path="/companies/", extra_head=extra_head
    )
    write_page(f"companies/{slug}/index.html", page)


def build_companies_index(all_companies):
    """Generate /companies/ index page listing all companies."""
    title = f"Companies Hiring {ROLE_NAME} Professionals ({CURRENT_YEAR})"
    description = (
        f"Browse companies actively hiring {ROLE_NAME.lower()} professionals. "
        f"Sorted by number of open positions with salary data and locations."
    )
    canonical = "/companies/"
    crumbs = [("Home", "/"), ("Companies", None)]

    # Sort by job count descending
    sorted_companies = sorted(all_companies.items(), key=lambda x: -len(x[1]))

    rows = ""
    for company_name, jobs in sorted_companies:
        if len(jobs) < 2:
            continue
        slug = slugify(company_name)
        n_jobs = len(jobs)
        locations = get_company_locations(jobs)
        loc_str = ", ".join(locations[:3])
        if len(locations) > 3:
            loc_str += f" +{len(locations) - 3} more"

        rows += f"""<tr>
    <td><a href="/companies/{slug}/">{company_name}</a></td>
    <td>{n_jobs}</td>
    <td>{loc_str if loc_str else 'Not specified'}</td>
</tr>
"""

    # Count companies with 2+ jobs
    qualified_count = sum(1 for jobs in all_companies.values() if len(jobs) >= 2)

    body = f"""<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Companies Hiring {ROLE_NAME} Professionals</h1>
        <p class="page-subtitle">{qualified_count} companies with multiple open positions</p>
    </div>

    <div class="salary-content">
        <div class="table-wrapper" style="overflow-x: auto;">
            <table class="data-table" style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Open Positions</th>
                        <th>Locations</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""
    body += newsletter_cta_html(f"Get {ROLE_NAME.lower()} job alerts in your inbox.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(
        title=title, description=description,
        canonical_path=canonical, body_content=body,
        active_path="/companies/", extra_head=extra_head
    )
    write_page("companies/index.html", page)


def build_all_company_pages(project_dir):
    """Main entry point: build company index + detail pages."""
    jobs = load_jobs(project_dir)
    companies = get_company_data(jobs)

    # Filter to companies with 2+ jobs
    qualified = {k: v for k, v in companies.items() if len(v) >= 2}

    if not qualified:
        print(f"  Skipping company pages (no companies with 2+ jobs)")
        return

    print(f"\n  Building company pages ({len(qualified)} companies)...")
    build_companies_index(companies)
    print(f"  Built: companies/index.html")

    for company_name, jobs in sorted(qualified.items()):
        build_company_page(company_name, jobs, companies)

    print(f"  Built: {len(qualified)} company detail pages")
