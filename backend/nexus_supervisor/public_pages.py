"""
Public pages HTML rendering utilities for NEXUS-ON marketing site.
Shared base template and data loading functions.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("nexus_supervisor")

# Path to data directory
DATA_DIR = Path(__file__).parent.parent / "data"


def load_modules_data() -> List[Dict[str, Any]]:
    """Load modules.json data. Separated for easy DB migration later."""
    try:
        with open(DATA_DIR / "modules.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load modules.json: {e}")
        return []


def load_benchmark_data() -> List[Dict[str, Any]]:
    """Load benchmark.json data. Separated for easy DB migration later."""
    try:
        with open(DATA_DIR / "benchmark.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load benchmark.json: {e}")
        return []


def render_page(title: str, body_html: str, current_page: str = "") -> str:
    """
    Shared base template for all public pages.
    
    Args:
        title: Page title
        body_html: HTML content for the body
        current_page: Current page identifier for nav highlighting
    
    Returns:
        Complete HTML page
    """
    nav_items = [
        ("Home", "/"),
        ("Intro", "/intro"),
        ("Developer", "/developer"),
        ("Modules", "/modules"),
        ("Benchmark", "/benchmark"),
        ("App", "/app"),
    ]
    
    nav_html = ""
    for label, url in nav_items:
        active_class = " active" if current_page == label.lower() else ""
        nav_html += f'<a href="{url}" class="nav-link{active_class}">{label}</a>\n'
    
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} - NEXUS-ON</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ 
      font-family: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, 
                   "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", 
                   "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0; 
      background: #FFFFFF; 
      color: #111111;
      line-height: 1.6;
    }}
    
    /* Navigation */
    nav {{ 
      background: #F7F7F8; 
      border-bottom: 1px solid #E6E6EA; 
      padding: 16px 24px; 
      display: flex; 
      gap: 24px; 
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .nav-brand {{ 
      font-size: 18px; 
      font-weight: 600; 
      color: #111111; 
      margin-right: auto;
      text-decoration: none;
    }}
    .nav-link {{ 
      color: #3C3C43; 
      text-decoration: none; 
      font-size: 14px;
      font-weight: 500;
      padding: 8px 12px;
      border-radius: 12px;
      transition: all 0.18s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .nav-link:hover {{ 
      background: #EFF6FF;
      color: #2563EB;
    }}
    .nav-link.active {{ 
      background: #2563EB; 
      color: #FFFFFF;
    }}
    
    /* Container */
    .container {{ 
      max-width: 1240px; 
      margin: 0 auto; 
      padding: 48px 24px;
    }}
    .container-narrow {{ 
      max-width: 768px; 
      margin: 0 auto; 
      padding: 48px 24px;
    }}
    
    /* Typography */
    h1 {{ 
      font-size: 28px; 
      font-weight: 600; 
      color: #111111; 
      margin: 0 0 12px 0;
      line-height: 1.25;
    }}
    h2 {{ 
      font-size: 22px; 
      font-weight: 600; 
      color: #111111; 
      margin: 32px 0 12px 0;
      line-height: 1.25;
    }}
    h3 {{ 
      font-size: 18px; 
      font-weight: 600; 
      color: #111111; 
      margin: 24px 0 8px 0;
      line-height: 1.25;
    }}
    p {{ 
      font-size: 14px; 
      color: #3C3C43; 
      margin: 0 0 12px 0;
    }}
    .lead {{ 
      font-size: 18px; 
      color: #3C3C43; 
      margin-bottom: 24px;
      line-height: 1.75;
    }}
    .small {{ 
      font-size: 12px; 
      color: #6B6B73;
    }}
    
    /* Cards */
    .card {{ 
      background: #FFFFFF; 
      border: 1px solid #E6E6EA; 
      border-radius: 18px; 
      padding: 20px;
      margin-bottom: 16px;
      transition: all 0.18s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .card:hover {{ 
      border-color: #2563EB;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
      transform: translateY(-1px);
    }}
    .card-title {{ 
      font-size: 18px; 
      font-weight: 600; 
      color: #111111; 
      margin-bottom: 8px;
    }}
    .card-text {{ 
      font-size: 14px; 
      color: #3C3C43;
    }}
    
    /* Grid */
    .grid-3 {{ 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
      gap: 16px;
      margin-top: 24px;
    }}
    
    /* Buttons */
    .btn {{ 
      display: inline-block;
      background: #2563EB; 
      color: #FFFFFF; 
      border: 0; 
      border-radius: 12px; 
      padding: 12px 24px; 
      font-size: 14px;
      font-weight: 500;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.18s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .btn:hover {{ 
      background: #1D4ED8;
      transform: translateY(-1px);
    }}
    .btn-large {{ 
      padding: 16px 32px; 
      font-size: 16px;
    }}
    
    /* Badges */
    .badge {{ 
      display: inline-block;
      padding: 4px 12px; 
      border-radius: 999px; 
      font-size: 12px;
      font-weight: 500;
    }}
    .badge-green {{ 
      background: #F0FDF4; 
      color: #16A34A;
    }}
    .badge-yellow {{ 
      background: #FFFBEB; 
      color: #F59E0B;
    }}
    .badge-red {{ 
      background: #FEF2F2; 
      color: #DC2626;
    }}
    
    /* Table */
    table {{ 
      width: 100%; 
      border-collapse: collapse; 
      margin-top: 16px;
      font-size: 14px;
    }}
    th {{ 
      background: #F7F7F8; 
      border: 1px solid #E6E6EA; 
      padding: 12px; 
      text-align: left; 
      font-weight: 600;
      color: #111111;
    }}
    td {{ 
      border: 1px solid #E6E6EA; 
      padding: 12px;
      color: #3C3C43;
    }}
    tr:hover {{ 
      background: #F7F7F8;
    }}
    
    /* Hero section */
    .hero {{ 
      text-align: center; 
      padding: 64px 24px;
      background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%);
    }}
    .hero h1 {{ 
      font-size: 32px; 
      margin-bottom: 16px;
    }}
    .hero .lead {{ 
      font-size: 20px;
      max-width: 600px;
      margin: 0 auto 32px auto;
    }}
    
    /* Footer */
    footer {{ 
      background: #F7F7F8; 
      border-top: 1px solid #E6E6EA; 
      padding: 32px 24px;
      text-align: center;
      margin-top: 64px;
    }}
    footer p {{ 
      color: #6B6B73; 
      font-size: 12px;
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
      nav {{ 
        flex-wrap: wrap; 
        gap: 12px;
      }}
      .nav-brand {{ 
        width: 100%; 
        margin-bottom: 8px;
      }}
      .hero h1 {{ 
        font-size: 24px;
      }}
      .hero .lead {{ 
        font-size: 16px;
      }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="/" class="nav-brand">NEXUS-ON</a>
    {nav_html}
  </nav>
  
  {body_html}
  
  <footer>
    <p>&copy; 2026 NEXUS-ON. Developed by Prof. Nam Hyunwoo, Seokyeong University.</p>
  </footer>
</body>
</html>
"""
