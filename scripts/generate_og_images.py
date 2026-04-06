# scripts/generate_og_images.py
# Playwright-based OG image generator for SEnablers.
# Renders HTML templates at 1200x630 and screenshots to PNG.
#
# Usage:
#   from generate_og_images import generate_og_images, og_filename_from_path, og_template_for_path
#   generate_og_images(pages_data, output_dir, templates_dir)
#
# Or run standalone:
#   python3 scripts/generate_og_images.py

import os
import time
import html as html_module


def og_filename_from_path(rel_path):
    """Convert a page rel_path to an OG image filename.

    Examples:
        salary/junior/index.html -> salary-junior.png
        index.html -> index.png
        tools/clay-review/index.html -> tools-clay-review.png
        glossary/api/index.html -> glossary-api.png
    """
    # Strip index.html suffix
    stem = rel_path.replace("/index.html", "").replace("index.html", "")
    # Strip any remaining .html extension (e.g. 404.html -> 404)
    if stem.endswith(".html"):
        stem = stem[:-5]
    # Strip trailing slash
    stem = stem.strip("/")
    # Replace path separators with hyphens
    if stem:
        return stem.replace("/", "-") + ".png"
    return "index.png"


def og_template_for_path(rel_path):
    """Map a page rel_path to the appropriate OG template name.

    Returns template name (without .html extension).
    """
    if rel_path.startswith("salary/"):
        return "og-salary"
    if rel_path.startswith("tools/"):
        return "og-tool"
    if rel_path.startswith("insights/") or rel_path.startswith("blog/"):
        return "og-default"
    if rel_path.startswith("glossary/"):
        return "og-glossary"
    return "og-default"


def _og_category_for_path(rel_path):
    """Determine the {{CATEGORY}} value for tool pages."""
    if "-vs-" in rel_path:
        return "COMPARISON"
    if "-alternatives" in rel_path:
        return "ALTERNATIVES"
    if "best-" in rel_path:
        return "ROUNDUP"
    if "-review" in rel_path:
        return "TOOL REVIEW"
    if "category/" in rel_path:
        return "TOOL CATEGORY"
    return "TOOLS"


def generate_og_images(pages_data, output_dir, templates_dir, skip=False):
    """Generate OG images for all pages.

    Args:
        pages_data: list of dicts with keys:
            rel_path, title, subtitle, template, og_filename
        output_dir: path to output/ directory
        templates_dir: path to og-templates/ directory
        skip: if True, skip generation and return early
    """
    if skip:
        print("  Skipping OG image generation")
        return

    if not pages_data:
        print("  No pages to generate OG images for")
        return

    start = time.time()

    # Ensure output directory exists
    og_dir = os.path.join(output_dir, "assets", "og")
    os.makedirs(og_dir, exist_ok=True)

    # Load all template HTML files
    template_cache = {}
    for fname in os.listdir(templates_dir):
        if fname.endswith(".html") and fname.startswith("og-"):
            tpl_name = fname.replace(".html", "")
            with open(os.path.join(templates_dir, fname), "r", encoding="utf-8") as f:
                template_cache[tpl_name] = f.read()

    if not template_cache:
        print("  WARNING: No OG templates found in", templates_dir)
        return

    # Import Playwright here so the module can be imported without it installed
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})

        for i, page_info in enumerate(pages_data):
            template_name = page_info.get("template", "og-default")
            template_html = template_cache.get(template_name, template_cache.get("og-default", ""))

            if not template_html:
                continue

            # Escape HTML entities in title/subtitle for safe injection
            title = html_module.escape(page_info.get("title", "SEnablers"))
            subtitle = html_module.escape(page_info.get("subtitle", ""))
            category = page_info.get("category", "")

            # Auto-compute category for tool pages if not provided
            if not category and template_name == "og-tool":
                category = _og_category_for_path(page_info.get("rel_path", ""))

            # Replace placeholders
            rendered = template_html.replace("{{TITLE}}", title)
            rendered = rendered.replace("{{SUBTITLE}}", subtitle)
            rendered = rendered.replace("{{CATEGORY}}", category)

            og_path = os.path.join(og_dir, page_info["og_filename"])
            page.set_content(rendered, wait_until="networkidle")
            page.screenshot(path=og_path)

            # Progress indicator every 50 pages
            if (i + 1) % 50 == 0:
                print(f"    Generated {i + 1}/{len(pages_data)} OG images...")

        browser.close()

    elapsed = time.time() - start
    print(f"  Generated {len(pages_data)} OG images in {elapsed:.1f}s")


if __name__ == "__main__":
    """Standalone test: generate OG images for a small test set."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    templates_dir = os.path.join(project_dir, "og-templates")
    output_dir = os.path.join(project_dir, "output")

    # Create output dir if needed
    os.makedirs(os.path.join(output_dir, "assets", "og"), exist_ok=True)

    test_pages = [
        {
            "rel_path": "index.html",
            "title": "SEnablers",
            "subtitle": "Career intelligence and industry data",
            "template": "og-default",
            "og_filename": "index.png",
        },
        {
            "rel_path": "salary/junior/index.html",
            "title": "Junior Salary Guide",
            "subtitle": "$85K-$120K",
            "template": "og-salary",
            "og_filename": "salary-junior.png",
        },
        {
            "rel_path": "tools/example-review/index.html",
            "title": "Example Tool Review 2026",
            "subtitle": "Category and use case overview",
            "template": "og-tool",
            "og_filename": "tools-example-review.png",
            "category": "TOOL REVIEW",
        },
        {
            "rel_path": "glossary/example-term/index.html",
            "title": "What is Example Term?",
            "subtitle": "Clear definition with real examples",
            "template": "og-glossary",
            "og_filename": "glossary-example-term.png",
        },
    ]

    print("=== OG Image Test Generation ===")
    generate_og_images(test_pages, output_dir, templates_dir)
    print("Done! Check output/assets/og/")
