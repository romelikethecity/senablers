# scripts/nav_config.py
# Site constants, navigation, and footer configuration.
# Pure data — zero logic, zero imports.

SITE_NAME = "SEnablers"
SITE_URL = "https://senablers.com"
SITE_TAGLINE = "Career intelligence for sales enablement professionals"
COPYRIGHT_YEAR = "2026"
CURRENT_YEAR = 2026
CSS_VERSION = "1"

CTA_HREF = "/newsletter/"
CTA_LABEL = "Get the Weekly Brief"

SIGNUP_WORKER_URL = "https://se-newsletter-signup.rome-workers.workers.dev/subscribe"

GA_MEASUREMENT_ID = ""
GOOGLE_SITE_VERIFICATION = ""  # Set to verification filename (e.g., "google1234abcd.html") to generate file
GOOGLE_SITE_VERIFICATION_META = ""  # Set to verification code for meta tag method (alternative to HTML file)

NAV_ITEMS = [
    {
        "href": "/salary/",
        "label": "Salary Data",
        "children": [
            {"href": "/salary/", "label": "Salary Index"},
            {"href": "/salary/by-seniority/", "label": "By Seniority"},
            {"href": "/salary/by-location/", "label": "By Location"},
            {"href": "/salary/comparisons/", "label": "Comparisons"},
            {"href": "/salary/calculator/", "label": "Salary Calculator"},
        ],
    },
    {
        "href": "/tools/",
        "label": "Tools",
        "children": [
            {"href": "/tools/", "label": "Tools Index"},
            {"href": "/tools/category/content-management/", "label": "Tool Categories"},
            {"href": "/tools/highspot-review/", "label": "Tool Reviews"},
        ],
    },
    {
        "href": "/careers/",
        "label": "Careers",
        "children": [
            {"href": "/careers/", "label": "Career Guides"},
            {"href": "/careers/how-to-break-into-enablement/", "label": "Break Into Enablement"},
            {"href": "/careers/job-growth/", "label": "Job Market Growth"},
        ],
    },
    {"href": "/glossary/", "label": "Glossary"},
    {
        "href": "/resources/",
        "label": "Resources",
        "children": [
            {"href": "/comparisons/", "label": "Comparisons"},
            {"href": "/blog/", "label": "Blog"},
            {"href": "/insights/", "label": "Insights"},
            {"href": "/jobs/", "label": "Job Board"},
        ],
    },
]

FOOTER_COLUMNS = {
    "Salary Data": [
        {"href": "/salary/", "label": "Salary Index"},
        {"href": "/salary/by-seniority/", "label": "By Seniority"},
        {"href": "/salary/by-location/", "label": "By Location"},
        {"href": "/salary/comparisons/", "label": "Comparisons"},
        {"href": "/salary/calculator/", "label": "Salary Calculator"},
    ],
    "Resources": [
        {"href": "/tools/", "label": "Enablement Tools"},
        {"href": "/tools/category/content-management/", "label": "Tool Categories"},
        {"href": "/comparisons/", "label": "Comparisons"},
        {"href": "/careers/", "label": "Career Guides"},
        {"href": "/glossary/", "label": "Glossary"},
        {"href": "/jobs/", "label": "Job Board"},
        {"href": "/blog/", "label": "Blog"},
        {"href": "/insights/", "label": "Insights"},
        {"href": "/newsletter/", "label": "Newsletter"},
        {"href": "/about/", "label": "About"},
    ],
    "Site": [
        {"href": "/privacy/", "label": "Privacy Policy"},
        {"href": "/terms/", "label": "Terms of Service"},
    ],
    "Sales Enablement Resources": [
        {"href": "https://gtmepulse.com", "label": "GTME Pulse", "external": True},
        {"href": "https://therevopsreport.com", "label": "RevOps Report", "external": True},
        {"href": "https://b2bsalestools.com", "label": "B2B Sales Tools", "external": True},
        {"href": "https://datastackguide.com", "label": "DataStack Guide", "external": True},
    ],
}
