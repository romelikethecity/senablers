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


# ---------------------------------------------------------------------------
# Load real data from JSON
# ---------------------------------------------------------------------------

def load_comp_data():
    """Load comp_analysis.json and return parsed dict."""
    path = os.path.join(DATA_DIR, "comp_analysis.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_market_data():
    """Load market_intelligence.json and return parsed dict."""
    path = os.path.join(DATA_DIR, "market_intelligence.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

COMP_DATA = load_comp_data()
MARKET_DATA = load_market_data()

# Real salary data from comp_analysis.json
SALARY_BY_SENIORITY = {
    "entry": {
        "label": "Entry Level",
        "slug": "entry",
        "min": int(COMP_DATA["by_seniority"]["Entry"]["min_base_avg"]),
        "max": int(COMP_DATA["by_seniority"]["Entry"]["max_base_avg"]),
        "median": int(COMP_DATA["by_seniority"]["Entry"]["median"]),
        "count": COMP_DATA["by_seniority"]["Entry"]["count"],
    },
    "mid": {
        "label": "Mid-Level",
        "slug": "mid-level",
        "min": int(COMP_DATA["by_seniority"]["Mid"]["min_base_avg"]),
        "max": int(COMP_DATA["by_seniority"]["Mid"]["max_base_avg"]),
        "median": int(COMP_DATA["by_seniority"]["Mid"]["median"]),
        "count": COMP_DATA["by_seniority"]["Mid"]["count"],
    },
    "senior": {
        "label": "Senior",
        "slug": "senior",
        "min": int(COMP_DATA["by_seniority"]["Senior"]["min_base_avg"]),
        "max": int(COMP_DATA["by_seniority"]["Senior"]["max_base_avg"]),
        "median": int(COMP_DATA["by_seniority"]["Senior"]["median"]),
        "count": COMP_DATA["by_seniority"]["Senior"]["count"],
    },
    "director": {
        "label": "Director / VP",
        "slug": "director-vp",
        "min": int(COMP_DATA["by_seniority"]["Director"]["min_base_avg"]),
        "max": int(COMP_DATA["by_seniority"]["Director"]["max_base_avg"]),
        "median": int(COMP_DATA["by_seniority"]["Director"]["median"]),
        "count": COMP_DATA["by_seniority"]["Director"]["count"],
    },
}

SALARY_BY_METRO = {}
for metro, data in COMP_DATA["by_metro"].items():
    if metro == "Unknown":
        continue
    SALARY_BY_METRO[metro] = {
        "label": metro,
        "slug": metro.lower().replace(" ", "-"),
        "min": int(data["min_base_avg"]),
        "max": int(data["max_base_avg"]),
        "median": int(data["median"]),
        "count": data["count"],
    }

SALARY_BY_REMOTE = COMP_DATA["by_remote"]
SALARY_STATS = COMP_DATA["salary_stats"]
TOP_PAYING = COMP_DATA["top_paying_roles"]

# ---------------------------------------------------------------------------
# Tool data — curated enablement tools with real mention counts
# ---------------------------------------------------------------------------

TOOL_MENTIONS = MARKET_DATA.get("tools", {})

TOOL_DATABASE = {
    # Content Management
    "highspot": {
        "name": "Highspot", "slug": "highspot",
        "category": "content-management", "category_label": "Content Management",
        "mentions": TOOL_MENTIONS.get("Highspot", 0),
        "tagline": "The leading sales enablement platform for content management, guided selling, and analytics.",
        "founded": "2012", "hq": "Seattle, WA", "employees": "800+",
        "pricing": "Custom enterprise pricing (typically $50-75/user/mo)",
        "url": "https://www.highspot.com",
        "best_for": "Mid-market and enterprise teams needing unified content management with analytics",
        "strengths": ["Content management and AI-powered search", "Sales play and guided selling workflows", "Analytics and content performance tracking", "CRM integration (Salesforce, Dynamics)", "Pitch intelligence and buyer engagement"],
        "weaknesses": ["Premium pricing limits SMB adoption", "Implementation can take 2-3 months", "Advanced features require training", "Limited free trial availability"],
        "verdict": "Highspot is the category leader in sales enablement content management. With 22 mentions across 219 job postings in our data, it is the most-requested enablement platform. Best suited for teams of 50+ reps who need centralized content, guided selling, and engagement analytics.",
        "rating": {"value": 4.6, "count": 850},
    },
    "seismic": {
        "name": "Seismic", "slug": "seismic",
        "category": "content-management", "category_label": "Content Management",
        "mentions": TOOL_MENTIONS.get("Seismic", 0),
        "tagline": "Enterprise enablement platform combining content automation, training, and analytics.",
        "founded": "2010", "hq": "San Diego, CA", "employees": "1,500+",
        "pricing": "Custom enterprise pricing (typically $60-85/user/mo)",
        "url": "https://www.seismic.com",
        "best_for": "Large enterprise teams with complex content workflows and compliance requirements",
        "strengths": ["Content automation and dynamic assembly", "LiveDocs for personalized content at scale", "Seismic Learning (formerly Lessonly) integration", "Strong compliance and governance controls", "Deep analytics and attribution"],
        "weaknesses": ["Higher price point than most competitors", "Steep learning curve for administrators", "Can be over-engineered for smaller teams", "Content migration from legacy systems is complex"],
        "verdict": "Seismic is the enterprise heavyweight in enablement. Its content automation engine and compliance controls make it the default for regulated industries. The Lessonly acquisition adds training capabilities. Best for organizations with 200+ reps and complex content needs.",
        "rating": {"value": 4.4, "count": 720},
    },
    "showpad": {
        "name": "Showpad", "slug": "showpad",
        "category": "content-management", "category_label": "Content Management",
        "mentions": TOOL_MENTIONS.get("Showpad", 0),
        "tagline": "Content management and coaching platform built for manufacturing, life sciences, and B2B sales.",
        "founded": "2011", "hq": "Ghent, Belgium / Chicago, IL", "employees": "500+",
        "pricing": "Custom pricing (typically $35-55/user/mo)",
        "url": "https://www.showpad.com",
        "best_for": "Manufacturing and life sciences companies with field sales teams",
        "strengths": ["Strong vertical expertise (manufacturing, life sciences)", "Content management with offline access", "Coaching and training modules", "Interactive content experiences (3D, AR)", "European data compliance (GDPR native)"],
        "weaknesses": ["Smaller market share than Highspot/Seismic", "Analytics less mature than category leaders", "Limited conversation intelligence", "Fewer native integrations than competitors"],
        "verdict": "Showpad carved out a defensible niche in manufacturing and life sciences enablement. The offline access, interactive content, and GDPR-native architecture make it the go-to for European and field-heavy sales orgs. Less dominant in pure tech sales.",
        "rating": {"value": 4.3, "count": 480},
    },
    "bigtincan": {
        "name": "Bigtincan", "slug": "bigtincan",
        "category": "content-management", "category_label": "Content Management",
        "mentions": 0,
        "tagline": "AI-powered content management and sales engagement for enterprises with complex buyer journeys.",
        "founded": "2011", "hq": "Waltham, MA", "employees": "300+",
        "pricing": "Custom pricing (starting ~$30/user/mo)",
        "url": "https://www.bigtincan.com",
        "best_for": "Enterprise teams with document-heavy sales processes and large content libraries",
        "strengths": ["AI-powered content recommendations", "Document automation and generation", "Acquired ClearSlide and Brainshark capabilities", "Strong mobile experience", "Content hub with intelligent search"],
        "weaknesses": ["Multiple acquisitions created fragmented UX", "Less brand recognition than Highspot/Seismic", "Integration complexity from merged products", "Support quality varies by region"],
        "verdict": "Bigtincan has assembled a broad enablement suite through acquisitions (ClearSlide, Brainshark, Agnitio). The AI content engine is genuinely strong, but the product experience can feel stitched together. Worth evaluating if you need document automation at scale.",
        "rating": {"value": 4.0, "count": 290},
    },
    "guru": {
        "name": "Guru", "slug": "guru",
        "category": "content-management", "category_label": "Content Management",
        "mentions": 0,
        "tagline": "Knowledge management platform that brings verified company information to every conversation.",
        "founded": "2015", "hq": "Philadelphia, PA", "employees": "200+",
        "pricing": "Free tier; paid from $10/user/mo",
        "url": "https://www.getguru.com",
        "best_for": "Teams needing real-time knowledge access during calls and meetings",
        "strengths": ["Browser extension and Slack integration", "AI-powered knowledge suggestions", "Verification workflows keep content current", "Low price point and free tier", "Fast implementation (days, not months)"],
        "weaknesses": ["Not a full enablement platform (no guided selling)", "Limited analytics compared to Highspot/Seismic", "Content management less robust for large libraries", "More knowledge base than sales enablement"],
        "verdict": "Guru sits at the intersection of knowledge management and sales enablement. It is not a direct Highspot competitor but fills a specific gap: getting the right information to reps in real time. Great as a complement to a larger enablement stack, or as a starting point for small teams.",
        "rating": {"value": 4.5, "count": 610},
    },
    # Training Platforms
    "mindtickle": {
        "name": "Mindtickle", "slug": "mindtickle",
        "category": "training", "category_label": "Training & Readiness",
        "mentions": TOOL_MENTIONS.get("Mindtickle", 0) + TOOL_MENTIONS.get("Mindtickle Training", 0),
        "tagline": "Sales readiness platform combining training, coaching, and conversation intelligence.",
        "founded": "2012", "hq": "San Francisco, CA", "employees": "600+",
        "pricing": "Custom pricing (typically $30-50/user/mo)",
        "url": "https://www.mindtickle.com",
        "best_for": "Organizations building structured onboarding and ongoing readiness programs",
        "strengths": ["Comprehensive readiness and certification programs", "AI-driven coaching and role-play", "Conversation intelligence built in", "Sales competency tracking and scoring", "Strong onboarding automation"],
        "weaknesses": ["Primarily training-focused, weaker on content management", "Can be complex to configure initially", "Pricing not transparent", "Overlaps with conversation intelligence tools"],
        "verdict": "Mindtickle is the strongest pure-play readiness platform. With 6 mentions across job postings, it shows consistent demand. The combination of training, coaching, and conversation intelligence makes it a one-stop shop for sales readiness, though content management requires a separate tool.",
        "rating": {"value": 4.4, "count": 520},
    },
    "gong": {
        "name": "Gong", "slug": "gong",
        "category": "conversation-intelligence", "category_label": "Conversation Intelligence",
        "mentions": TOOL_MENTIONS.get("Gong", 0) + TOOL_MENTIONS.get("Gong Engage", 0),
        "tagline": "Revenue intelligence platform built on conversation data, deal analytics, and AI coaching.",
        "founded": "2015", "hq": "San Francisco, CA", "employees": "1,200+",
        "pricing": "Custom pricing (typically $100-150/user/mo)",
        "url": "https://www.gong.io",
        "best_for": "Sales orgs that want data-driven coaching and deal visibility from call recordings",
        "strengths": ["Industry-leading conversation AI and transcription", "Deal intelligence and pipeline analytics", "Coaching workflows with AI insights", "Massive integration ecosystem", "Gong Engage for sequencing and outreach"],
        "weaknesses": ["Premium pricing makes it expensive at scale", "Privacy concerns in some regulated industries", "Can create surveillance perception among reps", "Requires consistent call recording adoption"],
        "verdict": "Gong is the dominant conversation intelligence platform with 15 mentions in our data. It has expanded beyond call recording into full revenue intelligence. The data moat from millions of recorded conversations powers genuinely differentiated AI. Essential for data-driven sales orgs, but the price tag and privacy considerations are real.",
        "rating": {"value": 4.7, "count": 1100},
    },
    "lessonly": {
        "name": "Lessonly (Seismic Learning)", "slug": "lessonly",
        "category": "training", "category_label": "Training & Readiness",
        "mentions": TOOL_MENTIONS.get("Lessonly", 0) + TOOL_MENTIONS.get("Lessonly Training", 0),
        "tagline": "Simple, intuitive training platform now integrated into the Seismic enablement suite.",
        "founded": "2012", "hq": "Indianapolis, IN (now Seismic)", "employees": "Part of Seismic",
        "pricing": "Available as Seismic Learning or standalone (from $25/user/mo)",
        "url": "https://www.seismic.com/seismic-learning/",
        "best_for": "Teams that want easy-to-build training content without a complex LMS",
        "strengths": ["Drag-and-drop lesson builder", "Practice and coaching workflows", "Fast implementation and onboarding", "Now benefits from Seismic's content engine", "Strong user adoption rates"],
        "weaknesses": ["Acquired by Seismic, standalone future uncertain", "Less advanced than Mindtickle for readiness", "Limited conversation intelligence", "Analytics less sophisticated than competitors"],
        "verdict": "Lessonly (now Seismic Learning) pioneered accessible sales training. The product is genuinely easy to use, which drives adoption. The Seismic acquisition adds content management muscle but creates uncertainty for standalone buyers. Still a strong choice for training-first use cases.",
        "rating": {"value": 4.5, "count": 580},
    },
    "saleshood": {
        "name": "SalesHood", "slug": "saleshood",
        "category": "training", "category_label": "Training & Readiness",
        "mentions": 0,
        "tagline": "Sales enablement platform focused on training, coaching, and content sharing for growing teams.",
        "founded": "2013", "hq": "San Francisco, CA", "employees": "50+",
        "pricing": "From $50/user/mo",
        "url": "https://www.saleshood.com",
        "best_for": "Mid-market companies building their first structured enablement program",
        "strengths": ["All-in-one training, content, and coaching", "Mutual action plans and buyer engagement", "Video coaching and practice tools", "Competitive pricing vs enterprise platforms", "Quick deployment for mid-market"],
        "weaknesses": ["Smaller company with less investment than leaders", "Fewer integrations than Highspot/Seismic", "Not well-known outside enablement circles", "Limited analyst coverage"],
        "verdict": "SalesHood is a mid-market alternative to the enterprise enablement platforms. The all-in-one approach (training + content + coaching) appeals to teams that want one platform instead of three. Less proven at enterprise scale but strong value for 50-200 rep organizations.",
        "rating": {"value": 4.2, "count": 180},
    },
    "brainshark": {
        "name": "Brainshark", "slug": "brainshark",
        "category": "training", "category_label": "Training & Readiness",
        "mentions": TOOL_MENTIONS.get("Brainshark", 0) + TOOL_MENTIONS.get("Brainshark Training", 0),
        "tagline": "Sales readiness platform for video coaching, training, and content authoring.",
        "founded": "1999", "hq": "Waltham, MA (now Bigtincan)", "employees": "Part of Bigtincan",
        "pricing": "Custom pricing (contact Bigtincan)",
        "url": "https://www.bigtincan.com/products/readiness/",
        "best_for": "Organizations that need video-based coaching and training at scale",
        "strengths": ["Video coaching and practice at scale", "Presentation-to-video content authoring", "Sales scorecard and readiness reporting", "Long track record (25+ years)", "Now combined with Bigtincan content engine"],
        "weaknesses": ["Acquired by Bigtincan, product direction evolving", "Dated UI compared to newer competitors", "Less innovative than Mindtickle/Gong", "Unclear standalone product roadmap"],
        "verdict": "Brainshark was a pioneer in video coaching and sales readiness. The Bigtincan acquisition gives it content management capabilities but creates uncertainty. If you are already in the Bigtincan ecosystem, Brainshark's training tools add value. For new buyers, Mindtickle or Lessonly are more modern alternatives.",
        "rating": {"value": 3.9, "count": 340},
    },
    # Digital Sales Rooms
    "aligned": {
        "name": "Aligned", "slug": "aligned",
        "category": "digital-sales-rooms", "category_label": "Digital Sales Rooms",
        "mentions": 0,
        "tagline": "Digital sales rooms that replace email threads with collaborative buyer workspaces.",
        "founded": "2021", "hq": "Tel Aviv, Israel", "employees": "50+",
        "pricing": "Free tier; paid from $49/user/mo",
        "url": "https://www.aligned.com",
        "best_for": "B2B sales teams with complex, multi-stakeholder deal cycles",
        "strengths": ["Clean, modern buyer experience", "Mutual action plans built in", "Real-time buyer engagement analytics", "Free tier for individual reps", "Fast-growing product with frequent updates"],
        "weaknesses": ["Newer company, less proven at scale", "Limited content management vs full platforms", "Fewer integrations than established players", "Not yet a full enablement platform"],
        "verdict": "Aligned is one of the fastest-growing digital sales room platforms. The product focuses on making the buyer experience better, not just giving sellers another tool. The free tier makes it easy to trial. Best for teams selling complex B2B deals with multiple stakeholders.",
        "rating": {"value": 4.6, "count": 120},
    },
    "enableus": {
        "name": "Enable.us (Mediafly)", "slug": "enableus",
        "category": "digital-sales-rooms", "category_label": "Digital Sales Rooms",
        "mentions": 0,
        "tagline": "Digital sales rooms and content sharing platform acquired by Mediafly.",
        "founded": "2020", "hq": "San Francisco, CA (now Mediafly)", "employees": "Part of Mediafly",
        "pricing": "Custom pricing (contact Mediafly)",
        "url": "https://www.mediafly.com",
        "best_for": "Enterprise teams needing digital sales rooms integrated with content management",
        "strengths": ["Purpose-built digital sales rooms", "Content sharing and buyer engagement tracking", "Now integrated with Mediafly's content platform", "Mutual action plans and deal rooms", "Enterprise-grade security"],
        "weaknesses": ["Acquired by Mediafly, integration still evolving", "Less standalone identity", "Fewer reviews than competitors", "Pricing not transparent"],
        "verdict": "Enable.us was an early digital sales room innovator before the Mediafly acquisition. The combined platform adds content management and analytics. Worth evaluating if you are already considering Mediafly, but standalone DSR buyers should also look at Aligned and GetAccept.",
        "rating": {"value": 4.1, "count": 90},
    },
    "getaccept": {
        "name": "GetAccept", "slug": "getaccept",
        "category": "digital-sales-rooms", "category_label": "Digital Sales Rooms",
        "mentions": 0,
        "tagline": "All-in-one digital sales room with e-signatures, proposals, and buyer engagement tracking.",
        "founded": "2015", "hq": "San Francisco, CA / Malmoe, Sweden", "employees": "200+",
        "pricing": "From $25/user/mo",
        "url": "https://www.getaccept.com",
        "best_for": "SMB and mid-market teams that want proposals, e-sign, and deal rooms in one platform",
        "strengths": ["Combines proposals, e-sign, and digital rooms", "Video messaging in proposals", "CPQ integration for quotes", "Affordable pricing for SMBs", "Strong European presence"],
        "weaknesses": ["E-sign less mature than DocuSign", "Content management is basic", "Less enterprise-grade than competitors", "Video features can feel gimmicky"],
        "verdict": "GetAccept bundles digital sales rooms with proposals and e-signatures. The all-in-one approach is compelling for SMBs that do not want three separate tools. The pricing is accessible. For pure DSR functionality at enterprise scale, Aligned or Enable.us may be stronger.",
        "rating": {"value": 4.2, "count": 210},
    },
    "trumpet": {
        "name": "Trumpet", "slug": "trumpet",
        "category": "digital-sales-rooms", "category_label": "Digital Sales Rooms",
        "mentions": 0,
        "tagline": "Digital sales rooms that create personalized buyer microsites for every deal.",
        "founded": "2021", "hq": "London, UK", "employees": "30+",
        "pricing": "Free tier; paid from $36/user/mo",
        "url": "https://www.sendtrumpet.com",
        "best_for": "Sales teams that want branded, personalized buyer experiences without design resources",
        "strengths": ["Beautiful, customizable buyer microsites", "Built-in mutual action plans", "No-code page builder", "Free tier available", "Strong onboarding content features"],
        "weaknesses": ["Early-stage company", "Limited enterprise features", "Fewer integrations than mature platforms", "UK-based, smaller US presence"],
        "verdict": "Trumpet is a UK-based digital sales room startup that punches above its weight on design. The buyer microsites look polished without needing a designer. Early stage means fewer enterprise features, but the free tier and fast iteration make it worth testing for SMB and mid-market teams.",
        "rating": {"value": 4.4, "count": 85},
    },
    "dock": {
        "name": "Dock", "slug": "dock",
        "category": "digital-sales-rooms", "category_label": "Digital Sales Rooms",
        "mentions": 0,
        "tagline": "Client-facing workspaces for sales, onboarding, and customer success teams.",
        "founded": "2021", "hq": "San Francisco, CA", "employees": "30+",
        "pricing": "Free tier; paid from $49/user/mo",
        "url": "https://www.dock.us",
        "best_for": "Revenue teams that need deal rooms and onboarding workspaces in one platform",
        "strengths": ["Spans sales, onboarding, and CS use cases", "Clean, Notion-like workspace builder", "Order forms and e-sign built in", "Content management library", "Strong template system"],
        "weaknesses": ["Newer company, still building enterprise features", "Limited conversation intelligence", "Smaller user base than established platforms", "May try to do too much"],
        "verdict": "Dock extends digital sales rooms into onboarding and customer success. The Notion-like builder is intuitive, and spanning the full customer lifecycle is a smart differentiator. Best for teams that want one workspace tool from first call to renewal.",
        "rating": {"value": 4.5, "count": 95},
    },
    # Conversation Intelligence
    "chorus": {
        "name": "Chorus (ZoomInfo)", "slug": "chorus",
        "category": "conversation-intelligence", "category_label": "Conversation Intelligence",
        "mentions": TOOL_MENTIONS.get("Chorus", 0) + TOOL_MENTIONS.get("Zoominfo", 0),
        "tagline": "Conversation intelligence platform now integrated into ZoomInfo's revenue operating system.",
        "founded": "2015", "hq": "San Francisco, CA (now ZoomInfo)", "employees": "Part of ZoomInfo",
        "pricing": "Bundled with ZoomInfo (contact for pricing)",
        "url": "https://www.zoominfo.com/products/chorus",
        "best_for": "Teams already using ZoomInfo that want conversation intelligence integrated with contact data",
        "strengths": ["Deep integration with ZoomInfo contact data", "Call recording and transcription", "Deal intelligence and pipeline visibility", "Combined signals from conversations + intent data", "Large training data set from ZoomInfo ecosystem"],
        "weaknesses": ["Standalone product identity fading into ZoomInfo", "Gong has stronger brand recognition", "Pricing tied to ZoomInfo bundle", "Less innovation pace than independent competitors"],
        "verdict": "Chorus was Gong's primary competitor before the ZoomInfo acquisition. The integration with ZoomInfo's contact and intent data is a genuine advantage, but the product is increasingly a feature within ZoomInfo rather than a standalone platform. If you use ZoomInfo, it is a natural add. Otherwise, Gong is the category standard.",
        "rating": {"value": 4.3, "count": 640},
    },
    "clari-copilot": {
        "name": "Clari Copilot", "slug": "clari-copilot",
        "category": "conversation-intelligence", "category_label": "Conversation Intelligence",
        "mentions": TOOL_MENTIONS.get("Clari", 0),
        "tagline": "Real-time conversation intelligence and revenue platform for pipeline accuracy.",
        "founded": "2012", "hq": "Sunnyvale, CA", "employees": "700+",
        "pricing": "Custom pricing (contact Clari)",
        "url": "https://www.clari.com/copilot",
        "best_for": "Revenue leaders who need pipeline accuracy and real-time deal coaching",
        "strengths": ["Real-time battlecards and coaching during calls", "Integrated with Clari's revenue platform", "Pipeline analytics and forecasting", "Automated CRM updates from conversations", "Revenue leak detection"],
        "weaknesses": ["Conversation intelligence is newer addition to Clari", "Less call data than Gong", "Primarily a revenue platform, CI is a module", "Pricing requires Clari platform commitment"],
        "verdict": "Clari Copilot (formerly Wingman) adds conversation intelligence to Clari's revenue platform. The real-time coaching during calls is a differentiator. Best for teams already investing in Clari for forecasting that want CI added to the stack. For standalone conversation intelligence, Gong remains the benchmark.",
        "rating": {"value": 4.2, "count": 310},
    },
    # CRM
    "salesforce": {
        "name": "Salesforce", "slug": "salesforce",
        "category": "crm", "category_label": "CRM",
        "mentions": TOOL_MENTIONS.get("Salesforce", 0),
        "tagline": "The dominant CRM platform and the system of record for most enterprise sales teams.",
        "founded": "1999", "hq": "San Francisco, CA", "employees": "70,000+",
        "pricing": "From $25/user/mo (Sales Cloud); Enterprise from $165/user/mo",
        "url": "https://www.salesforce.com",
        "best_for": "Enterprise and mid-market organizations that need a highly customizable CRM ecosystem",
        "strengths": ["Market-leading CRM with massive ecosystem", "AppExchange with 5,000+ integrations", "Salesforce Einstein AI capabilities", "Customizable for any sales process", "Industry-specific solutions"],
        "weaknesses": ["Expensive at enterprise scale", "Complex to administer and customize", "Implementation can take months", "User adoption often challenging"],
        "verdict": "Salesforce appeared in 63 of 219 job postings, making it the most-mentioned tool in enablement hiring by a wide margin. It is not an enablement tool per se, but it is the CRM backbone that every enablement platform must integrate with. Enablement professionals need Salesforce fluency.",
        "rating": {"value": 4.3, "count": 15000},
    },
    "hubspot": {
        "name": "HubSpot", "slug": "hubspot",
        "category": "crm", "category_label": "CRM",
        "mentions": TOOL_MENTIONS.get("Hubspot", 0) + TOOL_MENTIONS.get("Hubspot Marketing", 0),
        "tagline": "All-in-one CRM platform with growing sales enablement features for SMB and mid-market.",
        "founded": "2006", "hq": "Cambridge, MA", "employees": "7,000+",
        "pricing": "Free CRM; Sales Hub from $20/user/mo; Enterprise from $150/user/mo",
        "url": "https://www.hubspot.com",
        "best_for": "SMB and mid-market teams that want CRM, marketing, and basic enablement in one platform",
        "strengths": ["Free CRM tier with generous features", "Unified marketing, sales, and service hub", "Growing playbooks and enablement features", "Easier to administer than Salesforce", "Content management for sales assets"],
        "weaknesses": ["Enablement features less mature than dedicated platforms", "Enterprise features still catching up", "Can get expensive as you add hubs", "Less customizable than Salesforce for complex processes"],
        "verdict": "HubSpot appeared in 17 job postings. Its Sales Hub includes basic enablement features (playbooks, sequences, content management) that reduce the need for a separate platform at smaller companies. For teams under 100 reps, HubSpot may be enough. Larger orgs typically add Highspot or Seismic on top.",
        "rating": {"value": 4.5, "count": 10000},
    },
    # Additional enablement tools
    "allego": {
        "name": "Allego", "slug": "allego",
        "category": "training", "category_label": "Training & Readiness",
        "mentions": TOOL_MENTIONS.get("Allego", 0) + TOOL_MENTIONS.get("Allego Training", 0),
        "tagline": "Sales enablement platform built for video coaching, content management, and distributed teams.",
        "founded": "2013", "hq": "Waltham, MA", "employees": "300+",
        "pricing": "Custom pricing (typically $40-65/user/mo)",
        "url": "https://www.allego.com",
        "best_for": "Distributed sales teams that need video-first coaching and peer learning",
        "strengths": ["Video coaching and peer-to-peer learning", "Content management with mobile-first design", "AI-driven content recommendations", "Strong for distributed and remote teams", "Conversation intelligence module"],
        "weaknesses": ["Less market share than Highspot/Seismic/Mindtickle", "Can feel video-heavy for teams that prefer text", "Pricing competitive but not transparent", "Smaller integration ecosystem"],
        "verdict": "Allego is a solid mid-market enablement platform with particular strength in video coaching and distributed team workflows. With 4 mentions in job postings, it has consistent but niche demand. Best for organizations where video-based learning and mobile access are priorities.",
        "rating": {"value": 4.3, "count": 380},
    },
    "salesloft": {
        "name": "SalesLoft", "slug": "salesloft",
        "category": "crm", "category_label": "Sales Engagement",
        "mentions": TOOL_MENTIONS.get("Salesloft", 0),
        "tagline": "Sales engagement platform for cadences, pipeline management, and revenue workflows.",
        "founded": "2011", "hq": "Atlanta, GA", "employees": "700+",
        "pricing": "Custom pricing (typically $75-125/user/mo)",
        "url": "https://www.salesloft.com",
        "best_for": "Sales teams that need structured outreach cadences and pipeline management",
        "strengths": ["Best-in-class sales cadence and sequencing", "Pipeline management and deal intelligence", "Conversation intelligence built in", "Strong Salesforce integration", "Coaching and analytics"],
        "weaknesses": ["Not a traditional enablement platform", "Overlaps with CRM features", "Premium pricing", "Can create email fatigue if not managed"],
        "verdict": "SalesLoft appeared in 6 job postings. It is a sales engagement platform rather than pure enablement, but the overlap is real. Enablement professionals often own SalesLoft cadence creation, template management, and coaching workflows. Worth knowing even if it is not in your enablement stack.",
        "rating": {"value": 4.4, "count": 900},
    },
    "workramp": {
        "name": "WorkRamp", "slug": "workramp",
        "category": "training", "category_label": "Training & Readiness",
        "mentions": TOOL_MENTIONS.get("Workramp", 0) + TOOL_MENTIONS.get("Workramp Training", 0),
        "tagline": "Learning management platform for employee training, sales onboarding, and customer education.",
        "founded": "2015", "hq": "San Francisco, CA", "employees": "200+",
        "pricing": "Custom pricing (from $25/user/mo)",
        "url": "https://www.workramp.com",
        "best_for": "Companies that need both internal sales training and external customer education",
        "strengths": ["Dual-use: internal training + customer academy", "Modern, clean learning experience", "Content authoring tools built in", "Integrates with Salesforce and Slack", "Growing AI features for content creation"],
        "weaknesses": ["Less sales-specific than Mindtickle", "Smaller brand in enablement circles", "Limited conversation intelligence", "Competes with broader LMS platforms"],
        "verdict": "WorkRamp with 4 mentions in job postings offers a modern LMS that spans internal and external training. The dual-use capability (sales training + customer education) is a genuine differentiator. For teams that need onboarding and customer-facing learning in one platform, it is a strong option.",
        "rating": {"value": 4.3, "count": 250},
    },
}

# Category definitions
TOOL_CATEGORIES = {
    "content-management": {
        "label": "Content Management",
        "slug": "content-management",
        "description": "Platforms that help sales teams find, share, and track the content they use with buyers. Content management is the foundation of sales enablement.",
        "tools": ["highspot", "seismic", "showpad", "bigtincan", "guru"],
    },
    "training": {
        "label": "Training & Readiness",
        "slug": "training",
        "description": "Platforms focused on sales training, onboarding, coaching, and readiness. These tools help reps learn faster and perform better.",
        "tools": ["mindtickle", "lessonly", "saleshood", "brainshark", "allego", "workramp"],
    },
    "digital-sales-rooms": {
        "label": "Digital Sales Rooms",
        "slug": "digital-sales-rooms",
        "description": "Collaborative buyer workspaces that replace email threads with shared deal rooms. The fastest-growing category in enablement.",
        "tools": ["aligned", "enableus", "getaccept", "trumpet", "dock"],
    },
    "conversation-intelligence": {
        "label": "Conversation Intelligence",
        "slug": "conversation-intelligence",
        "description": "Platforms that record, transcribe, and analyze sales conversations to surface coaching insights and deal signals.",
        "tools": ["gong", "chorus", "clari-copilot"],
    },
    "crm": {
        "label": "CRM & Sales Engagement",
        "slug": "crm",
        "description": "CRM and sales engagement platforms that serve as the system of record for sales teams. Every enablement tool connects to these.",
        "tools": ["salesforce", "hubspot", "salesloft"],
    },
}

# Comparison definitions for tools
TOOL_COMPARISONS = [
    {
        "slug": "highspot-vs-seismic",
        "tool_a": "highspot", "tool_b": "seismic",
        "title": "Highspot vs Seismic",
        "description": "The two category leaders in sales enablement content management, compared on features, pricing, and use cases.",
        "summary": "Highspot and Seismic are the two dominant content management platforms in sales enablement. Highspot leads in guided selling and ease of use. Seismic leads in content automation, compliance, and enterprise scale. Highspot has 22 mentions in our job data vs Seismic's 7, suggesting broader mid-market adoption. Seismic's acquisition of Lessonly gives it a training advantage. Choose Highspot for a cleaner UX and faster deployment. Choose Seismic for content automation at scale and regulated industries.",
    },
    {
        "slug": "gong-vs-chorus",
        "tool_a": "gong", "tool_b": "chorus",
        "title": "Gong vs Chorus (ZoomInfo)",
        "description": "The two leading conversation intelligence platforms: standalone Gong vs ZoomInfo-integrated Chorus.",
        "summary": "Gong and Chorus defined the conversation intelligence category. Gong remains independent and has 15 mentions in our data vs Chorus's 3. Gong's larger data moat and faster innovation pace give it the edge as a standalone platform. Chorus's advantage is integration with ZoomInfo's contact and intent data. If you already pay for ZoomInfo, Chorus adds CI without a new vendor. If you are buying standalone, Gong is the category standard.",
    },
    {
        "slug": "highspot-vs-showpad",
        "tool_a": "highspot", "tool_b": "showpad",
        "title": "Highspot vs Showpad",
        "description": "North American category leader vs the European content management specialist. Feature and vertical comparison.",
        "summary": "Highspot dominates the North American enablement market with 22 job mentions vs Showpad's 1. Showpad has carved out a defensible niche in manufacturing, life sciences, and European markets where GDPR-native architecture matters. Highspot is stronger on guided selling, analytics, and CRM integration. Showpad is stronger on offline access, interactive content (3D/AR), and vertical-specific workflows. Choose Highspot for SaaS/tech sales. Choose Showpad for field sales in manufacturing or life sciences.",
    },
    {
        "slug": "mindtickle-vs-saleshood",
        "tool_a": "mindtickle", "tool_b": "saleshood",
        "title": "Mindtickle vs SalesHood",
        "description": "Enterprise readiness platform vs mid-market all-in-one enablement. Training, coaching, and readiness compared.",
        "summary": "Mindtickle is the enterprise readiness leader with 6 job mentions and 600+ employees. SalesHood is a mid-market alternative with an all-in-one approach. Mindtickle is stronger on AI coaching, conversation intelligence, and certification programs. SalesHood bundles training, content, and buyer engagement at a lower price point. Choose Mindtickle for organizations with 200+ reps and dedicated enablement teams. Choose SalesHood for mid-market teams that want one platform instead of assembling a stack.",
    },
    {
        "slug": "aligned-vs-dock",
        "tool_a": "aligned", "tool_b": "dock",
        "title": "Aligned vs Dock",
        "description": "Two fast-growing digital sales room startups compared on features, pricing, and use cases.",
        "summary": "Aligned and Dock are both 2021-vintage DSR platforms with similar pricing and free tiers. Aligned focuses purely on the buyer deal experience with strong engagement analytics. Dock spans sales, onboarding, and customer success with a Notion-like builder. Choose Aligned if you want the best pure deal room experience. Choose Dock if you want one workspace tool that extends into onboarding and renewal.",
    },
    {
        "slug": "gong-vs-mindtickle",
        "tool_a": "gong", "tool_b": "mindtickle",
        "title": "Gong vs Mindtickle",
        "description": "Revenue intelligence vs sales readiness. Two different approaches to improving rep performance, compared.",
        "summary": "Gong and Mindtickle attack rep performance from different angles. Gong analyzes what reps actually do on calls and in deals. Mindtickle trains and certifies reps before they get on calls. Gong has 15 mentions vs Mindtickle's 6 in our data. The best enablement stacks use both: Mindtickle for structured training and certification, Gong for real-time coaching and deal intelligence. If you can only pick one, Gong provides more immediate pipeline impact. Mindtickle provides more structured skill development.",
    },
    {
        "slug": "seismic-vs-showpad",
        "tool_a": "seismic", "tool_b": "showpad",
        "title": "Seismic vs Showpad",
        "description": "Two enterprise content management platforms compared. Content automation vs vertical specialization.",
        "summary": "Seismic and Showpad both serve enterprise content management but with different strengths. Seismic leads in content automation (LiveDocs), compliance, and scale. Showpad leads in vertical depth (manufacturing, life sciences) and interactive content. Seismic has the Lessonly training integration. Showpad has stronger GDPR compliance. Seismic is the default for Fortune 500 and regulated industries. Showpad wins in manufacturing field sales. Both are premium-priced enterprise tools.",
    },
]

# Salary comparison data — enablement vs adjacent roles
SALARY_COMPARISONS = [
    {
        "slug": "vs-sales-training",
        "role": "Sales Training Manager",
        "title": "Sales Enablement vs Sales Training Manager",
        "description": "How does sales enablement compensation compare to sales training? We break down the salary differences, career paths, and role scope.",
        "other_median": 95000, "other_min": 70000, "other_max": 140000,
        "enablement_median": int(COMP_DATA["salary_stats"]["median"]),
        "analysis": "Sales enablement roles pay approximately 15-20% more than pure sales training positions. The premium reflects the broader scope: enablement owns content strategy, tool stack management, and cross-functional alignment in addition to training. Sales training managers typically focus on onboarding, methodology adoption, and skills development. Both roles benefit from understanding adult learning theory, but enablement requires stronger data analysis and technology management skills. The career ceiling is also higher in enablement, with Director/VP paths reaching $200K+ total compensation.",
    },
    {
        "slug": "vs-sales-ops",
        "role": "Sales Operations Manager",
        "title": "Sales Enablement vs Sales Operations",
        "description": "Enablement vs operations: two sides of the revenue coin. Salary data, scope differences, and which path pays more.",
        "other_median": 115000, "other_min": 80000, "other_max": 165000,
        "enablement_median": int(COMP_DATA["salary_stats"]["median"]),
        "analysis": "Sales operations and sales enablement salaries are closely matched, with ops holding a slight edge at the mid-level. Operations professionals manage CRM administration, territory planning, quota setting, and process optimization. Enablement professionals manage content, training, tools, and seller productivity. The roles frequently overlap, especially at smaller companies where one person handles both. At the Director level, compensation converges. The main salary difference comes from ops professionals who specialize in Salesforce administration or RevOps, which command premium rates. Enablement offers more creative work and buyer-facing impact.",
    },
    {
        "slug": "vs-revops",
        "role": "Revenue Operations Manager",
        "title": "Sales Enablement vs Revenue Operations",
        "description": "RevOps is the newer, broader function. How do enablement salaries stack up against the RevOps market?",
        "other_median": 125000, "other_min": 90000, "other_max": 185000,
        "enablement_median": int(COMP_DATA["salary_stats"]["median"]),
        "analysis": "Revenue operations roles currently command a 10-15% premium over equivalent enablement positions. RevOps is the hot function, spanning marketing ops, sales ops, and CS ops under one umbrella. This broader scope and the technical skills required (BI tools, data engineering, system architecture) drive the salary premium. However, senior enablement leaders who can demonstrate revenue impact close the gap. The market is also evolving: many organizations are merging enablement into RevOps or creating hybrid roles. Enablement professionals who add RevOps skills (data analysis, process design, technology architecture) position themselves for the highest-paying roles.",
    },
    {
        "slug": "vs-product-marketing",
        "role": "Product Marketing Manager",
        "title": "Sales Enablement vs Product Marketing",
        "description": "Product marketing creates the messaging. Enablement delivers it. How do the salaries compare?",
        "other_median": 120000, "other_min": 85000, "other_max": 175000,
        "enablement_median": int(COMP_DATA["salary_stats"]["median"]),
        "analysis": "Product marketing managers earn approximately 8-12% more than equivalent enablement roles at the mid-level. Product marketing is more established as a function, with clearer career paths and more budget ownership. PMMs own positioning, messaging, competitive intelligence, and launch strategy. Enablement owns the translation of that strategy into seller behavior. The best enablement professionals work closely with product marketing but focus on activation and adoption rather than creation. At the VP level, product marketing tends to sit closer to the CEO, which drives higher compensation. Enablement professionals can close the gap by taking on competitive intelligence and content strategy ownership.",
    },
    {
        "slug": "vs-learning-development",
        "role": "Learning & Development Manager",
        "title": "Sales Enablement vs L&D Manager",
        "description": "L&D is the broader corporate function. Sales enablement is the revenue-focused specialization. Salary comparison inside.",
        "other_median": 90000, "other_min": 65000, "other_max": 135000,
        "enablement_median": int(COMP_DATA["salary_stats"]["median"]),
        "analysis": "Sales enablement roles pay 20-25% more than general L&D positions. The premium exists because enablement is directly tied to revenue outcomes, while L&D supports broader organizational development. L&D managers design learning programs across all departments. Enablement managers focus exclusively on revenue team performance. The revenue connection creates more measurable impact and justifies higher compensation. L&D professionals transitioning into enablement should emphasize their curriculum design and adult learning skills while building competency in sales processes, CRM systems, and revenue metrics. The transition typically comes with a meaningful salary increase.",
    },
]

# Tool roundup data
TOOL_ROUNDUPS = [
    {
        "slug": "best-sales-enablement-platforms",
        "title": "Best Sales Enablement Platforms 2026",
        "description": "Ranked comparison of the top sales enablement platforms for content management, training, and analytics. Based on real job market data.",
        "tools": ["highspot", "seismic", "showpad", "mindtickle", "allego", "bigtincan", "saleshood"],
        "intro": "We analyzed 219 sales enablement job postings to identify which platforms employers actually require. This ranking combines job market demand, feature depth, and practitioner feedback. Highspot leads with 22 mentions, followed by Seismic (7), Mindtickle (6), and Allego (4).",
    },
    {
        "slug": "best-conversation-intelligence",
        "title": "Best Conversation Intelligence Tools 2026",
        "description": "Ranked comparison of Gong, Chorus, Clari Copilot, and other conversation intelligence platforms for sales teams.",
        "tools": ["gong", "chorus", "clari-copilot"],
        "intro": "Conversation intelligence is the fastest-adopted enablement technology. Gong dominates with 15 mentions across 219 job postings, followed by Chorus/ZoomInfo (3) and Clari (1). These platforms record, transcribe, and analyze sales conversations to surface coaching insights.",
    },
    {
        "slug": "best-digital-sales-rooms",
        "title": "Best Digital Sales Rooms 2026",
        "description": "Comparison of Aligned, Dock, GetAccept, Trumpet, and Enable.us for creating collaborative buyer workspaces.",
        "tools": ["aligned", "dock", "getaccept", "trumpet", "enableus"],
        "intro": "Digital sales rooms replace email threads with collaborative buyer workspaces. This is the fastest-growing category in enablement tech. All five platforms launched in the last five years, and most offer free tiers. We compare them on buyer experience, pricing, and integration depth.",
    },
    {
        "slug": "best-sales-training-platforms",
        "title": "Best Sales Training Platforms 2026",
        "description": "Ranked comparison of Mindtickle, Lessonly, Brainshark, SalesHood, Allego, and WorkRamp for sales training and readiness.",
        "tools": ["mindtickle", "lessonly", "brainshark", "saleshood", "allego", "workramp"],
        "intro": "Sales training platforms help enablement teams onboard new reps, certify skills, and deliver ongoing coaching. Mindtickle leads in job market demand with 6 mentions, followed by Allego (4), WorkRamp (4), Lessonly (2), and Brainshark (2). We compare them on training depth, coaching tools, and ease of use.",
    },
]


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
    """Generate the salary index page with real data."""
    title = "Sales Enablement Salary Data 2026"
    description = (
        f"Salary benchmarks for {SALARY_STATS['count_with_salary']} sales enablement roles."
        f" {fmt_salary(SALARY_STATS['median'])} median. By seniority, location, and remote status."
        " Independent data from real job postings."
    )

    crumbs = [("Home", "/"), ("Salary Data", None)]
    cards = ""
    for key, data in SALARY_BY_SENIORITY.items():
        cards += f'''<a href="/salary/by-seniority/{data['slug']}/" class="salary-index-card">
    <h3>{data['label']}</h3>
    <div class="card-range">{fmt_salary(data['min'])} - {fmt_salary(data['max'])}</div>
    <p>Median: {fmt_salary(data['median'])} ({data['count']} roles)</p>
</a>
'''

    metro_cards = ""
    for metro, data in SALARY_BY_METRO.items():
        metro_cards += f'''<a href="/salary/by-location/{data['slug']}/" class="salary-index-card">
    <h3>{data['label']}</h3>
    <div class="card-range">{fmt_salary(data['min'])} - {fmt_salary(data['max'])}</div>
    <p>Median: {fmt_salary(data['median'])} ({data['count']} roles)</p>
</a>
'''

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">SALARY DATA</div>
        <h1>Sales Enablement Salary Index</h1>
        <p>How much do enablement professionals earn? Data from {SALARY_STATS['count_with_salary']} real job postings with disclosed compensation. {fmt_salary(SALARY_STATS['median'])} median base salary.</p>
    </div>
</div>
<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(SALARY_STATS['median'])}</span>
        <span class="stat-label">Median Salary</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(SALARY_STATS['min'])} - {fmt_salary(SALARY_STATS['max'])}</span>
        <span class="stat-label">Full Range</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{SALARY_STATS['count_with_salary']}</span>
        <span class="stat-label">Roles Analyzed</span>
    </div>
</div>
<div class="salary-content">
    <h2>By Seniority Level</h2>
    <div class="salary-index-grid">
        {cards}
    </div>

    <h2>By Metro Area</h2>
    <div class="salary-index-grid">
        {metro_cards}
    </div>

    <h2>Explore More</h2>
    <div class="related-links-grid">
        <a href="/salary/by-seniority/" class="related-link-card">All Seniority Levels</a>
        <a href="/salary/by-location/" class="related-link-card">All Metro Areas</a>
        <a href="/salary/remote-vs-onsite/" class="related-link-card">Remote vs Onsite</a>
        <a href="/salary/calculator/" class="related-link-card">Salary Calculator</a>
        <a href="/salary/methodology/" class="related-link-card">Our Methodology</a>
    </div>

    <h2>Role Comparisons</h2>
    <div class="related-links-grid">
''' + "".join(f'        <a href="/salary/{c["slug"]}/" class="related-link-card">{c["title"]}</a>\n' for c in SALARY_COMPARISONS) + '''    </div>
</div>
'''
    body += newsletter_cta_html("Get weekly salary updates.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/salary/", body_content=body,
                            active_path="/salary/", extra_head=extra_head)
    write_page("salary/index.html", page)
    print(f"  Built: salary/index.html")


def build_salary_seniority_index():
    """Generate the seniority index page."""
    title = "Sales Enablement Salary by Seniority Level 2026"
    description = "Salary breakdown by seniority for sales enablement. Entry, mid, senior, and director compensation from real job postings."

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Seniority", None)]
    cards = ""
    for key, data in SALARY_BY_SENIORITY.items():
        cards += f'''<a href="/salary/by-seniority/{data['slug']}/" class="salary-index-card">
    <h3>{data['label']}</h3>
    <div class="card-range">{fmt_salary(data['min'])} - {fmt_salary(data['max'])}</div>
    <p>Median: {fmt_salary(data['median'])} | {data['count']} roles</p>
</a>
'''

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">SALARY BY SENIORITY</div>
        <h1>Enablement Salary by Seniority Level</h1>
        <p>How compensation scales from entry-level to Director/VP in sales enablement. Based on {SALARY_STATS['count_with_salary']} roles with disclosed salary data.</p>
    </div>
</div>
<div class="salary-content">
    <div class="salary-index-grid">
        {cards}
    </div>

    <h2>Key Findings</h2>
    <ul>
        <li>Entry-level enablement roles start at {fmt_salary(SALARY_BY_SENIORITY['entry']['median'])} median, competitive with other go-to-market entry roles.</li>
        <li>The biggest salary jump happens from mid-level ({fmt_salary(SALARY_BY_SENIORITY['mid']['median'])}) to senior ({fmt_salary(SALARY_BY_SENIORITY['senior']['median'])}), a {int((SALARY_BY_SENIORITY['senior']['median'] / SALARY_BY_SENIORITY['mid']['median'] - 1) * 100)}% increase.</li>
        <li>Director/VP roles reach {fmt_salary(SALARY_BY_SENIORITY['director']['max'])} at the top end, with a {fmt_salary(SALARY_BY_SENIORITY['director']['median'])} median.</li>
        <li>Senior-level roles represent the largest cohort at {SALARY_BY_SENIORITY['senior']['count']} positions, followed by mid-level at {SALARY_BY_SENIORITY['mid']['count']}.</li>
    </ul>

    <h2>Related</h2>
    <div class="related-links-grid">
        <a href="/salary/by-location/" class="related-link-card">Salary by Location</a>
        <a href="/salary/remote-vs-onsite/" class="related-link-card">Remote vs Onsite</a>
        <a href="/salary/calculator/" class="related-link-card">Salary Calculator</a>
    </div>
</div>
'''
    body += newsletter_cta_html("Get weekly salary updates by level.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/salary/by-seniority/", body_content=body,
                            active_path="/salary/", extra_head=extra_head)
    write_page("salary/by-seniority/index.html", page)
    print(f"  Built: salary/by-seniority/index.html")


def build_salary_seniority_pages():
    """Generate individual seniority detail pages."""
    for key, data in SALARY_BY_SENIORITY.items():
        title = f"{data['label']} Sales Enablement Salary 2026"
        description = f"{data['label']} sales enablement salary: {fmt_salary(data['median'])} median, {fmt_salary(data['min'])}-{fmt_salary(data['max'])} range. Based on {data['count']} real job postings."

        crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Seniority", "/salary/by-seniority/"), (data['label'], None)]

        # Build context paragraphs per level
        level_context = {
            "entry": f'''<p>Entry-level enablement roles include Sales Enablement Coordinator, Associate, and Specialist positions. These roles typically support content management, training coordination, and basic analytics. Most require 0-3 years of experience, with backgrounds in sales, marketing, or L&D.</p>
            <p>The {fmt_salary(data['median'])} median reflects a competitive starting salary for go-to-market roles. Entry enablement pays more than many marketing coordinator positions and is on par with BDR team leads transitioning into enablement.</p>
            <h3>Typical Responsibilities</h3>
            <ul>
                <li>Content organization and CRM/enablement platform administration</li>
                <li>Training session coordination and logistics</li>
                <li>Onboarding program support for new hires</li>
                <li>Sales asset creation and template management</li>
                <li>Basic reporting on content usage and training completion</li>
            </ul>''',
            "mid": f'''<p>Mid-level enablement roles include Sales Enablement Manager and Program Manager positions. These roles own specific workstreams: onboarding programs, content strategy, tool administration, or training development. Typically 3-6 years of experience.</p>
            <p>At {fmt_salary(data['median'])} median, mid-level enablement is competitive with equivalent sales operations and marketing manager roles. The {data['count']} positions in our data set represent the largest hiring cohort, indicating strong demand.</p>
            <h3>Typical Responsibilities</h3>
            <ul>
                <li>Sales onboarding program ownership and optimization</li>
                <li>Content strategy and editorial calendar management</li>
                <li>Enablement platform administration (Highspot, Seismic, etc.)</li>
                <li>Sales methodology reinforcement and coaching programs</li>
                <li>Cross-functional alignment with product marketing and sales leadership</li>
            </ul>''',
            "senior": f'''<p>Senior enablement roles include Senior Sales Enablement Manager, Principal, and Lead positions. These roles set strategy, manage programs end-to-end, and often lead small teams. Typically 6-10 years of experience with demonstrated impact on revenue metrics.</p>
            <p>The {fmt_salary(data['median'])} median for senior roles represents a significant premium over mid-level. Senior enablement professionals are expected to connect enablement programs to pipeline and revenue outcomes, not just activity metrics.</p>
            <h3>Typical Responsibilities</h3>
            <ul>
                <li>Enablement strategy development and executive alignment</li>
                <li>Program design tied to revenue outcomes and pipeline impact</li>
                <li>Sales methodology selection and global rollout</li>
                <li>Team leadership and enablement headcount management</li>
                <li>Tech stack evaluation, procurement, and optimization</li>
                <li>Executive reporting on enablement ROI and program effectiveness</li>
            </ul>''',
            "director": f'''<p>Director and VP-level enablement roles lead the entire function. These positions set the enablement vision, manage teams of 5-20+, own significant budgets, and report to CROs or CMOs. Typically 10+ years of experience with a track record of scaling enablement programs.</p>
            <p>The {fmt_salary(data['median'])} median puts Director/VP enablement on par with other go-to-market leadership roles. Top-end compensation of {fmt_salary(data['max'])} is achievable at large enterprises, particularly with equity and bonus components.</p>
            <h3>Typical Responsibilities</h3>
            <ul>
                <li>Enablement vision and multi-year strategy</li>
                <li>Team building, hiring, and organizational design</li>
                <li>Budget ownership for enablement tools, content, and programs</li>
                <li>Executive stakeholder management (CRO, CMO, CEO)</li>
                <li>Global enablement program standardization</li>
                <li>Board-level reporting on enablement impact and revenue contribution</li>
            </ul>''',
        }

        body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">{data['label'].upper()} SALARY</div>
        <h1>{data['label']} Sales Enablement Salary</h1>
        <p>{fmt_salary(data['median'])} median from {data['count']} roles. Range: {fmt_salary(data['min'])} to {fmt_salary(data['max'])}.</p>
    </div>
</div>
<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data['min'])}</span>
        <span class="stat-label">Average Minimum</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data['median'])}</span>
        <span class="stat-label">Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data['max'])}</span>
        <span class="stat-label">Average Maximum</span>
    </div>
</div>
<div class="salary-content">
    <h2>What Does {data['label']} Enablement Pay?</h2>
    {level_context.get(key, "")}

    <h2>Other Seniority Levels</h2>
    <div class="related-links-grid">
''' + "".join(f'        <a href="/salary/by-seniority/{d["slug"]}/" class="related-link-card">{d["label"]}: {fmt_salary(d["median"])} median</a>\n' for k, d in SALARY_BY_SENIORITY.items() if k != key) + '''    </div>
</div>
'''
        body += newsletter_cta_html("Get salary updates for your level.")

        extra_head = get_breadcrumb_schema(crumbs)
        page = get_page_wrapper(title=title, description=description,
                                canonical_path=f"/salary/by-seniority/{data['slug']}/",
                                body_content=body, active_path="/salary/",
                                extra_head=extra_head)
        write_page(f"salary/by-seniority/{data['slug']}/index.html", page)
        print(f"  Built: salary/by-seniority/{data['slug']}/index.html")


def build_salary_location_index():
    """Generate the location index page."""
    title = "Sales Enablement Salary by Metro Area 2026"
    description = "Enablement salary data for New York, San Francisco, Seattle, Boston, and Los Angeles. Real compensation from job postings."

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Location", None)]
    cards = ""
    for metro, data in sorted(SALARY_BY_METRO.items(), key=lambda x: x[1]["median"], reverse=True):
        cards += f'''<a href="/salary/by-location/{data['slug']}/" class="salary-index-card">
    <h3>{data['label']}</h3>
    <div class="card-range">{fmt_salary(data['min'])} - {fmt_salary(data['max'])}</div>
    <p>Median: {fmt_salary(data['median'])} | {data['count']} roles</p>
</a>
'''

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">SALARY BY LOCATION</div>
        <h1>Enablement Salary by Metro Area</h1>
        <p>How enablement compensation varies across major U.S. metro areas. Based on {SALARY_STATS['count_with_salary']} roles with disclosed salary data.</p>
    </div>
</div>
<div class="salary-content">
    <div class="salary-index-grid">
        {cards}
    </div>

    <h2>Key Findings</h2>
    <ul>
        <li>Boston leads in median salary at {fmt_salary(SALARY_BY_METRO['Boston']['median'])}, driven by biotech and enterprise tech companies.</li>
        <li>San Francisco and Seattle both exceed {fmt_salary(160000)} median, reflecting cost of living and tech company concentration.</li>
        <li>New York has the most roles ({SALARY_BY_METRO['New York']['count']}) with a {fmt_salary(SALARY_BY_METRO['New York']['median'])} median.</li>
        <li>Remote roles pay a {fmt_salary(int(SALARY_BY_REMOTE['remote']['median']))} median. See the <a href="/salary/remote-vs-onsite/">remote vs onsite breakdown</a>.</li>
    </ul>

    <h2>Related</h2>
    <div class="related-links-grid">
        <a href="/salary/remote-vs-onsite/" class="related-link-card">Remote vs Onsite Pay</a>
        <a href="/salary/by-seniority/" class="related-link-card">Salary by Seniority</a>
        <a href="/salary/calculator/" class="related-link-card">Salary Calculator</a>
    </div>
</div>
'''
    body += newsletter_cta_html("Get location-specific salary updates.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/salary/by-location/", body_content=body,
                            active_path="/salary/", extra_head=extra_head)
    write_page("salary/by-location/index.html", page)
    print(f"  Built: salary/by-location/index.html")


def build_salary_location_pages():
    """Generate individual metro area salary pages."""
    metro_context = {
        "New York": "New York is the largest enablement market by volume. Financial services, media, and enterprise SaaS companies drive demand. The city's high cost of living is partially offset by competitive salaries, though remote options have compressed the premium somewhat.",
        "San Francisco": "San Francisco and the broader Bay Area remain the highest-paying enablement market. SaaS companies, enterprise software vendors, and tech startups concentrate here. Most Highspot, Seismic, and Gong roles list SF as a primary location.",
        "Seattle": "Seattle's enablement market is anchored by Highspot (headquartered here), Amazon, and Microsoft. The city offers strong compensation with somewhat lower cost of living than San Francisco. Growing fast as enablement vendors and tech companies expand.",
        "Boston": "Boston commands the highest median salary in our data, driven by biotech, healthcare tech, and enterprise software companies. HubSpot's presence creates additional demand. The concentration of research universities supports a strong talent pipeline.",
        "Los Angeles": "Los Angeles has a diverse enablement market spanning entertainment, media, and tech. The wide salary range reflects the mix of startup and enterprise roles. Growing as more companies establish West Coast operations outside of the Bay Area.",
    }

    for metro, data in SALARY_BY_METRO.items():
        title = f"Sales Enablement Salary in {metro} 2026"
        description = f"Enablement salary in {metro}: {fmt_salary(data['median'])} median, {fmt_salary(data['min'])}-{fmt_salary(data['max'])} range. {data['count']} roles analyzed."

        crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("By Location", "/salary/by-location/"), (metro, None)]
        context = metro_context.get(metro, f"{metro} is an active enablement hiring market with competitive compensation.")

        body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">{metro.upper()} SALARY</div>
        <h1>Sales Enablement Salary in {metro}</h1>
        <p>{fmt_salary(data['median'])} median from {data['count']} roles in the {metro} metro area.</p>
    </div>
</div>
<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data['min'])}</span>
        <span class="stat-label">Average Minimum</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data['median'])}</span>
        <span class="stat-label">Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(data['max'])}</span>
        <span class="stat-label">Average Maximum</span>
    </div>
</div>
<div class="salary-content">
    <h2>Enablement Market in {metro}</h2>
    <p>{context}</p>
    <p>The {data['count']} roles we tracked in {metro} show a {fmt_salary(data['min'])} to {fmt_salary(data['max'])} base salary range. This compares to a national median of {fmt_salary(SALARY_STATS['median'])} across all metros.</p>

    <h2>Other Metro Areas</h2>
    <div class="related-links-grid">
''' + "".join(f'        <a href="/salary/by-location/{d["slug"]}/" class="related-link-card">{m}: {fmt_salary(d["median"])} median</a>\n' for m, d in SALARY_BY_METRO.items() if m != metro) + f'''        <a href="/salary/remote-vs-onsite/" class="related-link-card">Remote vs Onsite Pay</a>
    </div>
</div>
'''
        body += newsletter_cta_html(f"Get salary updates for {metro}.")

        extra_head = get_breadcrumb_schema(crumbs)
        page = get_page_wrapper(title=title, description=description,
                                canonical_path=f"/salary/by-location/{data['slug']}/",
                                body_content=body, active_path="/salary/",
                                extra_head=extra_head)
        write_page(f"salary/by-location/{data['slug']}/index.html", page)
        print(f"  Built: salary/by-location/{data['slug']}/index.html")


def build_salary_remote_vs_onsite():
    """Generate remote vs onsite salary comparison page."""
    remote = SALARY_BY_REMOTE["remote"]
    onsite = SALARY_BY_REMOTE["onsite"]
    title = "Remote vs Onsite Sales Enablement Salary 2026"
    description = f"Remote enablement: {fmt_salary(int(remote['median']))} median. Onsite: {fmt_salary(int(onsite['median']))} median. {remote['count']} remote vs {onsite['count']} onsite roles analyzed."

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Remote vs Onsite", None)]

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">REMOTE VS ONSITE</div>
        <h1>Remote vs Onsite Enablement Salary</h1>
        <p>Does working remotely cost you money in enablement? We compared {remote['count']} remote roles against {onsite['count']} onsite/hybrid positions.</p>
    </div>
</div>
<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(int(remote['median']))}</span>
        <span class="stat-label">Remote Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(int(onsite['median']))}</span>
        <span class="stat-label">Onsite Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{int((onsite['median'] / remote['median'] - 1) * 100)}%</span>
        <span class="stat-label">Onsite Premium</span>
    </div>
</div>
<div class="salary-content">
    <h2>The Remote Pay Gap in Enablement</h2>
    <p>Onsite and hybrid enablement roles pay approximately {int((onsite['median'] / remote['median'] - 1) * 100)}% more than fully remote positions at the median. The remote median of {fmt_salary(int(remote['median']))} compares to {fmt_salary(int(onsite['median']))} for onsite roles.</p>

    <p>This gap reflects several factors: onsite roles skew toward higher-cost metros (New York, San Francisco, Seattle), where companies adjust for cost of living. Remote roles draw from a national talent pool, which compresses salaries toward the national average. Additionally, some employers apply geographic pay adjustments that reduce remote compensation.</p>

    <h2>Remote Enablement: Salary Range</h2>
    <ul>
        <li>Average minimum base: {fmt_salary(int(remote['min_base_avg']))}</li>
        <li>Median base: {fmt_salary(int(remote['median']))}</li>
        <li>Average maximum base: {fmt_salary(int(remote['max_base_avg']))}</li>
        <li>Total remote roles analyzed: {remote['count']}</li>
    </ul>

    <h2>Onsite/Hybrid Enablement: Salary Range</h2>
    <ul>
        <li>Average minimum base: {fmt_salary(int(onsite['min_base_avg']))}</li>
        <li>Median base: {fmt_salary(int(onsite['median']))}</li>
        <li>Average maximum base: {fmt_salary(int(onsite['max_base_avg']))}</li>
        <li>Total onsite/hybrid roles analyzed: {onsite['count']}</li>
    </ul>

    <h2>Should You Negotiate Remote Pay?</h2>
    <p>The gap narrows at senior and director levels where companies compete for scarce talent regardless of location. If you are negotiating a remote enablement offer, benchmark against metro-specific data for the company's HQ location, not national averages. Many companies set remote bands based on headquarters or tier-based geographic zones.</p>

    <h2>Related</h2>
    <div class="related-links-grid">
        <a href="/salary/by-location/" class="related-link-card">Salary by Metro Area</a>
        <a href="/salary/by-seniority/" class="related-link-card">Salary by Seniority</a>
        <a href="/salary/calculator/" class="related-link-card">Salary Calculator</a>
    </div>
</div>
'''
    body += newsletter_cta_html("Get remote salary alerts.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/salary/remote-vs-onsite/", body_content=body,
                            active_path="/salary/", extra_head=extra_head)
    write_page("salary/remote-vs-onsite/index.html", page)
    print(f"  Built: salary/remote-vs-onsite/index.html")


def build_salary_calculator():
    """Generate email-gated salary calculator page."""
    title = "Sales Enablement Salary Calculator 2026"
    description = "Estimate your market value as a sales enablement professional. Enter your seniority, location, and experience to get a personalized salary range."

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Salary Calculator", None)]

    # Build option lists from real data
    seniority_options = "".join(f'<option value="{k}">{d["label"]} ({fmt_salary(d["median"])} median)</option>' for k, d in SALARY_BY_SENIORITY.items())
    location_options = '<option value="national">National Average</option>' + "".join(f'<option value="{d["slug"]}">{m} ({fmt_salary(d["median"])} median)</option>' for m, d in SALARY_BY_METRO.items())

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">SALARY CALCULATOR</div>
        <h1>Enablement Salary Calculator</h1>
        <p>Get a personalized salary estimate based on your seniority, location, and work arrangement. Powered by data from {SALARY_STATS['count_with_salary']} real job postings.</p>
    </div>
</div>
<div class="salary-content">
    <div class="calculator-container">
        <div class="calculator-gate" id="calcGate">
            <h2>Get Your Salary Estimate</h2>
            <p>Enter your email to unlock the calculator. We will send you a personalized salary report.</p>
            <form class="calculator-gate-form" id="calcGateForm">
                <input type="email" placeholder="Your work email" aria-label="Email address" required id="calcEmail">
                <button type="submit" class="btn btn--primary">Unlock Calculator</button>
            </form>
            <p class="hero-signup-note">Free. No spam. Unsubscribe anytime.</p>
        </div>
        <div class="calculator-form" id="calcForm" style="display:none;">
            <h2>Your Salary Estimate</h2>
            <div class="calc-field">
                <label for="calcSeniority">Seniority Level</label>
                <select id="calcSeniority">
                    {seniority_options}
                </select>
            </div>
            <div class="calc-field">
                <label for="calcLocation">Location</label>
                <select id="calcLocation">
                    {location_options}
                    <option value="remote">Fully Remote</option>
                </select>
            </div>
            <div class="calc-result" id="calcResult">
                <div class="calc-result-label">Estimated Base Salary Range</div>
                <div class="calc-result-range" id="calcRange">Select your details above</div>
                <div class="calc-result-note" id="calcNote"></div>
            </div>
        </div>
    </div>

    <h2>How the Calculator Works</h2>
    <p>This calculator uses salary data from {SALARY_STATS['count_with_salary']} sales enablement job postings with disclosed compensation. We cross-reference your seniority level and location against our database to produce a realistic base salary range. Total compensation (including bonus, equity, and benefits) typically adds 15-30% on top of base salary for mid-level and above.</p>

    <h2>Related</h2>
    <div class="related-links-grid">
        <a href="/salary/by-seniority/" class="related-link-card">Salary by Seniority</a>
        <a href="/salary/by-location/" class="related-link-card">Salary by Location</a>
        <a href="/salary/remote-vs-onsite/" class="related-link-card">Remote vs Onsite</a>
        <a href="/salary/methodology/" class="related-link-card">Methodology</a>
    </div>
</div>
<script>
(function() {{
    var salaryData = {json.dumps({k: {"min": d["min"], "max": d["max"], "median": d["median"]} for k, d in SALARY_BY_SENIORITY.items()})};
    var locationMult = {json.dumps({d["slug"]: round(d["median"] / SALARY_STATS["median"], 2) for m, d in SALARY_BY_METRO.items()})};
    locationMult["national"] = 1.0;
    locationMult["remote"] = {round(SALARY_BY_REMOTE["remote"]["median"] / SALARY_STATS["median"], 2)};

    var gate = document.getElementById('calcGate');
    var form = document.getElementById('calcForm');
    var gateForm = document.getElementById('calcGateForm');

    gateForm.addEventListener('submit', function(e) {{
        e.preventDefault();
        var email = document.getElementById('calcEmail').value.trim();
        if (!email) return;
        gate.style.display = 'none';
        form.style.display = 'block';
        // Fire newsletter signup
        var SIGNUP_URL = '{SIGNUP_WORKER_URL}';
        fetch(SIGNUP_URL, {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{email: email, list: 'senablers'}})
        }}).catch(function() {{}});
        if (typeof gtag === 'function') {{ gtag('event', 'calculator_unlock', {{'event_category': 'engagement', 'event_label': email}}); }}
        updateCalc();
    }});

    function updateCalc() {{
        var seniority = document.getElementById('calcSeniority').value;
        var location = document.getElementById('calcLocation').value;
        var base = salaryData[seniority];
        if (!base) return;
        var mult = locationMult[location] || 1.0;
        var min = Math.round(base.min * mult / 1000) * 1000;
        var max = Math.round(base.max * mult / 1000) * 1000;
        var median = Math.round(base.median * mult / 1000) * 1000;
        document.getElementById('calcRange').textContent = '$' + (min/1000) + 'K - $' + (max/1000) + 'K';
        document.getElementById('calcNote').textContent = 'Estimated median: $' + (median/1000) + 'K base salary';
    }}

    document.getElementById('calcSeniority').addEventListener('change', updateCalc);
    document.getElementById('calcLocation').addEventListener('change', updateCalc);
}})();
</script>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/salary/calculator/", body_content=body,
                            active_path="/salary/", extra_head=extra_head)
    write_page("salary/calculator/index.html", page)
    print(f"  Built: salary/calculator/index.html")


def build_salary_methodology():
    """Generate salary methodology page."""
    title = "Sales Enablement Salary Data Methodology"
    description = "How we collect, clean, and analyze sales enablement salary data. Sources, sample size, and limitations explained."

    crumbs = [("Home", "/"), ("Salary Data", "/salary/"), ("Methodology", None)]

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">METHODOLOGY</div>
        <h1>Salary Data Methodology</h1>
        <p>Transparency about how we collect and analyze enablement compensation data.</p>
    </div>
</div>
<div class="salary-content">
    <h2>Data Sources</h2>
    <p>Our salary data comes from {COMP_DATA['total_records']} sales enablement job postings collected in 2026. We track postings that include "sales enablement," "revenue enablement," and "sales readiness" in the title or description across major job boards and company career pages.</p>

    <h2>Sample Size</h2>
    <ul>
        <li>Total job postings analyzed: {COMP_DATA['total_records']}</li>
        <li>Postings with disclosed salary data: {SALARY_STATS['count_with_salary']} ({COMP_DATA['disclosure_rate']}% disclosure rate)</li>
        <li>Salary range: {fmt_salary(SALARY_STATS['min'])} to {fmt_salary(SALARY_STATS['max'])}</li>
        <li>Median base salary: {fmt_salary(SALARY_STATS['median'])}</li>
        <li>Average base salary: {fmt_salary(int(SALARY_STATS['avg']))}</li>
    </ul>

    <h2>Seniority Classification</h2>
    <p>We classify roles into four seniority levels based on title keywords and job description analysis:</p>
    <ul>
        <li><strong>Entry:</strong> Coordinator, Associate, Specialist, Analyst (0-3 years experience) - {SALARY_BY_SENIORITY['entry']['count']} roles</li>
        <li><strong>Mid-Level:</strong> Manager, Program Manager (3-6 years) - {SALARY_BY_SENIORITY['mid']['count']} roles</li>
        <li><strong>Senior:</strong> Senior Manager, Principal, Lead (6-10 years) - {SALARY_BY_SENIORITY['senior']['count']} roles</li>
        <li><strong>Director/VP:</strong> Director, VP, Head of (10+ years) - {SALARY_BY_SENIORITY['director']['count']} roles</li>
    </ul>

    <h2>Location Classification</h2>
    <p>Metro areas are assigned based on the posted job location. Remote roles are classified separately. Roles listing multiple locations are assigned to the primary listed location. {COMP_DATA['by_metro']['Unknown']['count']} roles did not have a classifiable location and are excluded from metro-specific analysis.</p>

    <h2>Salary Metrics</h2>
    <p>When a job posting lists a salary range (e.g., "$120K - $160K"), we record both the minimum and maximum. Our "average minimum" and "average maximum" metrics represent the average of these figures across all postings in a category. The "median" is the midpoint of all salary midpoints (average of min and max for each posting).</p>

    <h2>Limitations</h2>
    <ul>
        <li>Only {COMP_DATA['disclosure_rate']}% of postings disclose salary data, which may introduce selection bias.</li>
        <li>Companies required by state law to disclose salary (NY, CO, CA, WA) are overrepresented.</li>
        <li>Base salary only. Total compensation (bonus, equity, benefits) is not captured systematically.</li>
        <li>Sample size for individual metros is small (4-28 roles per city), so metro data should be used directionally.</li>
        <li>Job titles are self-reported by companies and may not reflect standardized seniority levels.</li>
    </ul>

    <h2>Update Frequency</h2>
    <p>Data is refreshed as new job postings are collected. The current dataset reflects postings as of {COMP_DATA['generated_at'][:10]}.</p>

    <h2>Related</h2>
    <div class="related-links-grid">
        <a href="/salary/" class="related-link-card">Salary Index</a>
        <a href="/salary/by-seniority/" class="related-link-card">By Seniority</a>
        <a href="/salary/by-location/" class="related-link-card">By Location</a>
    </div>
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/salary/methodology/", body_content=body,
                            active_path="/salary/", extra_head=extra_head)
    write_page("salary/methodology/index.html", page)
    print(f"  Built: salary/methodology/index.html")


def build_salary_comparison_pages():
    """Generate salary comparison pages (enablement vs adjacent roles)."""
    for comp in SALARY_COMPARISONS:
        title = f"{comp['title']} Salary Comparison 2026"
        description = comp['description']

        crumbs = [("Home", "/"), ("Salary Data", "/salary/"), (comp['title'], None)]

        diff = comp['enablement_median'] - comp['other_median']
        diff_pct = int((diff / comp['other_median']) * 100)
        diff_word = "more" if diff > 0 else "less"

        body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">ROLE COMPARISON</div>
        <h1>{comp['title']}</h1>
        <p>How does sales enablement compensation compare to {comp['role'].lower()} roles? Real data from job postings.</p>
    </div>
</div>
<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(comp['enablement_median'])}</span>
        <span class="stat-label">Enablement Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{fmt_salary(comp['other_median'])}</span>
        <span class="stat-label">{comp['role']} Median</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{abs(diff_pct)}% {diff_word}</span>
        <span class="stat-label">Enablement Premium</span>
    </div>
</div>
<div class="salary-content">
    <h2>Salary Comparison</h2>
    <div class="comparison-table-wrap">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Sales Enablement</th>
                    <th>{comp['role']}</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Median Salary</td>
                    <td>{fmt_salary(comp['enablement_median'])}</td>
                    <td>{fmt_salary(comp['other_median'])}</td>
                </tr>
                <tr>
                    <td>Typical Range</td>
                    <td>{fmt_salary(SALARY_STATS['min'])} - {fmt_salary(SALARY_STATS['max'])}</td>
                    <td>{fmt_salary(comp['other_min'])} - {fmt_salary(comp['other_max'])}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <h2>Analysis</h2>
    <p>{comp['analysis']}</p>

    <h2>Other Comparisons</h2>
    <div class="related-links-grid">
''' + "".join(f'        <a href="/salary/{c["slug"]}/" class="related-link-card">{c["title"]}</a>\n' for c in SALARY_COMPARISONS if c["slug"] != comp["slug"]) + '''        <a href="/salary/" class="related-link-card">Salary Index</a>
    </div>
</div>
'''
        body += newsletter_cta_html("Get salary comparison updates.")

        extra_head = get_breadcrumb_schema(crumbs)
        page = get_page_wrapper(title=title, description=description,
                                canonical_path=f"/salary/{comp['slug']}/",
                                body_content=body, active_path="/salary/",
                                extra_head=extra_head)
        write_page(f"salary/{comp['slug']}/index.html", page)
        print(f"  Built: salary/{comp['slug']}/index.html")


def build_tools_index():
    """Generate the tools index page."""
    title = "Sales Enablement Tool Reviews 2026"
    description = (
        "Honest reviews of Highspot, Seismic, Mindtickle, Gong, Showpad, and 15+ more enablement tools."
        " No pay-to-play rankings. Independent analysis based on real job market data."
    )

    crumbs = [("Home", "/"), ("Tools", None)]

    # Featured tools — sorted by mention count
    featured = sorted(TOOL_DATABASE.values(), key=lambda x: x.get("mentions", 0), reverse=True)[:8]
    tool_cards = ""
    for tool in featured:
        mention_text = f" ({tool['mentions']} job mentions)" if tool['mentions'] > 0 else ""
        tool_cards += f'''<a href="/tools/{tool['slug']}-review/" class="preview-card">
    <h3>{tool['name']}</h3>
    <p>{tool['tagline']}{mention_text}</p>
    <span class="preview-link">Read review &rarr;</span>
</a>
'''

    # Category links
    cat_links = ""
    for cat_key, cat in TOOL_CATEGORIES.items():
        cat_links += f'<a href="/tools/category/{cat["slug"]}/" class="related-link-card">{cat["label"]} ({len(cat["tools"])} tools)</a>\n'

    # Comparison links
    comp_links = ""
    for comp in TOOL_COMPARISONS[:6]:
        comp_links += f'<a href="/tools/compare/{comp["slug"]}/" class="comparison-link"><span class="vs-badge">VS</span> {comp["title"]}</a>\n'

    # Roundup links
    roundup_links = ""
    for roundup in TOOL_ROUNDUPS:
        roundup_links += f'<a href="/tools/best/{roundup["slug"]}/" class="related-link-card">{roundup["title"]}</a>\n'

    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Enablement Tool Reviews</h1>
        <p>Practitioner-tested reviews of {len(TOOL_DATABASE)} enablement tools. Rankings based on real job market data from {MARKET_DATA['total_jobs']} postings. No vendor bias, no pay-to-play.</p>
    </div>

    <h2>Most In-Demand Tools</h2>
    <div class="preview-grid">
        {tool_cards}
    </div>

    <h2>Browse by Category</h2>
    <div class="related-links-grid">
        {cat_links}
    </div>

    <h2>Head-to-Head Comparisons</h2>
    <div class="comparison-grid">
        {comp_links}
    </div>

    <h2>Best-Of Roundups</h2>
    <div class="related-links-grid">
        {roundup_links}
    </div>

    <h2>All Tools Reviewed</h2>
    <div class="related-links-grid">
''' + "".join(f'        <a href="/tools/{t["slug"]}-review/" class="related-link-card">{t["name"]}</a>\n' for t in sorted(TOOL_DATABASE.values(), key=lambda x: x["name"])) + '''    </div>
</div>
'''
    body += newsletter_cta_html("Get weekly tool updates.")

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/tools/", body_content=body,
                            active_path="/tools/", extra_head=extra_head)
    write_page("tools/index.html", page)
    print(f"  Built: tools/index.html")


def build_tool_review_pages():
    """Generate individual tool review pages."""
    for tool_key, tool in TOOL_DATABASE.items():
        title = f"{tool['name']} Review 2026: Pricing, Features, Pros and Cons"
        description = f"Independent {tool['name']} review for sales enablement teams. {tool['tagline']} Pricing, features, strengths, weaknesses, and verdict."

        crumbs = [("Home", "/"), ("Tools", "/tools/"), (f"{tool['name']} Review", None)]

        strengths_html = "".join(f"<li>{s}</li>" for s in tool["strengths"])
        weaknesses_html = "".join(f"<li>{w}</li>" for w in tool["weaknesses"])

        mention_section = ""
        if tool["mentions"] > 0:
            mention_section = f'''<div class="tool-mention-badge">
    <span class="mention-count">{tool['mentions']}</span>
    <span class="mention-label">mentions across {MARKET_DATA['total_jobs']} enablement job postings</span>
</div>'''

        # Find related comparisons
        related_comps = [c for c in TOOL_COMPARISONS if tool_key in (c["tool_a"], c["tool_b"])]
        comp_html = ""
        if related_comps:
            comp_html = "<h2>Head-to-Head Comparisons</h2>\n<div class=\"comparison-grid\">\n"
            for c in related_comps:
                comp_html += f'<a href="/tools/compare/{c["slug"]}/" class="comparison-link"><span class="vs-badge">VS</span> {c["title"]}</a>\n'
            comp_html += "</div>\n"

        # Find category peers
        cat = TOOL_CATEGORIES.get(tool["category"], {})
        peer_html = ""
        if cat:
            peers = [TOOL_DATABASE[t] for t in cat.get("tools", []) if t != tool_key and t in TOOL_DATABASE]
            if peers:
                peer_html = f'<h2>Other {cat["label"]} Tools</h2>\n<div class="related-links-grid">\n'
                for p in peers:
                    peer_html += f'<a href="/tools/{p["slug"]}-review/" class="related-link-card">{p["name"]}</a>\n'
                peer_html += '</div>\n'

        rating = tool.get("rating", {})
        rating_html = ""
        if rating:
            rating_html = f'''<div class="tool-rating">
    <span class="rating-value">{rating["value"]}/5</span>
    <span class="rating-count">({rating["count"]} reviews)</span>
</div>'''

        schema_data = {
            "name": tool["name"],
            "description": tool["tagline"],
            "category": "BusinessApplication",
            "os": "Web",
            "url": tool["url"],
            "price_range": tool["pricing"],
        }
        if rating:
            schema_data["rating"] = {"value": rating["value"], "count": rating["count"]}

        body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">{tool['category_label'].upper()} TOOL</div>
        <h1>{tool['name']} Review</h1>
        <p>{tool['tagline']}</p>
        {mention_section}
        {rating_html}
    </div>
</div>
<div class="salary-content">
    <h2>Overview</h2>
    <div class="tool-overview-grid">
        <div class="tool-detail"><strong>Founded:</strong> {tool['founded']}</div>
        <div class="tool-detail"><strong>HQ:</strong> {tool['hq']}</div>
        <div class="tool-detail"><strong>Employees:</strong> {tool['employees']}</div>
        <div class="tool-detail"><strong>Category:</strong> {tool['category_label']}</div>
        <div class="tool-detail"><strong>Pricing:</strong> {tool['pricing']}</div>
        <div class="tool-detail"><strong>Best For:</strong> {tool['best_for']}</div>
    </div>

    <h2>Strengths</h2>
    <ul class="pros-list">{strengths_html}</ul>

    <h2>Weaknesses</h2>
    <ul class="cons-list">{weaknesses_html}</ul>

    <h2>Verdict</h2>
    <p>{tool['verdict']}</p>

    {comp_html}
    {peer_html}

    <h2>Related</h2>
    <div class="related-links-grid">
        <a href="/tools/category/{tool['category']}/" class="related-link-card">{tool['category_label']} Tools</a>
        <a href="/tools/" class="related-link-card">All Tool Reviews</a>
    </div>
</div>
'''
        body += newsletter_cta_html(f"Get updates on {tool['name']} and other tools.")

        extra_head = get_breadcrumb_schema(crumbs)
        extra_head += get_software_application_schema(schema_data)

        page = get_page_wrapper(title=title, description=description,
                                canonical_path=f"/tools/{tool['slug']}-review/",
                                body_content=body, active_path="/tools/",
                                extra_head=extra_head)
        write_page(f"tools/{tool['slug']}-review/index.html", page)
        print(f"  Built: tools/{tool['slug']}-review/index.html")


def build_tool_category_pages():
    """Generate tool category pages."""
    for cat_key, cat in TOOL_CATEGORIES.items():
        tools_in_cat = [TOOL_DATABASE[t] for t in cat["tools"] if t in TOOL_DATABASE]
        title = f"Best {cat['label']} Tools for Sales Enablement 2026"
        description = f"Reviews of {len(tools_in_cat)} {cat['label'].lower()} tools for sales enablement. {cat['description']}"

        crumbs = [("Home", "/"), ("Tools", "/tools/"), (cat["label"], None)]

        tool_cards = ""
        for tool in sorted(tools_in_cat, key=lambda x: x.get("mentions", 0), reverse=True):
            mention_text = f" | {tool['mentions']} job mentions" if tool['mentions'] > 0 else ""
            rating = tool.get("rating", {})
            rating_text = f" | {rating['value']}/5" if rating else ""
            tool_cards += f'''<a href="/tools/{tool['slug']}-review/" class="salary-index-card">
    <h3>{tool['name']}</h3>
    <div class="card-range">{tool['pricing']}</div>
    <p>{tool['tagline']}{mention_text}{rating_text}</p>
</a>
'''

        # Related comparisons within this category
        cat_tools = set(cat["tools"])
        related_comps = [c for c in TOOL_COMPARISONS if c["tool_a"] in cat_tools or c["tool_b"] in cat_tools]
        comp_html = ""
        if related_comps:
            comp_html = "<h2>Head-to-Head Comparisons</h2>\n<div class=\"comparison-grid\">\n"
            for c in related_comps:
                comp_html += f'<a href="/tools/compare/{c["slug"]}/" class="comparison-link"><span class="vs-badge">VS</span> {c["title"]}</a>\n'
            comp_html += "</div>\n"

        body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">{cat['label'].upper()}</div>
        <h1>{cat['label']} Tools</h1>
        <p>{cat['description']}</p>
    </div>
</div>
<div class="salary-content">
    <div class="salary-index-grid">
        {tool_cards}
    </div>

    {comp_html}

    <h2>Other Categories</h2>
    <div class="related-links-grid">
''' + "".join(f'        <a href="/tools/category/{c["slug"]}/" class="related-link-card">{c["label"]}</a>\n' for ck, c in TOOL_CATEGORIES.items() if ck != cat_key) + '''    </div>
</div>
'''
        body += newsletter_cta_html(f"Get {cat['label'].lower()} tool updates.")

        extra_head = get_breadcrumb_schema(crumbs)
        page = get_page_wrapper(title=title, description=description,
                                canonical_path=f"/tools/category/{cat['slug']}/",
                                body_content=body, active_path="/tools/",
                                extra_head=extra_head)
        write_page(f"tools/category/{cat['slug']}/index.html", page)
        print(f"  Built: tools/category/{cat['slug']}/index.html")


def build_tool_comparison_pages():
    """Generate tool comparison pages."""
    for comp in TOOL_COMPARISONS:
        tool_a = TOOL_DATABASE.get(comp["tool_a"], {})
        tool_b = TOOL_DATABASE.get(comp["tool_b"], {})
        if not tool_a or not tool_b:
            continue

        title = f"{comp['title']} Comparison 2026: Features, Pricing, Verdict"
        description = comp["description"]

        crumbs = [("Home", "/"), ("Tools", "/tools/"), (comp["title"], None)]

        rating_a = tool_a.get("rating", {})
        rating_b = tool_b.get("rating", {})

        body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">TOOL COMPARISON</div>
        <h1>{comp['title']}</h1>
        <p>{comp['description']}</p>
    </div>
</div>
<div class="salary-stats">
    <div class="salary-stat-card">
        <span class="stat-value">{tool_a['mentions']}</span>
        <span class="stat-label">{tool_a['name']} Job Mentions</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">VS</span>
        <span class="stat-label">Head to Head</span>
    </div>
    <div class="salary-stat-card">
        <span class="stat-value">{tool_b['mentions']}</span>
        <span class="stat-label">{tool_b['name']} Job Mentions</span>
    </div>
</div>
<div class="salary-content">
    <h2>Quick Comparison</h2>
    <div class="comparison-table-wrap">
        <table class="data-table">
            <thead>
                <tr><th></th><th>{tool_a['name']}</th><th>{tool_b['name']}</th></tr>
            </thead>
            <tbody>
                <tr><td>Founded</td><td>{tool_a['founded']}</td><td>{tool_b['founded']}</td></tr>
                <tr><td>HQ</td><td>{tool_a['hq']}</td><td>{tool_b['hq']}</td></tr>
                <tr><td>Employees</td><td>{tool_a['employees']}</td><td>{tool_b['employees']}</td></tr>
                <tr><td>Pricing</td><td>{tool_a['pricing']}</td><td>{tool_b['pricing']}</td></tr>
                <tr><td>Category</td><td>{tool_a['category_label']}</td><td>{tool_b['category_label']}</td></tr>
                <tr><td>Rating</td><td>{rating_a.get('value', 'N/A')}/5 ({rating_a.get('count', 'N/A')} reviews)</td><td>{rating_b.get('value', 'N/A')}/5 ({rating_b.get('count', 'N/A')} reviews)</td></tr>
                <tr><td>Job Mentions</td><td>{tool_a['mentions']}</td><td>{tool_b['mentions']}</td></tr>
                <tr><td>Best For</td><td>{tool_a['best_for']}</td><td>{tool_b['best_for']}</td></tr>
            </tbody>
        </table>
    </div>

    <h2>{tool_a['name']} Strengths</h2>
    <ul>{"".join(f"<li>{s}</li>" for s in tool_a['strengths'])}</ul>

    <h2>{tool_b['name']} Strengths</h2>
    <ul>{"".join(f"<li>{s}</li>" for s in tool_b['strengths'])}</ul>

    <h2>Our Take</h2>
    <p>{comp['summary']}</p>

    <h2>Read Full Reviews</h2>
    <div class="related-links-grid">
        <a href="/tools/{tool_a['slug']}-review/" class="related-link-card">{tool_a['name']} Review</a>
        <a href="/tools/{tool_b['slug']}-review/" class="related-link-card">{tool_b['name']} Review</a>
    </div>

    <h2>Other Comparisons</h2>
    <div class="comparison-grid">
''' + "".join(f'        <a href="/tools/compare/{c["slug"]}/" class="comparison-link"><span class="vs-badge">VS</span> {c["title"]}</a>\n' for c in TOOL_COMPARISONS if c["slug"] != comp["slug"]) + '''    </div>
</div>
'''
        body += newsletter_cta_html("Get tool comparison updates.")

        extra_head = get_breadcrumb_schema(crumbs)
        page = get_page_wrapper(title=title, description=description,
                                canonical_path=f"/tools/compare/{comp['slug']}/",
                                body_content=body, active_path="/tools/",
                                extra_head=extra_head)
        write_page(f"tools/compare/{comp['slug']}/index.html", page)
        print(f"  Built: tools/compare/{comp['slug']}/index.html")


def build_tool_roundup_pages():
    """Generate best-of roundup pages."""
    for roundup in TOOL_ROUNDUPS:
        tools_in_roundup = [TOOL_DATABASE[t] for t in roundup["tools"] if t in TOOL_DATABASE]
        title = roundup["title"]
        description = roundup["description"]

        crumbs = [("Home", "/"), ("Tools", "/tools/"), (title, None)]

        tool_sections = ""
        for i, tool in enumerate(tools_in_roundup, 1):
            rating = tool.get("rating", {})
            rating_text = f"{rating['value']}/5 ({rating['count']} reviews)" if rating else "N/A"
            mention_text = f"{tool['mentions']} job mentions" if tool['mentions'] > 0 else "Niche tool"

            tool_sections += f'''
    <div class="roundup-entry">
        <h3>{i}. {tool['name']}</h3>
        <div class="roundup-meta">
            <span>{rating_text}</span> | <span>{mention_text}</span> | <span>{tool['pricing']}</span>
        </div>
        <p><strong>Best for:</strong> {tool['best_for']}</p>
        <p>{tool['verdict']}</p>
        <a href="/tools/{tool['slug']}-review/" class="preview-link">Read full review &rarr;</a>
    </div>
'''

        body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">BEST-OF ROUNDUP</div>
        <h1>{title}</h1>
        <p>{roundup['intro']}</p>
    </div>
</div>
<div class="salary-content">
    {tool_sections}

    <h2>Other Roundups</h2>
    <div class="related-links-grid">
''' + "".join(f'        <a href="/tools/best/{r["slug"]}/" class="related-link-card">{r["title"]}</a>\n' for r in TOOL_ROUNDUPS if r["slug"] != roundup["slug"]) + '''    </div>
</div>
'''
        body += newsletter_cta_html("Get weekly tool roundups.")

        extra_head = get_breadcrumb_schema(crumbs)
        page = get_page_wrapper(title=title, description=description,
                                canonical_path=f"/tools/best/{roundup['slug']}/",
                                body_content=body, active_path="/tools/",
                                extra_head=extra_head)
        write_page(f"tools/best/{roundup['slug']}/index.html", page)
        print(f"  Built: tools/best/{roundup['slug']}/index.html")


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
    build_salary_seniority_index()
    build_salary_seniority_pages()
    build_salary_location_index()
    build_salary_location_pages()
    build_salary_remote_vs_onsite()
    build_salary_calculator()
    build_salary_methodology()
    build_salary_comparison_pages()

    print("\n  Building tool pages...")
    build_tools_index()
    build_tool_review_pages()
    build_tool_category_pages()
    build_tool_comparison_pages()
    build_tool_roundup_pages()

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
