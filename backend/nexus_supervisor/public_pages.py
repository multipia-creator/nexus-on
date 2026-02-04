"""
Public pages HTML rendering for NEXUS-ON marketing site.
Live2D Character + Autonomous AI + Human-in-the-loop concept.

Design System: NEXUS UI v1.1
- White + High-Chroma Blue Accent
- Pretendard Font
- 8pt Grid Spacing
- 180ms Motion
- Live2D Character Integration
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("nexus_supervisor")

# Path to data directory
DATA_DIR = Path(__file__).parent.parent / "data"


def load_modules_data() -> List[Dict[str, Any]]:
    """Load modules.json data."""
    try:
        with open(DATA_DIR / "modules.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load modules.json: {e}")
        return []


def load_benchmark_data() -> List[Dict[str, Any]]:
    """Load benchmark.json data."""
    try:
        with open(DATA_DIR / "benchmark.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load benchmark.json: {e}")
        return []


def render_base_styles() -> str:
    """NEXUS UI v1.1 base styles."""
    return """
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
      
      :root {
        /* Colors */
        --bg-primary: #FFFFFF;
        --bg-secondary: #F7F7F8;
        --text-primary: #111111;
        --text-secondary: #3C3C43;
        --text-tertiary: #6B6B73;
        --accent-primary: #2563EB;
        --accent-hover: #1D4ED8;
        --accent-soft: #EFF6FF;
        --border-default: #E6E6EA;
        --border-strong: #D1D1D6;
        
        /* Status Colors */
        --status-green: #16A34A;
        --status-green-bg: #F0FDF4;
        --status-yellow: #F59E0B;
        --status-yellow-bg: #FFFBEB;
        --status-red: #DC2626;
        --status-red-bg: #FEF2F2;
        
        /* Typography */
        --font-sans: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, 
                     "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
        --text-2xl: 28px;
        --text-xl: 22px;
        --text-lg: 18px;
        --text-base: 14px;
        --text-sm: 12px;
        
        /* Spacing (8pt Grid) */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 20px;
        --space-6: 24px;
        --space-8: 32px;
        --space-12: 48px;
        --space-16: 64px;
        
        /* Radius */
        --radius-card: 18px;
        --radius-control: 12px;
        --radius-pill: 999px;
        
        /* Shadow */
        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 6px 18px rgba(0, 0, 0, 0.10);
        
        /* Motion */
        --duration-ui: 180ms;
        --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
      }
      
      * { box-sizing: border-box; margin: 0; padding: 0; }
      
      body {
        font-family: var(--font-sans);
        font-size: var(--text-base);
        color: var(--text-primary);
        background: var(--bg-primary);
        line-height: 1.5;
      }
      
      /* Navigation */
      nav {
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border-default);
        padding: var(--space-4) var(--space-6);
        display: flex;
        align-items: center;
        gap: var(--space-6);
        position: sticky;
        top: 0;
        z-index: 100;
      }
      
      .nav-brand {
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--text-primary);
        text-decoration: none;
        margin-right: auto;
      }
      
      .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: var(--text-base);
        font-weight: 500;
        padding: var(--space-2) var(--space-3);
        border-radius: var(--radius-control);
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .nav-link:hover {
        background: var(--accent-soft);
        color: var(--accent-primary);
      }
      
      .nav-link.active {
        background: var(--accent-primary);
        color: #FFFFFF;
      }
      
      /* Container */
      .container {
        max-width: 1240px;
        margin: 0 auto;
        padding: var(--space-12) var(--space-6);
      }
      
      .container-narrow {
        max-width: 768px;
        margin: 0 auto;
        padding: var(--space-12) var(--space-6);
      }
      
      /* Hero */
      .hero {
        text-align: center;
        padding: var(--space-16) var(--space-6);
        background: linear-gradient(135deg, var(--accent-soft) 0%, var(--bg-primary) 100%);
      }
      
      .hero h1 {
        font-size: 32px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-4);
        line-height: 1.25;
      }
      
      .hero .lead {
        font-size: var(--text-lg);
        color: var(--text-secondary);
        max-width: 600px;
        margin: 0 auto var(--space-8);
        line-height: 1.75;
      }
      
      /* Buttons */
      .btn {
        display: inline-block;
        padding: var(--space-3) var(--space-6);
        border-radius: var(--radius-control);
        font-size: var(--text-base);
        font-weight: 500;
        text-decoration: none;
        transition: all var(--duration-ui) var(--ease-out);
        border: 0;
        cursor: pointer;
      }
      
      .btn-primary {
        background: var(--accent-primary);
        color: #FFFFFF;
      }
      
      .btn-primary:hover {
        background: var(--accent-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
      }
      
      .btn-secondary {
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-default);
      }
      
      .btn-secondary:hover {
        border-color: var(--accent-primary);
        color: var(--accent-primary);
      }
      
      .btn-group {
        display: flex;
        gap: var(--space-3);
        justify-content: center;
        flex-wrap: wrap;
      }
      
      /* Grid */
      .grid-3 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--space-4);
        margin-top: var(--space-8);
      }
      
      .grid-2 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
        gap: var(--space-4);
        margin-top: var(--space-8);
      }
      
      /* Cards */
      .card {
        background: var(--bg-primary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-card);
        padding: var(--space-5);
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .card:hover {
        border-color: var(--accent-primary);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
      }
      
      .card-title {
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-2);
      }
      
      .card-text {
        font-size: var(--text-base);
        color: var(--text-secondary);
        line-height: 1.75;
      }
      
      .card-icon {
        width: 48px;
        height: 48px;
        margin-bottom: var(--space-3);
        color: var(--accent-primary);
      }
      
      /* Badge */
      .badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-pill);
        font-size: var(--text-sm);
        font-weight: 500;
      }
      
      .badge-stable {
        background: var(--status-green-bg);
        color: var(--status-green);
      }
      
      .badge-beta {
        background: var(--status-yellow-bg);
        color: var(--status-yellow);
      }
      
      .badge-alpha {
        background: var(--status-red-bg);
        color: var(--status-red);
      }
      
      /* Table */
      table {
        width: 100%;
        border-collapse: collapse;
        margin-top: var(--space-6);
        font-size: var(--text-base);
      }
      
      th {
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        padding: var(--space-3);
        text-align: left;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      td {
        border: 1px solid var(--border-default);
        padding: var(--space-3);
        color: var(--text-secondary);
      }
      
      tr:hover {
        background: var(--bg-secondary);
      }
      
      /* Live2D Placeholder */
      .live2d-placeholder {
        position: fixed;
        top: var(--space-4);
        right: var(--space-4);
        width: 280px;
        height: 320px;
        background: linear-gradient(135deg, var(--accent-soft) 0%, var(--bg-secondary) 100%);
        border: 2px solid var(--accent-primary);
        border-radius: var(--radius-card);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: var(--space-2);
        z-index: 90;
        box-shadow: var(--shadow-lg);
      }
      
      .live2d-placeholder-icon {
        font-size: 48px;
      }
      
      .live2d-placeholder-text {
        font-size: var(--text-sm);
        color: var(--text-tertiary);
        text-align: center;
      }
      
      /* Footer */
      footer {
        background: var(--bg-secondary);
        border-top: 1px solid var(--border-default);
        padding: var(--space-8) var(--space-6);
        text-align: center;
        margin-top: var(--space-16);
      }
      
      footer p {
        color: var(--text-tertiary);
        font-size: var(--text-sm);
      }
      
      /* Responsive */
      @media (max-width: 768px) {
        nav {
          flex-wrap: wrap;
          gap: var(--space-3);
        }
        
        .nav-brand {
          width: 100%;
          margin-bottom: var(--space-2);
        }
        
        .hero h1 {
          font-size: 24px;
        }
        
        .hero .lead {
          font-size: var(--text-base);
        }
        
        .live2d-placeholder {
          width: 140px;
          height: 160px;
          bottom: var(--space-4);
          right: var(--space-4);
          top: auto;
        }
        
        .live2d-placeholder-icon {
          font-size: 32px;
        }
      }
    </style>
    """


def render_navigation(current_page: str = "") -> str:
    """Render navigation bar."""
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
    
    return f"""
    <nav>
      <a href="/" class="nav-brand">NEXUS-ON</a>
      {nav_html}
    </nav>
    """


def render_live2d_placeholder(state: str = "idle") -> str:
    """Render Live2D character placeholder."""
    states = {
        "idle": ("🤖", "Idle"),
        "listening": ("👂", "Listening"),
        "speaking": ("💬", "Speaking"),
        "thinking": ("🤔", "Thinking"),
        "busy": ("⚙️", "Busy"),
    }
    
    icon, label = states.get(state, states["idle"])
    
    return f"""
    <div class="live2d-placeholder" data-state="{state}">
      <div class="live2d-placeholder-icon">{icon}</div>
      <div class="live2d-placeholder-text">
        Live2D Character<br>{label}
      </div>
    </div>
    """


def render_page(title: str, body_html: str, current_page: str = "", live2d_state: str = "idle") -> str:
    """Render complete HTML page with NEXUS UI v1.1."""
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} - NEXUS-ON</title>
  {render_base_styles()}
</head>
<body>
  {render_navigation(current_page)}
  {render_live2d_placeholder(live2d_state)}
  
  {body_html}
  
  <footer>
    <p>&copy; 2026 NEXUS-ON. Developed by Prof. Nam Hyunwoo, Seokyeong University.</p>
    <p style="margin-top: 8px;">
      <a href="https://github.com/multipia-creator/nexus-on" style="color: var(--accent-primary); text-decoration: none;">GitHub</a>
    </p>
  </footer>
</body>
</html>
"""


def landing_page() -> str:
    """Landing page: Hero + 3 Pillars."""
    body = """
    <div class="hero">
      <h1>Your Always-On AI Character Assistant<br>with Human Oversight</h1>
      <p class="lead">
        NEXUS is a local, always-available AI assistant powered by Live2D character and Claude Sonnet 4.5. 
        It executes multi-step tasks autonomously, but always asks permission for critical actions.
      </p>
      <div class="btn-group">
        <a href="/intro" class="btn btn-primary">Learn More</a>
        <a href="/app" class="btn btn-secondary">Try NEXUS-ON</a>
      </div>
    </div>
    
    <div class="container">
      <h2 style="text-align: center; font-size: var(--text-xl); margin-bottom: var(--space-8);">
        3 Core Principles
      </h2>
      
      <div class="grid-3">
        <div class="card">
          <div class="card-icon">🎨</div>
          <div class="card-title">Visual Presence</div>
          <div class="card-text">
            Live2D character provides visual feedback for every action. 
            Idle, Speaking, Listening, Thinking—you always know what's happening.
          </div>
        </div>
        
        <div class="card">
          <div class="card-icon">🤖</div>
          <div class="card-title">Autonomous Execution</div>
          <div class="card-text">
            NEXUS handles complex workflows automatically. 
            Research, document analysis, scheduling—all in one conversation.
          </div>
        </div>
        
        <div class="card">
          <div class="card-icon">👤</div>
          <div class="card-title">Human Approval Gates</div>
          <div class="card-text">
            RED actions (external sharing, file deletion) require your explicit approval. 
            GREEN tasks run automatically, YELLOW notify you, RED wait for yes/no.
          </div>
        </div>
      </div>
    </div>
    """
    
    return render_page("Home", body, "home", "idle")


def intro_page() -> str:
    """Introduction page: Why NEXUS?"""
    body = """
    <div class="container-narrow">
      <h1 style="font-size: var(--text-2xl); margin-bottom: var(--space-4);">Why NEXUS-ON?</h1>
      <p class="lead" style="margin-bottom: var(--space-8);">
        Most AI assistants are either too autonomous (unpredictable) or too manual (inefficient). 
        NEXUS balances both.
      </p>
      
      <h2 style="font-size: var(--text-xl); margin-top: var(--space-12); margin-bottom: var(--space-4);">The Problem</h2>
      <p style="margin-bottom: var(--space-3); color: var(--text-secondary);">
        ❌ <strong>ChatGPT/Claude</strong>: Great for chat, but no autonomous execution<br>
        ❌ <strong>AutoGPT</strong>: Too autonomous, no control, unpredictable behavior<br>
        ❌ <strong>Existing assistants</strong>: No visual feedback, status unclear
      </p>
      
      <h2 style="font-size: var(--text-xl); margin-top: var(--space-12); margin-bottom: var(--space-4);">Our Solution</h2>
      <p style="margin-bottom: var(--space-6); color: var(--text-secondary);">
        NEXUS combines the best of both worlds: <strong>autonomous execution</strong> with <strong>mandatory approval gates</strong> 
        for risky actions. Plus, a <strong>Live2D character</strong> shows you exactly what's happening.
      </p>
      
      <div class="card" style="margin-top: var(--space-8);">
        <h3 style="font-size: var(--text-lg); margin-bottom: var(--space-3);">4 Key Differentiators</h3>
        <ul style="list-style: none; padding: 0;">
          <li style="margin-bottom: var(--space-3); color: var(--text-secondary);">
            <strong>1️⃣ Live2D Character</strong><br>
            4 animation states (Idle/Speaking/Listening/Thinking) + status glow (Busy=yellow, Alert=red)
          </li>
          <li style="margin-bottom: var(--space-3); color: var(--text-secondary);">
            <strong>2️⃣ Human-in-the-loop by Design</strong><br>
            GREEN (auto), YELLOW (notify), RED (approval required)
          </li>
          <li style="margin-bottom: var(--space-3); color: var(--text-secondary);">
            <strong>3️⃣ Local-First Architecture</strong><br>
            Data stays local, multi-LLM support, native Korean HWP
          </li>
          <li style="margin-bottom: var(--space-3); color: var(--text-secondary);">
            <strong>4️⃣ Always-On Availability</strong><br>
            Background execution, SSE real-time updates, multi-tenant
          </li>
        </ul>
      </div>
      
      <div style="text-align: center; margin-top: var(--space-12);">
        <a href="/modules" class="btn btn-primary">Explore Modules</a>
        <a href="/developer" class="btn btn-secondary" style="margin-left: var(--space-3);">Meet the Creator</a>
      </div>
    </div>
    """
    
    return render_page("Introduction", body, "intro", "listening")


def developer_page() -> str:
    """Developer page: About the Creator."""
    body = """
    <div class="container-narrow">
      <h1 style="font-size: var(--text-2xl); margin-bottom: var(--space-4);">Meet the Creator</h1>
      
      <div class="card" style="margin-top: var(--space-8);">
        <h2 style="font-size: var(--text-xl); margin-bottom: var(--space-2);">Professor Nam Hyunwoo</h2>
        <p style="color: var(--text-tertiary); margin-bottom: var(--space-4);">서경대학교 (Seokyeong University)</p>
        
        <p style="color: var(--text-secondary); line-height: 1.75; margin-bottom: var(--space-4);">
          Prof. Nam specializes in AI systems, human-computer interaction, and autonomous agent design. 
          NEXUS-ON emerged from his research into safer, more controllable AI assistants that respect user 
          agency while enabling complex workflows.
        </p>
        
        <h3 style="font-size: var(--text-lg); margin-top: var(--space-6); margin-bottom: var(--space-3);">Research Interests</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary);">
          <li style="margin-bottom: var(--space-2);">• AI Safety & Alignment</li>
          <li style="margin-bottom: var(--space-2);">• Multi-agent Systems & Orchestration</li>
          <li style="margin-bottom: var(--space-2);">• Korean NLP & Document Processing</li>
          <li style="margin-bottom: var(--space-2);">• Human-in-the-loop AI Design</li>
          <li style="margin-bottom: var(--space-2);">• Visual Feedback in AI Interfaces</li>
        </ul>
      </div>
      
      <div class="card" style="margin-top: var(--space-6);">
        <h3 style="font-size: var(--text-lg); margin-bottom: var(--space-3);">Why I Built NEXUS</h3>
        <p style="color: var(--text-secondary); line-height: 1.75; margin-bottom: var(--space-4);">
          As a researcher, I work with complex multi-step tasks (literature review, data analysis), 
          Korean documents (HWP files), multiple AI models, and sensitive data requiring local storage. 
          Existing AI assistants fell short.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.75; margin-bottom: var(--space-4);">
          <strong>ChatGPT</strong>: Great for chat, but no autonomy<br>
          <strong>AutoGPT</strong>: Too autonomous, no control<br>
          <strong>Custom scripts</strong>: No visual feedback, hard to debug
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.75;">
          <strong>NEXUS bridges this gap</strong>: Autonomous multi-step execution + Visual feedback via Live2D character + 
          Mandatory approval for risky actions + Native Korean document support + Local-first, multi-LLM architecture.
        </p>
      </div>
      
      <div style="text-align: center; margin-top: var(--space-12);">
        <a href="https://github.com/multipia-creator/nexus-on" class="btn btn-primary">View on GitHub</a>
      </div>
    </div>
    """
    
    return render_page("Developer", body, "developer", "thinking")


def modules_page() -> str:
    """Modules page: What's Inside."""
    modules = load_modules_data()
    
    # Status badge mapping
    status_badges = {
        "stable": '<span class="badge badge-stable">✅ Production Ready</span>',
        "beta": '<span class="badge badge-beta">⚠️ Beta</span>',
        "alpha": '<span class="badge badge-alpha">🚧 Alpha</span>',
    }
    
    module_cards_html = ""
    for module in modules:
        status_badge = status_badges.get(module.get("status", "alpha"), "")
        
        # Key features list
        features_html = ""
        for feature in module.get("key_features", []):
            features_html += f"<li>• {feature}</li>"
        
        module_cards_html += f"""
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-3);">
            <div>
              <div class="card-icon">{module.get('icon', '📦')}</div>
              <h3 class="card-title">{module.get('name', 'Unknown')}</h3>
            </div>
            {status_badge}
          </div>
          
          <p style="color: var(--text-tertiary); font-size: var(--text-sm); margin-bottom: var(--space-3);">
            {module.get('tagline', '')}
          </p>
          
          <p class="card-text" style="margin-bottom: var(--space-4);">
            {module.get('description', '')}
          </p>
          
          <details style="margin-top: var(--space-3);">
            <summary style="cursor: pointer; color: var(--accent-primary); font-weight: 500;">
              Key Features
            </summary>
            <ul style="list-style: none; padding: 0; margin-top: var(--space-2); color: var(--text-secondary); font-size: var(--text-sm);">
              {features_html}
            </ul>
          </details>
        </div>
        """
    
    body = f"""
    <div class="container">
      <h1 style="font-size: var(--text-2xl); margin-bottom: var(--space-4); text-align: center;">
        8 Integrated Modules for Autonomous Workflows
      </h1>
      <p class="lead" style="text-align: center; margin-bottom: var(--space-8);">
        Each module works independently, but they're designed to work together seamlessly—just like a real assistant.
      </p>
      
      <div class="grid-2">
        {module_cards_html}
      </div>
      
      <div style="text-align: center; margin-top: var(--space-12);">
        <a href="/benchmark" class="btn btn-primary">See How We Compare</a>
      </div>
    </div>
    """
    
    return render_page("Modules", body, "modules", "speaking")


def benchmark_page() -> str:
    """Benchmark page: How We Compare."""
    benchmark_data = load_benchmark_data()
    
    # Find NEXUS entry
    nexus_entry = next((item for item in benchmark_data if item.get("product") == "NEXUS-ON"), None)
    
    # Differentiation card
    differentiation_html = ""
    if nexus_entry:
        strengths_html = ""
        for strength in nexus_entry.get("strengths", []):
            strengths_html += f"<li style='margin-bottom: var(--space-2);'>✅ {strength}</li>"
        
        differentiation_html = f"""
        <div class="card" style="background: var(--accent-soft); border-color: var(--accent-primary); margin-bottom: var(--space-12);">
          <h2 style="font-size: var(--text-xl); margin-bottom: var(--space-4); color: var(--accent-primary);">
            💡 What Makes NEXUS Different?
          </h2>
          <p style="color: var(--text-secondary); margin-bottom: var(--space-4); line-height: 1.75;">
            NEXUS is the only assistant that combines <strong>visual presence</strong> (Live2D character) + 
            <strong>autonomy</strong> (multi-step execution) + <strong>control</strong> (approval gates) + 
            <strong>local-first</strong> (data control) + <strong>multi-LLM</strong> (no vendor lock-in).
          </p>
          <ul style="list-style: none; padding: 0; color: var(--text-secondary);">
            {strengths_html}
          </ul>
        </div>
        """
    
    # Comparison table
    table_rows_html = ""
    for item in benchmark_data:
        product_name = item.get("product", "Unknown")
        company = item.get("company", "")
        positioning = item.get("positioning", "")
        price_tier = item.get("price_tier", "")
        deployment = item.get("deployment", "")
        
        # Highlight NEXUS row
        row_style = 'background: var(--accent-soft);' if product_name == "NEXUS-ON" else ''
        
        table_rows_html += f"""
        <tr style="{row_style}">
          <td><strong>{product_name}</strong><br><span style="font-size: var(--text-sm); color: var(--text-tertiary);">{company}</span></td>
          <td style="font-size: var(--text-sm);">{positioning}</td>
          <td style="font-size: var(--text-sm);">{price_tier}</td>
          <td style="font-size: var(--text-sm);">{deployment}</td>
        </tr>
        """
    
    body = f"""
    <div class="container">
      <h1 style="font-size: var(--text-2xl); margin-bottom: var(--space-4); text-align: center;">
        Choose the Right AI Assistant for Your Needs
      </h1>
      <p class="lead" style="text-align: center; margin-bottom: var(--space-8);">
        NEXUS is designed for researchers, teams, and power users who need both autonomy and control.
      </p>
      
      {differentiation_html}
      
      <h2 style="font-size: var(--text-xl); margin-bottom: var(--space-4);">Comparison Table</h2>
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Positioning</th>
            <th>Price Tier</th>
            <th>Deployment</th>
          </tr>
        </thead>
        <tbody>
          {table_rows_html}
        </tbody>
      </table>
      
      <div style="text-align: center; margin-top: var(--space-12);">
        <a href="/app" class="btn btn-primary">Try NEXUS-ON</a>
        <a href="/intro" class="btn btn-secondary" style="margin-left: var(--space-3);">Learn More</a>
      </div>
    </div>
    """
    
    return render_page("Benchmark", body, "benchmark", "busy")
