import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(OUT_DIR, "terrain_data.json")

with open(data_path, "r", encoding="utf-8") as f:
    terrain_data = json.load(f)

terrain_json_str = json.dumps(terrain_data, separators=(',', ':'))

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Appalachian 3D Topographical Explorer: Berry & Mahantango Mountains, Lykens Valley</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #080c16;
            color: #f1f5f9;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            user-select: none;
        }}
        #canvas-container {{
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            cursor: grab;
        }}
        #canvas-container:active {{ cursor: grabbing; }}
        
        header {{
            position: absolute;
            top: 16px;
            left: 16px;
            right: 16px;
            pointer-events: none;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            z-index: 10;
        }}
        .title-badge {{
            background: rgba(15, 23, 42, 0.94);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.16);
            padding: 14px 20px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.65);
            pointer-events: auto;
            max-width: 580px;
        }}
        h1 {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .subtitle {{
            font-size: 0.8rem;
            color: #94a3b8;
            line-height: 1.4;
        }}
        .badge-pill {{
            display: inline-block;
            background: #0284c7;
            color: #fff;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 7px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }}
        .badge-pa {{
            background: #b45309;
        }}
        .badge-towns {{
            background: #d97706;
        }}

        .controls-panel {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(15, 23, 42, 0.94);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 12px;
            padding: 16px;
            width: 320px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.7);
            z-index: 10;
            max-height: calc(100vh - 170px);
            overflow-y: auto;
        }}
        .control-group {{ margin-bottom: 12px; }}
        .control-group:last-child {{ margin-bottom: 0; }}
        .control-group label {{
            display: flex;
            justify-content: space-between;
            font-size: 0.76rem;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 5px;
        }}
        .val-badge {{
            color: #38bdf8;
            font-family: monospace;
            font-weight: 700;
        }}
        .control-group input[type="range"] {{
            width: 100%;
            height: 5px;
            border-radius: 3px;
            background: #334155;
            outline: none;
            accent-color: #38bdf8;
            cursor: pointer;
        }}
        .btn-group {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-top: 5px;
        }}
        .btn-group-3 {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 5px;
            margin-top: 5px;
        }}
        button.action-btn {{
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 7px 8px;
            font-size: 0.72rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        button.action-btn:hover {{
            background: #38bdf8;
            color: #0f172a;
            border-color: #38bdf8;
        }}
        button.action-btn.active {{
            background: #0284c7;
            color: #fff;
            border-color: #38bdf8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
        }}

        .corridors-card {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(15, 23, 42, 0.94);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 12px;
            padding: 12px 16px;
            width: 280px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.7);
            z-index: 10;
        }}
        .corridor-title {{
            font-size: 0.76rem;
            font-weight: 700;
            color: #cbd5e1;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .corridor-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            padding: 5px 8px;
            margin-bottom: 5px;
            font-size: 0.70rem;
            cursor: pointer;
            transition: background 0.15s, border-color 0.15s;
        }}
        .corridor-item:hover {{
            background: rgba(56, 189, 248, 0.18);
            border-color: #38bdf8;
        }}
        .corridor-item strong {{ color: #f8fafc; }}
        .corridor-item span {{ color: #94a3b8; font-size: 0.65rem; }}

        .legend-card {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(15, 23, 42, 0.94);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 12px;
            padding: 12px 16px;
            width: 280px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.7);
            z-index: 10;
        }}
        .legend-title {{
            font-size: 0.75rem;
            font-weight: 700;
            color: #cbd5e1;
            margin-bottom: 7px;
            display: flex;
            justify-content: space-between;
        }}
        .legend-bar {{
            height: 12px;
            border-radius: 4px;
            background: linear-gradient(to right, #0284c7 0%, #15803d 15%, #65a30d 35%, #eab308 55%, #b45309 78%, #f8fafc 100%);
            border: 1px solid rgba(255,255,255,0.2);
            margin-bottom: 5px;
        }}
        .legend-ticks {{
            display: flex;
            justify-content: space-between;
            font-size: 0.65rem;
            color: #94a3b8;
            font-family: monospace;
        }}

        #feature-modal {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 23, 42, 0.96);
            backdrop-filter: blur(16px);
            border: 1px solid #38bdf8;
            border-radius: 14px;
            padding: 18px 22px;
            width: 380px;
            max-width: 90vw;
            box-shadow: 0 20px 45px rgba(0,0,0,0.85);
            z-index: 20;
            display: none;
        }}
        #feature-modal h3 {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        #feature-modal .feat-elev {{
            font-size: 0.82rem;
            color: #38bdf8;
            font-weight: 700;
            font-family: monospace;
            margin-bottom: 8px;
        }}
        #feature-modal .feat-desc {{
            font-size: 0.78rem;
            color: #cbd5e1;
            line-height: 1.45;
            margin-bottom: 12px;
        }}
        #feature-modal .modal-btns {{
            display: flex;
            justify-content: flex-end;
            gap: 8px;
        }}

        #probe-card {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.6);
            border-radius: 10px;
            padding: 8px 16px;
            min-width: 240px;
            display: none;
            z-index: 15;
            box-shadow: 0 10px 25px rgba(0,0,0,0.7);
            text-align: center;
            pointer-events: none;
            transition: opacity 0.25s ease;
        }}
        #probe-card h3 {{
            font-size: 0.65rem;
            font-weight: 700;
            color: #38bdf8;
            margin-bottom: 1px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        #probe-val {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc;
            font-family: monospace;
        }}
        #probe-sub {{
            font-size: 0.68rem;
            color: #94a3b8;
            margin-top: 1px;
            font-family: monospace;
        }}

        .poi-label {{
            position: absolute;
            transform: translate(-50%, -100%);
            padding: 4px 8px;
            background: rgba(15, 23, 42, 0.94);
            border: 1px solid #38bdf8;
            color: #fff;
            font-size: 0.72rem;
            font-weight: 600;
            border-radius: 6px;
            pointer-events: auto;
            white-space: nowrap;
            box-shadow: 0 4px 14px rgba(0,0,0,0.65);
            transition: opacity 0.15s, transform 0.15s;
            cursor: pointer;
        }}
        .poi-label:hover {{
            transform: translate(-50%, -105%) scale(1.06);
            z-index: 100 !important;
        }}
        .poi-label.borough {{
            border-color: #f59e0b;
            color: #fef3c7;
        }}
        .poi-label.village {{
            border-color: #38bdf8;
            color: #e0f2fe;
        }}
        .poi-label.mountain {{
            border-color: #f97316;
            color: #fed7aa;
        }}
        .poi-label.mountain-north {{
            border-color: #ef4444;
            color: #fca5a5;
        }}
        .poi-label.valley {{
            border-color: #06b6d4;
            color: #a5f3fc;
        }}
        .poi-label.river {{
            border-color: #0284c7;
            color: #bae6fd;
        }}
        .poi-label::after {{
            content: "";
            position: absolute;
            bottom: -5px;
            left: 50%;
            transform: translateX(-50%);
            border-width: 5px 5px 0;
            border-style: solid;
            border-color: rgba(15, 23, 42, 0.94) transparent transparent;
        }}
        .tag-pill {{
            font-size: 0.58rem;
            font-weight: 700;
            padding: 1px 4px;
            border-radius: 3px;
            margin-left: 4px;
            text-transform: uppercase;
        }}
        .tag-pill.bor {{ background: #b45309; color: #fff; }}
        .tag-pill.vil {{ background: #0369a1; color: #fff; }}
        .tag-pill.geo {{ background: #b91c1c; color: #fff; }}

        .nav-hint {{
            margin-top: 8px;
            font-size: 0.68rem;
            color: #64748b;
            line-height: 1.4;
        }}
        #geo-badge {{
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 0.68rem;
            color: #94a3b8;
        }}

        /* Auto-Hide and Smooth Transitions for Overlay Panels */
        .title-badge,
        .controls-panel,
        .corridors-card,
        .legend-card {{
            transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1),
                        transform 0.35s cubic-bezier(0.16, 1, 0.3, 1),
                        visibility 0.35s;
            will-change: transform, opacity;
        }}

        body.hud-hidden header .title-badge {{
            opacity: 0;
            transform: translateY(-30px);
            pointer-events: none;
            visibility: hidden;
        }}
        body.hud-hidden .controls-panel {{
            opacity: 0;
            transform: translateX(-360px);
            pointer-events: none;
            visibility: hidden;
        }}
        body.hud-hidden .corridors-card {{
            opacity: 0;
            transform: translateX(340px);
            pointer-events: none;
            visibility: hidden;
        }}
        body.hud-hidden .legend-card {{
            opacity: 0;
            transform: translateX(340px);
            pointer-events: none;
            visibility: hidden;
        }}

        /* Floating Controls Toggle Button */
        #floating-hud-toggle {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 9px;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(56, 189, 248, 0.45);
            color: #f8fafc;
            padding: 10px 18px;
            border-radius: 24px;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(0,0,0,0.65), 0 0 16px rgba(56, 189, 248, 0.25);
            font-size: 0.8rem;
            font-weight: 600;
            opacity: 0;
            transform: translateY(12px) scale(0.92);
            pointer-events: none;
            visibility: hidden;
            transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1),
                        transform 0.3s cubic-bezier(0.16, 1, 0.3, 1),
                        background 0.15s, border-color 0.15s, box-shadow 0.15s, visibility 0.3s;
        }}
        #floating-hud-toggle:hover {{
            background: rgba(30, 41, 59, 0.98);
            border-color: #38bdf8;
            box-shadow: 0 12px 30px rgba(0,0,0,0.75), 0 0 24px rgba(56, 189, 248, 0.45);
            transform: translateY(-2px) scale(1.02);
        }}
        body.hud-hidden #floating-hud-toggle {{
            opacity: 1;
            transform: translateY(0) scale(1);
            pointer-events: auto;
            visibility: visible;
        }}
        #floating-hud-toggle svg {{
            color: #38bdf8;
            transition: transform 0.4s ease;
        }}
        #floating-hud-toggle:hover svg {{
            transform: rotate(45deg);
        }}
        .hud-badge-key {{
            background: rgba(56, 189, 248, 0.2);
            color: #38bdf8;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.4);
            font-family: monospace;
        }}

        /* Panel Top-Bar & Pin Controls */
        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 10px;
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .panel-title-area {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: 0.3px;
        }}
        .panel-header-buttons {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .header-btn {{
            background: #1e293b;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #94a3b8;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 0.68rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.15s ease;
        }}
        .header-btn:hover {{
            background: #334155;
            color: #f8fafc;
            border-color: #38bdf8;
        }}
        .header-btn.pinned {{
            background: rgba(2, 132, 199, 0.25);
            border-color: #38bdf8;
            color: #38bdf8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
        }}
        .header-btn.close-btn {{
            padding: 4px 6px;
        }}
        .header-btn.close-btn:hover {{
            background: rgba(239, 68, 68, 0.2);
            border-color: #ef4444;
            color: #fca5a5;
        }}

        /* Card Collapse & Header Chevron Buttons */
        .card-collapse-btn {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #94a3b8;
            font-size: 0.68rem;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 4px;
            line-height: 1;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .card-collapse-btn:hover {{
            background: rgba(56, 189, 248, 0.18);
            border-color: #38bdf8;
            color: #38bdf8;
        }}
        .card-collapsed .card-content {{
            display: none !important;
        }}
        .card-collapsed .card-collapse-btn span {{
            transform: rotate(-90deg);
        }}
        .controls-panel.card-collapsed {{
            max-height: 52px;
            overflow: hidden;
            padding-bottom: 8px;
        }}
        .controls-panel.card-collapsed .panel-header {{
            margin-bottom: 0;
            border-bottom: none;
            padding-bottom: 0;
        }}
        .card-collapse-btn span {{
            display: inline-block;
            transition: transform 0.2s ease;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="canvas-container"></div>
    <header>
        <div class="title-badge" id="title-card">
            <h1>
                Appalachian 3D Topography
                <span class="badge-pill">USGS DEM</span>
                <span class="badge-pill badge-pa">Pennsylvania</span>
                <span class="badge-pill badge-towns">17 Towns &amp; Boroughs</span>
                <button id="toggle-title-btn" class="card-collapse-btn" style="margin-left: auto;" title="Collapse / Expand Description"><span>▾</span></button>
            </h1>
            <div class="card-content">
                <p class="subtitle" style="margin-top: 4px;">
                    3D topological model of <strong>Mahantango Mountain</strong> (North), <strong>Berry Mountain</strong> (South), the intervening <strong>Lykens Valley</strong>, and its historic settlement network.
                </p>
            </div>
        </div>
    </header>

    <div id="probe-card">
        <h3>Terrain Cursor Probe</h3>
        <div id="probe-val">-- ft</div>
        <div id="probe-sub">Lat: -- | Lon: --</div>
    </div>

    <!-- Regional Border Corridors -->
    <div class="corridors-card" id="corridors-card">
        <div class="corridor-title">
            <span>Bordering Corridors</span>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.65rem; color: #38bdf8;">Click to Orient</span>
                <button id="toggle-corridors-btn" class="card-collapse-btn" title="Collapse / Expand Corridors"><span>▾</span></button>
            </div>
        </div>
        <div class="card-content">
            <div class="corridor-item" id="corr-halifax">
                <div><strong>◄ South: Halifax</strong><br><span>PA-147 / River (~6 mi)</span></div>
                <span style="font-size: 0.8rem;">↓</span>
            </div>
            <div class="corridor-item" id="corr-herndon">
                <div><strong>▲ North: Herndon</strong><br><span>PA-147 / Sunbury (~3 mi)</span></div>
                <span style="font-size: 0.8rem;">↑</span>
            </div>
            <div class="corridor-item" id="corr-hegins">
                <div><strong>East: Valley View &amp; Hegins ►</strong><br><span>PA-25 / Hegins Valley (~5 mi)</span></div>
                <span style="font-size: 0.8rem;">→</span>
            </div>
            <div class="corridor-item" id="corr-towercity">
                <div><strong>East: Tower City ►</strong><br><span>US-209 / Coal Field (~4 mi)</span></div>
                <span style="font-size: 0.8rem;">→</span>
            </div>
        </div>
    </div>

    <!-- Controls Panel -->
    <div class="controls-panel" id="controls-panel">
        <div class="panel-header">
            <div class="panel-title-area">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
                <span>Controls &amp; Layers</span>
            </div>
            <div class="panel-header-buttons">
                <button id="pin-btn" class="header-btn" title="Pin controls (keep always visible)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6l.8.8.8-.8v-6H18v-2l-2-2z"/>
                    </svg>
                    <span id="pin-text">Auto-Hide</span>
                </button>
                <button id="toggle-controls-btn" class="header-btn card-collapse-btn" title="Collapse / Expand Controls Panel">
                    <span>▾</span>
                </button>
                <button id="hud-hide-btn" class="header-btn close-btn" title="Hide All Overlay Windows (Press H)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        </div>

        <div class="card-content" id="controls-panel-body">
            <div class="control-group">
                <label>
                    <span>Vertical Relief Exaggeration</span>
                    <span class="val-badge" id="exag-val">2.5x</span>
                </label>
                <input type="range" id="exag-slider" min="1.0" max="5.0" step="0.1" value="2.5">
            </div>

            <div class="control-group">
                <label>
                    <span>Sun Light Azimuth</span>
                    <span class="val-badge" id="sun-val">315° NW</span>
                </label>
                <input type="range" id="sun-slider" min="0" max="360" step="5" value="315">
            </div>

            <div class="control-group">
                <label>Camera Presets</label>
                <div class="btn-group">
                    <button class="action-btn active" id="btn-valley">Valley Flight</button>
                    <button class="action-btn" id="btn-central">Central Valley</button>
                    <button class="action-btn" id="btn-lykens">Eastern Mining</button>
                    <button class="action-btn" id="btn-gap">River Gap</button>
                    <button class="action-btn" id="btn-mahantango">North Gaps</button>
                    <button class="action-btn" id="btn-topdown">Top-Down Map</button>
                </div>
            </div>

            <div class="control-group">
                <label>Town &amp; Landmark Labels</label>
                <div class="btn-group-3">
                    <button class="action-btn active" id="lbl-all">All</button>
                    <button class="action-btn" id="lbl-major">Boroughs</button>
                    <button class="action-btn" id="lbl-off">Off</button>
                </div>
            </div>

            <div class="control-group">
                <label>Rendering &amp; Animation</label>
                <div class="btn-group">
                    <button class="action-btn" id="tour-btn">Tour Orbit</button>
                    <button class="action-btn" id="wire-btn">Wireframe</button>
                    <button class="action-btn" id="reset-btn">Reset View</button>
                    <button class="action-btn" id="btn-regional">Overview</button>
                </div>
            </div>

            <div id="geo-badge">
                <strong>Geology:</strong> Folded Alleghanian sandstone ramparts enclosing fertile agricultural Devonian red shale basin, breached by antecedent Susquehanna River.
            </div>

            <div class="nav-hint">
                <strong>Navigation:</strong> Left-drag to Rotate | Right-drag to Pan | Scroll to Zoom | Click any pin for history.<br>
                <strong>Overlay:</strong> Controls auto-hide when navigating. Press <strong>H</strong> to toggle, or click <strong>Pin</strong> to keep open.
            </div>
        </div>
    </div>

    <!-- Feature Inspector Modal -->
    <div id="feature-modal">
        <h3 id="modal-name">Town Name <span id="modal-type-badge" class="tag-pill bor">Borough</span></h3>
        <div class="feat-elev" id="modal-elev">Elevation: -- ft AMSL</div>
        <div class="feat-desc" id="modal-desc">Description of the town or feature.</div>
        <div class="modal-btns">
            <button class="action-btn" id="modal-fly-btn" style="background:#0284c7; color:#fff;">Fly Here</button>
            <button class="action-btn" id="modal-close-btn">Close</button>
        </div>
    </div>

    <div class="legend-card" id="legend-card">
        <div class="legend-title">
            <span>Elevation (AMSL)</span>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span>Hypsometric Scale</span>
                <button id="toggle-legend-btn" class="card-collapse-btn" title="Collapse / Expand Legend"><span>▾</span></button>
            </div>
        </div>
        <div class="card-content">
            <div class="legend-bar"></div>
            <div class="legend-ticks">
                <span>360ft (River)</span>
                <span>600ft (Valley)</span>
                <span>1,100ft</span>
                <span>1,745ft (Peak)</span>
            </div>
        </div>
    </div>

    <!-- Floating HUD Controls Toggle Button -->
    <button id="floating-hud-toggle" title="Show Controls (Press H)">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        <span>Controls</span>
        <span class="hud-badge-key">H</span>
    </button>

    <div id="poi-container"></div>

    <script>
        const TERRAIN_DATA = {terrain_json_str};

        let scene, camera, renderer, controls;
        let terrainMesh, wireframeMesh, baseSkirtGroup;
        let skirtGeoms = [];
        let pois = [];
        let isTouring = false;
        let tourAngle = 0;
        let currentExaggeration = 2.5;
        let labelFilter = "all"; // "all", "major", "off"
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();
        let sunLight;
        let selectedPOI = null;

        const ROWS = TERRAIN_DATA.shape[0];
        const COLS = TERRAIN_DATA.shape[1];
        const ELEV = TERRAIN_DATA.elevations_ft;
        const LATS = TERRAIN_DATA.lats;
        const LONS = TERRAIN_DATA.lons;
        const MIN_E = TERRAIN_DATA.elev_min_ft;
        const MAX_E = TERRAIN_DATA.elev_max_ft;

        const WORLD_W = 120.0;
        const WORLD_H = WORLD_W * (ROWS / COLS);
        const BASE_RELIEF_UNIT = 1.433;
        const PEDESTAL_BASE_Y = -1.8;

        let isCamTransitioning = false;
        let camStartPos = new THREE.Vector3();
        let camEndPos = new THREE.Vector3();
        let targetStartPos = new THREE.Vector3();
        let targetEndPos = new THREE.Vector3();
        let camTransitionProgress = 0;

        function init() {{
            const container = document.getElementById("canvas-container");

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x080c16);
            scene.fog = new THREE.FogExp2(0x080c16, 0.0032);

            camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.5, 1200);
            camera.position.set(-45, 16, 12);

            renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2 - 0.02;
            controls.minDistance = 6;
            controls.maxDistance = 260;
            controls.target.set(10, 2, -2);

            // Lighting
            const ambient = new THREE.AmbientLight(0xffffff, 0.52);
            scene.add(ambient);

            sunLight = new THREE.DirectionalLight(0xfffaed, 1.45);
            updateSunPosition(315);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            sunLight.shadow.camera.near = 10;
            sunLight.shadow.camera.far = 250;
            sunLight.shadow.camera.left = -70;
            sunLight.shadow.camera.right = 70;
            sunLight.shadow.camera.top = 50;
            sunLight.shadow.camera.bottom = -50;
            sunLight.shadow.bias = -0.0004;
            scene.add(sunLight);

            const hemiLight = new THREE.HemisphereLight(0x93c5fd, 0x1e293b, 0.45);
            scene.add(hemiLight);

            buildTerrainMesh();
            buildPedestalSkirts();
            buildPOIMarkers();

            setCameraView("valley", false);

            window.addEventListener("resize", onWindowResize);
            window.addEventListener("mousemove", onMouseMove);

            document.getElementById("exag-slider").addEventListener("input", (e) => {{
                currentExaggeration = parseFloat(e.target.value);
                document.getElementById("exag-val").textContent = currentExaggeration.toFixed(1) + "x";
                updateTerrainGeometry();
            }});

            document.getElementById("sun-slider").addEventListener("input", (e) => {{
                const deg = parseInt(e.target.value);
                let dir = "NW";
                if (deg >= 337 || deg < 23) dir = "N";
                else if (deg >= 23 && deg < 68) dir = "NE";
                else if (deg >= 68 && deg < 113) dir = "E";
                else if (deg >= 113 && deg < 158) dir = "SE";
                else if (deg >= 158 && deg < 203) dir = "S";
                else if (deg >= 203 && deg < 248) dir = "SW";
                else if (deg >= 248 && deg < 293) dir = "W";
                document.getElementById("sun-val").textContent = deg + "° " + dir;
                updateSunPosition(deg);
            }});

            // Preset Buttons
            document.getElementById("btn-valley").addEventListener("click", () => setCameraView("valley", true));
            document.getElementById("btn-central").addEventListener("click", () => setCameraView("central", true));
            document.getElementById("btn-lykens").addEventListener("click", () => setCameraView("lykens", true));
            document.getElementById("btn-gap").addEventListener("click", () => setCameraView("gap", true));
            document.getElementById("btn-mahantango").addEventListener("click", () => setCameraView("mahantango", true));
            document.getElementById("btn-topdown").addEventListener("click", () => setCameraView("topdown", true));
            document.getElementById("btn-regional").addEventListener("click", () => setCameraView("regional", true));

            // Label filter buttons
            document.getElementById("lbl-all").addEventListener("click", () => setLabelFilter("all"));
            document.getElementById("lbl-major").addEventListener("click", () => setLabelFilter("major"));
            document.getElementById("lbl-off").addEventListener("click", () => setLabelFilter("off"));

            // Other buttons
            document.getElementById("tour-btn").addEventListener("click", toggleTour);
            document.getElementById("wire-btn").addEventListener("click", toggleWireframe);
            document.getElementById("reset-btn").addEventListener("click", () => setCameraView("valley", true));

            // Corridor Click Handlers
            document.getElementById("corr-halifax").addEventListener("click", () => {{
                flyToCoords(-76.957, 40.525, new THREE.Vector3(-76.957, 40.560, 0), true);
            }});
            document.getElementById("corr-herndon").addEventListener("click", () => {{
                flyToCoords(-76.907, 40.660, new THREE.Vector3(-76.907, 40.620, 0), true);
            }});
            document.getElementById("corr-hegins").addEventListener("click", () => {{
                flyToCoords(-76.620, 40.630, new THREE.Vector3(-76.660, 40.630, 0), true);
            }});
            document.getElementById("corr-towercity").addEventListener("click", () => {{
                flyToCoords(-76.618, 40.582, new THREE.Vector3(-76.660, 40.582, 0), true);
            }});

            // Modal Handlers
            document.getElementById("modal-close-btn").addEventListener("click", () => {{
                document.getElementById("feature-modal").style.display = "none";
            }});
            document.getElementById("modal-fly-btn").addEventListener("click", () => {{
                if (selectedPOI) {{
                    flyToFeature(selectedPOI);
                    document.getElementById("feature-modal").style.display = "none";
                }}
            }});

            setupHUDManager();
            animate();
        }}

        function updateSunPosition(deg) {{
            const rad = (deg * Math.PI) / 180;
            const dist = 90;
            sunLight.position.set(Math.cos(rad) * dist, 55, Math.sin(rad) * dist);
        }}

        function getElevationColor(e, lon) {{
            if (lon < -76.93 && e <= 385) {{
                return new THREE.Color(0x0284c7);
            }}

            const t = Math.max(0, Math.min(1, (e - MIN_E) / (MAX_E - MIN_E)));
            const color = new THREE.Color();

            if (t < 0.12) {{
                color.lerpColors(new THREE.Color(0x0f766e), new THREE.Color(0x15803d), t / 0.12);
            }} else if (t < 0.35) {{
                color.lerpColors(new THREE.Color(0x15803d), new THREE.Color(0x65a30d), (t - 0.12) / 0.23);
            }} else if (t < 0.58) {{
                color.lerpColors(new THREE.Color(0x65a30d), new THREE.Color(0xd97706), (t - 0.35) / 0.23);
            }} else if (t < 0.82) {{
                color.lerpColors(new THREE.Color(0xd97706), new THREE.Color(0x9a3412), (t - 0.58) / 0.24);
            }} else {{
                color.lerpColors(new THREE.Color(0x9a3412), new THREE.Color(0xf1f5f9), (t - 0.82) / 0.18);
            }}
            return color;
        }}

        function calcHeight(elevFt) {{
            const zNorm = (elevFt - MIN_E) / (MAX_E - MIN_E);
            return zNorm * BASE_RELIEF_UNIT * currentExaggeration;
        }}

        function buildTerrainMesh() {{
            const geom = new THREE.PlaneGeometry(WORLD_W, WORLD_H, COLS - 1, ROWS - 1);
            geom.rotateX(-Math.PI / 2);

            const pos = geom.attributes.position;
            const colors = new Float32Array(pos.count * 3);

            for (let i = 0; i < pos.count; i++) {{
                const r = Math.floor(i / COLS);
                const c = i % COLS;
                const e = ELEV[r][c];
                const lon = LONS[c];

                pos.setY(i, calcHeight(e));

                const col = getElevationColor(e, lon);
                colors[i * 3] = col.r;
                colors[i * 3 + 1] = col.g;
                colors[i * 3 + 2] = col.b;
            }}

            geom.setAttribute("color", new THREE.BufferAttribute(colors, 3));
            geom.computeVertexNormals();

            const mat = new THREE.MeshStandardMaterial({{
                vertexColors: true,
                roughness: 0.80,
                metalness: 0.06,
                flatShading: false
            }});

            terrainMesh = new THREE.Mesh(geom, mat);
            terrainMesh.receiveShadow = true;
            terrainMesh.castShadow = true;
            scene.add(terrainMesh);

            const wireMat = new THREE.MeshBasicMaterial({{
                color: 0x38bdf8,
                wireframe: true,
                transparent: true,
                opacity: 0.18
            }});
            wireframeMesh = new THREE.Mesh(geom, wireMat);
            wireframeMesh.visible = false;
            scene.add(wireframeMesh);
        }}

        function buildPedestalSkirts() {{
            baseSkirtGroup = new THREE.Group();
            skirtGeoms = [];

            const skirtMat = new THREE.MeshStandardMaterial({{
                color: 0x111827,
                roughness: 0.95,
                metalness: 0.05,
                side: THREE.DoubleSide
            }});

            const nGeom = createEdgeSkirtGeometry(COLS, (c) => {{
                const x = ((c / (COLS - 1)) - 0.5) * WORLD_W;
                const y = calcHeight(ELEV[0][c]);
                const z = -WORLD_H * 0.5;
                return [x, y, z];
            }});
            baseSkirtGroup.add(new THREE.Mesh(nGeom, skirtMat));
            skirtGeoms.push({{ geom: nGeom, type: "north" }});

            const sGeom = createEdgeSkirtGeometry(COLS, (c) => {{
                const x = ((c / (COLS - 1)) - 0.5) * WORLD_W;
                const y = calcHeight(ELEV[ROWS - 1][c]);
                const z = WORLD_H * 0.5;
                return [x, y, z];
            }});
            baseSkirtGroup.add(new THREE.Mesh(sGeom, skirtMat));
            skirtGeoms.push({{ geom: sGeom, type: "south" }});

            const wGeom = createEdgeSkirtGeometry(ROWS, (r) => {{
                const x = -WORLD_W * 0.5;
                const y = calcHeight(ELEV[r][0]);
                const z = ((r / (ROWS - 1)) - 0.5) * WORLD_H;
                return [x, y, z];
            }});
            baseSkirtGroup.add(new THREE.Mesh(wGeom, skirtMat));
            skirtGeoms.push({{ geom: wGeom, type: "west" }});

            const eGeom = createEdgeSkirtGeometry(ROWS, (r) => {{
                const x = WORLD_W * 0.5;
                const y = calcHeight(ELEV[r][COLS - 1]);
                const z = ((r / (ROWS - 1)) - 0.5) * WORLD_H;
                return [x, y, z];
            }});
            baseSkirtGroup.add(new THREE.Mesh(eGeom, skirtMat));
            skirtGeoms.push({{ geom: eGeom, type: "east" }});

            const baseGeom = new THREE.PlaneGeometry(WORLD_W, WORLD_H);
            baseGeom.rotateX(Math.PI / 2);
            baseGeom.translate(0, PEDESTAL_BASE_Y, 0);
            baseSkirtGroup.add(new THREE.Mesh(baseGeom, skirtMat));

            scene.add(baseSkirtGroup);
        }}

        function createEdgeSkirtGeometry(count, coordFn) {{
            const geom = new THREE.BufferGeometry();
            const positions = new Float32Array(count * 2 * 3);
            const indices = [];

            for (let i = 0; i < count; i++) {{
                const [x, yTop, z] = coordFn(i);
                positions[i * 6 + 0] = x;
                positions[i * 6 + 1] = yTop;
                positions[i * 6 + 2] = z;
                positions[i * 6 + 3] = x;
                positions[i * 6 + 4] = PEDESTAL_BASE_Y;
                positions[i * 6 + 5] = z;

                if (i < count - 1) {{
                    const t0 = i * 2;
                    const b0 = i * 2 + 1;
                    const t1 = (i + 1) * 2;
                    const b1 = (i + 1) * 2 + 1;
                    indices.push(t0, b0, t1);
                    indices.push(t1, b0, b1);
                }}
            }}

            geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
            geom.setIndex(indices);
            geom.computeVertexNormals();
            return geom;
        }}

        function updateTerrainGeometry() {{
            const pos = terrainMesh.geometry.attributes.position;
            for (let i = 0; i < pos.count; i++) {{
                const r = Math.floor(i / COLS);
                const c = i % COLS;
                const e = ELEV[r][c];
                pos.setY(i, calcHeight(e));
            }}
            pos.needsUpdate = true;
            terrainMesh.geometry.computeVertexNormals();

            skirtGeoms.forEach(item => {{
                const p = item.geom.attributes.position;
                if (item.type === "north") {{
                    for (let c = 0; c < COLS; c++) p.setY(c * 2, calcHeight(ELEV[0][c]));
                }} else if (item.type === "south") {{
                    for (let c = 0; c < COLS; c++) p.setY(c * 2, calcHeight(ELEV[ROWS - 1][c]));
                }} else if (item.type === "west") {{
                    for (let r = 0; r < ROWS; r++) p.setY(r * 2, calcHeight(ELEV[r][0]));
                }} else if (item.type === "east") {{
                    for (let r = 0; r < ROWS; r++) p.setY(r * 2, calcHeight(ELEV[r][COLS - 1]));
                }}
                p.needsUpdate = true;
                item.geom.computeVertexNormals();
            }});

            pois.forEach(p => {{
                const worldPos = latLonToWorld(p.data.lat, p.data.lon, p.data.elev_ft);
                p.pinMesh.position.set(worldPos.x, worldPos.y, worldPos.z);
                p.currentWorldY = worldPos.y;
            }});
        }}

        function latLonToWorld(lat, lon, elevFt) {{
            const u = (lon - TERRAIN_DATA.bounds.lon_min) / (TERRAIN_DATA.bounds.lon_max - TERRAIN_DATA.bounds.lon_min);
            const v = (TERRAIN_DATA.bounds.lat_max - lat) / (TERRAIN_DATA.bounds.lat_max - TERRAIN_DATA.bounds.lat_min);

            const x = (u - 0.5) * WORLD_W;
            const z = (v - 0.5) * WORLD_H;
            const y = calcHeight(elevFt);

            return new THREE.Vector3(x, y, z);
        }}

        function buildPOIMarkers() {{
            const container = document.getElementById("poi-container");
            container.innerHTML = "";
            pois = [];

            TERRAIN_DATA.features.forEach(feat => {{
                const worldPos = latLonToWorld(feat.lat, feat.lon, feat.elev_ft);

                const pinGroup = new THREE.Group();
                pinGroup.position.set(worldPos.x, worldPos.y, worldPos.z);

                let pinColor = 0xf59e0b;
                let badgeClass = "borough";
                let tagText = "BOROUGH";
                let tagClass = "bor";
                let priority = 2; // Priority for collision resolution: 1 = highest

                if (feat.type === "borough") {{
                    pinColor = 0xf59e0b;
                    badgeClass = "borough";
                    tagText = "BOROUGH";
                    tagClass = "bor";
                    priority = 2;
                }} else if (feat.type === "village") {{
                    pinColor = 0x38bdf8;
                    badgeClass = "village";
                    tagText = "VILLAGE";
                    tagClass = "vil";
                    priority = 3;
                }} else if (feat.type === "mountain") {{
                    pinColor = feat.name.includes("Mahantango") ? 0xef4444 : 0xf97316;
                    badgeClass = feat.name.includes("Mahantango") ? "mountain-north" : "mountain";
                    tagText = "RIDGE";
                    tagClass = "geo";
                    priority = 1;
                }} else if (feat.type === "river" || feat.type === "valley") {{
                    pinColor = 0x06b6d4;
                    badgeClass = feat.type === "river" ? "river" : "valley";
                    tagText = feat.type === "river" ? "GAP" : "VALLEY";
                    tagClass = "geo";
                    priority = 1;
                }}

                const needleH = feat.type === "borough" ? 1.8 : 1.3;
                const pinGeom = new THREE.CylinderGeometry(0.08, 0.08, needleH, 8);
                pinGeom.translate(0, needleH * 0.5, 0);
                const pinMat = new THREE.MeshBasicMaterial({{ color: pinColor }});
                const pinMesh = new THREE.Mesh(pinGeom, pinMat);
                pinGroup.add(pinMesh);

                const orbRadius = feat.type === "borough" ? 0.38 : 0.26;
                const orbGeom = new THREE.SphereGeometry(orbRadius, 16, 16);
                const orbMat = new THREE.MeshBasicMaterial({{ color: feat.type === "borough" ? 0xffffff : 0xffffff }});
                const orbMesh = new THREE.Mesh(orbGeom, orbMat);
                orbMesh.position.set(0, needleH, 0);
                pinGroup.add(orbMesh);

                const discGeom = new THREE.RingGeometry(0.12, 0.45, 16);
                discGeom.rotateX(-Math.PI / 2);
                const discMat = new THREE.MeshBasicMaterial({{ color: pinColor, side: THREE.DoubleSide, transparent: true, opacity: 0.6 }});
                const discMesh = new THREE.Mesh(discGeom, discMat);
                discMesh.position.set(0, 0.02, 0);
                pinGroup.add(discMesh);

                scene.add(pinGroup);

                const el = document.createElement("div");
                el.className = "poi-label " + badgeClass;
                el.innerHTML = "<strong>" + feat.name + "</strong><span class=\\"tag-pill " + tagClass + "\\">" + tagText + "</span><br><span style=\\"font-size:0.65rem;opacity:0.85;font-family:monospace;\\">" + feat.elev_ft + " ft AMSL</span>";

                el.addEventListener("click", (e) => {{
                    e.stopPropagation();
                    openFeatureModal(feat);
                }});

                container.appendChild(el);

                pois.push({{
                    data: feat,
                    worldX: worldPos.x,
                    worldZ: worldPos.z,
                    currentWorldY: worldPos.y,
                    pinMesh: pinGroup,
                    needleH: needleH,
                    domElement: el,
                    priority: priority,
                    isMajor: (feat.type === "borough" || feat.type === "mountain" || feat.type === "river" || feat.type === "valley"),
                    screenX: 0,
                    screenY: 0
                }});
            }});
        }}

        function setLabelFilter(mode) {{
            labelFilter = mode;
            ["all", "major", "off"].forEach(m => {{
                document.getElementById("lbl-" + m).classList.toggle("active", m === mode);
            }});

            pois.forEach(p => {{
                if (mode === "off") {{
                    p.pinMesh.visible = false;
                    p.domElement.style.display = "none";
                }} else if (mode === "major") {{
                    p.pinMesh.visible = p.isMajor;
                    p.domElement.style.display = p.isMajor ? "block" : "none";
                }} else {{
                    p.pinMesh.visible = true;
                    p.domElement.style.display = "block";
                }}
            }});
        }}

        function openFeatureModal(feat) {{
            selectedPOI = feat;
            document.getElementById("modal-name").firstChild.textContent = feat.name + " ";
            const badge = document.getElementById("modal-type-badge");
            badge.textContent = feat.type.toUpperCase();
            badge.className = "tag-pill " + (feat.type === "borough" ? "bor" : feat.type === "village" ? "vil" : "geo");
            document.getElementById("modal-elev").textContent = "Elevation: " + feat.elev_ft + " ft AMSL (" + Math.round(feat.elev_ft * 0.3048) + " m)";
            document.getElementById("modal-desc").textContent = feat.desc + " [Coordinates: " + feat.lat.toFixed(4) + "°N, " + Math.abs(feat.lon).toFixed(4) + "°W]";
            document.getElementById("feature-modal").style.display = "block";
        }}

        function flyToFeature(feat) {{
            const worldPos = latLonToWorld(feat.lat, feat.lon, feat.elev_ft);
            const targetPos = new THREE.Vector3(worldPos.x, worldPos.y + 0.5, worldPos.z);
            const camPos = new THREE.Vector3(worldPos.x - 12, worldPos.y + 7, worldPos.z + 14);
            animateCameraTo(camPos, targetPos);
        }}

        function flyToCoords(lon, lat, lookOffset, animated = true) {{
            const targetPos = latLonToWorld(lat, lon, 600);
            const camPos = targetPos.clone().add(new THREE.Vector3(lookOffset.x, 15, lookOffset.y));
            if (animated) {{
                animateCameraTo(camPos, targetPos);
            }} else {{
                camera.position.copy(camPos);
                controls.target.copy(targetPos);
                controls.update();
            }}
        }}

        function updatePOIScreens() {{
            if (labelFilter === "off") return;

            const tempV = new THREE.Vector3();
            const visiblePois = [];

            pois.forEach(p => {{
                if (labelFilter === "major" && !p.isMajor) {{
                    p.domElement.style.display = "none";
                    return;
                }}

                tempV.set(p.worldX, p.currentWorldY + p.needleH + 0.35, p.worldZ);
                tempV.project(camera);

                if (tempV.z > 1.0 || tempV.x < -1.1 || tempV.x > 1.1 || tempV.y < -1.1 || tempV.y > 1.1) {{
                    p.domElement.style.display = "none";
                    return;
                }}

                p.screenX = (tempV.x * 0.5 + 0.5) * window.innerWidth;
                p.screenY = (-(tempV.y * 0.5) + 0.5) * window.innerHeight;
                p.camDist = tempV.z;
                visiblePois.push(p);
            }});

            // Smart Screen-space Collision Avoidance
            visiblePois.sort((a, b) => a.priority - b.priority);

            const placedBoxes = [];
            visiblePois.forEach(p => {{
                const w = 110;
                const h = 32;
                const x0 = p.screenX - w * 0.5;
                const y0 = p.screenY - h;
                const x1 = x0 + w;
                const y1 = p.screenY;

                let collides = false;
                for (let b of placedBoxes) {{
                    if (!(x1 < b.x0 || x0 > b.x1 || y1 < b.y0 || y0 > b.y1)) {{
                        collides = true;
                        break;
                    }}
                }}

                if (collides && !p.isMajor) {{
                    p.domElement.style.display = "none";
                }} else {{
                    p.domElement.style.display = "block";
                    p.domElement.style.left = p.screenX + "px";
                    p.domElement.style.top = p.screenY + "px";
                    placedBoxes.push({{ x0, y0, x1, y1 }});
                }}
            }});
        }}

        function setCameraView(preset, animated = true) {{
            isTouring = false;
            document.getElementById("tour-btn").classList.remove("active");
            document.getElementById("tour-btn").textContent = "Tour Orbit";

            ["valley", "central", "lykens", "gap", "mahantango", "regional", "topdown"].forEach(p => {{
                const el = document.getElementById("btn-" + p);
                if (el) el.classList.toggle("active", p === preset);
            }});

            let camPos, targetPos;
            switch(preset) {{
                case "valley":
                    camPos = new THREE.Vector3(-42, 13, 2);
                    targetPos = new THREE.Vector3(12, 1.5, -2);
                    break;
                case "central":
                    camPos = new THREE.Vector3(2, 16, 26);
                    targetPos = new THREE.Vector3(0, 1.8, 2);
                    break;
                case "lykens":
                    camPos = new THREE.Vector3(34, 18, 22);
                    targetPos = new THREE.Vector3(26, 2.2, 4);
                    break;
                case "gap":
                    camPos = new THREE.Vector3(-66, 12, 3);
                    targetPos = new THREE.Vector3(-24, 1.0, 0);
                    break;
                case "mahantango":
                    camPos = new THREE.Vector3(6, 16, -34);
                    targetPos = new THREE.Vector3(2, 2.0, -14);
                    break;
                case "regional":
                    camPos = new THREE.Vector3(-8, 48, 54);
                    targetPos = new THREE.Vector3(0, 1.0, 0);
                    break;
                case "topdown":
                    camPos = new THREE.Vector3(0, 96, 0.01);
                    targetPos = new THREE.Vector3(0, 0, 0);
                    break;
            }}

            if (animated) {{
                animateCameraTo(camPos, targetPos);
            }} else {{
                camera.position.copy(camPos);
                controls.target.copy(targetPos);
                controls.update();
            }}
        }}

        function animateCameraTo(camPos, targetPos) {{
            camStartPos.copy(camera.position);
            camEndPos.copy(camPos);
            targetStartPos.copy(controls.target);
            targetEndPos.copy(targetPos);
            camTransitionProgress = 0;
            isCamTransitioning = true;
        }}

        let isPinned = false;
        let isHudVisible = true;
        let isHoveringHUD = false;
        let isInteractingCanvas = false;
        let autoHideTimer = null;
        let probeTimer = null;
        const HIDE_TIMEOUT_MS = 4000;

        function showHUD() {{
            isHudVisible = true;
            document.body.classList.remove("hud-hidden");
            resetAutoHideTimer();
        }}

        function hideHUD(force = false) {{
            const modal = document.getElementById("feature-modal");
            const modalOpen = modal && modal.style.display === "block";
            if ((isPinned || modalOpen) && !force) return;
            isHudVisible = false;
            document.body.classList.add("hud-hidden");
            if (autoHideTimer) {{
                clearTimeout(autoHideTimer);
                autoHideTimer = null;
            }}
        }}

        function toggleHUD() {{
            if (isHudVisible) {{
                hideHUD(true);
            }} else {{
                showHUD();
            }}
        }}

        function togglePin() {{
            isPinned = !isPinned;
            const pinBtn = document.getElementById("pin-btn");
            const pinText = document.getElementById("pin-text");
            if (isPinned) {{
                pinBtn.classList.add("pinned");
                pinText.textContent = "Pinned";
                pinBtn.title = "Pinned: Controls stay visible. Click to unpin.";
                showHUD();
            }} else {{
                pinBtn.classList.remove("pinned");
                pinText.textContent = "Auto-Hide";
                pinBtn.title = "Auto-Hide active: Controls hide when inactive or orbiting. Click to pin.";
                resetAutoHideTimer();
            }}
        }}

        function resetAutoHideTimer() {{
            if (autoHideTimer) {{
                clearTimeout(autoHideTimer);
                autoHideTimer = null;
            }}
            if (isPinned || isHoveringHUD || isInteractingCanvas || !isHudVisible) return;
            autoHideTimer = setTimeout(() => {{
                hideHUD();
            }}, HIDE_TIMEOUT_MS);
        }}

        function setupHUDManager() {{
            // Floating toggle button
            document.getElementById("floating-hud-toggle").addEventListener("click", (e) => {{
                e.stopPropagation();
                showHUD();
            }});

            // Panel header buttons
            document.getElementById("pin-btn").addEventListener("click", (e) => {{
                e.stopPropagation();
                togglePin();
            }});
            document.getElementById("hud-hide-btn").addEventListener("click", (e) => {{
                e.stopPropagation();
                hideHUD(true);
            }});

            // Card collapse toggles
            const setupCollapse = (btnId, cardId) => {{
                const btn = document.getElementById(btnId);
                const card = document.getElementById(cardId);
                if (btn && card) {{
                    btn.addEventListener("click", (e) => {{
                        e.stopPropagation();
                        card.classList.toggle("card-collapsed");
                    }});
                }}
            }};
            setupCollapse("toggle-controls-btn", "controls-panel");
            setupCollapse("toggle-title-btn", "title-card");
            setupCollapse("toggle-corridors-btn", "corridors-card");
            setupCollapse("toggle-legend-btn", "legend-card");

            // Prevent auto-hiding while cursor is inside any control panel
            const hudCards = document.querySelectorAll(".controls-panel, .corridors-card, .legend-card, .title-badge, #feature-modal");
            hudCards.forEach(card => {{
                card.addEventListener("mouseenter", () => {{
                    isHoveringHUD = true;
                    if (autoHideTimer) {{
                        clearTimeout(autoHideTimer);
                        autoHideTimer = null;
                    }}
                }});
                card.addEventListener("mouseleave", () => {{
                    isHoveringHUD = false;
                    if (isHudVisible) {{
                        resetAutoHideTimer();
                    }}
                }});
                card.addEventListener("touchstart", () => {{
                    isHoveringHUD = true;
                    if (autoHideTimer) {{
                        clearTimeout(autoHideTimer);
                        autoHideTimer = null;
                    }}
                }}, {{ passive: true }});
            }});

            // Detect user interaction with 3D canvas / OrbitControls
            controls.addEventListener("start", () => {{
                isInteractingCanvas = true;
                const probe = document.getElementById("probe-card");
                if (probe) probe.style.display = "none";
                if (!isPinned) {{
                    hideHUD();
                }}
            }});

            controls.addEventListener("end", () => {{
                isInteractingCanvas = false;
            }});

            window.addEventListener("pointerup", () => {{
                isInteractingCanvas = false;
            }});
            window.addEventListener("mouseup", () => {{
                isInteractingCanvas = false;
            }});

            // Mouse wheel zooming on canvas
            renderer.domElement.addEventListener("wheel", () => {{
                const probe = document.getElementById("probe-card");
                if (probe) probe.style.display = "none";
                if (!isPinned && isHudVisible) {{
                    hideHUD();
                }}
            }}, {{ passive: true }});

            // Pointer down on canvas
            renderer.domElement.addEventListener("pointerdown", () => {{
                if (!isPinned && isHudVisible) {{
                    hideHUD();
                }}
            }});

            // Mouse movement resets timer only when HUD is currently visible and not interacting
            window.addEventListener("mousemove", (e) => {{
                if (isHudVisible && !isInteractingCanvas && !isHoveringHUD) {{
                    resetAutoHideTimer();
                }}
            }});

            // Touch events on mobile/touchscreen outside HUD
            renderer.domElement.addEventListener("touchstart", () => {{
                if (!isPinned && isHudVisible) {{
                    hideHUD();
                }}
            }}, {{ passive: true }});

            // Keyboard shortcut 'H' or 'C' to toggle HUD, 'P' to toggle Pin, Escape to close
            window.addEventListener("keydown", (e) => {{
                if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
                if (e.key === "h" || e.key === "H" || e.key === "c" || e.key === "C") {{
                    e.preventDefault();
                    toggleHUD();
                }} else if (e.key === "p" || e.key === "P") {{
                    e.preventDefault();
                    togglePin();
                }} else if (e.key === "Escape" && isHudVisible) {{
                    hideHUD(true);
                }}
            }});

            // Start initial timer
            resetAutoHideTimer();
        }}

        function toggleTour() {{
            isTouring = !isTouring;
            const btn = document.getElementById("tour-btn");
            if (isTouring) {{
                btn.classList.add("active");
                btn.textContent = "Pause Orbit";
                tourAngle = Math.atan2(camera.position.z - controls.target.z, camera.position.x - controls.target.x);
                if (!isPinned) {{
                    setTimeout(() => hideHUD(), 400);
                }}
            }} else {{
                btn.classList.remove("active");
                btn.textContent = "Tour Orbit";
            }}
        }}

        function toggleWireframe() {{
            wireframeMesh.visible = !wireframeMesh.visible;
            document.getElementById("wire-btn").classList.toggle("active", wireframeMesh.visible);
        }}

        function onMouseMove(event) {{
            if (isInteractingCanvas) {{
                const probeCard = document.getElementById("probe-card");
                if (probeCard) probeCard.style.display = "none";
                return;
            }}

            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObject(terrainMesh);
            const probeCard = document.getElementById("probe-card");

            if (intersects.length > 0) {{
                const pt = intersects[0].point;
                const u = pt.x / WORLD_W + 0.5;
                const v = pt.z / WORLD_H + 0.5;
                if (u >= 0 && u <= 1 && v >= 0 && v <= 1) {{
                    const c = Math.min(COLS - 1, Math.max(0, Math.round(u * (COLS - 1))));
                    const r = Math.min(ROWS - 1, Math.max(0, Math.round(v * (ROWS - 1))));
                    const elev = ELEV[r][c];
                    const lat = LATS[r];
                    const lon = LONS[c];

                    probeCard.style.display = "block";
                    probeCard.style.opacity = "1";
                    document.getElementById("probe-val").textContent = elev.toFixed(0) + " ft (" + (elev * 0.3048).toFixed(0) + " m)";
                    document.getElementById("probe-sub").textContent = "Lat: " + lat.toFixed(4) + "° N | Lon: " + Math.abs(lon).toFixed(4) + "° W";

                    if (probeTimer) clearTimeout(probeTimer);
                    probeTimer = setTimeout(() => {{
                        probeCard.style.opacity = "0";
                        setTimeout(() => {{
                            if (probeCard.style.opacity === "0") probeCard.style.display = "none";
                        }}, 250);
                    }}, 2500);
                    return;
                }}
            }}
            probeCard.style.display = "none";
        }}

        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

        function animate() {{
            requestAnimationFrame(animate);

            if (isCamTransitioning) {{
                camTransitionProgress += 0.035;
                if (camTransitionProgress >= 1.0) {{
                    camTransitionProgress = 1.0;
                    isCamTransitioning = false;
                }}
                const t = 1 - Math.pow(1 - camTransitionProgress, 3);
                camera.position.lerpVectors(camStartPos, camEndPos, t);
                controls.target.lerpVectors(targetStartPos, targetEndPos, t);
                controls.update();
            }} else if (isTouring) {{
                tourAngle += 0.0035;
                const orbitR = 64;
                camera.position.x = controls.target.x + Math.cos(tourAngle) * orbitR;
                camera.position.z = controls.target.z + Math.sin(tourAngle) * orbitR;
                camera.position.y = 28 + Math.sin(tourAngle * 2) * 5;
                controls.update();
            }} else {{
                controls.update();
            }}

            updatePOIScreens();
            renderer.render(scene, camera);
        }}

        window.onload = init;
    </script>
</body>
</html>
"""

viewer_path = os.path.join(OUT_DIR, "appalachian_3d_viewer.html")
with open(viewer_path, "w", encoding="utf-8") as f:
    f.write(html_content)

index_path = os.path.join(OUT_DIR, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated {viewer_path} and {index_path} ({len(html_content)} bytes)")

