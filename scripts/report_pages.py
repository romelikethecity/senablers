# scripts/report_pages.py
# Lead magnet report landing pages: salary report, tool stack report, index.

import os
import json

from nav_config import *
from templates import (get_page_wrapper, write_page, get_breadcrumb_schema,
                       breadcrumb_html, newsletter_cta_html, ALL_PAGES)


ROLE = "Sales Enablement"
ROLE_SHORT = "Sales Enablement"
LIST_SLUG = "senablers"
CSS_PREFIX = "se"


def load_report_data(project_dir):
    data_dir = os.path.join(project_dir, "data")
    with open(os.path.join(data_dir, "comp_analysis.json")) as f:
        comp = json.load(f)
    with open(os.path.join(data_dir, "market_intelligence.json")) as f:
        market = json.load(f)
    return comp, market


def fmt_salary(n):
    if n >= 1000:
        return f"${n // 1000}K"
    return f"${n:,}"


def fmt_number(n):
    return f"{n:,}"


def _gate_form_css():
    return """
<style>
.report-hero {
    padding: 3rem 1.5rem;
    text-align: center;
    background: var(--se-bg-tinted);
}
.report-hero-inner {
    max-width: 720px;
    margin: 0 auto;
}
.report-hero h1 {
    font-size: 2.2rem;
    margin-bottom: 0.75rem;
    line-height: 1.2;
}
.report-hero .report-subtitle {
    font-size: 1.15rem;
    color: var(--se-text-secondary, #64748b);
    margin-bottom: 0;
}
.report-content {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 1.5rem 3rem;
}
.report-content h2 {
    font-size: 1.5rem;
    margin-top: 2.5rem;
    margin-bottom: 1rem;
}
.report-content h3 {
    font-size: 1.15rem;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}
.report-content p, .report-content li {
    line-height: 1.7;
    font-size: 1.05rem;
}
.report-content ul, .report-content ol {
    padding-left: 1.25rem;
    margin-bottom: 1.25rem;
}
.report-content li {
    margin-bottom: 0.4rem;
}
.report-preview-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}
.report-stat-card {
    background: var(--se-bg-surface, #fff);
    border: 1px solid var(--se-border, #e2e8f0);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
}
.report-stat-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--se-accent);
    margin-bottom: 0.25rem;
}
.report-stat-label {
    font-size: 0.85rem;
    color: var(--se-text-secondary, #64748b);
    font-weight: 500;
}
.report-gate {
    background: #f8fafc;
    border: 2px solid var(--se-accent);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin: 2.5rem 0;
}
.report-gate h2 {
    margin-top: 0;
    font-size: 1.4rem;
}
.report-gate p {
    color: var(--se-text-secondary, #64748b);
    margin-bottom: 1.5rem;
    max-width: 480px;
    margin-left: auto;
    margin-right: auto;
}
.report-gate-form {
    display: flex;
    gap: 0.75rem;
    max-width: 440px;
    margin: 0 auto;
    flex-wrap: wrap;
    justify-content: center;
}
.report-gate-form input[type="email"] {
    flex: 1;
    min-width: 220px;
    padding: 0.75rem 1rem;
    border: 1px solid var(--se-border, #e2e8f0);
    border-radius: 8px;
    font-size: 1rem;
    background: var(--se-bg-surface, #fff);
    color: var(--se-text-primary, #1e293b);
}
.report-gate-form button {
    padding: 0.75rem 1.75rem;
    background: var(--se-accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
}
.report-gate-form button:hover {
    background: var(--se-accent-hover);
}
.report-download-btn {
    display: none;
    margin: 1.5rem auto 0;
}
.report-download-btn a {
    display: inline-block;
    padding: 1rem 2.5rem;
    background: var(--se-accent);
    color: #fff;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: 700;
    text-decoration: none;
    transition: background 0.15s, transform 0.1s;
}
.report-download-btn a:hover {
    background: var(--se-accent-hover);
    transform: translateY(-1px);
}
.report-toc {
    background: var(--se-bg-surface, #fff);
    border: 1px solid var(--se-border, #e2e8f0);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin: 2rem 0;
}
.report-toc h3 {
    margin-top: 0;
    margin-bottom: 0.75rem;
}
.report-toc ol {
    padding-left: 1.25rem;
    margin-bottom: 0;
}
.report-toc li {
    margin-bottom: 0.35rem;
}
.report-tool-preview {
    display: grid;
    gap: 0.75rem;
    margin: 1.5rem 0;
}
.report-tool-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: var(--se-bg-surface, #fff);
    border: 1px solid var(--se-border, #e2e8f0);
    border-radius: 8px;
}
.report-tool-rank {
    font-weight: 700;
    color: var(--se-accent);
    min-width: 2rem;
}
.report-tool-name {
    flex: 1;
    font-weight: 600;
}
.report-tool-pct {
    color: var(--se-text-secondary, #64748b);
    font-size: 0.9rem;
}
.report-index-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}
.report-index-card {
    background: var(--se-bg-surface, #fff);
    border: 1px solid var(--se-border, #e2e8f0);
    border-radius: 14px;
    padding: 2rem;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.report-index-card:hover {
    border-color: var(--se-accent);
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.report-index-card h3 {
    margin-top: 0;
}
.report-index-card h3 a {
    color: var(--se-accent);
    text-decoration: none;
}
.report-index-card p {
    color: var(--se-text-secondary, #64748b);
    margin-bottom: 1rem;
}
.report-index-card .report-card-cta {
    display: inline-block;
    padding: 0.5rem 1.25rem;
    background: var(--se-accent);
    color: #fff;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
}
</style>
"""


def _gate_form_js(download_url, form_id):
    return f"""
<script>
(function() {{
    var form = document.getElementById('{form_id}');
    if (!form) return;
    form.onsubmit = function(e) {{
        e.preventDefault();
        var emailInput = form.querySelector('input[type="email"]');
        var btn = form.querySelector('button');
        var email = emailInput ? emailInput.value.trim() : '';
        if (!email) return;
        var origText = btn.textContent;
        btn.textContent = 'Processing...';
        btn.disabled = true;
        fetch('{SIGNUP_WORKER_URL}', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{email: email, list: '{LIST_SLUG}'}})
        }})
        .then(function(r) {{ return r.json(); }})
        .then(function(data) {{
            if (data.success) {{
                if (typeof gtag === 'function') {{
                    gtag('event', 'lead_magnet_download', {{
                        'event_category': 'conversion',
                        'event_label': '{form_id}'
                    }});
                }}
                form.style.display = 'none';
                var dlBtn = document.getElementById('{form_id}-download');
                if (dlBtn) {{
                    dlBtn.style.display = 'block';
                }}
            }} else {{
                btn.textContent = origText;
                btn.disabled = false;
                var err = document.createElement('p');
                err.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 0.75rem;';
                err.textContent = data.error || 'Something went wrong. Try again.';
                var existing = form.querySelector('.signup-error');
                if (existing) existing.remove();
                err.className = 'signup-error';
                form.appendChild(err);
            }}
        }})
        .catch(function() {{
            btn.textContent = origText;
            btn.disabled = false;
        }});
    }};
}})();
</script>
"""


def build_salary_report(project_dir, comp, market):
    """Build /reports/salary-report/ landing page."""
    stats = comp["salary_stats"]
    total = comp["total_records"]
    by_seniority = comp["by_seniority"]
    by_metro = comp.get("by_metro", {})

    sen_sorted = sorted(
        [(k, v) for k, v in by_seniority.items() if k != "Unknown"],
        key=lambda x: x[1]["count"], reverse=True
    )[:4]

    metro_sorted = sorted(
        [(k, v) for k, v in by_metro.items() if k != "Unknown"],
        key=lambda x: x[1]["count"], reverse=True
    )[:3]

    stat_cards = f"""
<div class="report-preview-stats">
    <div class="report-stat-card">
        <div class="report-stat-value">{fmt_salary(stats["median"])}</div>
        <div class="report-stat-label">Median Base Salary</div>
    </div>
    <div class="report-stat-card">
        <div class="report-stat-value">{fmt_number(total)}</div>
        <div class="report-stat-label">Job Postings Analyzed</div>
    </div>
    <div class="report-stat-card">
        <div class="report-stat-value">{fmt_salary(stats["max"])}</div>
        <div class="report-stat-label">Highest Salary Found</div>
    </div>
    <div class="report-stat-card">
        <div class="report-stat-value">{comp["disclosure_rate"]}%</div>
        <div class="report-stat-label">Salary Disclosure Rate</div>
    </div>
</div>
"""

    sen_preview = ""
    for level, data in sen_sorted:
        sen_preview += f'<li><strong>{level}</strong>: {fmt_salary(data["median"])} median ({data["count"]} postings)</li>\n'

    metro_preview = ""
    for city, data in metro_sorted:
        metro_preview += f'<li><strong>{city}</strong>: {fmt_salary(data["median"])} median</li>\n'

    bc_items = [("Home", "/"), ("Reports", "/reports/"), ("2026 Salary Report", None)]
    bc_schema = get_breadcrumb_schema(bc_items)
    bc_visual = breadcrumb_html(bc_items)

    role_lower = ROLE_SHORT.lower()

    body = f"""{_gate_form_css()}
<div class="report-hero">
    <div class="report-hero-inner">
        {bc_visual}
        <h1>The 2026 {ROLE} Salary Report</h1>
        <p class="report-subtitle">A data-driven breakdown of {role_lower} compensation across seniority levels, cities, company stages, and remote work. Based on {fmt_number(total)} real job postings.</p>
    </div>
</div>

<div class="report-content">

    <h2>Preview: Key Findings</h2>
    <p>Here is a snapshot of what the full report covers. These numbers come directly from our analysis of {fmt_number(total)} {role_lower} job postings collected in 2026.</p>

    {stat_cards}

    <h3>Salary by Seniority (Preview)</h3>
    <p>The full report breaks down compensation across every seniority band, from entry-level to VP and above. Here are a few highlights:</p>
    <ul>
        {sen_preview}
    </ul>

    <h3>Salary by City (Preview)</h3>
    <p>Location still matters for compensation, even in a remote-first world. Top-paying metros for {role_lower} roles:</p>
    <ul>
        {metro_preview}
    </ul>

    <div class="report-gate" id="salary-gate">
        <h2>Download the Full Report (Free)</h2>
        <p>Enter your email to get the complete 2026 {ROLE} Salary Report with all seniority bands, 15+ metros, remote premiums, and negotiation benchmarks.</p>
        <form class="report-gate-form" id="salary-report-form" onsubmit="return false;">
            <input type="email" placeholder="Your work email" aria-label="Email address" required>
            <button type="submit">Get the Report</button>
        </form>
        <div class="report-download-btn" id="salary-report-form-download">
            <a href="/reports/downloads/2026-{LIST_SLUG}-salary-report.pdf">Download Your Report (PDF)</a>
        </div>
    </div>

    <h2>What Is Inside the Full Report</h2>

    <div class="report-toc">
        <h3>Table of Contents</h3>
        <ol>
            <li>Executive Summary and Methodology</li>
            <li>Overall Compensation Landscape</li>
            <li>Salary by Seniority Level (Entry through VP+)</li>
            <li>Salary by Metro Area (15+ Cities)</li>
            <li>Salary by Company Stage (Startup, Mid-Market, Enterprise)</li>
            <li>Remote vs. Onsite vs. Hybrid Premium Analysis</li>
            <li>Equity and Variable Compensation Trends</li>
            <li>Salary Negotiation Benchmarks and Tactics</li>
            <li>Year-over-Year Trends</li>
            <li>Appendix: Raw Data Tables</li>
        </ol>
    </div>

    <h3>Salary by Seniority</h3>
    <p>The report covers every level from individual contributor to VP+. You will see median base, total comp ranges, and how quickly pay scales with promotions. We also break out "Head of" and "Lead" roles that sit between manager and director, a band that is growing fast in {role_lower}.</p>

    <h3>Salary by City</h3>
    <p>We analyze compensation in 15+ metro areas including New York, San Francisco, Los Angeles, Chicago, Seattle, Austin, Boston, Denver, and more. Each city section includes cost-of-living context so you can compare adjusted pay, not just raw numbers.</p>

    <h3>Company Stage Breakdown</h3>
    <p>Startup, mid-market, and enterprise employers pay differently. The report quantifies the gap and explains the tradeoffs: base salary vs. equity upside, team size, and scope of role. If you are deciding between a Series B startup and a Fortune 500, the data is here.</p>

    <h3>Remote Premium Analysis</h3>
    <p>Remote {role_lower} roles command a measurable premium in some segments and a discount in others. The report breaks down where remote work pays more, where it does not, and which seniority levels benefit most from location-independent roles.</p>

    <h3>Negotiation Benchmarks</h3>
    <p>Knowing the market is step one. The final chapter provides concrete negotiation ranges by seniority and region, so you walk into your next compensation conversation with data, not guesses. Includes percentile bands (25th, 50th, 75th, 90th) for every segment.</p>

    <h2>Who This Report Is For</h2>
    <ul>
        <li><strong>{ROLE} professionals</strong> evaluating a new offer or preparing for a raise conversation</li>
        <li><strong>Hiring managers</strong> benchmarking compensation bands for open roles</li>
        <li><strong>Recruiters</strong> who need to set competitive offers that actually close candidates</li>
        <li><strong>HR and People Ops teams</strong> building or auditing pay bands for {role_lower} functions</li>
    </ul>

    <h2>Methodology</h2>
    <p>This report is built from {fmt_number(total)} {role_lower} job postings collected in 2026. We pull listings from major job boards daily, normalize titles to standard seniority bands, extract disclosed salary ranges, and geocode each posting to a metro area. Only postings with verified salary data are included in compensation analysis. The full methodology is in Chapter 1 of the report.</p>

    {newsletter_cta_html("Get weekly salary data and career intelligence.")}
</div>

{_gate_form_js(f"/reports/downloads/2026-{LIST_SLUG}-salary-report.pdf", "salary-report-form")}
"""

    page = get_page_wrapper(
        f"Free Download: The 2026 {ROLE} Salary Report",
        f"Download the free 2026 {ROLE} Salary Report. Data from {fmt_number(total)} job postings covering salary by seniority, city, company stage, and remote premium.",
        "/reports/salary-report/",
        body,
        active_path="/reports/",
        extra_head=bc_schema,
    )
    write_page("reports/salary-report/index.html", page)
    print("    Built: /reports/salary-report/")


def build_tool_stack_report(project_dir, comp, market):
    """Build /reports/tool-stack-report/ landing page."""
    total = market["total_jobs"]
    tools = market.get("tools", {})

    skip_generic = {"Rag", "Rust", "Aws", "Azure", "Gcp", "Python", "Javascript",
                    "Kubernetes", "Docker", "Prompt Engineering", "Langchain",
                    "Openai", "Anthropic", "Cohere", "Gemini", "Claude", "Bedrock"}
    real_tools = [(name, count) for name, count in tools.items() if name not in skip_generic]
    top5 = real_tools[:5]
    top10 = real_tools[:10]

    tool_rows = ""
    for i, (name, count) in enumerate(top5, 1):
        pct = round(count / total * 100, 1)
        tool_rows += f"""
    <div class="report-tool-row">
        <span class="report-tool-rank">#{i}</span>
        <span class="report-tool-name">{name}</span>
        <span class="report-tool-pct">{pct}% of postings</span>
    </div>"""

    more_tools = ", ".join([name for name, _ in top10[5:]])

    bc_items = [("Home", "/"), ("Reports", "/reports/"), ("2026 Tool Stack Report", None)]
    bc_schema = get_breadcrumb_schema(bc_items)
    bc_visual = breadcrumb_html(bc_items)

    role_lower = ROLE_SHORT.lower()

    body = f"""{_gate_form_css()}
<div class="report-hero">
    <div class="report-hero-inner">
        {bc_visual}
        <h1>The 2026 {ROLE} Tool Stack Report</h1>
        <p class="report-subtitle">Which tools are {role_lower} teams actually using? A data-driven ranking based on {fmt_number(total)} job postings, updated for 2026.</p>
    </div>
</div>

<div class="report-content">

    <h2>Preview: Top 5 Tools by Job Demand</h2>
    <p>Every tool mention below is pulled directly from job postings. This is not a survey or vendor ranking. It is what companies are actually hiring for in 2026.</p>

    <div class="report-tool-preview">
        {tool_rows}
    </div>

    <p>Also in the top 10: <strong>{more_tools}</strong>. The full report ranks 50+ tools across every major category.</p>

    <div class="report-preview-stats">
        <div class="report-stat-card">
            <div class="report-stat-value">{fmt_number(total)}</div>
            <div class="report-stat-label">Job Postings Analyzed</div>
        </div>
        <div class="report-stat-card">
            <div class="report-stat-value">{len(tools)}+</div>
            <div class="report-stat-label">Tools Tracked</div>
        </div>
        <div class="report-stat-card">
            <div class="report-stat-value">10+</div>
            <div class="report-stat-label">Tool Categories</div>
        </div>
        <div class="report-stat-card">
            <div class="report-stat-value">2026</div>
            <div class="report-stat-label">Data Year</div>
        </div>
    </div>

    <div class="report-gate" id="tool-gate">
        <h2>Download the Full Report (Free)</h2>
        <p>Enter your email to get the complete 2026 {ROLE} Tool Stack Report with 50+ tool rankings, category breakdowns, and emerging tool analysis.</p>
        <form class="report-gate-form" id="tool-report-form" onsubmit="return false;">
            <input type="email" placeholder="Your work email" aria-label="Email address" required>
            <button type="submit">Get the Report</button>
        </form>
        <div class="report-download-btn" id="tool-report-form-download">
            <a href="/reports/downloads/2026-{LIST_SLUG}-tool-stack-report.pdf">Download Your Report (PDF)</a>
        </div>
    </div>

    <h2>What Is Inside the Full Report</h2>

    <div class="report-toc">
        <h3>Table of Contents</h3>
        <ol>
            <li>Executive Summary and Methodology</li>
            <li>Overall Tool Adoption Rankings (50+ Tools)</li>
            <li>Category Breakdown: CRM, Automation, Analytics, and More</li>
            <li>Emerging Tools: Fastest-Growing Mentions in 2026</li>
            <li>Tool Combinations: Most Common Stacks</li>
            <li>Hiring Signals: What Tool Requirements Tell You About the Role</li>
            <li>Enterprise vs. Startup Tool Preferences</li>
            <li>Tool Adoption by Seniority Level</li>
            <li>Year-over-Year Trend Analysis</li>
            <li>Appendix: Full Tool Rankings Table</li>
        </ol>
    </div>

    <h3>Complete Tool Rankings</h3>
    <p>The full report ranks every tool we track by the percentage of {role_lower} job postings that mention it. This is not a "best of" list based on opinions. It is a direct measurement of what companies require when they hire. You will see exactly which platforms dominate and which are losing ground.</p>

    <h3>Category Breakdowns</h3>
    <p>Tools are organized into categories: CRM, marketing automation, analytics and BI, intent data, engagement platforms, and more. Each category section covers the top tools, their market share within the category, and how they compare on adoption trends.</p>

    <h3>Emerging Tools</h3>
    <p>Which tools are growing fastest in job postings? This section identifies platforms that are gaining traction in 2026 and may not be on your radar yet. Early adoption of the right tools is a career differentiator.</p>

    <h3>Hiring Signals</h3>
    <p>When a posting requires specific tool combinations, that tells you something about the team structure and maturity of the org. This chapter decodes what tool requirements reveal about the role, the team, and the company stage. Useful for job seekers evaluating fit and hiring managers writing better job descriptions.</p>

    <h3>Enterprise vs. Startup Preferences</h3>
    <p>Enterprise companies and startups favor different tools. The report quantifies the gap. If you are moving from a large company to a startup (or vice versa), this section shows you which skills transfer and which ones you will need to pick up.</p>

    <h2>Who This Report Is For</h2>
    <ul>
        <li><strong>{ROLE} professionals</strong> deciding which tools to learn next for career growth</li>
        <li><strong>Hiring managers</strong> writing job descriptions with realistic tool requirements</li>
        <li><strong>Vendors and analysts</strong> tracking competitive market share</li>
        <li><strong>Career switchers</strong> building a tool stack that matches real hiring demand</li>
    </ul>

    <h2>Methodology</h2>
    <p>This report is built from {fmt_number(total)} {role_lower} job postings collected in 2026. We extract every tool, platform, and technology mentioned in each posting, normalize names (e.g., "SFDC" and "Salesforce" are merged), and count unique postings per tool. The result is an unbiased adoption ranking based on actual hiring behavior, not vendor claims or user surveys.</p>

    {newsletter_cta_html("Get weekly tool reviews and market intelligence.")}
</div>

{_gate_form_js(f"/reports/downloads/2026-{LIST_SLUG}-tool-stack-report.pdf", "tool-report-form")}
"""

    page = get_page_wrapper(
        f"Free Download: The 2026 {ROLE} Tool Stack Report",
        f"Download the free 2026 {ROLE} Tool Stack Report. Rankings of 50+ tools based on {fmt_number(total)} job postings, with category breakdowns and emerging trends.",
        "/reports/tool-stack-report/",
        body,
        active_path="/reports/",
        extra_head=bc_schema,
    )
    write_page("reports/tool-stack-report/index.html", page)
    print("    Built: /reports/tool-stack-report/")


def build_reports_index(project_dir, comp, market):
    """Build /reports/ index page linking to both reports."""
    total_jobs = comp["total_records"]
    median_salary = comp["salary_stats"]["median"]
    tools_count = len(market.get("tools", {}))

    bc_items = [("Home", "/"), ("Reports", None)]
    bc_schema = get_breadcrumb_schema(bc_items)
    bc_visual = breadcrumb_html(bc_items)

    role_lower = ROLE_SHORT.lower()

    body = f"""{_gate_form_css()}
<div class="report-hero">
    <div class="report-hero-inner">
        {bc_visual}
        <h1>Free {ROLE} Reports</h1>
        <p class="report-subtitle">Data-driven reports for {role_lower} professionals. Built from {fmt_number(total_jobs)} job postings, updated for 2026.</p>
    </div>
</div>

<div class="report-content">
    <div class="report-index-grid">
        <div class="report-index-card">
            <h3><a href="/reports/salary-report/">The 2026 {ROLE} Salary Report</a></h3>
            <p>Complete salary breakdown by seniority, city, company stage, and remote work status. Includes negotiation benchmarks and percentile bands. Based on {fmt_number(total_jobs)} postings with a {fmt_salary(median_salary)} median base salary.</p>
            <a href="/reports/salary-report/" class="report-card-cta">Download Free Report</a>
        </div>
        <div class="report-index-card">
            <h3><a href="/reports/tool-stack-report/">The 2026 {ROLE} Tool Stack Report</a></h3>
            <p>Rankings of {tools_count}+ tools by hiring demand. Category breakdowns, emerging tools, enterprise vs. startup preferences, and hiring signal analysis. See what companies actually require.</p>
            <a href="/reports/tool-stack-report/" class="report-card-cta">Download Free Report</a>
        </div>
    </div>

    <h2>Why Our Reports Are Different</h2>
    <p>Most industry reports rely on self-reported survey data or vendor partnerships. Ours do not. Every number in these reports comes from actual job postings: real salary ranges disclosed by real companies, and real tool requirements written by real hiring managers.</p>
    <p>We collect {role_lower} job postings daily, normalize the data, and analyze it. No sponsorships, no pay-to-play rankings, no survey bias. Just the market as it actually is.</p>

    {newsletter_cta_html("Get weekly data and analysis delivered to your inbox.")}
</div>
"""

    page = get_page_wrapper(
        f"Free {ROLE} Reports and Downloads",
        f"Download free {ROLE} reports including salary data and tool stack rankings. Built from {fmt_number(total_jobs)} job postings, updated for 2026.",
        "/reports/",
        body,
        active_path="/reports/",
        extra_head=bc_schema,
    )
    write_page("reports/index.html", page)
    print("    Built: /reports/")


def build_all_report_pages(project_dir=None):
    """Build all report pages. Called from build.py main()."""
    if project_dir is None:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("\n  Building report pages...")
    comp, market = load_report_data(project_dir)
    build_reports_index(project_dir, comp, market)
    build_salary_report(project_dir, comp, market)
    build_tool_stack_report(project_dir, comp, market)
