#!/usr/bin/env python3
"""Generate the Sales Enablement resources page using the site's native templates."""

import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

import templates
from templates import get_page_wrapper, write_page

templates.OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
templates.SKIP_OG = True

# ---------------------------------------------------------------------------
# Resource data
# ---------------------------------------------------------------------------

RESOURCE_DATA = {
    "title": "Best Resources for Sales Enablement Professionals in 2026",
    "slug": "best-sales-enablement-resources",
    "description": "Curated list of the best newsletters, communities, platforms, podcasts, and training for sales enablement professionals.",
    "canonical": "https://thegtmindex.com/sales-enablement/",
    "intro": "Sales enablement owns the intersection of content, training, and technology that makes sellers effective. The role has expanded from content management to encompass onboarding, coaching, analytics, and AI-assisted selling.\n\nThis list covers the communities, platforms, and content that enablement practitioners actually use. No vendor rankings disguised as editorial.",
    "sections": [
        {"title": "Newsletters", "items": [
            {"name": "Sales Enablement Collective Newsletter", "url": "https://www.salesenablementcollective.com/", "desc": "Newsletter with insights and resources, reaching 18,000+ enablement professionals."},
        ]},
        {"title": "Blogs & Websites", "items": [
            {"name": "Spekit Blog", "url": "https://www.spekit.com/blog", "desc": "Revenue enablement trends, AI strategies, and just-in-time enablement content."},
            {"name": "Highspot Resource Library", "url": "https://www.highspot.com/library/", "desc": "Guides, templates, and Gartner reports from a leading enablement platform."},
            {"name": "Seismic Resources", "url": "https://www.seismic.com/newsroom/", "desc": "Product releases, research reports, and enablement content from the leading enablement platform."},
            {"name": "FFWD Sales Enablement", "url": "https://www.goffwd.com/", "desc": "Felix Krueger's consulting firm with 'This Month In Sales Enablement' content roundups."},
            {"name": "SE Nablers", "url": "https://senablers.com/", "desc": "Sales enablement professional community and career resources.", "owned": True},
            {"name": "MOPs Report", "url": "https://mopsreport.com/", "desc": "Marketing operations career intelligence with tool reviews and salary data for the enablement-adjacent MOps function.", "owned": True},
        ]},
        {"title": "Communities", "items": [
            {"name": "Sales Enablement Collective", "url": "https://www.salesenablementcollective.com/", "desc": "18,000+ member community with newsletter, podcast, summits, and resources library."},
            {"name": "Revenue Enablement Society", "url": "https://www.resociety.global", "desc": "Not-for-profit professional membership association with chapter programs and free community."},
        ]},
        {"title": "Podcasts", "items": [
            {"name": "Stories From The Trenches Podcast", "url": "https://open.spotify.com/show/6ZX0GntzGgAFGrpQI5FvwX", "desc": "RES podcast where enablement practitioners share real-world experiences, hosted by Paul Butterfield."},
            {"name": "The State of Sales Enablement Podcast", "url": "https://www.goffwd.com/thestateofsalesenablement/", "desc": "Monthly podcast by Felix Krueger with actionable advice from B2B enablement leaders."},
        ]},
    ],
}


def build_body_content(data):
    """Build the resource page body content."""
    sections_html = ""
    schema_items = []
    position = 1

    for section in data["sections"]:
        if not section["items"]:
            continue
        items_html = ""
        for i, item in enumerate(section["items"], 1):
            owned_badge = ""
            if item.get("owned"):
                owned_badge = ' <span style="display:inline-block;background:#FEF3C7;color:#92400E;font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;vertical-align:middle;margin-left:4px;">OUR PICK</span>'
            items_html += f'''
            <div style="margin-bottom:24px;">
                <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">
                    {i}. <a href="{item['url']}" target="_blank" rel="noopener" style="text-decoration:underline;text-decoration-color:#E5E7EB;text-underline-offset:3px;">{item['name']}</a>{owned_badge}
                </h3>
                <p style="font-size:14px;color:#6B7280;line-height:1.6;">{item['desc']}</p>
            </div>'''
            schema_items.append({
                "@type": "ListItem",
                "position": position,
                "name": item["name"],
                "url": item["url"]
            })
            position += 1

        sections_html += f'''
        <section style="margin-bottom:48px;">
            <h2 style="font-size:22px;font-weight:700;margin-bottom:20px;padding-bottom:8px;border-bottom:2px solid #F3F4F6;">{section['title']}</h2>
            {items_html}
        </section>'''

    intro_html = "\n".join(f"<p style='font-size:16px;color:#4B5563;line-height:1.7;margin-bottom:12px;'>{p.strip()}</p>" for p in data["intro"].split("\n\n") if p.strip())

    body = f'''
    <div style="max-width:760px;margin:0 auto;padding:40px 24px 80px;">
        <nav style="font-size:13px;color:#6B7280;margin-bottom:24px;" aria-label="Breadcrumb">
            <a href="/" style="text-decoration:none;">Home</a> &rsaquo; <span>{data['title']}</span>
        </nav>

        <h1 style="font-size:32px;font-weight:700;line-height:1.2;margin-bottom:20px;letter-spacing:-0.5px;">{data['title']}</h1>

        <div style="margin-bottom:40px;">
            {intro_html}
        </div>

        {sections_html}

        <div style="margin-top:48px;padding:32px;background:#F9FAFB;border-radius:12px;border:1px solid #E5E7EB;">
            <h2 style="font-size:18px;font-weight:600;margin-bottom:12px;">How We Curated This List</h2>
            <p style="font-size:14px;color:#6B7280;line-height:1.7;">Three criteria. First, does this resource teach you something you can't learn from a Google search? Second, is it actively maintained and producing new content? Third, do practitioners in the role actually recommend it to peers? We don't accept payment for listings. We review and update this page quarterly.</p>
        </div>

        <p style="margin-top:32px;font-size:14px;color:#6B7280;">
            This page is part of <a href="https://thegtmindex.com/sales-enablement/" style="color:#DC2626;text-decoration:underline;">The GTM Index</a>, a cross-site directory of curated resources for go-to-market professionals.
        </p>
    </div>'''

    schema = f'''    <script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@graph": [{"@type": "ItemList", "name": data["title"], "description": data["description"], "numberOfItems": len(schema_items), "itemListElement": schema_items}, {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://senablers.com"}, {"@type": "ListItem", "position": 2, "name": data["title"], "item": data["canonical"]}]}]}, indent=2)}
    </script>
'''
    return body, schema


def main():
    data = RESOURCE_DATA
    body, schema = build_body_content(data)

    page = get_page_wrapper(
        data["title"],
        data["description"],
        f"/{data['slug']}/",
        body,
        extra_head=schema,
    )

    # Replace self-canonical with cross-site canonical
    page = page.replace(
        f'<link rel="canonical" href="https://senablers.com/{data["slug"]}/">',
        f'<link rel="canonical" href="{data["canonical"]}">'
    )

    write_page(f"{data['slug']}/index.html", page)
    print(f"  Built: {data['slug']}/index.html")


if __name__ == "__main__":
    main()
