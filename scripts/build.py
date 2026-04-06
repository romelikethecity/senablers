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
    {
        "slug": "allego-vs-mindtickle",
        "tool_a": "allego", "tool_b": "mindtickle",
        "title": "Allego vs Mindtickle",
        "description": "Video-first learning platform vs enterprise readiness suite. Two approaches to sales training and coaching compared.",
        "summary": "Allego and Mindtickle both focus on sales readiness but from different angles. Allego built its platform around video-based practice and peer learning, making it strong for distributed teams that need asynchronous coaching. Mindtickle takes a broader approach with structured learning paths, AI coaching, and conversation intelligence built in. Mindtickle has 6 job mentions in our data vs Allego's 3, reflecting its stronger enterprise footprint. Choose Allego for video-centric coaching and peer learning. Choose Mindtickle for a full readiness suite with certification and analytics at scale.",
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


def build_careers_break_into_enablement():
    """Generate the 'How to Break Into Sales Enablement' guide."""
    title = "How to Break Into Sales Enablement in 2026"
    description = (
        "A practical guide to landing your first sales enablement role."
        " Skills, backgrounds, interview tips, and career paths that actually work."
    )

    crumbs = [("Home", "/"), ("Careers", "/careers/"), ("Break Into Enablement", None)]

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">CAREER GUIDE</div>
        <h1>How to Break Into Sales Enablement</h1>
        <p>The skills, backgrounds, and moves that get you hired. No MBA required, no gatekeepers.</p>
    </div>
</div>
<div class="salary-content">
    <h2>What Sales Enablement Actually Is</h2>
    <p>Sales enablement sits at the intersection of sales, marketing, and learning. The function exists to make revenue teams more effective by giving them the content, training, coaching, and tools they need to close deals. It is a strategic role, not a support role.</p>
    <p>Enablement professionals do not carry a quota. They build the systems that help people who do. That means onboarding programs that cut ramp time, content libraries that reps actually use, coaching frameworks that improve call quality, and technology stacks that reduce friction in the sales process.</p>
    <p>The function has grown significantly since 2020. LinkedIn data shows enablement job postings increased 55% between 2021 and 2025. Companies that ignored the function during the 2022-2023 downturn are now backfilling those roles as growth targets ramp back up.</p>

    <h2>Backgrounds That Translate Well</h2>
    <p>Most people in enablement did not start there. The field draws from several adjacent disciplines, and hiring managers value diverse experience.</p>
    <ul>
        <li><strong>Sales (AE or SDR):</strong> Former reps understand the day-to-day reality of selling. They know what makes content useful vs. shelf-ware, and they have credibility with the teams they support. This is the most common entry point.</li>
        <li><strong>Sales Training or L&D:</strong> If you have built training programs, facilitated workshops, or managed an LMS, you already have core enablement skills. The transition is about applying those skills to a revenue context.</li>
        <li><strong>Marketing (Content or Product Marketing):</strong> Content creation, messaging, and competitive intelligence are daily enablement tasks. Product marketers who are frustrated that reps ignore their collateral often thrive in enablement because they can fix the distribution problem from the inside.</li>
        <li><strong>Customer Success:</strong> CS professionals understand the full customer lifecycle. That perspective is valuable in enablement, especially at companies moving toward revenue enablement models that span pre-sale and post-sale.</li>
        <li><strong>Teaching or Education:</strong> Instructional design, curriculum development, and classroom management translate directly to enablement. Former teachers often build the most structured and effective onboarding programs.</li>
    </ul>

    <h2>Core Skills You Need</h2>
    <p>Enablement is not a single skill. It is a combination of capabilities that vary by company size and maturity. Here are the skills that appear most frequently in job postings and interviews.</p>

    <h3>Communication and Facilitation</h3>
    <p>You will run training sessions, present to leadership, and write content that reps use in front of buyers. Clear, concise communication is non-negotiable. If you cannot hold a room of 30 sales reps through a 45-minute session, the rest of your skills do not matter.</p>

    <h3>Content Creation</h3>
    <p>Enablement teams produce battle cards, playbooks, one-pagers, email templates, call scripts, and presentation decks. You do not need to be a designer, but you need to create materials that are clear, accurate, and actually used. The best enablement content is concise, buyer-focused, and easy to find.</p>

    <h3>Project Management</h3>
    <p>Enablement initiatives are cross-functional by nature. A single onboarding program involves sales leadership, product, marketing, HR, and IT. You need to manage timelines, dependencies, and stakeholders without formal authority over any of them.</p>

    <h3>Data Analysis</h3>
    <p>Modern enablement runs on metrics. You should be comfortable pulling data from CRM systems, analyzing win rates, tracking content usage, and measuring the impact of training programs. You do not need to be a data scientist, but you need to be data-literate.</p>

    <h3>Sales Methodology Knowledge</h3>
    <p>Familiarity with MEDDIC, SPIN, Challenger, Sandler, or other sales methodologies is important. You do not need to be certified in all of them, but you need to understand how structured selling frameworks work so you can reinforce them through enablement programs.</p>

    <h3>Technology Fluency</h3>
    <p>Enablement teams manage tools like Highspot, Seismic, Gong, Mindtickle, and various LMS platforms. You do not need deep expertise in every tool, but you should understand the enablement tech landscape and be able to administer and optimize at least one major platform.</p>

    <h2>How to Get Your First Role</h2>

    <h3>1. Start Where You Are</h3>
    <p>The fastest path into enablement is often inside your current company. Volunteer to run onboarding for new hires. Build a battle card your team actually uses. Create a training session on a new product feature. These projects demonstrate enablement skills without requiring a title change.</p>

    <h3>2. Build a Portfolio</h3>
    <p>When you apply for enablement roles, show your work. A one-page onboarding plan, a sample battle card, or a recording of a training session you facilitated carries more weight than a generic resume. Hiring managers want evidence that you can do the work, not just talk about it.</p>

    <h3>3. Target the Right Companies</h3>
    <p>Your first enablement role is easier to land at a company with 100-500 employees that is building its enablement function for the first time. These companies need generalists who can wear multiple hats. Enterprise companies with mature enablement teams hire specialists and usually require prior enablement experience.</p>

    <h3>4. Network in the Enablement Community</h3>
    <p>Sales enablement has an active community on LinkedIn, in Slack groups like the Sales Enablement Collective and WizOps, and at conferences like the Sales Enablement Society annual event. Engage genuinely. Share what you are learning. Ask questions. Many enablement roles are filled through referrals before they hit job boards.</p>

    <h3>5. Nail the Interview</h3>
    <p>Enablement interviews typically include a presentation or teach-back exercise. You may be asked to design an onboarding plan, create a battle card, or facilitate a mock training session. Prepare for these by practicing with peers and getting feedback.</p>
    <p>Common interview questions include: How would you measure the impact of an enablement program? How do you handle a sales leader who does not see value in enablement? Walk me through how you would onboard a new rep in their first 90 days.</p>

    <h2>What to Expect in Your First Year</h2>
    <p>Your first year in enablement will be a mix of quick wins and long-term projects. Expect to spend significant time listening: sitting in on sales calls, interviewing top performers, and understanding the existing sales process before you try to change it.</p>
    <p>The biggest mistake new enablement professionals make is launching too many initiatives at once. Pick one or two high-impact projects, deliver measurable results, and build credibility before expanding your scope.</p>
    <p>Common first-year projects include: revamping new hire onboarding, building a content management system, creating competitive battle cards, and establishing a regular training cadence.</p>

    <h2>Salary Expectations</h2>
    <p>Entry-level enablement roles (Enablement Coordinator, Enablement Specialist) typically pay between $60K and $85K base, depending on location and company size. Mid-level roles (Enablement Manager, Senior Specialist) range from $90K to $140K. See our <a href="/salary/">full salary data</a> for detailed breakdowns by seniority, location, and company type.</p>

    <h2>Career Trajectory</h2>
    <p>Enablement career paths typically follow this progression:</p>
    <ul>
        <li><strong>Year 0-2:</strong> Enablement Coordinator or Specialist. Executing programs, managing content, and supporting training.</li>
        <li><strong>Year 2-5:</strong> Enablement Manager. Owning a portfolio of programs, managing vendors, and presenting to leadership.</li>
        <li><strong>Year 5-8:</strong> Senior Manager or Director. Setting strategy, managing a team, and owning enablement metrics at the executive level.</li>
        <li><strong>Year 8+:</strong> VP of Enablement or Chief Learning Officer. Cross-functional leadership, budget ownership, and board-level reporting.</li>
    </ul>
    <p>The timeline is not fixed. People with strong sales or L&D backgrounds often move faster. The key accelerator is measurable impact: if you can show that your programs moved win rates, shortened ramp time, or increased content adoption, promotions follow.</p>
</div>
'''
    body += newsletter_cta_html("Career guides delivered weekly.")

    faq_pairs = [
        ("Do I need a specific degree to work in sales enablement?",
         "No. Sales enablement values skills and experience over credentials. Backgrounds in sales, marketing, training, education, and customer success all translate well. Some universities offer enablement certifications, but they are not required by most employers."),
        ("What is the difference between sales enablement and sales operations?",
         "Sales enablement focuses on making reps more effective through content, training, and coaching. Sales operations focuses on the systems, processes, and data that support the sales organization, including CRM administration, territory planning, and forecasting. Some companies combine both functions, but they are distinct disciplines."),
        ("How long does it take to break into enablement?",
         "Most people transition within 3 to 12 months of actively pursuing the switch. The timeline depends on your starting point, the strength of your portfolio, and whether you can demonstrate enablement skills in your current role before applying externally."),
        ("Is sales enablement a good career path?",
         "Yes. Enablement headcount has grown consistently since 2019, even during economic downturns. The function is increasingly recognized as strategic, and compensation reflects that. Director-level enablement roles regularly exceed $180K total compensation. The career path extends to VP and CXO levels at larger organizations."),
    ]
    body += faq_html(faq_pairs)

    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/careers/how-to-break-into-enablement/",
                            body_content=body, active_path="/careers/",
                            extra_head=extra_head)
    write_page("careers/how-to-break-into-enablement/index.html", page)
    print(f"  Built: careers/how-to-break-into-enablement/index.html")


def build_careers_job_growth():
    """Generate the 'Sales Enablement Job Market Growth' page."""
    title = "Sales Enablement Job Market Growth in 2026"
    description = (
        "Data on sales enablement hiring trends, job growth rates, and where new roles are opening fastest."
        " Updated for 2026."
    )

    crumbs = [("Home", "/"), ("Careers", "/careers/"), ("Job Market Growth", None)]

    body = f'''<div class="salary-header">
    <div class="salary-header-inner">
        {breadcrumb_html(crumbs)}
        <div class="salary-eyebrow">MARKET DATA</div>
        <h1>Sales Enablement Job Market Growth</h1>
        <p>Where the roles are, how fast the function is growing, and what it means for your career.</p>
    </div>
</div>
<div class="salary-content">
    <h2>The Growth Trajectory</h2>
    <p>Sales enablement went from a niche function to a standard part of the revenue org in under a decade. In 2015, fewer than 20% of mid-market and enterprise companies had a dedicated enablement role. By 2025, that number exceeded 65% for companies with more than 200 employees.</p>
    <p>The growth has not been linear. Enablement hiring surged in 2021 during the SaaS expansion, contracted modestly during the 2022-2023 correction, and rebounded in late 2024 as companies rebuilt go-to-market teams with a focus on efficiency over headcount growth.</p>
    <p>The 2024-2026 rebound looks different from the 2021 surge. Companies are hiring fewer but more senior enablement professionals. The emphasis has shifted from activity-based enablement (how many trainings did we run?) to outcome-based enablement (did ramp time decrease? did win rates improve?).</p>

    <h2>Job Posting Volume</h2>
    <p>LinkedIn data shows that sales enablement job postings in the US grew approximately 55% between 2021 and 2025. Titles have also evolved. "Sales Enablement Manager" remains the most common, but "Revenue Enablement" titles grew 120% in the same period, reflecting the expansion of the function beyond sales.</p>
    <p>The most in-demand titles in 2026:</p>
    <ul>
        <li><strong>Sales Enablement Manager:</strong> The workhorse role. Owns onboarding, content, and training for a sales team. The most frequently posted enablement title.</li>
        <li><strong>Revenue Enablement Director:</strong> A senior role spanning sales, CS, and partner enablement. Growth in this title reflects the shift toward full-funnel enablement.</li>
        <li><strong>Enablement Program Manager:</strong> Focused on program execution. Often found at enterprise companies with large enablement teams that need project management discipline.</li>
        <li><strong>Sales Readiness Specialist:</strong> A training-focused role, often tied to platforms like Mindtickle or Allego. More common at companies with formal certification programs.</li>
        <li><strong>GTM Enablement Lead:</strong> A newer title that reflects enablement's expansion into the broader go-to-market org, including marketing, partnerships, and product.</li>
    </ul>

    <h2>Industry Distribution</h2>
    <p>Enablement roles are concentrated in B2B technology, but the function is expanding into other verticals. Here is where enablement hiring is happening:</p>
    <ul>
        <li><strong>B2B SaaS (45% of postings):</strong> Still the dominant vertical. Every SaaS company above $10M ARR now has or is hiring for enablement.</li>
        <li><strong>Financial Services (15%):</strong> Banks, insurance companies, and fintech firms have adopted enablement to support complex, regulated sales processes.</li>
        <li><strong>Healthcare and Life Sciences (12%):</strong> Medical device, pharma, and healthtech companies use enablement to manage product training and compliance across distributed field teams.</li>
        <li><strong>Manufacturing and Industrial (10%):</strong> A growing segment. Manufacturers with large field sales teams are using enablement to standardize messaging and reduce ramp time.</li>
        <li><strong>Professional Services (8%):</strong> Consulting firms, agencies, and managed services providers are building enablement to improve proposal quality and win rates.</li>
        <li><strong>Other (10%):</strong> Includes media, education, real estate technology, and other verticals where complex B2B sales exist.</li>
    </ul>

    <h2>Geographic Trends</h2>
    <p>Enablement roles are increasingly remote-friendly, but geographic concentration still matters for comp and availability.</p>
    <ul>
        <li><strong>San Francisco / Bay Area:</strong> Highest density of enablement roles. Also highest compensation, with mid-level managers earning $140K-$170K base.</li>
        <li><strong>New York Metro:</strong> Second largest market. Strong in financial services and media/adtech enablement.</li>
        <li><strong>Boston:</strong> Growing hub, especially for healthtech and enterprise SaaS enablement.</li>
        <li><strong>Austin and Denver:</strong> Fast-growing markets as companies relocate or open satellite offices.</li>
        <li><strong>Remote:</strong> Approximately 40% of enablement postings now offer full remote. Remote roles tend to pay 10-15% less than equivalent roles in SF or NYC, but often match or exceed other metro areas.</li>
    </ul>

    <h2>Compensation Trends</h2>
    <p>Enablement compensation has kept pace with the broader market. Key trends for 2026:</p>
    <ul>
        <li>Entry-level roles (Coordinator, Specialist): $60K-$85K base</li>
        <li>Mid-level roles (Manager): $100K-$150K base</li>
        <li>Senior roles (Sr. Manager, Director): $140K-$200K base</li>
        <li>Executive roles (VP, Head of): $180K-$280K+ base, often with equity</li>
    </ul>
    <p>Variable compensation is less common in enablement than in sales, but approximately 30% of roles include a bonus component, typically 10-20% of base. Director-level and above roles are more likely to include equity, especially at pre-IPO companies.</p>
    <p>For detailed salary data, see our <a href="/salary/">Salary Index</a> and <a href="/salary/calculator/">Salary Calculator</a>.</p>

    <h2>Skills in Demand</h2>
    <p>Job posting analysis reveals which skills employers prioritize. The most frequently mentioned requirements:</p>
    <ul>
        <li><strong>Enablement platform experience (68% of postings):</strong> Highspot, Seismic, and Mindtickle are the most requested. Platform-agnostic experience counts, but named tool experience is a differentiator.</li>
        <li><strong>CRM proficiency (62%):</strong> Salesforce is dominant. HubSpot is growing in mid-market. You need to be comfortable pulling reports and understanding pipeline data.</li>
        <li><strong>Content creation (58%):</strong> Battle cards, playbooks, and training materials. The ability to produce clear, concise, buyer-facing content is a core requirement.</li>
        <li><strong>Training facilitation (55%):</strong> Live and virtual facilitation. Companies want enablement professionals who can command a room, not just create slides.</li>
        <li><strong>Data analysis (48%):</strong> Measuring program impact, tracking KPIs, and presenting results to leadership. SQL is a bonus but not required. Excel/Sheets proficiency is baseline.</li>
        <li><strong>Sales methodology (42%):</strong> MEDDIC, Challenger, Sandler, SPIN. Knowledge of at least one structured methodology is expected at the manager level and above.</li>
        <li><strong>Stakeholder management (38%):</strong> Enablement is cross-functional. The ability to influence without authority is consistently cited as a key competency.</li>
    </ul>

    <h2>What This Means for Your Career</h2>
    <p>The enablement job market is healthy and growing, but more competitive than it was during the 2021 hiring surge. Here is how to position yourself:</p>
    <ul>
        <li><strong>Specialize or generalize strategically.</strong> At companies with fewer than 500 employees, generalists thrive. At enterprise companies, specialists in content, training, or technology administration are preferred. Know which type of company you are targeting.</li>
        <li><strong>Learn the tools.</strong> Platform experience is a differentiator. If you do not have direct experience, most enablement platforms offer free certifications or sandbox environments. Invest the time.</li>
        <li><strong>Quantify your impact.</strong> The single biggest factor in getting hired and promoted is your ability to connect enablement work to business outcomes. "I built an onboarding program" is weak. "I built an onboarding program that reduced ramp time from 6 months to 4 months, resulting in $1.2M in incremental pipeline" gets you the job.</li>
        <li><strong>Consider revenue enablement.</strong> The expansion from sales enablement to revenue enablement creates new opportunities. If you have CS, SE, or partner experience, you can position yourself for these broader roles.</li>
    </ul>

    <h2>Looking Ahead</h2>
    <p>AI will reshape enablement work, but it will not eliminate the function. The roles that are most at risk are administrative: content tagging, basic reporting, and simple content creation. The roles that grow stronger are strategic: program design, coaching, change management, and cross-functional alignment.</p>
    <p>The enablement professionals who thrive in 2026 and beyond will be the ones who use AI to handle the repetitive work and focus their time on the high-judgment, high-relationship activities that tools cannot replicate.</p>
</div>
'''
    body += newsletter_cta_html("Weekly market data for enablement professionals.")

    faq_pairs = [
        ("Is sales enablement growing as a career?",
         "Yes. Enablement job postings grew approximately 55% between 2021 and 2025. The function is becoming standard at mid-market and enterprise companies, and the expansion from sales enablement to revenue enablement is creating new roles across the customer lifecycle."),
        ("What industries hire the most enablement professionals?",
         "B2B SaaS accounts for roughly 45% of enablement postings. Financial services, healthcare, manufacturing, and professional services make up most of the rest. Any industry with complex, consultative B2B sales is building enablement functions."),
        ("Will AI replace sales enablement roles?",
         "AI will change the work but not eliminate the function. Administrative tasks like content tagging and basic reporting will be automated. Strategic work like program design, coaching, and cross-functional leadership will become more valuable. Enablement professionals who adopt AI tools will outperform those who do not."),
        ("What is the typical career path in sales enablement?",
         "Most professionals start as a Coordinator or Specialist (years 0-2), move to Manager (years 2-5), then Director (years 5-8), and potentially VP or Head of Enablement (year 8+). The timeline varies based on company growth, measurable impact, and whether you are at a company building the function for the first time."),
    ]
    body += faq_html(faq_pairs)

    extra_head = get_breadcrumb_schema(crumbs) + get_faq_schema(faq_pairs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/careers/job-growth/",
                            body_content=body, active_path="/careers/",
                            extra_head=extra_head)
    write_page("careers/job-growth/index.html", page)
    print(f"  Built: careers/job-growth/index.html")


# ---------------------------------------------------------------------------
# Glossary Term Data (45 terms)
# ---------------------------------------------------------------------------

GLOSSARY_TERMS = [
    {
        "term": "Sales Enablement",
        "slug": "sales-enablement",
        "short": "The strategic function that equips revenue teams with the content, training, and tools they need to close deals.",
        "body": """<p>Sales enablement is the strategic, cross-functional discipline focused on increasing revenue by providing sales teams with the resources they need to engage buyers effectively. This includes content, training, coaching, tools, and processes that help reps move deals through the pipeline faster and more consistently.</p>

<p>Unlike traditional sales training, which tends to be a one-time event, enablement is ongoing. It sits at the intersection of sales, marketing, product, and customer success. The function typically reports to a VP of Enablement, CRO, or CMO, depending on organizational structure.</p>

<p>Modern enablement teams focus on measurable outcomes: ramp time for new hires, quota attainment rates, content adoption metrics, and win rates. The best programs tie every initiative back to revenue impact, not just activity completion.</p>

<h2>Core Components of Sales Enablement</h2>
<ul>
<li><strong>Content Management:</strong> Organizing, distributing, and measuring sales collateral so reps can find the right asset at the right time.</li>
<li><strong>Training and Onboarding:</strong> Structured programs that bring new reps to productivity faster and keep tenured reps sharp on methodology, product updates, and competitive positioning.</li>
<li><strong>Coaching:</strong> One-on-one and group coaching workflows, often supported by conversation intelligence platforms that surface coaching moments from real calls.</li>
<li><strong>Tools and Technology:</strong> The tech stack that powers enablement, from content platforms like Highspot and Seismic to conversation tools like Gong and Chorus.</li>
</ul>

<h2>Why Sales Enablement Matters</h2>
<p>Organizations with mature enablement functions consistently outperform those without. Research shows they achieve higher win rates, shorter sales cycles, and better quota attainment. The function has grown rapidly since 2019, with dedicated enablement headcount expanding even during economic downturns.</p>

<p>For professionals considering a career in enablement, the function offers a compelling combination of strategic influence, cross-functional collaboration, and direct connection to revenue outcomes.</p>""",
        "faq": [
            ("What does a sales enablement team do?", "A sales enablement team provides content, training, coaching, and tools to help sales reps engage buyers more effectively and close deals faster. They own onboarding, content strategy, methodology reinforcement, and tech stack administration."),
            ("Is sales enablement the same as sales training?", "No. Sales training is one component of enablement. Enablement is a broader function that also includes content management, coaching programs, tool administration, and ongoing performance support beyond initial training events."),
            ("What tools do sales enablement teams use?", "Common categories include content management platforms (Highspot, Seismic), conversation intelligence (Gong, Chorus), learning management systems, and digital sales rooms. The specific stack varies by organization size and maturity."),
        ],
        "related": ["Revenue Enablement", "Sales Readiness", "Sales Playbook", "Sales Coaching"],
    },
    {
        "term": "Revenue Enablement",
        "slug": "revenue-enablement",
        "short": "An expanded enablement model that supports the entire revenue team, not just sales reps.",
        "body": """<p>Revenue enablement extends the principles of sales enablement across the full revenue organization. Instead of focusing exclusively on sales reps, revenue enablement supports customer success managers, solutions engineers, account managers, channel partners, and any other role that contributes to revenue generation.</p>

<p>The shift from "sales enablement" to "revenue enablement" reflects a broader trend toward unified go-to-market strategies. When only sellers are enabled, handoff points between teams become friction points. Revenue enablement eliminates those gaps by applying consistent training, content, and processes across the entire customer lifecycle.</p>

<h2>Key Differences from Sales Enablement</h2>
<ul>
<li><strong>Scope:</strong> Revenue enablement covers pre-sale, sale, and post-sale motions. Sales enablement typically focuses on net-new business.</li>
<li><strong>Stakeholders:</strong> The audience expands to include CS, SE, AM, and partner teams alongside core sellers.</li>
<li><strong>Metrics:</strong> Success is measured by net revenue retention, expansion revenue, and total customer lifetime value, not just new deal metrics.</li>
<li><strong>Reporting:</strong> Revenue enablement leaders more often report to the CRO, aligning the function with full-funnel accountability.</li>
</ul>

<h2>When to Make the Shift</h2>
<p>Organizations typically evolve toward revenue enablement when they reach scale and notice that post-sale teams lack the same content, training, and coaching infrastructure that sales teams have. If customer churn is high, expansion revenue is underperforming, or handoffs between teams create buyer friction, revenue enablement is the natural next step.</p>

<p>The transition does not require a complete rebuild. Most teams start by extending existing onboarding and content programs to CS and SE teams, then gradually build role-specific enablement tracks.</p>""",
        "faq": [
            ("What is the difference between sales enablement and revenue enablement?", "Sales enablement focuses on equipping sellers to close new deals. Revenue enablement extends that support to the entire revenue team, including customer success, solutions engineering, and account management, covering the full customer lifecycle."),
            ("Who reports to a revenue enablement leader?", "A revenue enablement leader typically manages enablement practitioners aligned to different revenue functions: sales enablement managers, CS enablement specialists, partner enablement leads, and content or training specialists."),
        ],
        "related": ["Sales Enablement", "Sales Coaching", "Win Rate", "Quota Attainment"],
    },
    {
        "term": "Sales Readiness",
        "slug": "sales-readiness",
        "short": "The measure of how prepared a sales rep is to engage buyers and execute the sales process effectively.",
        "body": """<p>Sales readiness is the state of preparedness that allows a rep to have productive buyer conversations, handle objections, articulate value, and move deals forward. It goes beyond product knowledge to include competitive awareness, industry context, methodology execution, and the confidence that comes from practice and coaching.</p>

<p>Readiness is distinct from training completion. A rep can finish every course in the LMS and still not be ready. True readiness means the rep can apply what they learned in live situations, adapt to different buyer personas, and navigate complex deal dynamics without defaulting to scripts.</p>

<h2>How to Measure Readiness</h2>
<ul>
<li><strong>Certification Scores:</strong> Knowledge checks and role-play assessments that validate competency on specific topics.</li>
<li><strong>Ramp Metrics:</strong> Time to first deal, time to quota, and activity benchmarks that indicate a new hire is performing at expected levels.</li>
<li><strong>Manager Assessment:</strong> Qualitative evaluation from frontline managers on call quality, deal strategy, and buyer engagement.</li>
<li><strong>Conversation Intelligence:</strong> AI-driven analysis of recorded calls that identifies talk-to-listen ratio, filler words, topic coverage, and question frequency.</li>
</ul>

<h2>Building a Readiness Program</h2>
<p>Effective readiness programs combine structured learning paths with hands-on practice. This means pairing formal training modules with role-play exercises, shadowing programs, and real-time coaching on live deals. The best programs use spaced repetition to reinforce key concepts over time, preventing the "forgetting curve" that undermines one-time training events.</p>

<p>Readiness platforms like Brainshark, MindTickle, and WorkRamp offer features purpose-built for this: video practice submissions, AI scoring, and readiness dashboards that give managers visibility into team preparedness.</p>""",
        "faq": [
            ("How is sales readiness different from sales training?", "Sales training delivers knowledge. Sales readiness measures whether reps can actually apply that knowledge in buyer conversations. Training is an input; readiness is the outcome."),
            ("What tools support sales readiness?", "Readiness platforms like MindTickle, Brainshark, and WorkRamp combine learning management with practice exercises, certifications, and readiness scoring dashboards."),
        ],
        "related": ["Sales Onboarding", "Sales Certification", "Microlearning", "Sales Coaching"],
    },
    {
        "term": "Sales Onboarding",
        "slug": "sales-onboarding",
        "short": "The structured process of ramping new sales hires to full productivity through training, shadowing, and practice.",
        "body": """<p>Sales onboarding is the structured program that takes a new hire from their first day to full productivity. It covers product knowledge, sales methodology, tool proficiency, competitive positioning, buyer personas, and the internal processes reps need to operate effectively within the organization.</p>

<p>Onboarding is the highest-leverage activity in enablement. A well-designed program can cut ramp time by 30-50%, which translates directly to faster revenue contribution. Conversely, poor onboarding leads to early attrition, missed quotas, and frustrated sales managers.</p>

<h2>Onboarding Program Structure</h2>
<ul>
<li><strong>Week 1-2:</strong> Company orientation, product fundamentals, CRM and tool setup, initial methodology overview.</li>
<li><strong>Week 3-4:</strong> Deep dives into buyer personas, competitive landscape, objection handling, and deal mechanics.</li>
<li><strong>Month 2:</strong> Shadowing experienced reps, first solo calls with manager observation, and initial certification assessments.</li>
<li><strong>Month 3:</strong> Graduated ramp targets, ongoing coaching, and transition to the standard enablement cadence.</li>
</ul>

<h2>Best Practices</h2>
<p>The best onboarding programs are not lecture-heavy. They balance structured content with interactive exercises: mock discovery calls, competitive role-plays, and deal strategy workshops. Each module should have a clear assessment tied to it, so managers know when a rep is ready to progress.</p>

<p>Buddy programs pair new hires with tenured reps for informal mentorship. This accelerates cultural integration and gives new reps a safe space to ask questions they might hesitate to bring to their manager.</p>

<p>Measurement matters. Track time to first meeting booked, time to first deal, and time to full quota. Compare cohorts over time to quantify the impact of onboarding improvements.</p>""",
        "faq": [
            ("How long should sales onboarding take?", "Most B2B SaaS organizations target 30-90 days for onboarding, depending on deal complexity. Enterprise reps with longer sales cycles typically need longer ramp periods than SMB reps."),
            ("What is the most important metric for onboarding success?", "Time to productivity, usually measured as time to first closed deal or time to achieving quota. This single metric captures whether onboarding effectively prepared the rep to sell."),
        ],
        "related": ["Ramp Time", "Time to Productivity", "Sales Readiness", "Sales Certification"],
    },
    {
        "term": "Ramp Time",
        "slug": "ramp-time",
        "short": "The period between a sales rep's start date and the point where they consistently hit quota.",
        "body": """<p>Ramp time is the duration it takes for a new sales hire to reach full productivity. It is typically measured as the number of months from start date to consistently achieving quota, though some organizations define it as time to first closed deal or time to reaching a specific percentage of target.</p>

<p>Average ramp times vary significantly by segment. SMB reps often ramp in 3-4 months. Mid-market reps typically need 4-6 months. Enterprise reps can take 6-12 months or longer, reflecting the complexity of large deal cycles.</p>

<h2>Factors That Affect Ramp Time</h2>
<ul>
<li><strong>Deal Complexity:</strong> Longer sales cycles mean longer ramp periods because reps need more cycles to learn the full motion.</li>
<li><strong>Onboarding Quality:</strong> Structured programs with clear milestones and assessments consistently produce faster ramp than ad-hoc approaches.</li>
<li><strong>Sales Methodology:</strong> Reps who learn a defined methodology from day one make fewer costly mistakes during ramp.</li>
<li><strong>Manager Coaching:</strong> Frontline managers who invest in coaching new hires during ramp see measurably faster time to productivity.</li>
<li><strong>Prior Experience:</strong> Reps with relevant industry or segment experience ramp faster, though product-specific learning is still required.</li>
</ul>

<h2>Reducing Ramp Time</h2>
<p>The most effective lever is a structured onboarding program with graduated milestones. Each week should have specific learning objectives and assessments. Shadowing programs, practice exercises, and early deal involvement (even as an observer) all accelerate ramp.</p>

<p>Pre-boarding is an underused tactic. Sending product docs, competitive briefs, and methodology overviews before the start date lets reps hit the ground running on day one instead of spending their first week reading.</p>""",
        "faq": [
            ("What is the average ramp time for a B2B sales rep?", "Average ramp time is 3-4 months for SMB reps, 4-6 months for mid-market, and 6-12 months for enterprise. These ranges vary by industry, product complexity, and onboarding program quality."),
            ("How do you calculate ramp time?", "Most commonly, ramp time is the number of months from a rep's start date to the first month they achieve 100% of quota. Some organizations use a lower threshold, like 75%, or measure time to first closed deal."),
        ],
        "related": ["Time to Productivity", "Sales Onboarding", "Sales Readiness", "Quota Attainment"],
    },
    {
        "term": "Time to Productivity",
        "slug": "time-to-productivity",
        "short": "The elapsed time before a new hire contributes at expected performance levels, broader than just hitting quota.",
        "body": """<p>Time to productivity (TTP) measures how long it takes a new sales hire to perform at the level expected of a fully ramped rep. While often used interchangeably with ramp time, TTP can be a broader concept that includes not just quota attainment but also proficiency in sales methodology, tool usage, pipeline management, and buyer engagement quality.</p>

<p>TTP is a critical metric for enablement teams because it directly impacts revenue forecasting. Every month a rep is not productive represents unrealized revenue capacity. For a company hiring 20 reps per year with a 6-month TTP and $500K annual quota per rep, reducing TTP by one month unlocks over $800K in incremental pipeline capacity.</p>

<h2>How to Measure Time to Productivity</h2>
<ul>
<li><strong>Quota-Based:</strong> First month the rep hits 100% of quota (or a defined threshold like 80%).</li>
<li><strong>Activity-Based:</strong> When the rep's activity metrics (calls, meetings, pipeline generated) match the team average.</li>
<li><strong>Competency-Based:</strong> When the rep passes all certification milestones and managers confirm readiness.</li>
<li><strong>Composite:</strong> A weighted score combining quota performance, activity, and competency assessments.</li>
</ul>

<h2>Enablement's Role in Reducing TTP</h2>
<p>Enablement teams directly control many of the inputs that determine TTP. Better onboarding content reduces the knowledge gap. Structured practice exercises build confidence faster. Just-in-time resources help reps handle unfamiliar situations without waiting for manager guidance.</p>

<p>The most impactful intervention is usually front-loading deal exposure. Reps who observe live deals during their first two weeks internalize the sales motion faster than those who spend that time in classrooms. Blending structured learning with real deal context is the fastest path to productivity.</p>""",
        "faq": [
            ("Is time to productivity the same as ramp time?", "They are closely related but not identical. Ramp time usually refers to quota attainment specifically. Time to productivity can include broader competency measures like tool proficiency, methodology execution, and pipeline management quality."),
            ("What is a good time to productivity benchmark?", "For B2B SaaS, under 4 months for SMB and under 6 months for mid-market is considered strong. Enterprise is harder to benchmark due to longer deal cycles. Compare against your own historical data for the most meaningful benchmark."),
        ],
        "related": ["Ramp Time", "Sales Onboarding", "Sales Readiness", "Sales Velocity"],
    },
    {
        "term": "Sales Methodology",
        "slug": "sales-methodology",
        "short": "A structured framework that guides how reps qualify opportunities, run discovery, and advance deals.",
        "body": """<p>A sales methodology is a structured approach to selling that defines how reps should engage buyers at each stage of the deal cycle. It provides a common language, a set of qualification criteria, and a repeatable process that the entire team follows. Popular methodologies include MEDDPICC, BANT, Challenger, SPIN, Value Selling, and Solution Selling.</p>

<p>Methodology is different from a sales process. The process defines the stages a deal moves through (discovery, demo, proposal, close). The methodology defines how reps should behave within each stage: what questions to ask, what information to gather, and how to advance the deal.</p>

<h2>Why Methodology Matters for Enablement</h2>
<ul>
<li><strong>Consistency:</strong> A shared methodology means managers can coach to a common standard instead of letting every rep freelance their own approach.</li>
<li><strong>Forecasting:</strong> When deals are qualified using objective criteria (like MEDDPICC), pipeline accuracy improves because the team agrees on what makes a deal real.</li>
<li><strong>Onboarding:</strong> New reps with a methodology to follow ramp faster because they have a framework instead of guessing what to do next.</li>
<li><strong>Coaching:</strong> Managers can identify specific skill gaps (poor discovery, weak champion building) by evaluating reps against methodology criteria.</li>
</ul>

<h2>Choosing the Right Methodology</h2>
<p>The right methodology depends on your selling motion. Complex enterprise deals with multiple stakeholders benefit from MEDDPICC or Challenger. Transactional sales with shorter cycles may only need BANT. Value-based selling works well when differentiation depends on business impact rather than feature comparison.</p>

<p>The biggest mistake is adopting a methodology without investing in sustained reinforcement. Initial training gets reps aware. Ongoing coaching, CRM integration, and deal reviews are what drive adoption. Enablement teams that treat methodology as a launch event instead of a continuous program see adoption fade within 90 days.</p>""",
        "faq": [
            ("What is the most popular sales methodology?", "MEDDPICC is currently the most widely adopted methodology in B2B enterprise sales. Challenger Sale and SPIN Selling remain popular for specific use cases. The right choice depends on deal complexity, buyer dynamics, and organizational maturity."),
            ("How long does it take to implement a new sales methodology?", "Expect 3-6 months for initial rollout and 12-18 months for full adoption. The timeline depends on team size, CRM integration requirements, and how much the new methodology differs from current behavior."),
        ],
        "related": ["MEDDPICC", "BANT", "Challenger Sale", "SPIN Selling", "Value Selling", "Solution Selling"],
    },
    {
        "term": "MEDDPICC",
        "slug": "meddpicc",
        "short": "A deal qualification framework that evaluates Metrics, Economic Buyer, Decision Criteria, Decision Process, Paper Process, Identify Pain, Champion, and Competition.",
        "body": """<p>MEDDPICC is a deal qualification and progression framework widely used in B2B enterprise sales. Each letter represents a critical element that must be identified and validated for a deal to close: Metrics, Economic Buyer, Decision Criteria, Decision Process, Paper Process, Identify Pain, Champion, and Competition.</p>

<p>Developed originally at PTC in the 1990s (as MEDDIC), the framework has been adopted by hundreds of high-growth technology companies. The addition of "PP" (Paper Process) reflects the reality that procurement, legal review, and contract execution can derail deals that are otherwise won on merit.</p>

<h2>Breaking Down MEDDPICC</h2>
<ul>
<li><strong>Metrics:</strong> The quantifiable business outcomes the buyer expects. If you cannot articulate the buyer's success metrics, you do not understand the deal.</li>
<li><strong>Economic Buyer:</strong> The person with the authority and budget to approve the purchase. Deals without EB access stall.</li>
<li><strong>Decision Criteria:</strong> The formal and informal standards the buyer uses to evaluate solutions. Know these early or risk a late-stage surprise.</li>
<li><strong>Decision Process:</strong> The steps, stakeholders, and timeline the buyer follows to make a purchase decision.</li>
<li><strong>Paper Process:</strong> Procurement, legal, security review, and contract execution. Many deals die here due to timeline misalignment.</li>
<li><strong>Identify Pain:</strong> The specific business pain driving the initiative. No pain, no urgency, no deal.</li>
<li><strong>Champion:</strong> An internal advocate with power, influence, and a personal stake in your solution winning.</li>
<li><strong>Competition:</strong> Who else is in the deal, including the status quo (doing nothing).</li>
</ul>

<h2>Enablement's Role in MEDDPICC Adoption</h2>
<p>Enablement teams drive MEDDPICC adoption through CRM integration (custom fields for each element), coaching frameworks (deal review templates), training modules, and ongoing reinforcement. The most effective implementations make MEDDPICC the language of pipeline reviews, so managers and reps discuss deals using the same criteria every week.</p>""",
        "faq": [
            ("What does MEDDPICC stand for?", "Metrics, Economic Buyer, Decision Criteria, Decision Process, Paper Process, Identify Pain, Champion, and Competition. Each element represents a critical qualification checkpoint in complex B2B sales."),
            ("When should a company adopt MEDDPICC?", "MEDDPICC is best suited for organizations with complex, multi-stakeholder enterprise deals. If your average deal involves 3+ stakeholders, has a 60+ day cycle, and requires procurement approval, MEDDPICC is a strong fit."),
        ],
        "related": ["Sales Methodology", "BANT", "Discovery Call", "Win Rate", "Champion Enablement"],
    },
    {
        "term": "BANT",
        "slug": "bant",
        "short": "A lead qualification framework evaluating Budget, Authority, Need, and Timeline to determine if a prospect is sales-ready.",
        "body": """<p>BANT is a lead qualification framework that assesses four criteria: Budget (can the prospect afford the solution?), Authority (is the contact a decision-maker?), Need (does the prospect have a problem you solve?), and Timeline (is there urgency to act?). Originally developed at IBM, BANT became one of the most widely recognized qualification acronyms in B2B sales.</p>

<p>BANT is often the first qualification framework sales reps learn. Its simplicity makes it easy to adopt and train, which is part of its enduring popularity. However, modern sales practitioners debate whether BANT's linear, seller-centric approach still fits today's complex buying processes.</p>

<h2>How BANT Works in Practice</h2>
<ul>
<li><strong>Budget:</strong> Has the prospect allocated or can they allocate funds for this type of solution? This does not require a specific number, but there needs to be a realistic path to funding.</li>
<li><strong>Authority:</strong> Is the person you are speaking with able to make or significantly influence the buying decision? If not, you need to identify who can.</li>
<li><strong>Need:</strong> Does the prospect have a genuine business problem that your solution addresses? The need should be specific and acknowledged by the prospect, not assumed by the seller.</li>
<li><strong>Timeline:</strong> Is there a triggering event, deadline, or business driver that creates urgency? Without timeline pressure, deals stall indefinitely.</li>
</ul>

<h2>BANT Limitations</h2>
<p>Critics argue BANT is too rigid for modern enterprise sales. Buyers often do not have predetermined budgets for new categories. Authority is distributed across buying committees rather than residing in one person. Need may not be fully articulated until a skilled rep helps the prospect discover it through structured discovery.</p>

<p>Many enablement teams use BANT for initial lead qualification (SDR/BDR stage) but switch to more comprehensive frameworks like MEDDPICC for opportunity management once deals enter the pipeline. This layered approach balances simplicity at the top of the funnel with rigor in the middle and bottom.</p>""",
        "faq": [
            ("What does BANT stand for?", "Budget, Authority, Need, and Timeline. It is a lead qualification framework originally developed at IBM to help sales teams prioritize prospects based on these four criteria."),
            ("Is BANT still relevant in modern sales?", "BANT remains useful for initial lead qualification, especially at the SDR/BDR level. For complex enterprise deals, most organizations layer on more comprehensive frameworks like MEDDPICC for deeper opportunity qualification."),
        ],
        "related": ["Sales Methodology", "MEDDPICC", "Discovery Call", "Sales Process"],
    },
    {
        "term": "Challenger Sale",
        "slug": "challenger-sale",
        "short": "A sales methodology where reps teach, tailor, and take control of the conversation to reframe how buyers think about their problems.",
        "body": """<p>The Challenger Sale is a sales methodology based on research by CEB (now Gartner) that identified five seller profiles: the Hard Worker, the Lone Wolf, the Relationship Builder, the Problem Solver, and the Challenger. The research found that Challengers consistently outperformed other profiles, especially in complex B2B sales.</p>

<p>Challengers succeed by doing three things: teaching the buyer something new about their business, tailoring their message to different stakeholders, and taking control of the deal by pushing back constructively when needed. This approach contrasts with relationship-based selling, where reps focus primarily on building rapport and accommodating buyer requests.</p>

<h2>The Three T's of Challenger</h2>
<ul>
<li><strong>Teach:</strong> Challengers lead with insights that reframe how buyers see their problems. Instead of asking "what keeps you up at night?", they say "here is a problem you did not know you had, and here is what it is costing you."</li>
<li><strong>Tailor:</strong> The message is customized to the specific stakeholder. An economic buyer hears the financial impact. An end user hears how their workflow improves. Tailoring ensures each conversation resonates with the individual's priorities.</li>
<li><strong>Take Control:</strong> Challengers are comfortable with constructive tension. They push back on unreasonable timelines, challenge the buyer's assumptions, and steer the deal process rather than following it passively.</li>
</ul>

<h2>Enablement Implications</h2>
<p>Implementing Challenger requires significant enablement investment. Reps need industry-specific insights to teach with. They need persona-based messaging to tailor effectively. They need confidence-building coaching to take control without coming across as aggressive.</p>

<p>The biggest enablement challenge is content. Challenger selling requires a steady stream of provocative, data-backed insights that reps can deliver to buyers. This means close collaboration between enablement, product marketing, and competitive intelligence teams to produce teaching content on a regular cadence.</p>""",
        "faq": [
            ("What is the Challenger Sale methodology?", "The Challenger Sale is a methodology where reps teach buyers new insights about their business, tailor messages to each stakeholder, and take control of the deal process. It was developed from CEB/Gartner research showing Challengers outperform other seller types in complex sales."),
            ("Is Challenger Sale good for all types of selling?", "Challenger works best in complex, consultative B2B sales where buyers have multiple stakeholders and entrenched assumptions. For simple, transactional sales where the buyer knows exactly what they need, the Challenger approach can feel forced."),
        ],
        "related": ["Sales Methodology", "SPIN Selling", "Value Selling", "Discovery Call"],
    },
    {
        "term": "SPIN Selling",
        "slug": "spin-selling",
        "short": "A question-based methodology that guides reps through Situation, Problem, Implication, and Need-Payoff questions to uncover buyer needs.",
        "body": """<p>SPIN Selling is a consultative sales methodology developed by Neil Rackham based on analysis of over 35,000 sales calls. The framework teaches reps to guide buyer conversations using four types of questions: Situation questions, Problem questions, Implication questions, and Need-Payoff questions. Each type serves a specific purpose in helping the buyer articulate their own need for change.</p>

<p>The core insight behind SPIN is that effective sellers do not pitch. They ask questions that help buyers discover and verbalize their own pain. When a buyer says "we need to fix this" instead of hearing "you should buy our product," the motivation to act comes from within, making the deal more resilient to competition and internal resistance.</p>

<h2>The SPIN Question Types</h2>
<ul>
<li><strong>Situation:</strong> Gather facts about the buyer's current state. Keep these brief because they provide background but do not build value. Examples: "How many reps on your team?" or "What CRM do you use?"</li>
<li><strong>Problem:</strong> Identify specific difficulties, dissatisfactions, or challenges. These questions surface pain points. Example: "What challenges do you face getting new reps productive?"</li>
<li><strong>Implication:</strong> Explore the consequences and downstream effects of the problem. This is where urgency builds. Example: "What happens to pipeline when ramp takes that long?"</li>
<li><strong>Need-Payoff:</strong> Help the buyer envision the value of solving the problem. Example: "If you could cut ramp time in half, what would that mean for your quarterly number?"</li>
</ul>

<h2>SPIN and Modern Enablement</h2>
<p>SPIN remains one of the most research-backed methodologies available. Enablement teams often use SPIN as the foundation for discovery call training, even when a different methodology (like MEDDPICC) governs overall deal management. The questioning discipline that SPIN teaches is universally applicable.</p>

<p>Conversation intelligence platforms make SPIN coaching more effective by analyzing recorded calls for question type distribution. Managers can see whether reps are spending too long on Situation questions or skipping Implication questions entirely.</p>""",
        "faq": [
            ("What does SPIN stand for in SPIN Selling?", "Situation, Problem, Implication, and Need-Payoff. These are four types of questions that guide a consultative sales conversation from understanding the buyer's context to building urgency around a solution."),
            ("Is SPIN Selling still effective today?", "Yes. SPIN's question-based approach remains foundational to consultative selling. Many modern methodologies incorporate SPIN principles. It is especially effective for training reps on discovery call technique."),
        ],
        "related": ["Sales Methodology", "Challenger Sale", "Discovery Call", "Value Selling"],
    },
    {
        "term": "Value Selling",
        "slug": "value-selling",
        "short": "A methodology that focuses on articulating and quantifying the business value a solution delivers to the buyer.",
        "body": """<p>Value selling is a sales methodology centered on connecting your solution to measurable business outcomes for the buyer. Instead of leading with product features or competing on price, value sellers help prospects quantify the cost of their current problem and the financial return of solving it. The conversation shifts from "what does your product do?" to "what is this problem costing us, and what will the solution be worth?"</p>

<p>The framework requires reps to understand the buyer's business deeply enough to build a credible business case. This means knowing industry benchmarks, understanding the buyer's financial metrics, and being able to translate product capabilities into dollars and time saved.</p>

<h2>Core Elements of Value Selling</h2>
<ul>
<li><strong>Cost of Inaction:</strong> Quantify what the buyer loses by maintaining the status quo. This includes hard costs (wasted spend, revenue leakage) and soft costs (productivity loss, opportunity cost).</li>
<li><strong>Value Drivers:</strong> Identify the specific ways your solution creates value: revenue increase, cost reduction, risk mitigation, or time savings.</li>
<li><strong>Business Case:</strong> Build a financial model that shows projected ROI, payback period, and total value delivered over a defined timeframe.</li>
<li><strong>Stakeholder Alignment:</strong> Different stakeholders care about different value drivers. CFOs focus on ROI. Operations leaders focus on efficiency. End users focus on time savings.</li>
</ul>

<h2>Enablement for Value Selling</h2>
<p>Value selling demands strong enablement support. Reps need ROI calculators, industry benchmark data, customer proof points, and business case templates. They also need training on financial concepts: how to read a P&L, how to calculate ROI, and how to present a business case to a CFO who speaks in different terms than a VP of Sales.</p>

<p>The most effective value selling programs include a library of customer case studies organized by industry, company size, and use case, with specific metrics that reps can reference in their own business cases.</p>""",
        "faq": [
            ("What is value selling?", "Value selling is a methodology that focuses on quantifying and communicating the business impact of your solution. Rather than competing on features or price, value sellers help buyers understand the financial return of solving their problem."),
            ("How is value selling different from solution selling?", "Solution selling focuses on diagnosing problems and proposing tailored solutions. Value selling goes further by quantifying the financial impact of both the problem and the solution, building an explicit business case with ROI metrics."),
        ],
        "related": ["Solution Selling", "ROI Calculator", "Business Case", "Sales Methodology"],
    },
    {
        "term": "Solution Selling",
        "slug": "solution-selling",
        "short": "A methodology where reps diagnose buyer problems before prescribing solutions, positioning themselves as trusted advisors.",
        "body": """<p>Solution selling is a consultative methodology where the rep acts as a diagnostic advisor rather than a product pusher. The approach prioritizes understanding the buyer's situation, challenges, and goals before presenting any solution. When a recommendation comes, it is framed as a prescriptive response to the buyer's specific needs rather than a generic product pitch.</p>

<p>Developed in the 1980s by Mike Bosworth, solution selling was one of the first methodologies to formalize the idea that sellers should lead with questions, not features. It laid the groundwork for many modern approaches, including Challenger, SPIN, and Value Selling.</p>

<h2>How Solution Selling Works</h2>
<ul>
<li><strong>Pain Discovery:</strong> Identify the buyer's primary business pain through open-ended questions and active listening.</li>
<li><strong>Vision Creation:</strong> Help the buyer visualize what solving their problem looks like. This is where the rep starts connecting capabilities to the buyer's situation.</li>
<li><strong>Proof:</strong> Provide evidence that your solution can deliver the envisioned outcome: case studies, references, demonstrations, and pilot results.</li>
<li><strong>Close:</strong> Negotiate terms and navigate procurement with the credibility built through the diagnostic process.</li>
</ul>

<h2>Solution Selling in the Modern Stack</h2>
<p>While newer methodologies have evolved beyond solution selling's original framework, its core principle remains relevant: diagnose before you prescribe. Enablement teams still train reps on this discipline because the alternative, feature-dumping, is the most common failure mode for inexperienced sellers.</p>

<p>Modern enablement teams blend solution selling principles with other frameworks. A rep might use SPIN for discovery, solution selling for demo structure, and MEDDPICC for deal qualification. The methodologies complement rather than compete with each other.</p>""",
        "faq": [
            ("What is solution selling?", "Solution selling is a consultative sales methodology where reps diagnose the buyer's problems before recommending a solution. The focus is on understanding the buyer's specific needs rather than leading with product features."),
            ("Is solution selling outdated?", "The original framework has been superseded by newer methodologies, but the core principle of diagnosing before prescribing remains foundational. Most modern sales training incorporates solution selling concepts even when using different terminology."),
        ],
        "related": ["Value Selling", "SPIN Selling", "Discovery Call", "Sales Methodology"],
    },
    {
        "term": "Sales Playbook",
        "slug": "sales-playbook",
        "short": "A comprehensive guide that documents the sales process, messaging, objection handling, and best practices for a specific selling scenario.",
        "body": """<p>A sales playbook is a documented guide that gives reps everything they need to execute a specific selling motion. It includes the target buyer profile, key messaging, discovery questions, objection responses, competitive positioning, demo flow, proposal templates, and step-by-step guidance for each stage of the deal. Think of it as the operational manual for a sales rep.</p>

<p>Playbooks differ from general training materials in their specificity. A training course teaches concepts. A playbook tells the rep exactly what to do, say, and send at each point in a deal. The best playbooks are living documents that evolve based on what is actually working in the field.</p>

<h2>Types of Sales Playbooks</h2>
<ul>
<li><strong>New Hire Playbook:</strong> Comprehensive guide for onboarding that covers everything a new rep needs to know.</li>
<li><strong>Segment Playbook:</strong> Tailored for a specific market segment (enterprise, mid-market, SMB) with messaging and process adjustments for each.</li>
<li><strong>Product Launch Playbook:</strong> Guides reps through positioning, messaging, and selling a new product or feature.</li>
<li><strong>Competitive Playbook:</strong> Focused on winning against specific competitors with battle cards, objection handling, and differentiation tactics.</li>
<li><strong>Expansion Playbook:</strong> For account managers selling additional products or upgrading existing customers.</li>
</ul>

<h2>Building Effective Playbooks</h2>
<p>Start with your top performers. Interview them about what they do differently at each stage. Document those behaviors and turn them into repeatable guidance. The best playbooks are not theoretical; they are reverse-engineered from proven success.</p>

<p>Distribution matters as much as content. A 50-page PDF that no one reads is not a playbook. Modern enablement platforms let you embed playbook content directly into the CRM workflow, surfacing the right guidance at the right moment based on deal stage, buyer persona, or competitive situation.</p>""",
        "faq": [
            ("What should a sales playbook include?", "A sales playbook should include the ideal customer profile, buyer personas, messaging frameworks, discovery questions, objection handling scripts, competitive battle cards, demo guidelines, email templates, and stage-specific guidance for advancing deals."),
            ("How often should playbooks be updated?", "Review playbooks quarterly at minimum. Update them whenever there is a new product launch, competitive shift, pricing change, or when win/loss analysis reveals that messaging or tactics need adjustment."),
        ],
        "related": ["Battle Card", "Competitive Intelligence", "Sales Methodology", "Sales Content Management"],
    },
    {
        "term": "Battle Card",
        "slug": "battle-card",
        "short": "A concise reference document that arms reps with competitive positioning, objection handling, and differentiation talking points.",
        "body": """<p>A battle card is a quick-reference document designed to help sales reps compete effectively against a specific competitor. It distills competitive intelligence into actionable talking points: where you win, where the competitor is strong, common objections, recommended responses, customer proof points, and land mines to set during discovery.</p>

<p>Effective battle cards are short. If a rep cannot absorb the key points in under five minutes, the card is too long. The format should prioritize scannability with sections clearly labeled so reps can find what they need in the middle of a call.</p>

<h2>What to Include in a Battle Card</h2>
<ul>
<li><strong>Competitor Overview:</strong> One paragraph on who they are, their positioning, and their target market.</li>
<li><strong>Where We Win:</strong> Three to five specific differentiators with proof points. These must be defensible, not marketing claims.</li>
<li><strong>Where They Are Strong:</strong> Honest assessment of competitor strengths. Reps who ignore competitor advantages lose credibility with informed buyers.</li>
<li><strong>Objection Handling:</strong> Common objections buyers raise when considering the competitor, with specific responses.</li>
<li><strong>Discovery Landmines:</strong> Questions to ask early in discovery that expose the competitor's weaknesses or highlight requirements they cannot meet.</li>
<li><strong>Customer Proof:</strong> Named references or anonymized case studies where you won against this competitor.</li>
</ul>

<h2>Maintaining Battle Cards</h2>
<p>Battle cards go stale fast. Competitors ship new features, change pricing, hire new leadership, and shift positioning. Enablement teams should assign competitive intelligence ownership and update battle cards on a monthly or quarterly cycle.</p>

<p>Adoption tracking matters. If reps are not opening battle cards in the enablement platform, either the content is not useful or reps do not know it exists. Content engagement metrics help enablement teams iterate on format and distribution.</p>""",
        "faq": [
            ("What is a battle card in sales?", "A battle card is a concise reference document that gives sales reps competitive intelligence against a specific competitor. It includes differentiators, objection handling, discovery questions, and proof points to help reps compete effectively."),
            ("How long should a battle card be?", "One to two pages maximum. Battle cards should be scannable in under five minutes. If reps need more depth on a specific competitor, supplement the battle card with a longer competitive brief they can study outside of live conversations."),
        ],
        "related": ["Competitive Intelligence", "Sales Playbook", "Objection Handling", "Win/Loss Analysis"],
    },
    {
        "term": "Competitive Intelligence",
        "slug": "competitive-intelligence",
        "short": "The systematic collection and analysis of information about competitors to inform sales strategy and positioning.",
        "body": """<p>Competitive intelligence (CI) in the context of sales enablement refers to the process of gathering, analyzing, and distributing information about competitors so that sales teams can position effectively and win more deals. CI covers product capabilities, pricing, market positioning, customer sentiment, leadership changes, funding events, and strategic direction.</p>

<p>The best CI programs are proactive, not reactive. Instead of scrambling when a competitor comes up in a deal, enablement teams maintain a continuous feed of intelligence that gets packaged into battle cards, competitive briefs, and training sessions before reps need it.</p>

<h2>Sources of Competitive Intelligence</h2>
<ul>
<li><strong>Win/Loss Analysis:</strong> Structured interviews with buyers after closed deals reveal exactly why you won or lost against specific competitors.</li>
<li><strong>Sales Team Feedback:</strong> Reps hear competitive claims in every deal. A structured intake process captures this field intelligence.</li>
<li><strong>Product Analysis:</strong> Hands-on evaluation of competitor products through free trials, demos, and documentation review.</li>
<li><strong>Public Sources:</strong> Earnings calls, press releases, job postings (which signal strategic priorities), G2/Gartner reviews, and social media activity.</li>
<li><strong>Customer Advisory Boards:</strong> Existing customers who evaluated competitors during their purchase can share decision criteria and perceptions.</li>
</ul>

<h2>Delivering CI to Sales</h2>
<p>Intelligence is only valuable if it reaches reps when they need it. The most effective delivery mechanisms include battle cards in the enablement platform, competitive alerts via Slack or email, monthly competitive briefings, and competitive modules embedded in the onboarding program.</p>

<p>Track adoption. If battle cards are not being accessed, intelligence is not reaching the field. If win rates against specific competitors are not improving after CI investments, the intelligence may not be actionable enough.</p>""",
        "faq": [
            ("What is competitive intelligence in sales?", "Competitive intelligence is the systematic process of gathering and analyzing information about competitors so sales teams can differentiate effectively, handle objections, and win competitive deals. It covers product capabilities, pricing, positioning, and market strategy."),
            ("Who owns competitive intelligence in an organization?", "Ownership varies. In some organizations, product marketing owns CI. In others, enablement or a dedicated CI team handles it. The most effective model has product marketing generating insights and enablement packaging and distributing them to the field."),
        ],
        "related": ["Battle Card", "Win/Loss Analysis", "Sales Playbook", "Objection Handling"],
    },
    {
        "term": "Objection Handling",
        "slug": "objection-handling",
        "short": "The skill and process of addressing buyer concerns, hesitations, and pushback during the sales conversation.",
        "body": """<p>Objection handling is the skill of responding to buyer concerns in a way that addresses the underlying issue, maintains trust, and keeps the deal moving forward. Objections are not roadblocks. They are signals that the buyer is engaged but has unresolved questions, concerns, or risk perceptions that need to be addressed.</p>

<p>Common objection categories include price ("it is too expensive"), timing ("we are not ready yet"), competition ("we are also looking at X"), authority ("I need to check with my boss"), and status quo ("what we have works fine"). Each category requires a different response framework.</p>

<h2>Frameworks for Handling Objections</h2>
<ul>
<li><strong>Acknowledge, Question, Respond:</strong> Validate the concern, ask a clarifying question to understand the root cause, then respond to the real issue rather than the surface objection.</li>
<li><strong>Feel, Felt, Found:</strong> "I understand how you feel. Other customers felt the same way. What they found was..." This works for common objections with strong proof points.</li>
<li><strong>Isolate and Advance:</strong> "If we could resolve this concern, would you be comfortable moving forward?" This tests whether the objection is the real blocker or if there are deeper issues.</li>
</ul>

<h2>Enablement's Role in Objection Handling</h2>
<p>Enablement teams should maintain an objection library organized by category, competitor, and deal stage. Each objection should include the recommended response framework, supporting proof points, and links to relevant customer stories or data.</p>

<p>Role-play practice is the most effective training method for objection handling. Reading a response in a document is different from delivering it naturally in conversation. Regular practice sessions, whether in team meetings or through video recording platforms, build the muscle memory reps need to handle objections confidently in live calls.</p>

<p>Conversation intelligence tools surface common objections from real calls. Enablement teams can analyze which objections appear most frequently and whether reps are using the recommended responses effectively. This data-driven approach replaces guesswork with evidence.</p>""",
        "faq": [
            ("What is objection handling in sales?", "Objection handling is the process of addressing buyer concerns, hesitations, and pushback during a sales conversation. Effective handling turns objections into opportunities to build trust and demonstrate value."),
            ("What are the most common sales objections?", "The most common objections relate to price, timing, competition, authority, and status quo. Each requires a different response approach. Price objections often indicate insufficient value communication, not actual budget constraints."),
        ],
        "related": ["Battle Card", "Discovery Call", "Sales Coaching", "Sales Playbook"],
    },
    {
        "term": "Discovery Call",
        "slug": "discovery-call",
        "short": "The initial sales conversation focused on understanding the buyer's situation, challenges, goals, and decision process.",
        "body": """<p>A discovery call is the foundational sales conversation where the rep gathers information about the buyer's situation, challenges, goals, decision process, and success criteria. It is the most important call in the sales cycle because the quality of discovery determines the quality of everything that follows: the demo, the proposal, the business case, and the close.</p>

<p>Poor discovery is the root cause of most lost deals. When reps skip discovery or do it superficially, they demo features that do not matter to the buyer, propose solutions that miss the mark, and lose to competitors who took the time to understand the buyer's real needs.</p>

<h2>Anatomy of a Strong Discovery Call</h2>
<ul>
<li><strong>Pre-Call Research:</strong> Review the prospect's company, recent news, industry trends, and the specific person's role and background. Show up informed.</li>
<li><strong>Agenda Setting:</strong> Open with a clear agenda and time check. This establishes professionalism and gives the buyer confidence that the call will be productive.</li>
<li><strong>Situation Questions:</strong> Understand the current state: team size, tools in use, processes, and recent changes.</li>
<li><strong>Problem Questions:</strong> Uncover specific challenges, pain points, and frustrations with the current state.</li>
<li><strong>Impact Questions:</strong> Quantify the business impact of those problems. What is it costing in revenue, time, or productivity?</li>
<li><strong>Vision Questions:</strong> Explore what success looks like. What would change if the problem were solved?</li>
<li><strong>Process Questions:</strong> Understand decision-makers, timeline, budget, and evaluation criteria.</li>
</ul>

<h2>Common Discovery Mistakes</h2>
<p>The most common mistake is talking too much. Discovery calls should be at least 60% buyer talk time. Reps who dominate the conversation miss critical information. Other common mistakes include asking closed-ended questions that kill the conversation, jumping to solution mode too early, and failing to ask follow-up questions that dig deeper into surface-level answers.</p>""",
        "faq": [
            ("What is a discovery call in sales?", "A discovery call is the initial sales conversation focused entirely on understanding the buyer's situation, challenges, goals, and decision process. It is the foundation for every subsequent step in the deal."),
            ("How long should a discovery call last?", "Most discovery calls run 30-45 minutes for mid-market deals and 45-60 minutes for enterprise. The key is having enough time to cover situation, problem, impact, and process questions without rushing."),
        ],
        "related": ["SPIN Selling", "MEDDPICC", "Objection Handling", "Sales Process"],
    },
    {
        "term": "Sales Content Management",
        "slug": "sales-content-management",
        "short": "The practice of organizing, distributing, and measuring sales collateral so reps can find and use the right content at the right time.",
        "body": """<p>Sales content management (SCM) is the practice of creating, organizing, distributing, and measuring the effectiveness of sales collateral. It ensures that reps can find the right content for the right buyer at the right moment in the deal cycle. Without SCM, reps waste time searching for materials, use outdated content, or create their own off-brand assets.</p>

<p>Research consistently shows that reps spend 20-30% of their time looking for or creating content. That is a massive productivity drain. Effective SCM reclaims that time and ensures the content reps use is approved, current, and aligned with company messaging.</p>

<h2>Components of Sales Content Management</h2>
<ul>
<li><strong>Content Repository:</strong> A centralized platform (Highspot, Seismic, Showpad) where all sales collateral lives, organized by buyer stage, persona, and use case.</li>
<li><strong>Content Organization:</strong> Taxonomy and tagging that makes assets findable. The best systems use AI-powered search and recommendations based on deal context.</li>
<li><strong>Content Governance:</strong> Workflows for content creation, review, approval, and retirement. Every asset should have an owner and an expiration date.</li>
<li><strong>Content Analytics:</strong> Data on which content is being used, how buyers engage with it, and whether it correlates with deal outcomes.</li>
</ul>

<h2>Why Content Management Matters</h2>
<p>Content is the fuel of the sales process. Every email, presentation, case study, and proposal is content. When that content is scattered across shared drives, personal folders, and email threads, quality and consistency suffer.</p>

<p>Beyond organization, modern SCM platforms provide buyer engagement tracking. When a rep sends a case study, the platform shows whether the buyer opened it, how long they spent on each page, and whether they forwarded it to colleagues. This intelligence helps reps prioritize follow-up and gauge buyer interest.</p>""",
        "faq": [
            ("What is sales content management?", "Sales content management is the practice of organizing, distributing, and measuring sales collateral. It ensures reps can find approved, current content quickly and tracks how buyers engage with shared materials."),
            ("What tools are used for sales content management?", "Leading platforms include Highspot, Seismic, Showpad, and Guru. These tools centralize content, provide AI-powered search, enable buyer engagement tracking, and report on content effectiveness."),
        ],
        "related": ["Content Adoption", "Content Engagement", "Digital Sales Room", "Sales Playbook"],
    },
    {
        "term": "Digital Sales Room",
        "slug": "digital-sales-room",
        "short": "A personalized, shared digital space where sellers and buyers collaborate on deal materials, proposals, and next steps.",
        "body": """<p>A digital sales room (DSR) is a branded, personalized microsite or portal where sellers and buyers interact throughout the deal cycle. Instead of exchanging content via email attachments, the seller creates a shared space containing all relevant materials: presentations, case studies, proposals, contracts, mutual action plans, and meeting recordings.</p>

<p>DSRs solve the content chaos problem that plagues complex deals. When six stakeholders are evaluating a solution, keeping everyone aligned through email threads becomes impossible. A DSR gives every stakeholder a single destination to access materials, track progress, and engage with the selling team.</p>

<h2>Benefits of Digital Sales Rooms</h2>
<ul>
<li><strong>Buyer Experience:</strong> Buyers get a professional, organized space instead of digging through email attachments. This elevates the vendor's perceived professionalism.</li>
<li><strong>Engagement Intelligence:</strong> Sellers see exactly who accessed which content, how long they spent, and when. This reveals which stakeholders are engaged and which are disengaged.</li>
<li><strong>Multi-Stakeholder Alignment:</strong> Every decision-maker sees the same materials. No more version confusion or outdated documents circulating.</li>
<li><strong>Deal Velocity:</strong> When all materials are accessible in one place with a clear mutual action plan, deals move faster because friction is reduced at every handoff.</li>
</ul>

<h2>DSR Platforms</h2>
<p>Dedicated DSR platforms include Aligned, Dock, and GetAccept. Many enablement platforms (Highspot, Seismic) also offer DSR-like functionality. The key differentiator is engagement analytics: the ability to see buyer activity at the individual stakeholder level.</p>

<p>Adoption often starts with enterprise deals where the complexity justifies the setup investment. As reps see the engagement intelligence and buyer feedback, adoption typically expands to mid-market deals as well.</p>""",
        "faq": [
            ("What is a digital sales room?", "A digital sales room is a personalized, shared online space where sellers and buyers collaborate on deal materials. It replaces email attachments with a centralized portal that tracks buyer engagement and keeps all stakeholders aligned."),
            ("When should sales teams use digital sales rooms?", "DSRs are most valuable for complex deals with multiple stakeholders, long sales cycles, and significant content exchange. They are standard for enterprise sales and increasingly used in mid-market deals."),
        ],
        "related": ["Mutual Action Plan", "Sales Content Management", "Buyer Enablement", "Deal Cycle"],
    },
    {
        "term": "Mutual Action Plan",
        "slug": "mutual-action-plan",
        "short": "A shared document that outlines the agreed-upon steps, owners, and timelines for both buyer and seller to close a deal.",
        "body": """<p>A mutual action plan (MAP) is a collaborative document that outlines the steps, milestones, owners, and deadlines required to move from evaluation to signed contract. Unlike a traditional sales process that is seller-defined, a MAP is co-created with the buyer, making it a shared commitment rather than a unilateral follow-up plan.</p>

<p>MAPs are one of the most effective tools for improving deal predictability. When both parties agree to a timeline with specific milestones, the deal has structure. Without a MAP, deals drift because neither side has committed to a concrete next step beyond "we will follow up."</p>

<h2>What a Mutual Action Plan Includes</h2>
<ul>
<li><strong>Key Milestones:</strong> Technical evaluation, security review, executive sponsor meeting, proposal review, contract negotiation, go-live date.</li>
<li><strong>Owners:</strong> Who is responsible for each step on both sides. This surfaces the buying committee and ensures nothing falls through the cracks.</li>
<li><strong>Dates:</strong> Target completion dates for each milestone. Working backward from the desired go-live date creates natural urgency.</li>
<li><strong>Success Criteria:</strong> What must be true for each milestone to be considered complete. This prevents ambiguity.</li>
</ul>

<h2>When to Introduce a MAP</h2>
<p>The best time to introduce a MAP is after discovery when the buyer has confirmed interest and you are moving to evaluation. Presenting it too early feels presumptuous. Presenting it too late means the deal is already drifting.</p>

<p>Frame the MAP as a tool for the buyer's benefit: "Based on your target go-live date, here is what we need to accomplish together and by when. Does this align with your internal process?" This positions the seller as organized and buyer-centric.</p>

<p>Many reps embed MAPs in digital sales rooms where both parties can update progress in real time. This creates transparency and accountability without requiring constant email follow-ups.</p>""",
        "faq": [
            ("What is a mutual action plan in sales?", "A mutual action plan is a shared document co-created by the seller and buyer that outlines the steps, owners, and timelines needed to complete a purchase. It creates accountability on both sides and improves deal predictability."),
            ("When should a rep introduce a mutual action plan?", "After discovery when the buyer has confirmed interest and the deal is moving to evaluation. The MAP should be positioned as a benefit to the buyer: a clear roadmap that makes the evaluation process efficient and predictable."),
        ],
        "related": ["Digital Sales Room", "Deal Cycle", "Sales Process", "Pipeline Velocity"],
    },
    {
        "term": "Sales Coaching",
        "slug": "sales-coaching",
        "short": "The ongoing practice of developing sales reps through observation, feedback, and guided improvement of specific selling behaviors.",
        "body": """<p>Sales coaching is the ongoing, personalized development of sales reps through observation, feedback, and guided practice. Unlike training, which delivers knowledge to groups, coaching is one-on-one and focused on improving specific behaviors. A coach observes a rep's performance (on calls, in deal strategy, in pipeline management) and provides targeted feedback to close skill gaps.</p>

<p>Coaching is the highest-impact activity a sales manager performs. Research from CSO Insights found that organizations with a formal coaching program achieve 16.7% higher win rates than those without. Despite this, most managers spend less than 5% of their time coaching because operational tasks consume their calendars.</p>

<h2>Types of Sales Coaching</h2>
<ul>
<li><strong>Deal Coaching:</strong> Reviewing specific opportunities to improve strategy, stakeholder engagement, and next steps. This happens in pipeline reviews or one-on-one deal discussions.</li>
<li><strong>Skill Coaching:</strong> Working on foundational selling skills like discovery, objection handling, negotiation, or presentation delivery.</li>
<li><strong>Behavioral Coaching:</strong> Addressing habits and patterns like time management, activity levels, CRM hygiene, and prioritization.</li>
<li><strong>Call Coaching:</strong> Reviewing recorded sales calls to identify strengths and areas for improvement. Conversation intelligence tools make this scalable.</li>
</ul>

<h2>Enablement's Role in Coaching</h2>
<p>Enablement teams support coaching by providing managers with frameworks, scorecards, and content. A coaching playbook might include templates for one-on-one agendas, deal review checklists, and call scoring rubrics. Enablement also trains managers on how to coach effectively, because most first-time managers were promoted for selling, not coaching.</p>

<p>Conversation intelligence platforms like Gong and Chorus have transformed coaching by making call review efficient. Managers can review AI-generated summaries, flag specific moments, and leave timestamped feedback without listening to entire calls.</p>""",
        "faq": [
            ("What is the difference between sales training and coaching?", "Sales training delivers knowledge to groups through courses, workshops, and content. Sales coaching is one-on-one feedback on specific behaviors observed in a rep's actual performance. Training teaches the what; coaching refines the how."),
            ("How much time should managers spend coaching?", "Research suggests at least 3-5 hours per week for optimal results. The most impactful coaching is regular and structured: weekly one-on-ones with specific skill or deal focus, plus ad-hoc call reviews."),
        ],
        "related": ["Conversation Intelligence", "Call Recording", "Sales Readiness", "Win Rate"],
    },
    {
        "term": "Call Recording",
        "slug": "call-recording",
        "short": "The practice of recording sales calls and meetings for coaching, training, and performance analysis.",
        "body": """<p>Call recording in sales refers to the practice of capturing audio and video from sales conversations for later review, coaching, training, and analysis. What was once a compliance tool has become a core enablement asset. Recorded calls provide ground truth about what reps actually say in buyer conversations, replacing manager assumptions with observable evidence.</p>

<p>The rise of virtual selling accelerated call recording adoption. When every meeting is on Zoom or Teams, recording becomes trivially easy. The challenge has shifted from capturing calls to making recordings actionable: finding the right moments, extracting insights, and turning them into coaching and training content.</p>

<h2>Use Cases for Call Recording</h2>
<ul>
<li><strong>Coaching:</strong> Managers review calls to provide specific, evidence-based feedback. Instead of general advice like "ask better questions," a manager can point to a specific moment at 12:34 where the rep missed a follow-up opportunity.</li>
<li><strong>Onboarding:</strong> New hires learn faster by watching recordings of successful discovery calls, demos, and negotiation conversations from top performers.</li>
<li><strong>Win/Loss Analysis:</strong> Reviewing recorded calls from won and lost deals reveals what top performers do differently.</li>
<li><strong>Content Creation:</strong> Customer quotes, competitive intelligence, and objection patterns captured in calls become inputs for battle cards, case studies, and training content.</li>
</ul>

<h2>Legal Considerations</h2>
<p>Recording laws vary by jurisdiction. In the US, some states require all-party consent while others require only one-party consent. Most sales teams address this by announcing recording at the start of each call and getting verbal acknowledgment. Platforms like Gong and Chorus handle consent workflows automatically.</p>

<p>Call recordings also raise data privacy considerations under GDPR and similar regulations. Enablement teams should work with legal to establish clear policies on recording consent, data retention, and access controls.</p>""",
        "faq": [
            ("Why is call recording important for sales enablement?", "Call recording provides evidence-based coaching opportunities, accelerates onboarding through real examples, supports win/loss analysis, and captures competitive intelligence. It replaces assumptions about rep behavior with observable data."),
            ("Is it legal to record sales calls?", "Recording laws vary by jurisdiction. Most US states allow recording with one-party consent, but some require all-party consent. Best practice is to announce recording at the start of each call and get verbal acknowledgment."),
        ],
        "related": ["Conversation Intelligence", "Sales Coaching", "Win/Loss Analysis", "Sales Readiness"],
    },
    {
        "term": "Conversation Intelligence",
        "slug": "conversation-intelligence",
        "short": "AI-powered technology that records, transcribes, and analyzes sales conversations to surface coaching insights and deal intelligence.",
        "body": """<p>Conversation intelligence (CI) refers to AI-powered platforms that automatically record, transcribe, and analyze sales calls and meetings. These tools go beyond simple recording by using natural language processing to identify topics discussed, questions asked, objections raised, competitor mentions, next steps committed, and sentiment patterns throughout the conversation.</p>

<p>CI platforms like Gong, Chorus (ZoomInfo), and Clari Copilot have become essential infrastructure for modern enablement teams. They transform the previously invisible world of buyer conversations into structured, searchable, analyzable data.</p>

<h2>Key Capabilities</h2>
<ul>
<li><strong>Automatic Transcription:</strong> Real-time speech-to-text with speaker identification, making every call searchable by keyword or topic.</li>
<li><strong>Topic Detection:</strong> AI identifies when specific topics are discussed: pricing, competitors, technical requirements, next steps, budget, and more.</li>
<li><strong>Talk Ratio Analysis:</strong> Measures rep versus buyer talk time. The best discovery calls have 60%+ buyer talk time.</li>
<li><strong>Deal Intelligence:</strong> Aggregates conversation data across all calls in a deal to surface risk signals: missed stakeholders, unresolved objections, stalled timelines.</li>
<li><strong>Coaching Moments:</strong> AI flags specific moments that warrant manager review: long monologues, missed questions, competitor mentions, or pricing discussions.</li>
</ul>

<h2>Impact on Enablement</h2>
<p>Conversation intelligence has fundamentally changed how enablement teams operate. Instead of relying on self-reported data from reps and anecdotal feedback from managers, teams now have objective data about what happens in every buyer conversation.</p>

<p>This data powers everything from onboarding (curating call libraries for new hires) to content strategy (identifying which messaging resonates) to methodology adoption (measuring whether reps are executing the qualification framework). CI turns enablement from an art into a data-driven discipline.</p>""",
        "faq": [
            ("What is conversation intelligence?", "Conversation intelligence is AI-powered technology that records, transcribes, and analyzes sales conversations. It surfaces insights about talk ratios, topics discussed, competitor mentions, and deal risks that enable better coaching and decision-making."),
            ("What are the leading conversation intelligence platforms?", "Gong, Chorus (owned by ZoomInfo), and Clari Copilot are the market leaders. Each offers automatic recording, transcription, AI-powered analysis, and coaching workflows. Most integrate with CRM, calendar, and conferencing tools."),
        ],
        "related": ["Call Recording", "Sales Coaching", "Win/Loss Analysis", "Sales Readiness"],
    },
    {
        "term": "Win Rate",
        "slug": "win-rate",
        "short": "The percentage of sales opportunities that result in a closed-won deal, a key indicator of sales effectiveness.",
        "body": """<p>Win rate is the percentage of qualified sales opportunities that result in a closed-won deal. It is one of the most important metrics in sales because it directly reflects the team's ability to convert pipeline into revenue. A higher win rate means more efficient use of sales capacity and marketing investment.</p>

<p>Win rate can be calculated in multiple ways. The simplest is closed-won deals divided by total closed deals (won plus lost). Some organizations include open deals in the denominator, though this produces a less meaningful metric because open deals have not reached a final outcome.</p>

<h2>Benchmarking Win Rates</h2>
<ul>
<li><strong>Overall B2B SaaS:</strong> Average win rates typically fall between 20-30% for competitive deals. Best-in-class organizations achieve 30-40%.</li>
<li><strong>By Segment:</strong> SMB tends to have higher win rates (25-35%) but smaller deal sizes. Enterprise win rates are often lower (15-25%) but with larger deals.</li>
<li><strong>By Source:</strong> Inbound leads typically convert at higher rates than outbound because the buyer has self-selected interest.</li>
</ul>

<h2>Improving Win Rate Through Enablement</h2>
<p>Enablement teams influence win rate through several levers. Better discovery training means reps qualify more accurately, spending time on winnable deals. Competitive intelligence and battle cards help reps differentiate in competitive situations. Coaching on deal strategy prevents common mistakes that cost deals late in the cycle.</p>

<p>Win rate analysis by deal stage reveals where deals break down. If conversion from demo to proposal is strong but proposal to close is weak, the issue may be in negotiation skills or business case development. Stage-specific analysis helps enablement target interventions precisely.</p>

<p>Tracking win rate over time, segmented by rep, segment, competitor, and lead source, provides the granularity needed to identify systemic issues versus individual performance gaps.</p>""",
        "faq": [
            ("How do you calculate win rate?", "Win rate equals the number of closed-won deals divided by total closed deals (won plus lost), expressed as a percentage. Some organizations track competitive win rate separately, counting only deals where a specific competitor was in the evaluation."),
            ("What is a good win rate for B2B SaaS?", "Average B2B SaaS win rates range from 20-30%. Best-in-class organizations achieve 30-40%. Win rates vary significantly by segment, deal source, and competitive landscape, so internal benchmarks are more useful than industry averages."),
        ],
        "related": ["Win/Loss Analysis", "Sales Velocity", "Quota Attainment", "Pipeline Velocity"],
    },
    {
        "term": "Win/Loss Analysis",
        "slug": "win-loss-analysis",
        "short": "A structured review process that examines why deals were won or lost to extract insights for improving sales performance.",
        "body": """<p>Win/loss analysis is the systematic practice of interviewing buyers and reviewing deal data after opportunities close (both won and lost) to understand the factors that influenced the outcome. It is one of the highest-value activities in enablement because it provides direct buyer feedback on what is working and what is not.</p>

<p>The most valuable insights come from lost deals. Winners often attribute success to their own skill, but buyers who chose a competitor will tell you exactly where you fell short. This candid feedback is difficult to get any other way.</p>

<h2>Running a Win/Loss Program</h2>
<ul>
<li><strong>Buyer Interviews:</strong> The gold standard. A neutral third party (not the rep) interviews the buyer 2-4 weeks after the decision. Questions cover decision criteria, vendor evaluation, strengths and weaknesses of each option, and the final decision driver.</li>
<li><strong>Rep Debrief:</strong> Internal interviews with the rep and manager to capture the seller's perspective. Compare this with the buyer's feedback to identify perception gaps.</li>
<li><strong>Data Analysis:</strong> Quantitative review of deal attributes: deal size, cycle length, competitors present, stakeholders involved, and content shared.</li>
<li><strong>Pattern Identification:</strong> Aggregate findings across multiple deals to identify systemic themes, not just one-off issues.</li>
</ul>

<h2>Acting on Win/Loss Insights</h2>
<p>Win/loss analysis generates insights across multiple functions. Product teams learn about feature gaps. Marketing learns about positioning effectiveness. Enablement learns about skill gaps and content needs. Sales leadership learns about competitive dynamics and pricing sensitivity.</p>

<p>The most effective programs publish a monthly or quarterly win/loss report with clear themes and actionable recommendations. Each recommendation should have an owner and a deadline. Without this follow-through, win/loss analysis becomes an academic exercise.</p>""",
        "faq": [
            ("What is win/loss analysis?", "Win/loss analysis is a structured review of closed deals to understand why they were won or lost. It involves buyer interviews, rep debriefs, and data analysis to extract actionable insights for improving sales performance."),
            ("Who should conduct win/loss interviews?", "A neutral party, either an internal enablement professional or an external consultant, should conduct buyer interviews. Buyers are more candid with someone who was not involved in the deal. The rep should not interview their own buyer."),
        ],
        "related": ["Win Rate", "Competitive Intelligence", "Battle Card", "Sales Coaching"],
    },
    {
        "term": "Sales Velocity",
        "slug": "sales-velocity",
        "short": "A metric that measures how quickly deals move through the pipeline and generate revenue, combining deal count, value, win rate, and cycle length.",
        "body": """<p>Sales velocity measures how quickly a sales team generates revenue. It is calculated by multiplying the number of opportunities by the average deal value by the win rate, then dividing by the average sales cycle length. The formula: (Opportunities x Deal Value x Win Rate) / Cycle Length = Revenue per time period.</p>

<p>Sales velocity is a composite metric, which makes it uniquely useful. Improving any one of the four inputs improves velocity. This gives enablement and sales leadership multiple levers to pull, rather than focusing on a single metric in isolation.</p>

<h2>The Four Levers of Sales Velocity</h2>
<ul>
<li><strong>Number of Opportunities:</strong> More qualified deals entering the pipeline. Marketing, SDRs, and outbound efforts drive this lever.</li>
<li><strong>Average Deal Value:</strong> Larger deals through better positioning, multi-product selling, or moving upmarket. Enablement supports this through value selling training and business case development.</li>
<li><strong>Win Rate:</strong> Higher conversion through better qualification, competitive positioning, and deal execution. This is enablement's most direct lever.</li>
<li><strong>Sales Cycle Length:</strong> Shorter deal cycles through better discovery, mutual action plans, and stakeholder engagement. Enablement reduces cycle length by removing friction from the buyer journey.</li>
</ul>

<h2>Using Sales Velocity for Diagnosis</h2>
<p>Tracking velocity by segment, rep, and time period reveals where performance is breaking down. If velocity drops, the four-lever breakdown shows exactly which input changed. A velocity decline driven by falling win rates requires different intervention than one driven by longer cycle lengths.</p>

<p>Enablement teams should report on velocity alongside the four component metrics. This gives leadership a holistic view of sales performance and helps prioritize enablement investments toward the lever with the most room for improvement.</p>""",
        "faq": [
            ("How do you calculate sales velocity?", "Sales velocity equals (Number of Opportunities x Average Deal Value x Win Rate) divided by Average Sales Cycle Length. The result represents revenue generated per time period."),
            ("How can enablement improve sales velocity?", "Enablement improves velocity by increasing win rate (better training and competitive intelligence), reducing cycle length (mutual action plans and buyer enablement), and increasing deal value (value selling and business case development)."),
        ],
        "related": ["Win Rate", "Deal Cycle", "Pipeline Velocity", "Quota Attainment"],
    },
    {
        "term": "Deal Cycle",
        "slug": "deal-cycle",
        "short": "The total elapsed time from when an opportunity is created to when it closes, whether won or lost.",
        "body": """<p>The deal cycle (also called sales cycle) is the total elapsed time from when an opportunity enters the pipeline to when it reaches a closed-won or closed-lost status. It is a fundamental metric for forecasting, capacity planning, and evaluating sales efficiency. Longer deal cycles mean slower revenue realization and higher cost of sale.</p>

<p>Average deal cycles vary dramatically by segment and industry. SMB SaaS deals typically close in 14-30 days. Mid-market deals range from 30-90 days. Enterprise deals can take 6-12 months or longer, especially when procurement and legal review are involved.</p>

<h2>Stages of the Deal Cycle</h2>
<ul>
<li><strong>Discovery:</strong> Initial qualification conversations to understand the buyer's needs and determine mutual fit.</li>
<li><strong>Evaluation:</strong> Demos, technical assessments, proof of concept, and deeper dive into capabilities.</li>
<li><strong>Proposal:</strong> Formal proposal delivery, pricing discussion, and business case presentation.</li>
<li><strong>Negotiation:</strong> Terms and conditions, legal review, procurement process, and contract finalization.</li>
<li><strong>Close:</strong> Contract execution and handoff to implementation or customer success.</li>
</ul>

<h2>Reducing Deal Cycle Length</h2>
<p>Enablement teams reduce deal cycle length by removing friction at each stage. Better discovery templates help reps gather complete information on the first call instead of needing follow-ups. Pre-built demo environments eliminate the wait for custom demos. Business case templates accelerate the proposal stage. Mutual action plans keep both parties accountable to timelines.</p>

<p>Champion enablement is another powerful lever. When your internal champion has the materials they need to sell internally (executive summaries, ROI calculators, competitive comparisons), internal approvals move faster because the champion is not waiting for you to create those materials on demand.</p>""",
        "faq": [
            ("What is a deal cycle in sales?", "A deal cycle is the total time from when an opportunity enters the pipeline to when it closes. It is also called the sales cycle. Tracking deal cycle length helps with forecasting, capacity planning, and identifying process bottlenecks."),
            ("What is the average B2B SaaS deal cycle?", "SMB deals typically close in 14-30 days, mid-market in 30-90 days, and enterprise in 3-12 months. These ranges vary by product complexity, price point, and the buyer's procurement process."),
        ],
        "related": ["Sales Velocity", "Pipeline Velocity", "Mutual Action Plan", "Sales Process"],
    },
    {
        "term": "Pipeline Velocity",
        "slug": "pipeline-velocity",
        "short": "The speed at which opportunities progress through pipeline stages, indicating overall sales motion health.",
        "body": """<p>Pipeline velocity measures how quickly opportunities progress through the stages of the sales pipeline. While often used interchangeably with sales velocity, pipeline velocity focuses specifically on stage-to-stage conversion speed rather than the end-to-end revenue calculation. It answers the question: are deals moving through the pipeline at a healthy pace, or are they stalling?</p>

<p>Tracking pipeline velocity at the stage level provides diagnostic power that the composite sales velocity metric does not. If deals are moving quickly through discovery but stalling at the proposal stage, you have a specific problem to solve. If deals are entering the pipeline but not converting from stage one to stage two, qualification standards may be too loose.</p>

<h2>Measuring Pipeline Velocity</h2>
<ul>
<li><strong>Stage Conversion Rate:</strong> What percentage of deals advance from each stage to the next? Healthy pipelines maintain consistent conversion rates at each stage.</li>
<li><strong>Time in Stage:</strong> How many days do deals spend in each stage on average? Spikes in time-in-stage indicate bottlenecks.</li>
<li><strong>Stage Skip Rate:</strong> How often do deals skip stages? Frequent skipping may indicate that stages are not reflecting the actual buying process.</li>
<li><strong>Pipeline Coverage:</strong> The ratio of pipeline value to quota. Typical targets are 3-4x coverage, meaning the pipeline contains 3-4 times the quota amount to account for expected attrition.</li>
</ul>

<h2>Enablement Actions to Improve Velocity</h2>
<p>When velocity slows at a specific stage, enablement can diagnose the root cause and intervene. Slow discovery-to-demo conversion may indicate poor qualification. Slow demo-to-proposal may mean demos are not connecting with buyer needs. Slow proposal-to-close may indicate weak business case development or poor negotiation skills.</p>

<p>Pipeline reviews that include velocity metrics alongside deal details give managers the context to coach effectively. Instead of only asking "what is the next step?", managers can ask "this deal has been in evaluation for 45 days versus a 20-day average. What is blocking it?"</p>""",
        "faq": [
            ("What is pipeline velocity?", "Pipeline velocity measures how quickly deals progress through the stages of the sales pipeline. It includes stage conversion rates, time spent in each stage, and overall pipeline health indicators."),
            ("How is pipeline velocity different from sales velocity?", "Sales velocity is a composite formula (opportunities x deal value x win rate / cycle length) that measures overall revenue generation speed. Pipeline velocity focuses on stage-by-stage progression, providing more diagnostic detail about where deals are moving or stalling."),
        ],
        "related": ["Sales Velocity", "Deal Cycle", "Win Rate", "Sales Process"],
    },
    {
        "term": "Quota Attainment",
        "slug": "quota-attainment",
        "short": "The percentage of a sales rep's or team's revenue target that is achieved in a given period.",
        "body": """<p>Quota attainment is the percentage of a sales rep's or team's revenue target that is achieved within a defined period, typically monthly, quarterly, or annually. It is the most fundamental measure of sales performance. A rep achieving 100% quota attainment has met their target; above 100% indicates overperformance; below indicates a gap.</p>

<p>Average quota attainment across B2B SaaS is often cited around 50-60%, meaning roughly half of reps hit their number in any given period. Top-performing organizations achieve 60-70% attainment rates. These numbers highlight the gap between targets and execution that enablement teams work to close.</p>

<h2>Factors That Influence Quota Attainment</h2>
<ul>
<li><strong>Quota Setting:</strong> Unrealistic quotas guarantee low attainment regardless of rep quality. Quotas should be data-driven and achievable by at least 60-70% of the team.</li>
<li><strong>Territory/Account Quality:</strong> Uneven distribution of opportunity across territories creates attainment disparities unrelated to rep skill.</li>
<li><strong>Ramp Time:</strong> New reps in ramp mode pull down team attainment averages. Reducing ramp time directly improves aggregate attainment.</li>
<li><strong>Enablement Quality:</strong> Better training, content, coaching, and tools give reps more at-bats and higher conversion rates.</li>
<li><strong>Market Conditions:</strong> Economic headwinds, competitive dynamics, and industry-specific factors affect attainability.</li>
</ul>

<h2>Enablement's Impact on Attainment</h2>
<p>Enablement teams improve quota attainment by addressing the controllable inputs: reducing ramp time so new reps contribute sooner, improving win rates through better competitive intelligence and coaching, increasing deal values through value selling training, and shortening deal cycles by reducing buyer friction.</p>

<p>The most sophisticated enablement teams correlate their programs directly to attainment. They can show that reps who completed a specific certification achieve X% higher attainment, or that reps who use battle cards regularly win competitive deals at Y% higher rates. This data justifies continued investment in enablement resources.</p>""",
        "faq": [
            ("What is quota attainment?", "Quota attainment is the percentage of a sales target achieved in a given period. A rep at 100% has met their quota. It is the primary measure of individual and team sales performance."),
            ("What percentage of reps typically hit quota?", "Industry averages show 50-60% of B2B SaaS reps achieve quota in a given period. Top-performing organizations see 60-70% attainment rates. Attainment below 40% usually signals systemic issues beyond individual performance."),
        ],
        "related": ["Win Rate", "Sales Velocity", "Ramp Time", "Sales Coaching"],
    },
    {
        "term": "Sales Certification",
        "slug": "sales-certification",
        "short": "A formal assessment process that validates a rep's readiness to sell a product, execute a methodology, or handle a specific selling scenario.",
        "body": """<p>Sales certification is a structured assessment that verifies a rep has the knowledge and skills required to perform specific selling activities. Certifications can cover product knowledge, sales methodology execution, competitive positioning, demo delivery, objection handling, or any other competency that enablement teams need to validate before a rep engages buyers independently.</p>

<p>Certification programs serve two purposes. First, they create accountability: reps know they will be tested on the material, which drives engagement with training content. Second, they protect the buyer experience: a rep who has not been certified on a new product should not be positioning it in live deals.</p>

<h2>Types of Sales Certifications</h2>
<ul>
<li><strong>Knowledge Certifications:</strong> Written or multiple-choice assessments that test factual knowledge about products, processes, or competitive positioning.</li>
<li><strong>Skill Certifications:</strong> Performance-based assessments where reps demonstrate a skill through role-play, video submission, or live observation. These are harder to administer but far more valuable.</li>
<li><strong>Methodology Certifications:</strong> Assessments that verify a rep can execute the company's sales methodology (MEDDPICC qualification, Challenger teaching, etc.) in realistic scenarios.</li>
<li><strong>Ongoing Certifications:</strong> Recurring assessments that ensure continued proficiency, especially after product updates or competitive shifts.</li>
</ul>

<h2>Building Effective Certification Programs</h2>
<p>The best certifications test application, not recall. A rep who can recite product features is not necessarily a rep who can position those features against a competitor in a live conversation. Design assessments around realistic scenarios where the rep must demonstrate competency in context.</p>

<p>Tie certifications to business outcomes. If certified reps demonstrably outperform non-certified reps on key metrics, the program justifies its investment. If there is no measurable difference, the certification may be testing the wrong things or setting the bar too low.</p>""",
        "faq": [
            ("What is a sales certification?", "A sales certification is a formal assessment that validates a rep's knowledge and skill in a specific area: product expertise, methodology execution, competitive positioning, or demo delivery. It ensures reps are prepared before engaging buyers."),
            ("How often should sales certifications be updated?", "Certifications should be reviewed and updated at least quarterly, or whenever there is a significant product launch, competitive shift, or methodology change. Ongoing certifications with regular recertification prevent skills from going stale."),
        ],
        "related": ["Sales Readiness", "Sales Onboarding", "Microlearning", "Just-in-Time Learning"],
    },
    {
        "term": "Just-in-Time Learning",
        "slug": "just-in-time-learning",
        "short": "Delivering training content at the exact moment a rep needs it, rather than in advance during formal sessions.",
        "body": """<p>Just-in-time (JIT) learning delivers training content at the point of need rather than in a scheduled session. Instead of expecting reps to remember everything from a week-long onboarding program, JIT provides the right information at the right moment: a competitive brief before a call with a specific competitor, an objection handling guide when a deal enters negotiation, or a product FAQ when a rep is preparing for a technical discussion.</p>

<p>JIT learning addresses the fundamental flaw of traditional training: people forget most of what they learn within days. The Ebbinghaus forgetting curve shows that without reinforcement, learners lose 70% of new information within 24 hours. JIT bypasses this by delivering knowledge when context makes it sticky.</p>

<h2>How JIT Learning Works in Practice</h2>
<ul>
<li><strong>CRM-Triggered Content:</strong> When a deal moves to a new stage, the enablement platform surfaces relevant content automatically. Move to demo stage? Here is the demo best practices guide.</li>
<li><strong>Competitor-Triggered Content:</strong> When a competitor is tagged on an opportunity, the relevant battle card appears in the rep's workflow.</li>
<li><strong>Search-Driven Access:</strong> A well-organized content library with strong search lets reps find answers in seconds instead of asking Slack or waiting for manager response.</li>
<li><strong>AI-Powered Recommendations:</strong> Modern platforms use deal context to recommend the most relevant content, training modules, and best practices.</li>
</ul>

<h2>JIT and Enablement Platform Strategy</h2>
<p>JIT learning requires tight integration between the enablement platform, CRM, and content management system. The content needs to be tagged with metadata (deal stage, competitor, product, persona) that enables contextual delivery. Without this foundation, JIT becomes just another content library.</p>

<p>The enablement team's role shifts from scheduling training sessions to curating and tagging content for contextual delivery. This is a fundamentally different operating model that requires ongoing content governance and platform administration.</p>""",
        "faq": [
            ("What is just-in-time learning in sales?", "Just-in-time learning delivers training content at the exact moment a rep needs it, triggered by deal context, CRM events, or rep-initiated search. It replaces scheduled training with contextual, on-demand knowledge delivery."),
            ("How is JIT learning different from traditional training?", "Traditional training delivers knowledge in advance through scheduled sessions. JIT delivers knowledge at the point of need. The key advantage is retention: information delivered in context when the rep needs it is retained far better than information from a classroom session weeks earlier."),
        ],
        "related": ["Microlearning", "Spaced Repetition", "Sales Content Management", "Sales Readiness"],
    },
    {
        "term": "Microlearning",
        "slug": "microlearning",
        "short": "Short, focused learning modules (3-7 minutes) designed to teach a single concept or skill without disrupting the workday.",
        "body": """<p>Microlearning breaks training content into short, focused modules that teach a single concept or skill in 3-7 minutes. Instead of hour-long courses that require scheduling dedicated time, microlearning fits into the gaps in a rep's day: between meetings, during a commute, or as a quick refresher before a call.</p>

<p>The format aligns with how people actually consume information. Attention spans during training decline sharply after 10-15 minutes. Microlearning keeps each module within the window of peak engagement, improving retention without requiring large time commitments from busy sellers.</p>

<h2>Effective Microlearning Formats</h2>
<ul>
<li><strong>Short Video:</strong> 3-5 minute videos covering a single topic: how to handle a specific objection, a product feature walkthrough, or a competitive positioning update.</li>
<li><strong>Interactive Quizzes:</strong> Knowledge checks that reinforce key concepts through retrieval practice. More effective than passive video alone.</li>
<li><strong>Scenario-Based:</strong> "What would you do?" scenarios that present a realistic selling situation and ask the rep to choose the best response.</li>
<li><strong>Flashcards:</strong> Quick recall exercises for product specs, pricing, competitive differentiators, and methodology frameworks.</li>
<li><strong>Audio Snippets:</strong> Short audio clips from top performer calls that illustrate a specific technique.</li>
</ul>

<h2>Microlearning and Spaced Repetition</h2>
<p>Microlearning is most effective when combined with spaced repetition. Instead of completing a module once, the system resurfaces key concepts at increasing intervals. This leverages the spacing effect, a well-documented cognitive principle showing that distributed practice produces stronger long-term retention than massed practice.</p>

<p>Enablement platforms like MindTickle and WorkRamp support microlearning natively, with AI-driven recommendations that adjust the learning path based on individual performance and knowledge gaps.</p>""",
        "faq": [
            ("What is microlearning in sales enablement?", "Microlearning is the practice of delivering training in short, focused modules of 3-7 minutes each. Each module covers a single concept or skill, making it easy for reps to learn without dedicating large blocks of time."),
            ("Is microlearning effective for sales training?", "Yes. Research shows that microlearning combined with spaced repetition produces higher retention than traditional long-form training. The format fits the reality of a seller's schedule and keeps engagement high by staying within attention span limits."),
        ],
        "related": ["Spaced Repetition", "Just-in-Time Learning", "Sales Certification", "Sales Readiness"],
    },
    {
        "term": "Spaced Repetition",
        "slug": "spaced-repetition",
        "short": "A learning technique that revisits concepts at increasing intervals to strengthen long-term memory retention.",
        "body": """<p>Spaced repetition is a learning methodology that presents information at strategically increasing intervals to optimize long-term retention. Instead of reviewing material once and moving on, spaced repetition systems (SRS) schedule reviews at the precise moments when the learner is about to forget, reinforcing the memory just as it begins to decay.</p>

<p>The science behind spaced repetition is well-established. Hermann Ebbinghaus documented the forgetting curve in 1885, showing that memory decays exponentially without reinforcement. Spaced repetition counteracts this by timing reviews to coincide with the steepest part of the curve, converting short-term memory into long-term knowledge with minimal total study time.</p>

<h2>Spaced Repetition in Sales Enablement</h2>
<ul>
<li><strong>Product Knowledge:</strong> Key specs, pricing tiers, and feature capabilities reviewed at intervals until reps can recall them without hesitation.</li>
<li><strong>Competitive Positioning:</strong> Differentiation points and objection responses reinforced over time so they become natural in conversation.</li>
<li><strong>Methodology Frameworks:</strong> MEDDPICC criteria, SPIN question types, or Challenger principles revisited at intervals until they are automatic.</li>
<li><strong>Customer Stories:</strong> Proof points and case study metrics refreshed so reps can reference them credibly in live conversations.</li>
</ul>

<h2>Implementation Approaches</h2>
<p>Modern enablement platforms build spaced repetition into their learning modules. After a rep completes a training module, the system automatically schedules follow-up quizzes at 1 day, 3 days, 7 days, 14 days, and 30 days. Correct answers extend the interval; incorrect answers shorten it, focusing review time on weaker areas.</p>

<p>The enablement team's role is to identify which knowledge is worth reinforcing through SRS. Not everything needs spaced repetition. Focus on high-impact knowledge: competitive differentiators, pricing objection responses, qualification criteria, and product positioning for key personas. This keeps the learning load manageable while maximizing retention of mission-critical information.</p>""",
        "faq": [
            ("What is spaced repetition?", "Spaced repetition is a learning technique that schedules reviews of material at increasing intervals to strengthen long-term retention. It counteracts the natural forgetting curve by reinforcing knowledge just before it fades."),
            ("How effective is spaced repetition for sales training?", "Research shows spaced repetition can improve long-term retention by 50-80% compared to single-exposure learning. For sales teams, this means reps retain competitive positioning, product knowledge, and methodology frameworks far better than with traditional one-time training."),
        ],
        "related": ["Microlearning", "Just-in-Time Learning", "Sales Certification", "Sales Readiness"],
    },
    {
        "term": "Content Adoption",
        "slug": "content-adoption",
        "short": "The rate at which sales reps actually use the content enablement teams create and distribute.",
        "body": """<p>Content adoption measures whether sales reps are actually using the content that enablement and marketing teams produce. It is the gap between content created and content used. High adoption means reps find the content valuable and relevant. Low adoption means content is being produced that the field does not use, wasting production effort and leaving reps to improvise their own materials.</p>

<p>Industry data consistently shows that 60-70% of sales content goes unused. This represents a massive waste of marketing and enablement resources. Content adoption metrics help teams identify what is working, retire what is not, and focus production on formats and topics that reps actually need.</p>

<h2>Measuring Content Adoption</h2>
<ul>
<li><strong>View Rate:</strong> What percentage of reps have accessed a given asset? Low view rates may indicate distribution problems.</li>
<li><strong>Share Rate:</strong> What percentage of reps have shared the content with buyers? This is the most meaningful adoption metric because it indicates the rep found the content valuable enough to use in a deal.</li>
<li><strong>Time to First Use:</strong> How quickly after publishing does a new asset get used? Faster adoption suggests strong relevance and good distribution.</li>
<li><strong>Repeat Usage:</strong> Are reps using the content once or returning to it? Repeat usage suggests enduring value.</li>
</ul>

<h2>Improving Content Adoption</h2>
<p>The primary driver of low adoption is relevance. Reps do not use content because it does not match their actual selling needs. The fix is not better distribution; it is better content informed by field input.</p>

<p>Enablement teams should regularly survey reps and analyze deal data to understand content gaps. What do reps wish they had? What questions are buyers asking that existing content does not answer? What competitive situations lack adequate collateral?</p>

<p>Format matters too. Long whitepapers may have low adoption while one-page battle cards have high adoption. Meeting the field where they are, in terms of format, length, and accessibility, dramatically improves adoption rates.</p>""",
        "faq": [
            ("What is content adoption in sales enablement?", "Content adoption measures the rate at which sales reps actually use the content produced by enablement and marketing teams. High adoption means reps find content relevant and valuable. Low adoption indicates a gap between what is produced and what the field needs."),
            ("Why is so much sales content unused?", "Research shows 60-70% of sales content goes unused. Common reasons include poor relevance (content does not match actual selling needs), discoverability problems (reps cannot find it), and format issues (too long or complex for the situation)."),
        ],
        "related": ["Content Engagement", "Sales Content Management", "Sales Playbook", "Digital Sales Room"],
    },
    {
        "term": "Content Engagement",
        "slug": "content-engagement",
        "short": "Metrics that track how buyers interact with sales content after it is shared: views, time spent, pages read, and forwards.",
        "body": """<p>Content engagement measures how buyers interact with sales content after a rep shares it. This goes beyond whether the rep used the content (adoption) to tracking what the buyer did with it: did they open it, how long did they spend on each page, did they forward it to colleagues, and which sections held their attention?</p>

<p>Buyer engagement data is one of the most valuable signals in modern sales. When a buyer spends 15 minutes reading a case study and forwards it to three colleagues, that deal is advancing internally. When a buyer never opens a proposal, the deal may be in trouble. This intelligence helps reps prioritize follow-up and adjust their strategy based on actual buyer behavior.</p>

<h2>Key Engagement Metrics</h2>
<ul>
<li><strong>Open Rate:</strong> Did the buyer open the shared content? Low open rates may indicate poor subject lines or timing.</li>
<li><strong>Time Spent:</strong> How long did the buyer engage with the content? Longer engagement suggests genuine interest.</li>
<li><strong>Page-Level Analytics:</strong> Which specific pages or sections received the most attention? This reveals what matters most to the buyer.</li>
<li><strong>Forward Rate:</strong> Did the buyer share the content with colleagues? Forwards indicate internal champion behavior and deal expansion.</li>
<li><strong>Return Visits:</strong> Did the buyer come back to the content? Repeat views suggest the buyer is using it in their internal evaluation process.</li>
</ul>

<h2>Using Engagement Data</h2>
<p>Engagement data powers smarter selling. Reps can follow up with buyers who have shown high engagement, reference the specific sections that received attention, and identify additional stakeholders who received forwarded content. This turns every content share into an intelligence-gathering event.</p>

<p>At the aggregate level, engagement data tells enablement teams which content performs best. Assets with high engagement and correlation to deal advancement should be promoted. Assets with low engagement should be revised or retired. This closes the feedback loop between content production and field effectiveness.</p>""",
        "faq": [
            ("What is content engagement in sales?", "Content engagement tracks how buyers interact with sales content after it is shared. It measures opens, time spent, pages viewed, forwards, and return visits, providing intelligence about buyer interest and deal health."),
            ("How does content engagement data help sales reps?", "Engagement data tells reps which buyers are actively reviewing materials, which sections interest them most, and whether content is being shared internally. This helps reps prioritize follow-up and personalize their next conversation based on what the buyer cared about."),
        ],
        "related": ["Content Adoption", "Sales Content Management", "Digital Sales Room", "Buyer Enablement"],
    },
    {
        "term": "Buyer Enablement",
        "slug": "buyer-enablement",
        "short": "Providing buyers with the tools, content, and information they need to navigate their internal buying process and build consensus.",
        "body": """<p>Buyer enablement is the practice of equipping buyers with the resources they need to navigate their internal purchasing process. In complex B2B sales, the buyer's job does not end when they decide they want your product. They still need to build consensus among stakeholders, justify the investment to finance, clear security and legal reviews, and navigate procurement. Buyer enablement supports all of these internal activities.</p>

<p>Gartner research shows that B2B buying groups now average 6-10 decision-makers, each consuming 4-5 pieces of content independently. If sellers only enable themselves and not their buyers, deals stall because the internal champion lacks the tools to sell on their behalf.</p>

<h2>Buyer Enablement Materials</h2>
<ul>
<li><strong>Executive Summaries:</strong> One-pagers designed for economic buyers who will not read a 20-page proposal.</li>
<li><strong>ROI Calculators:</strong> Interactive tools that let the buyer model their own financial return using their specific numbers.</li>
<li><strong>Competitive Comparisons:</strong> Fair, factual comparisons the buyer can share internally to demonstrate due diligence.</li>
<li><strong>Security and Compliance Documentation:</strong> Pre-built answers to common security questionnaires and compliance certifications.</li>
<li><strong>Implementation Guides:</strong> Content that addresses the buyer's "what happens after we buy?" concerns.</li>
<li><strong>Internal Business Case Templates:</strong> Frameworks the champion can fill in and present to their leadership.</li>
</ul>

<h2>Why Buyer Enablement Accelerates Deals</h2>
<p>Deals stall most often not because the buyer does not want to purchase, but because they cannot get internal alignment. Buyer enablement removes that bottleneck by giving the champion everything they need to advocate internally without waiting for the seller to create materials on demand.</p>

<p>Digital sales rooms are the primary delivery mechanism for buyer enablement content. A well-organized DSR gives every stakeholder in the buying group direct access to the information relevant to their role, from the CFO's ROI summary to the IT team's security documentation.</p>""",
        "faq": [
            ("What is buyer enablement?", "Buyer enablement provides buyers with the tools, content, and information they need to navigate their internal purchasing process. It helps champions build consensus, justify investment, and clear procurement hurdles."),
            ("How is buyer enablement different from sales enablement?", "Sales enablement equips sellers. Buyer enablement equips the buyer's internal champion with materials to sell on your behalf inside their organization. Both are necessary for complex B2B deals."),
        ],
        "related": ["Champion Enablement", "Digital Sales Room", "Business Case", "ROI Calculator"],
    },
    {
        "term": "Champion Enablement",
        "slug": "champion-enablement",
        "short": "Equipping your internal champion within the buying organization with the tools and content to advocate for your solution.",
        "body": """<p>Champion enablement is a focused subset of buyer enablement that specifically arms your internal advocate (the champion) with everything they need to sell your solution inside their organization. The champion is the person who believes in your product, has influence within the buying group, and is willing to spend their political capital to push the deal forward.</p>

<p>Even the most enthusiastic champion will fail without proper support. They need to present your value proposition to executives who will never talk to you. They need to defend the investment against competing priorities. They need to navigate procurement without your direct involvement. Champion enablement provides the ammunition for all of these internal battles.</p>

<h2>What Champions Need</h2>
<ul>
<li><strong>Executive Presentation:</strong> A polished deck the champion can present to their leadership, customized with their specific data and use case.</li>
<li><strong>Business Case Template:</strong> A fillable framework that quantifies the financial impact in terms the CFO cares about: ROI, payback period, cost of inaction.</li>
<li><strong>Competitive Summary:</strong> A factual comparison the champion can reference when asked "have we looked at alternatives?"</li>
<li><strong>FAQ Document:</strong> Anticipated questions from different stakeholders (IT, finance, operations) with clear, concise answers.</li>
<li><strong>Implementation Timeline:</strong> A realistic project plan that shows the path from contract to value realization.</li>
</ul>

<h2>Identifying and Developing Champions</h2>
<p>Not every contact is a champion. Champions have three qualities: power (they can influence the decision), access (they can reach the economic buyer), and personal motivation (solving this problem helps their career). Identifying a true champion early in the deal is critical; without one, enterprise deals rarely close.</p>

<p>Enablement teams should build champion enablement kits that reps can customize for each deal. Pre-built templates reduce the time reps spend creating one-off materials and ensure consistent quality across the sales team.</p>""",
        "faq": [
            ("What is champion enablement?", "Champion enablement equips your internal advocate in the buying organization with the presentations, business cases, competitive comparisons, and FAQs they need to sell your solution internally to other stakeholders and decision-makers."),
            ("How do you identify a sales champion?", "A true champion has three qualities: power to influence the decision, access to the economic buyer, and personal motivation to see the deal succeed. They actively advance the deal and share internal intelligence with the seller."),
        ],
        "related": ["Buyer Enablement", "MEDDPICC", "Business Case", "Digital Sales Room"],
    },
    {
        "term": "Sales Kickoff (SKO)",
        "slug": "sales-kickoff-sko",
        "short": "An annual or semi-annual event that aligns the sales organization on strategy, goals, methodology, and motivation for the upcoming period.",
        "body": """<p>A sales kickoff (SKO) is a large-scale event, typically held annually or semi-annually, that brings the sales organization together to align on strategy, launch new initiatives, reinforce methodology, celebrate wins, and build team culture. SKOs are one of the largest investments enablement teams make, often costing $1,000-$3,000+ per attendee when accounting for travel, venue, and production.</p>

<p>The best SKOs balance strategic content with practical skills training and team-building. The worst ones are three days of executive keynotes that reps forget by the following Monday. The difference comes down to how well enablement teams design the event for lasting impact.</p>

<h2>SKO Content Pillars</h2>
<ul>
<li><strong>Strategy and Vision:</strong> Executive presentations on company direction, market positioning, and annual goals. Keep these concise; reps need context but not a board-level strategy review.</li>
<li><strong>Product and Roadmap:</strong> New product launches, feature updates, and roadmap previews that reps need to sell effectively in the upcoming period.</li>
<li><strong>Skills Training:</strong> Interactive workshops on methodology, negotiation, discovery, or other skills. These should be hands-on, not lecture-based.</li>
<li><strong>Competitive Updates:</strong> Changes in the competitive landscape, updated battle cards, and new positioning.</li>
<li><strong>Recognition:</strong> Awards and celebrations for top performers. This drives motivation and reinforces the behaviors the organization wants to see.</li>
</ul>

<h2>Making SKO Impact Last</h2>
<p>The biggest risk with SKOs is that the energy fades within weeks. Enablement teams should plan a 30-60-90 day reinforcement campaign after the event. This includes microlearning modules that revisit key sessions, manager-led follow-ups in team meetings, and certifications that test retention of critical content.</p>

<p>Recording sessions and making them available on-demand extends the value beyond the event itself. New hires who join after SKO can access the content, and reps can revisit sessions when they become contextually relevant.</p>""",
        "faq": [
            ("What is a sales kickoff?", "A sales kickoff (SKO) is an annual or semi-annual event that aligns the sales organization on strategy, goals, methodology, and culture. It combines executive presentations, skills training, product updates, and recognition."),
            ("How do you measure SKO effectiveness?", "Measure SKO impact through post-event knowledge assessments, 30/60/90-day content retention checks, methodology adoption metrics, and correlation with pipeline and revenue performance in the months following the event."),
        ],
        "related": ["Sales Methodology", "Sales Readiness", "Sales Certification", "Microlearning"],
    },
    {
        "term": "Pitch Deck",
        "slug": "pitch-deck",
        "short": "A presentation used by sales reps to introduce the company, product value, and solution fit during prospect meetings.",
        "body": """<p>A pitch deck is a structured presentation that sales reps use to introduce the company, establish credibility, communicate the product's value proposition, and create interest during prospect meetings. Unlike investor pitch decks, a sales pitch deck is designed to resonate with buyers by focusing on their specific challenges and the outcomes they can achieve.</p>

<p>The best pitch decks are not product-centric. They lead with the buyer's world: the market trends affecting their business, the challenges their peers face, and the cost of the status quo. Product capabilities enter the conversation only after the buyer's context has been established.</p>

<h2>Anatomy of an Effective Sales Pitch Deck</h2>
<ul>
<li><strong>Opening Hook (1-2 slides):</strong> A provocative insight or data point about the buyer's industry that establishes credibility and signals you understand their world.</li>
<li><strong>Problem Frame (2-3 slides):</strong> Articulate the specific challenges the buyer faces, ideally in terms they have already confirmed during discovery. Quantify the cost of these problems.</li>
<li><strong>Solution Overview (2-3 slides):</strong> How your product addresses the stated problems. Focus on outcomes, not features. Lead with what changes for the buyer, not what your product does.</li>
<li><strong>Proof (2-3 slides):</strong> Customer stories, metrics, and logos that validate your claims. Proof should be relevant to the buyer's industry and company size.</li>
<li><strong>Next Steps (1 slide):</strong> Clear call to action. What happens after this meeting? A demo, a technical evaluation, a stakeholder meeting?</li>
</ul>

<h2>Enablement's Role in Pitch Decks</h2>
<p>Enablement teams should own the master pitch deck and create modular versions for different segments, industries, and use cases. Reps should be able to customize the deck with buyer-specific details without rebuilding it from scratch each time.</p>

<p>Track which slides reps actually use and which they skip. If the entire team skips the same three slides, those slides are not working. Pitch deck analytics from enablement platforms reveal exactly how presentations perform in the field.</p>""",
        "faq": [
            ("What is a sales pitch deck?", "A sales pitch deck is a presentation used during prospect meetings to introduce the company, communicate value, and create interest. Unlike investor decks, sales pitch decks focus on the buyer's challenges and the outcomes the product delivers."),
            ("How many slides should a pitch deck have?", "An effective sales pitch deck typically has 10-15 slides. The key is keeping it focused and conversational. Decks that are too long become presentations instead of conversations, which kills engagement and discovery."),
        ],
        "related": ["Demo Script", "Sales Playbook", "Sales Content Management", "Discovery Call"],
    },
    {
        "term": "Demo Script",
        "slug": "demo-script",
        "short": "A structured guide for product demonstrations that ensures reps connect features to the buyer's specific needs and use cases.",
        "body": """<p>A demo script is a structured guide that helps sales reps deliver product demonstrations aligned to the buyer's specific needs. It is not a word-for-word script (which would sound robotic); rather, it is a framework that ensures the demo covers the right capabilities, connects features to buyer outcomes, and follows a logical flow that builds toward a clear next step.</p>

<p>The most common demo mistake is the "feature tour": showing every capability regardless of what the buyer cares about. Demo scripts prevent this by structuring the demonstration around the buyer's stated problems, discovered during earlier conversations. The script serves as a bridge between discovery insights and product capabilities.</p>

<h2>Components of a Demo Script</h2>
<ul>
<li><strong>Pre-Demo Setup:</strong> How to configure the demo environment, which data set to use, and how to personalize it for the specific buyer.</li>
<li><strong>Opening Recap:</strong> A brief summary of the buyer's challenges and goals (from discovery) that frames the entire demo. This shows the buyer you listened.</li>
<li><strong>Feature-to-Outcome Mapping:</strong> For each capability being demonstrated, the script connects it to a specific buyer pain point. "You mentioned X is costing you Y. Here is how we solve that."</li>
<li><strong>Interaction Points:</strong> Planned moments where the rep pauses to ask the buyer questions, confirm relevance, or invite feedback. Demos should be conversations, not presentations.</li>
<li><strong>Competitive Differentiators:</strong> Points in the demo where your unique strengths are most visible, with suggested commentary that highlights the differentiation naturally.</li>
<li><strong>Closing and Next Steps:</strong> How to transition from the demo to the next stage of the deal.</li>
</ul>

<h2>Segment-Specific Demo Scripts</h2>
<p>Enablement teams should maintain multiple demo scripts tailored to different buyer personas, industries, and use cases. An IT buyer cares about different capabilities than a sales leader. A healthcare company has different compliance requirements than a fintech company. Segment-specific scripts ensure every demo resonates with its audience.</p>""",
        "faq": [
            ("What is a demo script in sales?", "A demo script is a structured guide for delivering product demonstrations. It maps product capabilities to the buyer's specific needs, includes interaction points, and ensures the demo tells a story that resonates rather than simply touring features."),
            ("Should sales demos follow a rigid script?", "No. Demo scripts provide structure and guidance, not a word-for-word script. The best demos feel like conversations where the rep adapts to the buyer's reactions while ensuring key capabilities and differentiators are covered."),
        ],
        "related": ["Pitch Deck", "Sales Playbook", "Discovery Call", "Digital Sales Room"],
    },
    {
        "term": "ROI Calculator",
        "slug": "roi-calculator",
        "short": "An interactive tool that helps buyers quantify the financial return they can expect from implementing a solution.",
        "body": """<p>An ROI calculator is an interactive tool that helps buyers quantify the expected financial return from purchasing a solution. It typically takes buyer-specific inputs (team size, current costs, efficiency metrics, revenue targets) and produces outputs like projected cost savings, revenue increase, payback period, and total ROI over a defined timeframe.</p>

<p>ROI calculators serve dual purposes. For the buyer, they provide the financial justification needed to secure internal budget approval. For the seller, they anchor the conversation in business value rather than price, making it harder for procurement to reduce the deal to a feature-by-feature comparison.</p>

<h2>Building an Effective ROI Calculator</h2>
<ul>
<li><strong>Credible Inputs:</strong> Use industry benchmarks as defaults, but let the buyer input their own numbers. When the buyer uses their data, they own the result. When you force your numbers, it feels like marketing spin.</li>
<li><strong>Conservative Assumptions:</strong> Always err on the side of conservative projections. A calculator that promises 500% ROI loses credibility. A calculator that shows a realistic 150% ROI earns trust.</li>
<li><strong>Clear Methodology:</strong> Show the math. Buyers, especially finance stakeholders, want to understand how the number was calculated, not just see a final figure.</li>
<li><strong>Multiple Scenarios:</strong> Allow the buyer to model conservative, moderate, and aggressive scenarios. This gives them a range to present internally.</li>
</ul>

<h2>ROI Calculators in the Sales Process</h2>
<p>The optimal timing for an ROI calculator varies by deal. Some reps introduce it during discovery to quantify the cost of the problem. Others use it post-demo to build the business case. The key is using it as a collaborative exercise with the buyer, not a one-way presentation.</p>

<p>When the champion takes an ROI calculator to their CFO with their own inputs showing a 12-month payback, the deal accelerates. That champion just did half the selling for you, using a tool your enablement team built.</p>""",
        "faq": [
            ("What is an ROI calculator in sales?", "An ROI calculator is an interactive tool that helps buyers estimate the financial return of purchasing a solution. It takes buyer-specific inputs and produces projected savings, revenue impact, and payback period to support the business case."),
            ("When should a sales rep use an ROI calculator?", "ROI calculators are most effective during the proposal or business case stage, though some reps introduce them during discovery to quantify the cost of the buyer's current problem. Use them as a collaborative exercise, not a one-way presentation."),
        ],
        "related": ["Business Case", "Value Selling", "Buyer Enablement", "Champion Enablement"],
    },
    {
        "term": "Business Case",
        "slug": "business-case",
        "short": "A structured document that justifies a purchase by quantifying the financial impact, risks, and expected outcomes.",
        "body": """<p>A business case is a structured document that justifies a purchase decision by quantifying the financial impact, expected outcomes, implementation requirements, and risks. In B2B sales, the business case is often the document that gets a deal over the finish line because it gives the economic buyer and finance team the data they need to approve the investment.</p>

<p>Deals without a business case are vulnerable to budget cuts, competing priorities, and "do nothing" inertia. When a champion cannot articulate the financial rationale for the purchase, it gets deprioritized in favor of initiatives that have clear ROI documentation.</p>

<h2>Components of a Strong Business Case</h2>
<ul>
<li><strong>Executive Summary:</strong> A one-paragraph overview of the problem, solution, expected ROI, and recommended action. This is what the CFO reads.</li>
<li><strong>Current State Analysis:</strong> Quantified description of the buyer's current situation, including costs, inefficiencies, and risks of the status quo.</li>
<li><strong>Proposed Solution:</strong> What the buyer is purchasing, how it addresses the current state problems, and the expected timeline.</li>
<li><strong>Financial Analysis:</strong> ROI, total cost of ownership, payback period, net present value, or whatever financial metrics the buying organization uses for investment decisions.</li>
<li><strong>Risk Assessment:</strong> What could go wrong and how those risks are mitigated. Acknowledging risk builds credibility.</li>
<li><strong>Implementation Plan:</strong> Timeline, resource requirements, and milestones from purchase to value realization.</li>
</ul>

<h2>Enablement's Role in Business Cases</h2>
<p>Enablement teams should provide reps with business case templates, industry benchmarks, and customer proof points that make building a case efficient. A rep should not spend hours creating a business case from scratch for every deal. Pre-built frameworks with customizable inputs ensure consistency and quality while saving rep time.</p>

<p>Training reps on basic financial concepts (ROI, TCO, NPV) ensures they can speak the language of finance stakeholders. This is often an underdeveloped skill in sales organizations that focus primarily on product and methodology training.</p>""",
        "faq": [
            ("What is a business case in B2B sales?", "A business case is a document that justifies a purchase by quantifying the financial impact, expected outcomes, and implementation requirements. It gives decision-makers the data they need to approve the investment."),
            ("Who should build the business case?", "Ideally, it is co-created by the seller and the buyer's internal champion. The seller provides templates, benchmarks, and proof points. The champion customizes with internal data and presents it to their leadership team."),
        ],
        "related": ["ROI Calculator", "Value Selling", "Champion Enablement", "Buyer Enablement"],
    },
    {
        "term": "Proof of Concept (POC)",
        "slug": "proof-of-concept-poc",
        "short": "A limited implementation or trial that allows a buyer to validate a solution's capabilities before committing to a full purchase.",
        "body": """<p>A proof of concept (POC) is a limited, structured evaluation where the buyer tests a solution in their own environment to validate that it delivers the promised capabilities and outcomes. POCs are common in enterprise software sales where the risk of a bad purchase is high, the integration requirements are complex, and the buyer needs evidence beyond a demo before committing budget.</p>

<p>POCs are both an opportunity and a risk for sellers. Done well, a POC builds conviction across the buying committee by demonstrating real value in the buyer's actual environment. Done poorly, a POC becomes an unpaid consulting engagement that drains resources without advancing the deal.</p>

<h2>Structuring an Effective POC</h2>
<ul>
<li><strong>Clear Success Criteria:</strong> Define specific, measurable outcomes that both parties agree constitute success before the POC begins. Vague criteria lead to subjective evaluations.</li>
<li><strong>Time-Bounded:</strong> POCs should have a firm end date, typically 2-4 weeks. Open-ended POCs signal low buyer urgency and create resource drain.</li>
<li><strong>Scoped:</strong> Test the most critical use case, not every possible scenario. A focused POC that demonstrates clear value is more persuasive than a broad one that shows middling results across many areas.</li>
<li><strong>Stakeholder Commitment:</strong> The buyer must dedicate specific resources (a project lead, technical contact, executive sponsor) or the POC will not get the attention needed to succeed.</li>
</ul>

<h2>POC Management and Enablement</h2>
<p>Enablement teams support POCs by providing reps with POC playbooks that include templates for success criteria, kickoff agendas, check-in cadences, and evaluation scorecards. These templates standardize the process and prevent reps from agreeing to unwinnable POC terms.</p>

<p>The mutual action plan should incorporate the POC with clear milestones: kickoff, midpoint check-in, final evaluation, and go/no-go decision. Embedding the POC in the broader deal timeline prevents it from becoming an isolated exercise disconnected from the purchase decision.</p>""",
        "faq": [
            ("What is a proof of concept in sales?", "A proof of concept (POC) is a limited, time-bounded trial where the buyer tests a solution in their environment to validate its capabilities. It provides evidence beyond a demo that the product delivers real value before a full purchase commitment."),
            ("How long should a proof of concept last?", "Most B2B software POCs run 2-4 weeks. Shorter POCs keep momentum and urgency. Longer POCs risk resource drain and stalled decision-making. Always define a firm end date before the POC begins."),
        ],
        "related": ["Mutual Action Plan", "Deal Cycle", "Sales Process", "Business Case"],
    },
    {
        "term": "Sales Process",
        "slug": "sales-process",
        "short": "The defined sequence of stages that a deal moves through from initial contact to closed-won, providing structure and predictability.",
        "body": """<p>A sales process is the defined sequence of stages that a deal progresses through from initial qualification to close. It provides structure, predictability, and a common framework for the entire sales organization. While a sales methodology defines how reps should sell, the sales process defines the stages a deal moves through and the criteria for advancing from one stage to the next.</p>

<p>A well-defined sales process improves forecasting accuracy because everyone agrees on what it means for a deal to be at a given stage. Without defined stage criteria, one rep's "verbal commit" is another rep's "early exploration," making pipeline data unreliable.</p>

<h2>Common Sales Process Stages</h2>
<ul>
<li><strong>Qualification:</strong> Initial assessment of fit based on ICP criteria, budget indicators, and expressed interest. Gate: confirmed fit and scheduled discovery call.</li>
<li><strong>Discovery:</strong> Deep-dive conversation to understand the buyer's needs, challenges, and decision process. Gate: confirmed pain with quantified impact.</li>
<li><strong>Evaluation:</strong> Demo, POC, or technical assessment. Gate: positive evaluation outcome and identified stakeholders.</li>
<li><strong>Proposal:</strong> Formal proposal with pricing, business case, and implementation plan. Gate: proposal delivered and reviewed by buyer.</li>
<li><strong>Negotiation:</strong> Contract terms, legal review, procurement process. Gate: agreed terms pending signature.</li>
<li><strong>Closed Won:</strong> Contract executed, deal booked.</li>
</ul>

<h2>Enablement and the Sales Process</h2>
<p>Enablement teams ensure reps can execute each stage effectively. This means providing discovery templates for the discovery stage, demo scripts for evaluation, business case frameworks for the proposal stage, and negotiation training for the negotiation stage. Stage-specific enablement is more actionable than generic training because it connects learning directly to what the rep needs to do next.</p>

<p>Enablement also works with sales operations to define and refine stage criteria. If conversion rates drop at a specific stage, the criteria may need tightening (deals are entering the stage prematurely) or the enablement support for that stage may need improvement.</p>""",
        "faq": [
            ("What is a sales process?", "A sales process is the defined sequence of stages a deal moves through from qualification to close. Each stage has specific criteria that must be met before advancing, providing structure, predictability, and consistent forecasting."),
            ("What is the difference between a sales process and a sales methodology?", "The sales process defines the stages a deal moves through (what happens). The sales methodology defines how reps should engage buyers within each stage (how to do it). Both are needed: process provides structure, methodology provides technique."),
        ],
        "related": ["Sales Methodology", "Deal Cycle", "Pipeline Velocity", "Discovery Call"],
    },
]


def _glossary_slug(term):
    """Generate URL slug from term name."""
    slug = term.lower()
    slug = slug.replace("(sko)", "sko").replace("(poc)", "poc")
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return slug


def build_glossary_index():
    """Generate the glossary index page linking to all 45 term pages."""
    title = "Sales Enablement Glossary: 45 Key Terms Defined"
    description = (
        "Clear, practitioner-written definitions for 45 sales enablement terms."
        " From MEDDPICC to microlearning, every concept enablement professionals need to know."
    )

    crumbs = [("Home", "/"), ("Glossary", None)]

    # Group terms alphabetically
    from collections import OrderedDict
    alpha_groups = OrderedDict()
    for t in sorted(GLOSSARY_TERMS, key=lambda x: x["term"].lower()):
        letter = t["term"][0].upper()
        alpha_groups.setdefault(letter, []).append(t)

    term_list = ""
    for letter, terms in alpha_groups.items():
        term_list += f'<h2 class="glossary-letter" id="{letter}">{letter}</h2>\n'
        term_list += '<div class="related-links-grid">\n'
        for t in terms:
            term_list += f'    <a href="/glossary/{t["slug"]}/" class="related-link-card">{t["term"]}</a>\n'
        term_list += '</div>\n'

    # Letter jump nav
    letters = list(alpha_groups.keys())
    jump_nav = '<div class="glossary-jump-nav">' + " ".join(
        f'<a href="#{l}" class="glossary-jump-link">{l}</a>' for l in letters
    ) + '</div>\n'

    body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>Sales Enablement Glossary</h1>
        <p>Clear definitions for the terms that matter in sales enablement. {len(GLOSSARY_TERMS)} terms, written by practitioners.</p>
    </div>
    {jump_nav}
    {term_list}
</div>
'''
    body += newsletter_cta_html()

    extra_head = get_breadcrumb_schema(crumbs)
    page = get_page_wrapper(title=title, description=description,
                            canonical_path="/glossary/", body_content=body,
                            active_path="/glossary/", extra_head=extra_head)
    write_page("glossary/index.html", page)
    print(f"  Built: glossary/index.html")


def build_glossary_term_pages():
    """Generate individual glossary term pages with breadcrumb + FAQ schema."""
    for t in GLOSSARY_TERMS:
        term = t["term"]
        slug = t["slug"]
        short = t["short"]
        body_html = t["body"]
        faq_pairs = t["faq"]
        related = t["related"]

        title = f"What Is {term}? Definition and Guide"
        description = short

        crumbs = [("Home", "/"), ("Glossary", "/glossary/"), (term, None)]
        canonical = f"/glossary/{slug}/"

        # Related terms links
        related_html = ""
        if related:
            related_html = '<div class="related-links-grid">\n'
            for r in related:
                r_slug = _glossary_slug(r)
                # Only link if term exists in our glossary
                exists = any(gt["slug"] == r_slug for gt in GLOSSARY_TERMS)
                if exists:
                    related_html += f'    <a href="/glossary/{r_slug}/" class="related-link-card">{r}</a>\n'
                else:
                    related_html += f'    <span class="related-link-card">{r}</span>\n'
            related_html += '</div>\n'

        body = f'''<div class="container">
    <div class="page-header">
        {breadcrumb_html(crumbs)}
        <h1>What Is {term}?</h1>
        <p class="glossary-short-def">{short}</p>
    </div>
    <div class="glossary-body">
        {body_html}
    </div>

    {faq_html(faq_pairs)}

    <section class="glossary-related">
        <h2>Related Terms</h2>
        {related_html}
    </section>
</div>
'''
        body += newsletter_cta_html(f"Get weekly insights on {term.lower()} and more.")

        # Schema: breadcrumb + FAQ
        extra_head = get_breadcrumb_schema(crumbs)
        extra_head += get_faq_schema(faq_pairs)

        page_content = get_page_wrapper(
            title=title, description=description,
            canonical_path=canonical, body_content=body,
            active_path="/glossary/", extra_head=extra_head
        )
        write_page(f"glossary/{slug}/index.html", page_content)

    print(f"  Built: {len(GLOSSARY_TERMS)} glossary term pages")


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
        ("Highspot vs Seismic", "/tools/compare/highspot-vs-seismic/"),
        ("Gong vs Mindtickle", "/tools/compare/gong-vs-mindtickle/"),
        ("Showpad vs Highspot", "/tools/compare/highspot-vs-showpad/"),
        ("Allego vs Mindtickle", "/tools/compare/allego-vs-mindtickle/"),
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
    build_careers_break_into_enablement()
    build_careers_job_growth()

    print("\n  Building glossary...")
    build_glossary_index()
    build_glossary_term_pages()

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
