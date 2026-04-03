# scripts/templates.py
# HTML shell components, schema helpers, and page writer.
# Imports only from nav_config.py. Data flows one direction:
# build.py -> templates.py via function arguments.

import os
import json

from nav_config import *

# Module-level state (set by build.py at startup)
ALL_PAGES = []
OUTPUT_DIR = ""
SKIP_OG = False


# ---------------------------------------------------------------------------
# HTML Head
# ---------------------------------------------------------------------------

def get_html_head(title, description, canonical_path, extra_head="", og_image=""):
    """Generate complete <head> section."""
    canonical = f"{SITE_URL}{canonical_path}"
    full_title = f"{title} - {SITE_NAME}" if title != SITE_NAME else SITE_NAME

    og_image_tags = ""
    twitter_image_tag = ""
    if og_image:
        og_image_url = f"{SITE_URL}{og_image}"
        og_image_tags = f"""
    <meta property="og:image" content="{og_image_url}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">"""
        twitter_image_tag = f'\n    <meta name="twitter:image" content="{og_image_url}">'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#DC2626">
    <title>{full_title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical}">
    <meta name="robots" content="max-snippet:-1, max-image-preview:large, max-video-preview:-1">
{"" if not GOOGLE_SITE_VERIFICATION_META else f'    <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION_META}">'}

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{full_title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="{SITE_NAME}">{og_image_tags}

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{full_title}">
    <meta name="twitter:description" content="{description}">{twitter_image_tag}

    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="/assets/favicons/favicon.svg">
    <link rel="icon" type="image/x-icon" href="/assets/favicons/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicons/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/assets/favicons/apple-touch-icon.png">
    <link rel="manifest" href="/assets/favicons/site.webmanifest">

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Source+Code+Pro:wght@400;500&display=swap" rel="stylesheet">

    <!-- CSS -->
    <link rel="stylesheet" href="/assets/css/tokens.css">
    <link rel="stylesheet" href="/assets/css/components.css?v={CSS_VERSION}">
    <link rel="stylesheet" href="/assets/css/styles.css?v={CSS_VERSION}">
{"" if not GA_MEASUREMENT_ID else f"""
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>"""}
{extra_head}
</head>'''


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def get_nav_html(active_path=""):
    """Generate responsive nav with dropdowns and mobile hamburger."""
    nav_links = ""
    for item in NAV_ITEMS:
        active_class = ' class="active"' if active_path == item["href"] else ""

        if "children" in item:
            # Dropdown nav item
            children_html = ""
            for child in item["children"]:
                child_active = ' class="active"' if active_path == child["href"] else ""
                children_html += f'<li><a href="{child["href"]}"{child_active}>{child["label"]}</a></li>\n'

            nav_links += f'''<li class="nav-item nav-item--dropdown">
    <a href="{item["href"]}"{active_class}>{item["label"]}</a>
    <button class="nav-dropdown-toggle" aria-label="Toggle {item['label']} submenu" aria-expanded="false">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M3 5l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    </button>
    <ul class="nav-dropdown">
        {children_html}
    </ul>
</li>
'''
        else:
            nav_links += f'<li class="nav-item"><a href="{item["href"]}"{active_class}>{item["label"]}</a></li>\n'

    return f'''<nav class="site-nav">
    <div class="nav-container">
        <a href="/" class="nav-brand">
            <svg class="nav-icon" width="28" height="28" viewBox="0 0 48 48"><rect width="48" height="48" rx="11" fill="#DC2626"/><path d="M14 30 L24 20 L34 30" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.45"/><path d="M14 22 L24 12 L34 22" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.75"/><path d="M14 38 L24 28 L34 38" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.25"/></svg>
            <span class="nav-wordmark"><span class="nav-wordmark-name">S</span><span class="nav-wordmark-accent">Enablers</span></span>
        </a>
        <ul class="nav-links">
            {nav_links}
        </ul>
        <a href="{CTA_HREF}" class="btn btn--primary nav-cta">{CTA_LABEL}</a>
        <button class="nav-mobile-toggle" aria-label="Menu">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
    </div>
</nav>'''


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def get_footer_html():
    """Generate multi-column footer with newsletter form and copyright."""
    columns_html = ""
    for col_name, links in FOOTER_COLUMNS.items():
        links_html = ""
        for link in links:
            ext_attrs = ' target="_blank" rel="noopener"' if link.get("external") else ""
            links_html += f'<li><a href="{link["href"]}"{ext_attrs}>{link["label"]}</a></li>\n'
        columns_html += f'''<div class="footer-column">
    <h4>{col_name}</h4>
    <ul>
        {links_html}
    </ul>
</div>
'''

    return f'''<footer class="site-footer">
    <div class="footer-container">
        <div class="footer-grid">
            {columns_html}
            <div class="footer-column footer-newsletter">
                <h4>Stay in the loop</h4>
                <p>Weekly enablement salary data, tool updates, and career moves.</p>
                <form class="footer-newsletter-form" onsubmit="return false;">
                    <input type="email" placeholder="Your email" aria-label="Email address" required>
                    <button type="submit" class="btn btn--primary">Subscribe</button>
                </form>
            </div>
        </div>
        <div class="footer-bottom">
            <span>Copyright {COPYRIGHT_YEAR} {SITE_NAME}. All rights reserved.</span>
            <span>{SITE_TAGLINE}</span>
        </div>
    </div>
</footer>'''


# ---------------------------------------------------------------------------
# Page Wrapper
# ---------------------------------------------------------------------------

def get_page_wrapper(title, description, canonical_path, body_content,
                     active_path="", extra_head="", body_class=""):
    """Assemble a full HTML document."""
    bc = f' class="{body_class}"' if body_class else ""

    # Auto-compute OG image path from canonical_path (skip if OG generation disabled)
    og_image = ""
    if not SKIP_OG:
        og_stem = canonical_path.strip("/").replace("/", "-")
        if og_stem.endswith(".html"):
            og_stem = og_stem[:-5]
        og_image = f"/assets/og/{og_stem}.png" if og_stem else "/assets/og/index.png"

    head = get_html_head(title, description, canonical_path, extra_head, og_image=og_image)
    nav = get_nav_html(active_path)
    footer = get_footer_html()

    inline_js = f'''<script>
(function(){{
    // Mobile nav toggle
    var toggle = document.querySelector('.nav-mobile-toggle');
    var links = document.querySelector('.nav-links');
    if (toggle && links) {{
        toggle.addEventListener('click', function() {{
            links.classList.toggle('open');
            toggle.classList.toggle('open');
        }});
    }}
    // Dropdown toggles
    var dropdowns = document.querySelectorAll('.nav-dropdown-toggle');
    dropdowns.forEach(function(btn) {{
        btn.addEventListener('click', function(e) {{
            e.preventDefault();
            e.stopPropagation();
            var parent = btn.closest('.nav-item--dropdown');
            if (parent) {{
                parent.classList.toggle('open');
                btn.setAttribute('aria-expanded',
                    parent.classList.contains('open') ? 'true' : 'false');
            }}
        }});
    }});
    // Newsletter signup
    var SIGNUP_URL = '{SIGNUP_WORKER_URL}';
    document.querySelectorAll('.hero-signup, .footer-newsletter-form, .newsletter-cta-form').forEach(function(form) {{
        form.onsubmit = function(e) {{
            e.preventDefault();
            var emailInput = form.querySelector('input[type="email"]');
            var btn = form.querySelector('button');
            var email = emailInput ? emailInput.value.trim() : '';
            if (!email) return;
            var origText = btn.textContent;
            btn.textContent = 'Subscribing...';
            btn.disabled = true;
            fetch(SIGNUP_URL, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{email: email, list: 'senablers'}})
            }})
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
                if (data.success) {{
                    if (typeof gtag === 'function') {{ gtag('event', 'newsletter_signup', {{'event_category': 'engagement', 'event_label': email}}); }}
                    form.innerHTML = '<p style="color: var(--se-accent); font-weight: 600;">You\\\'re in! Check your inbox.</p>';
                }} else {{
                    btn.textContent = origText;
                    btn.disabled = false;
                    var err = document.createElement('p');
                    err.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 0.5rem;';
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
                var err = document.createElement('p');
                err.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 0.5rem;';
                err.textContent = 'Connection error. Please try again.';
                var existing = form.querySelector('.signup-error');
                if (existing) existing.remove();
                err.className = 'signup-error';
                form.appendChild(err);
            }});
        }};
    }});
}})();
</script>'''

    return f'''{head}
<body{bc}>
{nav}
<main class="main-content">
{body_content}
</main>
{footer}
{inline_js}
</body>
</html>'''


# ---------------------------------------------------------------------------
# Page Writer
# ---------------------------------------------------------------------------

def write_page(rel_path, content):
    """Write an HTML file and register it for sitemap."""
    full_path = os.path.join(OUTPUT_DIR, rel_path.lstrip("/"))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    ALL_PAGES.append(rel_path)


# ---------------------------------------------------------------------------
# Schema Helpers
# ---------------------------------------------------------------------------

def get_homepage_schema():
    """Generate Organization + WebSite @graph schema for homepage."""
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "name": SITE_NAME,
                "url": SITE_URL,
                "description": SITE_TAGLINE,
                "logo": f"{SITE_URL}/assets/logos/icon-mark.svg",
            },
            {
                "@type": "WebSite",
                "name": SITE_NAME,
                "url": SITE_URL,
                "description": SITE_TAGLINE,
            },
        ],
    }
    return f'    <script type="application/ld+json">{json.dumps(schema)}</script>\n'


def get_breadcrumb_schema(items):
    """Generate BreadcrumbList JSON-LD. items = [(label, url), ...]"""
    list_items = []
    for i, (label, url) in enumerate(items, 1):
        item = {"@type": "ListItem", "position": i, "name": label}
        if url:
            item["item"] = f"{SITE_URL}{url}"
        list_items.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": list_items,
    }
    return f'    <script type="application/ld+json">{json.dumps(schema)}</script>\n'


def get_faq_schema(qa_pairs):
    """Generate FAQPage JSON-LD. qa_pairs = [(question, answer), ...]"""
    entities = []
    for question, answer in qa_pairs:
        entities.append({
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": answer,
            },
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }
    return f'    <script type="application/ld+json">{json.dumps(schema)}</script>\n'


def get_software_application_schema(tool_data):
    """Generate SoftwareApplication JSON-LD for tool review pages."""
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": tool_data["name"],
        "description": tool_data.get("description", ""),
        "applicationCategory": tool_data.get("category", "BusinessApplication"),
        "operatingSystem": tool_data.get("os", "Web"),
        "url": tool_data.get("url", ""),
        "offers": {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": tool_data.get("price_range", "Contact for pricing"),
            "description": tool_data.get("price_range", "Contact for pricing"),
        },
    }
    rating = tool_data.get("rating")
    if rating:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(rating["value"]),
            "ratingCount": str(rating["count"]),
            "bestRating": "5",
            "worstRating": "1",
        }
    return f'    <script type="application/ld+json">{json.dumps(schema)}</script>\n'


def get_article_schema(title, description, slug, date_published, word_count):
    """Generate Article JSON-LD for insight articles."""
    url = f"{SITE_URL}/insights/{slug}/"
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "wordCount": word_count,
        "author": {
            "@type": "Person",
            "name": "Rome Thorndike",
            "url": f"{SITE_URL}/about/",
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL,
        },
        "datePublished": date_published,
        "dateModified": date_published,
        "url": url,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url,
        },
    }
    return f'    <script type="application/ld+json">{json.dumps(schema)}</script>\n'


# ---------------------------------------------------------------------------
# Visual Component Helpers
# ---------------------------------------------------------------------------

def breadcrumb_html(crumbs):
    """Generate visual breadcrumb. crumbs = [(label, url), ...] last item is current page."""
    parts = []
    for i, (label, url) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            parts.append(f'<span class="breadcrumb-current">{label}</span>')
        else:
            parts.append(f'<a href="{url}" class="breadcrumb-link">{label}</a>'
                         f'<span class="breadcrumb-sep">/</span>')
    return f'<nav class="breadcrumb" aria-label="Breadcrumb">{"".join(parts)}</nav>'


def faq_html(qa_pairs):
    """Render visible FAQ section. qa_pairs = [(question, answer), ...]"""
    items = ""
    for q, a in qa_pairs:
        items += f'''<div class="faq-item">
    <h3 class="faq-question">{q}</h3>
    <p class="faq-answer">{a}</p>
</div>
'''
    return f'''<section class="faq-section">
    <h2>Frequently Asked Questions</h2>
    {items}
</section>'''


def newsletter_cta_html(context=""):
    """Email capture block. JS handler wired via get_page_wrapper inline script."""
    ctx_text = f" {context}" if context else ""
    return f'''<section class="newsletter-cta">
    <h2>Get the Weekly Brief</h2>
    <p>Salary data, tool updates, and career moves for enablement professionals.{ctx_text}</p>
    <form class="newsletter-cta-form" onsubmit="return false;">
        <input type="email" placeholder="Your email" aria-label="Email address" required>
        <button type="submit" class="btn btn--primary">Subscribe</button>
    </form>
</section>'''


def definition_block(term, definition):
    """Glossary-style definition block."""
    return f'''<div class="definition-block">
    <h3 class="definition-term">{term}</h3>
    <p class="definition-text">{definition}</p>
</div>'''
