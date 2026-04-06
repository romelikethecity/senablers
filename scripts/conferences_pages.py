# scripts/conferences_pages.py
# Conference index page generator for SEnablers.

import os
import json

from nav_config import SITE_NAME, SITE_URL, CURRENT_YEAR
from templates import (get_page_wrapper, write_page, get_breadcrumb_schema,
                       breadcrumb_html, newsletter_cta_html)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def load_conferences():
    with open(os.path.join(DATA_DIR, "conferences.json"), "r") as f:
        return json.load(f)


def build_conferences_index():
    """Build /conferences/ index page."""
    conferences = load_conferences()
    role = "Sales Enablement"
    title = f"Best {role} Conferences in {CURRENT_YEAR}"
    description = (
        f"Top {len(conferences)} conferences for sales enablement professionals in {CURRENT_YEAR}. "
        f"Events covering content management, training, coaching, and revenue enablement strategy."
    )

    crumbs = [("Home", "/"), ("Conferences", None)]
    bc_schema = get_breadcrumb_schema([("Home", "/"), (f"{role} Conferences", f"{SITE_URL}/conferences/")])
    bc_html = breadcrumb_html(crumbs)

    cards_html = ""
    for conf in conferences:
        tags_html = "".join(
            f'<span class="conference-tag">{tag}</span>' for tag in conf["relevance_tags"][:4]
        )
        attendees = f"{conf['typical_attendees']:,}" if conf['typical_attendees'] else "TBA"
        cards_html += f'''<div class="conference-card">
    <div class="conference-card-header">
        <h3><a href="{conf['website_url']}" target="_blank" rel="noopener">{conf['name']}</a></h3>
        <span class="conference-organizer">by {conf['organizer']}</span>
    </div>
    <p class="conference-description">{conf['description']}</p>
    <div class="conference-meta">
        <span class="conference-location">{conf['location']}</span>
        <span class="conference-attendees">{attendees} typical attendees</span>
    </div>
    <div class="conference-tags">{tags_html}</div>
    <a href="{conf['website_url']}" target="_blank" rel="noopener" class="conference-link">Visit website</a>
</div>
'''

    body = f'''{bc_html}
<section class="page-header">
    <h1>{title}</h1>
    <p class="page-subtitle">Where enablement professionals learn what works, discover new tools, and connect with peers building the function.</p>
</section>

<section class="content-section">
    <div class="content-body">
        <p>Sales enablement has grown from a support function into a strategic discipline that sits at the center of revenue organizations. The shift from "sales enablement" to "revenue enablement" reflects a broader mandate that now includes onboarding, continuous learning, content management, coaching, and cross-functional alignment. Conferences are where this evolution happens in real time.</p>

        <p>The enablement conference landscape has expanded to match the function's growing scope. You can now find events dedicated specifically to enablement strategy, platform-specific user conferences from vendors like Seismic and Highspot, and broader sales and learning events with strong enablement tracks. The best practitioners attend a mix to stay well-rounded.</p>

        <p>We selected the {len(conferences)} conferences below based on their relevance to sales enablement and revenue enablement professionals in {CURRENT_YEAR}. Each event earns its place through content quality, speaker credibility, and the value of the peer connections you can make.</p>

        <h2>What Sets Great Enablement Conferences Apart</h2>
        <p>The best enablement events balance strategy with execution. You should leave with both a clearer vision of where the function is heading and specific tactics you can implement when you get back to your desk. Look for events with practitioner-led sessions, not just analyst presentations. The people running enablement programs daily have insights that outside observers simply cannot provide.</p>

        <p>Platform-specific events from Seismic, Highspot, and other vendors are particularly valuable if you use those tools. You will learn advanced features, connect with power users, and often influence the product roadmap directly through feedback sessions. Broader events like ATD and TSIA World give you perspective from adjacent disciplines like learning design and customer education that strengthen your enablement practice.</p>

        <h2>Top {role} Conferences in {CURRENT_YEAR}</h2>
    </div>
</section>

<section class="conferences-grid">
    {cards_html}
</section>

<section class="content-section">
    <div class="content-body">
        <h2>Building Your Conference Strategy</h2>
        <p>Enablement professionals are in a unique position at conferences because the skills you use daily, like designing learning experiences, facilitating knowledge transfer, and measuring behavior change, are exactly the skills that help you extract maximum value from events. Apply your own enablement lens to your conference experience.</p>

        <p>Set learning objectives before you go. Take structured notes during sessions. Synthesize your takeaways into an internal brief for your team when you return. Treat conference attendance the same way you would treat any other learning investment: with clear goals, active participation, and a plan for applying what you learn.</p>
    </div>
</section>

{newsletter_cta_html("Get conference recaps and enablement insights delivered weekly.")}
'''

    page = get_page_wrapper(
        title=title,
        description=description,
        canonical_path="/conferences/",
        body_content=body,
        active_path="/conferences/",
        extra_head=bc_schema,
    )
    write_page("/conferences/index.html", page)
    print(f"  Built: /conferences/ ({len(conferences)} conferences)")
