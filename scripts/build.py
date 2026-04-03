# scripts/build.py
# Main build pipeline: generates all pages, sitemap, robots, CNAME.
# Data + page generators live here. HTML shell lives in templates.py.
# Site constants live in nav_config.py.

import os
import sys
import re
import shutil
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav_config import *
import templates
from templates import (get_page_wrapper, write_page, get_homepage_schema,
                       get_breadcrumb_schema, get_faq_schema,
                       get_software_application_schema, get_article_schema,
                       breadcrumb_html, newsletter_cta_html, faq_html, ALL_PAGES)

# OG image generation state
OG_PAGES = []
SKIP_OG = "--skip-og" in sys.argv


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")

# Wire up templates module
templates.OUTPUT_DIR = OUTPUT_DIR
templates.SKIP_OG = SKIP_OG


# ---------------------------------------------------------------------------
# Salary Data (placeholder — populate from real data later)
# ---------------------------------------------------------------------------

def fmt_salary(n):
    """Format salary number: 132000 -> '$132K'"""
    return f"${n // 1000}K"


SALARY_BY_SENIORITY = {
    "junior": {
        "label": "Junior / Associate",
        "slug": "junior",
        "min": 65000, "max": 95000, "median": 78000,
    },
    "mid": {
        "label": "Mid-Level",
        "slug": "mid-level",
        "min": 90000, "max": 130000, "median": 110000,
    },
    "senior": {
        "label": "Senior",
        "slug": "senior",
        "min": 125000, "max": 175000, "median": 148000,
    },
    "director": {
        "label": "Director / VP",
        "slug": "director-vp",
        "min": 160000, "max": 240000, "median": 195000,
    },
}


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------

def build_homepage():
    """Generate the homepage with Organization+WebSite schema."""
    title = "Sales Enablement Salary and Career Intelligence"
    description = (
        "Salary benchmarks, tool reviews, and career data for sales enablement professionals."
        " Vendor-neutral. Updated weekly. Free."
    )

    body = '''<section class="hero">
    <div class="hero-inner">
        <h1>Sales Enablement, Finally Mapped Out</h1>
        <p class="hero-subtitle">Salary data, tool reviews, career paths, and job listings for the people who make revenue teams sell better.</p>
        <div class="stat-grid">
            <div class="stat-block">
                <span class="stat-value">12,000+</span>
                <span class="stat-label">Roles Tracked</span>
            </div>
            <div class="stat-block">
                <span class="stat-value">$65K&#8209;$240K+</span>
                <span class="stat-label">Salary Range</span>
            </div>
            <div class="stat-block">
                <span class="stat-value">45%</span>
                <span class="stat-label">3yr Growth</span>
            </div>
        </div>
        <form class="hero-signup" onsubmit="return false;">
            <input type="email" placeholder="Your email" aria-label="Email address" required>
            <button type="submit" class="btn btn--primary">Get the Weekly Brief</button>
        </form>
        <p class="hero-signup-note">Free weekly newsletter. Salary shifts, tool intel, career moves.</p>
    </div>
</section>

<section class="logo-bar">
    <p class="logo-bar-label">Tracking enablement hiring at companies like</p>
    <div class="logo-bar-row">
        <span class="logo-name">Highspot</span>
        <span class="logo-name">Seismic</span>
        <span class="logo-name">Gong</span>
        <span class="logo-name">Showpad</span>
        <span class="logo-name">Mindtickle</span>
        <span class="logo-name">Salesforce</span>
        <span class="logo-name">HubSpot</span>
        <span class="logo-name">Outreach</span>
        <span class="logo-name">Clari</span>
        <span class="logo-name">Allego</span>
    </div>
</section>

<section class="section-previews">
    <h2 class="section-previews-heading">Explore Enablement Intelligence</h2>
    <div class="preview-grid">
        <a href="/salary/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128176;</span></div>
            <h3>Salary Data</h3>
            <p>Breakdowns by seniority, location, and company stage. See where you stand against the market.</p>
            <span class="preview-link">Browse salary data &rarr;</span>
        </a>
        <a href="/tools/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128295;</span></div>
            <h3>Tool Reviews</h3>
            <p>Honest reviews of Highspot, Seismic, Mindtickle, Gong, Showpad, and more. No pay-to-play rankings.</p>
            <span class="preview-link">Browse tools &rarr;</span>
        </a>
        <a href="/careers/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128200;</span></div>
            <h3>Career Guides</h3>
            <p>How to break into enablement, level up to Director, and negotiate comp at every stage.</p>
            <span class="preview-link">Browse guides &rarr;</span>
        </a>
        <a href="/jobs/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128188;</span></div>
            <h3>Job Board</h3>
            <p>Curated enablement roles from top B2B companies. Updated weekly from thousands of tracked postings.</p>
            <span class="preview-link">View all jobs &rarr;</span>
        </a>
        <a href="/glossary/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128218;</span></div>
            <h3>Enablement Glossary</h3>
            <p>Clear definitions for sales enablement terms. Content management, buyer enablement, sales plays, and more.</p>
            <span class="preview-link">Browse glossary &rarr;</span>
        </a>
        <a href="/newsletter/" class="preview-card">
            <div class="preview-icon"><span class="preview-emoji">&#128232;</span></div>
            <h3>Weekly Brief</h3>
            <p>Salary shifts, tool updates, and hiring trends delivered every week. Built for enablement professionals.</p>
            <span class="preview-link">Get the weekly brief &rarr;</span>
        </a>
    </div>
</section>

'''
    body += newsletter_cta_html()

    page = get_page_wrapper(
        title=title,
        description=description,
        canonical_path="/",
        body_content=body,
        active_path="/",
        extra_head=get_homepage_schema(),
        body_class="page-home",
    )
    write_page("index.html", page)
    print(f"  Built: index.html")


def build_about_page():
    """Generate the about page."""
    title = "About SEnablers: Enablement Career Data"
    description = (
        "SEnablers provides vendor-neutral salary benchmarks, tool reviews, and career intelligence"
        " for sales enablement professionals. Independent and free."
    )

    crumbs = [("Home", "/"), ("About", None)]
    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>About SEnablers</h1>
        <p>Independent career intelligence for sales enablement professionals.</p>
    </div>
    <div class="salary-content">
        <h2>What Is SEnablers?</h2>
        <p>SEnablers is a free, vendor-neutral resource hub for sales enablement professionals. We track salary data, review enablement tools, and map career paths so you can make better decisions about your career.</p>

        <h2>Why Does This Exist?</h2>
        <p>Sales enablement is a $3B+ market with thousands of professionals, but no single source of truth for compensation, career paths, or honest tool reviews. We built SEnablers to fill that gap.</p>

        <h2>Who Runs This?</h2>
        <p>SEnablers is built and maintained by <strong>Rome Thorndike</strong>. No venture funding, no vendor partnerships, no bias.</p>
        <p>Questions? Reach out at <a href="mailto:rome@getprovyx.com">rome@getprovyx.com</a>.</p>
    </div>
</div>'''

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/about/", body_content=body,
                            active_path="/about/", extra_head=extra_head)
    write_page("about/index.html", page)
    print(f"  Built: about/index.html")


def build_newsletter_page():
    """Generate the newsletter signup page."""
    title = "The Weekly Brief: Enablement Career Intel"
    description = (
        "Free weekly newsletter with salary shifts, tool updates, and hiring trends for sales enablement"
        " professionals. No spam. Unsubscribe anytime. Independent."
    )

    crumbs = [("Home", "/"), ("Newsletter", None)]
    body = f'''<div class="container">
    <div class="newsletter-page">
        {breadcrumb_html(crumbs)}
        <h1>The Weekly Brief</h1>
        <p class="lead">Salary shifts, tool intel, and career moves for enablement professionals. Delivered every week.</p>
        <ul class="newsletter-features">
            <li>Enablement salary data and market shifts</li>
            <li>Tool updates from Highspot, Seismic, Gong, and others</li>
            <li>Career moves, promotions, and hiring trends</li>
            <li>No vendor bias. No fluff. Data and analysis only.</li>
        </ul>
        <form class="hero-signup" onsubmit="return false;">
            <input type="email" placeholder="Your email" aria-label="Email address" required>
            <button type="submit" class="btn btn--primary">Get the Weekly Brief</button>
        </form>
        <p class="hero-signup-note">Free. No spam. Unsubscribe anytime.</p>
    </div>
</div>'''

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/newsletter/", body_content=body,
                            active_path="/newsletter/", extra_head=extra_head)
    write_page("newsletter/index.html", page)
    print(f"  Built: newsletter/index.html")


def build_privacy_page():
    """Generate the privacy policy page."""
    title = "Privacy Policy for SEnablers.com"
    description = (
        "Privacy policy for SEnablers. We collect minimal data: email for newsletter,"
        " standard analytics. No data sales. No third-party trackers. Updated 2026."
    )

    body = f'''<div class="container">
    <div class="legal-content">
        <h1>Privacy Policy</h1>
        <p>Last updated: April 2026</p>

        <h2>What We Collect</h2>
        <p>If you sign up for our newsletter, we collect your email address. We use Google Analytics to track aggregate page views. That is it.</p>

        <h2>How We Use Your Data</h2>
        <p>Your email is used to send the weekly newsletter. Analytics data helps us understand which pages are useful. We do not sell, share, or rent your personal information to anyone.</p>

        <h2>Cookies</h2>
        <p>We use standard Google Analytics cookies. No advertising cookies. No retargeting pixels.</p>

        <h2>Third Parties</h2>
        <p>We use Resend to send emails and Cloudflare to host the site. Both have their own privacy policies.</p>

        <h2>Your Rights</h2>
        <p>You can unsubscribe from the newsletter at any time. To request data deletion, email <a href="mailto:rome@getprovyx.com">rome@getprovyx.com</a>.</p>

        <h2>Contact</h2>
        <p>Questions about this policy? Email <a href="mailto:rome@getprovyx.com">rome@getprovyx.com</a>.</p>
    </div>
</div>'''

    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/privacy/", body_content=body,
                            active_path="/privacy/")
    write_page("privacy/index.html", page)
    print(f"  Built: privacy/index.html")


def build_terms_page():
    """Generate the terms of service page."""
    title = "Terms of Service for SEnablers.com"
    description = (
        "Terms of service for SEnablers. Free to use. Content is for informational purposes only."
        " Salary data is aggregated from public sources. No guarantees. Updated 2026."
    )

    body = f'''<div class="container">
    <div class="legal-content">
        <h1>Terms of Service</h1>
        <p>Last updated: April 2026</p>

        <h2>Use of Site</h2>
        <p>SEnablers provides salary data, tool reviews, and career information for informational purposes only. Content should not be construed as legal, financial, or career advice.</p>

        <h2>Data Accuracy</h2>
        <p>We make reasonable efforts to ensure data accuracy but provide no warranties. Salary figures are aggregated estimates, not guarantees of compensation.</p>

        <h2>Intellectual Property</h2>
        <p>All content on SEnablers is the property of SEnablers unless otherwise noted. You may reference our data with attribution.</p>

        <h2>Newsletter</h2>
        <p>By subscribing, you agree to receive periodic emails. You can unsubscribe at any time via the link in each email.</p>

        <h2>Limitation of Liability</h2>
        <p>SEnablers is not liable for decisions made based on information provided on this site.</p>

        <h2>Contact</h2>
        <p>Questions? Email <a href="mailto:rome@getprovyx.com">rome@getprovyx.com</a>.</p>
    </div>
</div>'''

    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/terms/", body_content=body,
                            active_path="/terms/")
    write_page("terms/index.html", page)
    print(f"  Built: terms/index.html")


def build_404_page():
    """Generate the 404 error page."""
    title = "Page Not Found"
    description = "This page doesn't exist. Head back to the homepage for salary data, tool reviews, and career guides."

    body = '''<div class="container">
    <div class="error-page">
        <div class="error-code">404</div>
        <h1>Page Not Found</h1>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        <a href="/" class="btn btn--primary">Back to Home</a>
    </div>
</div>'''

    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/404.html", body_content=body)
    write_page("404.html", page)
    print(f"  Built: 404.html")


def build_salary_index():
    """Generate the salary index page."""
    title = "Sales Enablement Salary Data 2026"
    description = (
        "Salary benchmarks for sales enablement professionals by seniority, location, and company stage."
        " Independent data. Updated weekly. Free to browse."
    )

    crumbs = [("Home", "/"), ("Salary Data", None)]
    cards = ""
    for key, data in SALARY_BY_SENIORITY.items():
        cards += f'''<a href="/salary/by-seniority/{data['slug']}/" class="salary-index-card">
    <h3>{data['label']}</h3>
    <div class="card-range">{fmt_salary(data['min'])} - {fmt_salary(data['max'])}</div>
    <p>Median: {fmt_salary(data['median'])}</p>
</a>
'''

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>Sales Enablement Salary Index</h1>
        <p>How much do enablement professionals earn? Explore salary data by seniority, location, and company stage.</p>
    </div>
</div>
<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(78000)}</span>
        <span class="stat-label">Junior Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(148000)}</span>
        <span class="stat-label">Senior Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(195000)}</span>
        <span class="stat-label">Director Median</span>
    </div>
</div>
<div class="salary-content">
    <h2>By Seniority</h2>
    <div class="salary-index-grid">
        {cards}
    </div>
    <h2>Explore More</h2>
    <div class="related-links-grid">
        <a href="/salary/by-location/" class="related-link-card">Salary by Location</a>
        <a href="/salary/comparisons/" class="related-link-card">Role Comparisons</a>
        <a href="/salary/calculator/" class="related-link-card">Salary Calculator</a>
        <a href="/careers/" class="related-link-card">Career Guides</a>
    </div>
</div>
'''
    body += newsletter_cta_html("Get weekly salary updates.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/salary/", body_content=body,
                            active_path="/salary/", extra_head=extra_head)
    write_page("salary/index.html", page)
    print(f"  Built: salary/index.html")


def build_tools_index():
    """Generate the tools index page."""
    title = "Sales Enablement Tool Reviews 2026"
    description = (
        "Honest reviews of Highspot, Seismic, Mindtickle, Gong, Showpad, and more enablement tools."
        " No pay-to-play rankings. Independent analysis."
    )

    crumbs = [("Home", "/"), ("Tools", None)]
    tools = [
        ("Highspot", "Content management, guided selling, analytics. The category leader."),
        ("Seismic", "Content automation, training, analytics. Enterprise-grade enablement."),
        ("Mindtickle", "Readiness, coaching, content. Strong on sales training and certification."),
        ("Gong", "Revenue intelligence, call recording, deal analytics. The conversation data platform."),
        ("Showpad", "Content management, coaching, buyer engagement. Strong in manufacturing and life sciences."),
        ("Allego", "Video coaching, content management, readiness. Built for distributed sales teams."),
    ]

    tool_cards = ""
    for name, desc in tools:
        slug = name.lower().replace(" ", "-")
        tool_cards += f'''<a href="/tools/{slug}-review/" class="preview-card">
    <h3>{name}</h3>
    <p>{desc}</p>
    <span class="preview-link">Read review &rarr;</span>
</a>
'''

    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Enablement Tool Reviews</h1>
        <p>Practitioner-tested reviews of the tools enablement teams use every day. Honest scores, no vendor bias.</p>
    </div>
    <div class="preview-grid">
        {tool_cards}
    </div>
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/tools/", body_content=body,
                            active_path="/tools/", extra_head=extra_head)
    write_page("tools/index.html", page)
    print(f"  Built: tools/index.html")


def build_careers_index():
    """Generate the careers index page."""
    title = "Sales Enablement Career Guides 2026"
    description = (
        "Career guides for sales enablement professionals. How to break in, level up to Director,"
        " and negotiate comp at every stage. Data-backed advice."
    )

    crumbs = [("Home", "/"), ("Careers", None)]
    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Enablement Career Guides</h1>
        <p>How to break into enablement, level up, and negotiate comp. Data-backed career intelligence.</p>
    </div>
    <div class="preview-grid">
        <a href="/careers/how-to-break-into-enablement/" class="preview-card">
            <h3>Break Into Enablement</h3>
            <p>The roles, skills, and paths that get you hired in sales enablement. No MBA required.</p>
            <span class="preview-link">Read guide &rarr;</span>
        </a>
        <a href="/careers/job-growth/" class="preview-card">
            <h3>Job Market Growth</h3>
            <p>Enablement hiring trends, growth rates, and where the roles are opening fastest.</p>
            <span class="preview-link">See the data &rarr;</span>
        </a>
        <a href="/salary/" class="preview-card">
            <h3>Salary Data</h3>
            <p>What enablement professionals earn at every level, in every major market.</p>
            <span class="preview-link">Browse salaries &rarr;</span>
        </a>
    </div>
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/careers/", body_content=body,
                            active_path="/careers/", extra_head=extra_head)
    write_page("careers/index.html", page)
    print(f"  Built: careers/index.html")


def build_glossary_index():
    """Generate the glossary index page."""
    title = "Sales Enablement Glossary: Key Terms"
    description = (
        "Clear definitions for sales enablement terms. Content management, buyer enablement, sales plays,"
        " digital sales rooms, readiness, and more. Free reference."
    )

    crumbs = [("Home", "/"), ("Glossary", None)]
    terms = [
        "Sales Enablement", "Content Management", "Buyer Enablement", "Sales Plays",
        "Digital Sales Rooms", "Sales Readiness", "Sales Coaching", "Revenue Intelligence",
        "Guided Selling", "Sales Content Analytics",
    ]

    term_list = ""
    for term in terms:
        slug = term.lower().replace(" ", "-")
        term_list += f'<a href="/glossary/{slug}/" class="related-link-card">{term}</a>\n'

    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Enablement Glossary</h1>
        <p>Clear definitions for the terms that matter in sales enablement.</p>
    </div>
    <div class="related-links-grid">
        {term_list}
    </div>
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/glossary/", body_content=body,
                            active_path="/glossary/", extra_head=extra_head)
    write_page("glossary/index.html", page)
    print(f"  Built: glossary/index.html")


def build_jobs_index():
    """Generate the job board page."""
    title = "Sales Enablement Jobs: Current Openings"
    description = (
        "Curated sales enablement job listings from top B2B companies. Updated weekly. Filter by seniority,"
        " location, and remote. Free to browse and apply."
    )

    crumbs = [("Home", "/"), ("Job Board", None)]
    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Enablement Job Board</h1>
        <p>Curated sales enablement roles from top B2B companies. Updated weekly.</p>
    </div>
    <div class="salary-content">
        <p>Job listings are coming soon. Sign up for the Weekly Brief to get notified when roles go live.</p>
    </div>
</div>
'''
    body += newsletter_cta_html("Get job alerts in your inbox.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/jobs/", body_content=body,
                            active_path="/jobs/", extra_head=extra_head)
    write_page("jobs/index.html", page)
    print(f"  Built: jobs/index.html")


def build_blog_index():
    """Generate the blog index page."""
    title = "Sales Enablement Blog: Analysis and Data"
    description = (
        "Data-driven articles on sales enablement trends, tool adoption, salary shifts, and career paths."
        " Written by practitioners, not marketers. Independent analysis."
    )

    crumbs = [("Home", "/"), ("Blog", None)]
    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Enablement Blog</h1>
        <p>Data-driven analysis of enablement trends, tools, and career paths.</p>
    </div>
    <div class="salary-content">
        <p>Articles are coming soon. Sign up for the Weekly Brief to get the first posts in your inbox.</p>
    </div>
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/blog/", body_content=body,
                            active_path="/blog/", extra_head=extra_head)
    write_page("blog/index.html", page)
    print(f"  Built: blog/index.html")


def build_insights_index():
    """Generate the insights index page."""
    title = "Sales Enablement Insights and Research"
    description = (
        "Research and analysis on sales enablement. Market sizing, tool trends, compensation data, and hiring"
        " intelligence. Free to read. Vendor-neutral research."
    )

    crumbs = [("Home", "/"), ("Insights", None)]
    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Enablement Insights</h1>
        <p>Research and analysis on enablement market trends, compensation, and tool adoption.</p>
    </div>
    <div class="salary-content">
        <p>Insights are coming soon. Sign up for the Weekly Brief to get the first reports in your inbox.</p>
    </div>
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/insights/", body_content=body,
                            active_path="/insights/", extra_head=extra_head)
    write_page("insights/index.html", page)
    print(f"  Built: insights/index.html")


def build_comparisons_index():
    """Generate the comparisons index page."""
    title = "Enablement Tool Comparisons: Head to Head"
    description = (
        "Side-by-side comparisons of sales enablement tools. Highspot vs Seismic, Gong vs Mindtickle, and more."
        " Independent analysis with pricing and feature data."
    )

    crumbs = [("Home", "/"), ("Comparisons", None)]
    comparisons = [
        ("Highspot vs Seismic", "/comparisons/highspot-vs-seismic/"),
        ("Gong vs Mindtickle", "/comparisons/gong-vs-mindtickle/"),
        ("Showpad vs Highspot", "/comparisons/showpad-vs-highspot/"),
        ("Allego vs Mindtickle", "/comparisons/allego-vs-mindtickle/"),
    ]

    links = ""
    for label, href in comparisons:
        links += f'<a href="{href}" class="comparison-link"><span class="vs-badge">VS</span> {label.split(" vs ")[0]} vs {label.split(" vs ")[1]}</a>\n'

    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Tool Comparisons</h1>
        <p>Head-to-head comparisons of the tools enablement teams evaluate most.</p>
    </div>
    <div class="comparison-grid">
        {links}
    </div>
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/comparisons/", body_content=body,
                            active_path="/comparisons/", extra_head=extra_head)
    write_page("comparisons/index.html", page)
    print(f"  Built: comparisons/index.html")


# ---------------------------------------------------------------------------
# Sitemap & Robots
# ---------------------------------------------------------------------------

def build_sitemap():
    urls = ""
    for page_path in ALL_PAGES:
        clean = page_path.replace("index.html", "")
        if not clean.startswith("/"):
            clean = "/" + clean
        if not clean.endswith("/"):
            clean += "/"
        if clean == "//":
            clean = "/"
        urls += f"  <url>\n    <loc>{SITE_URL}{clean}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n  </url>\n"

    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"  Built: sitemap.xml ({len(ALL_PAGES)} URLs)")


def build_robots():
    content = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Built: robots.txt")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"=== SEnablers Build ({BUILD_DATE}) ===\n")

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    print("  Cleaned output/")

    shutil.copytree(ASSETS_DIR, os.path.join(OUTPUT_DIR, "assets"))
    print("  Copied assets/")

    print("\n  Building core pages...")
    build_homepage()
    build_about_page()
    build_newsletter_page()
    build_privacy_page()
    build_terms_page()
    build_404_page()

    print("\n  Building salary pages...")
    build_salary_index()

    print("\n  Building tool pages...")
    build_tools_index()

    print("\n  Building career pages...")
    build_careers_index()

    print("\n  Building glossary...")
    build_glossary_index()

    print("\n  Building job board...")
    build_jobs_index()

    print("\n  Building blog...")
    build_blog_index()

    print("\n  Building insights...")
    build_insights_index()

    print("\n  Building comparisons...")
    build_comparisons_index()

    print("\n  Building meta files...")
    build_sitemap()
    build_robots()

    with open(os.path.join(OUTPUT_DIR, "CNAME"), "w", encoding="utf-8") as f:
        f.write("senablers.com\n")
    print("  Built: CNAME")

    # Google Search Console verification file
    if GOOGLE_SITE_VERIFICATION:
        verification_path = os.path.join(OUTPUT_DIR, GOOGLE_SITE_VERIFICATION)
        with open(verification_path, "w", encoding="utf-8") as f:
            f.write(f"google-site-verification: {GOOGLE_SITE_VERIFICATION}")
        print(f"  Generated {GOOGLE_SITE_VERIFICATION}")

    print(f"\n=== Build complete: {len(ALL_PAGES)} pages ===")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Preview: cd output && python3 -m http.server 8090")


if __name__ == "__main__":
    main()
