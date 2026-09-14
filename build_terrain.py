import io
import json
import math
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.ndimage import gaussian_filter

OUT_DIR = r'C:\Users\chadr\.gemini\antigravity\scratch\appalachian_3d'
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Load terrain data
data_path = os.path.join(OUT_DIR, 'terrain_data.json')
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

elev_raw = np.array(data['elevations_ft'])
lats = np.array(data['lats'])
lons = np.array(data['lons'])

# Smooth slightly to remove DEM tile sampling quantization stepping artifacts
elev = gaussian_filter(elev_raw, sigma=0.85)

# Save smoothed elevations back to JSON so 3D WebGL viewer has the clean mesh
data['elevations_ft'] = np.round(elev, 1).tolist()
data['elev_min_ft'] = float(np.min(elev))
data['elev_max_ft'] = float(np.max(elev))
with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print('Updated terrain_data.json with smoothed DEM grid and feature metadata.')

ROWS, COLS = elev.shape
LON_GRID, LAT_GRID = np.meshgrid(lons, lats)
BASE_DATUM = 180.0  # Base level for solid 3D block pedestal (feet)

def get_elev(lat, lon):
    r = np.abs(lats - lat).argmin()
    c = np.abs(lons - lon).argmin()
    return float(elev[r, c])

# Master Towns Dataset (All towns within the terrain grid)
TOWNS = [
    # Incorporated Boroughs (Major centers)
    {'name': 'Millersburg', 'lat': 40.5411, 'lon': -76.9569, 'elev': 446, 'borough': True,
     'desc': 'Susquehanna Water Gap & historic ferry'},
    {'name': 'Elizabethville', 'lat': 40.5489, 'lon': -76.8150, 'elev': 663, 'borough': True,
     'desc': 'Southern Lykens Valley commercial borough'},
    {'name': 'Berrysburg', 'lat': 40.6025, 'lon': -76.8114, 'elev': 723, 'borough': True,
     'desc': 'Central valley historic agricultural borough'},
    {'name': 'Gratz', 'lat': 40.6111, 'lon': -76.7178, 'elev': 815, 'borough': True,
     'desc': 'Northern valley borough & historic fair'},
    {'name': 'Lykens', 'lat': 40.5694, 'lon': -76.7025, 'elev': 677, 'borough': True,
     'desc': 'Historic anthracite mining borough'},
    {'name': 'Williamstown', 'lat': 40.5817, 'lon': -76.6186, 'elev': 757, 'borough': True,
     'desc': 'Eastern Williams Valley borough'},
    {'name': 'Pillow (Uniontown)', 'lat': 40.6406, 'lon': -76.8033, 'elev': 546, 'borough': True,
     'desc': 'Historic Mahantango Creek water gap borough'},

    # Villages & Valley Settlements
    {'name': 'Lenkerville', 'lat': 40.5311, 'lon': -76.9583, 'elev': 488, 'borough': False,
     'desc': 'Riverfront community south of Millersburg'},
    {'name': 'Killinger', 'lat': 40.5658, 'lon': -76.9036, 'elev': 536, 'borough': False,
     'desc': 'Western Lykens Valley crossroads'},
    {'name': 'Loyalton', 'lat': 40.5606, 'lon': -76.7561, 'elev': 597, 'borough': False,
     'desc': 'Valley settlement along US-209 & creek'},
    {'name': 'Wiconisco', 'lat': 40.5753, 'lon': -76.6781, 'elev': 764, 'borough': False,
     'desc': 'Historic mining community east of Lykens'},
    {'name': 'Spring Glen', 'lat': 40.6331, 'lon': -76.6431, 'elev': 715, 'borough': False,
     'desc': 'Hubley Township agricultural community'},
    {'name': 'Sacramento', 'lat': 40.6289, 'lon': -76.6019, 'elev': 630, 'borough': False,
     'desc': 'Eastern valley entrance community'},
    {'name': 'Klingerstown', 'lat': 40.6558, 'lon': -76.7386, 'elev': 539, 'borough': False,
     'desc': 'Mahantango Creek water gap village'},
    {'name': 'Dalmatia', 'lat': 40.6486, 'lon': -76.9069, 'elev': 490, 'borough': False,
     'desc': 'Historic river town north of Mahantango Mtn'},
    {'name': 'Hebe', 'lat': 40.6625, 'lon': -76.8208, 'elev': 857, 'borough': False,
     'desc': 'Upland village north of Mahantango Mtn'},
    {'name': 'Hickory Corners', 'lat': 40.6692, 'lon': -76.8833, 'elev': 646, 'borough': False,
     'desc': 'Northern valley farming settlement'}
]

def add_block_pedestal(ax, lons_m, lats_m, elev_m, base_z=BASE_DATUM):
    """Adds solid vertical skirt walls to turn 3D surface into an architectural block model."""
    x_n, y_n, z_top_n = lons_m[0, :], lats_m[0, :], elev_m[0, :]
    verts_n = []
    for j in range(len(x_n) - 1):
        verts_n.append([
            [x_n[j], y_n[j], z_top_n[j]],
            [x_n[j+1], y_n[j+1], z_top_n[j+1]],
            [x_n[j+1], y_n[j+1], base_z],
            [x_n[j], y_n[j], base_z]
        ])
    ax.add_collection3d(Poly3DCollection(verts_n, facecolors='#1e293b', edgecolors='#0f172a', lw=0.4, alpha=0.98))

    x_s, y_s, z_top_s = lons_m[-1, :], lats_m[-1, :], elev_m[-1, :]
    verts_s = []
    for j in range(len(x_s) - 1):
        verts_s.append([
            [x_s[j], y_s[j], z_top_s[j]],
            [x_s[j+1], y_s[j+1], z_top_s[j+1]],
            [x_s[j+1], y_s[j+1], base_z],
            [x_s[j], y_s[j], base_z]
        ])
    ax.add_collection3d(Poly3DCollection(verts_s, facecolors='#334155', edgecolors='#0f172a', lw=0.4, alpha=0.98))

    x_w, y_w, z_top_w = lons_m[:, 0], lats_m[:, 0], elev_m[:, 0]
    verts_w = []
    for i in range(len(x_w) - 1):
        verts_w.append([
            [x_w[i], y_w[i], z_top_w[i]],
            [x_w[i+1], y_w[i+1], z_top_w[i+1]],
            [x_w[i+1], y_w[i+1], base_z],
            [x_w[i], y_w[i], base_z]
        ])
    ax.add_collection3d(Poly3DCollection(verts_w, facecolors='#1e293b', edgecolors='#0f172a', lw=0.4, alpha=0.98))

    x_e, y_e, z_top_e = lons_m[:, -1], lats_m[:, -1], elev_m[:, -1]
    verts_e = []
    for i in range(len(x_e) - 1):
        verts_e.append([
            [x_e[i], y_e[i], z_top_e[i]],
            [x_e[i+1], y_e[i+1], z_top_e[i+1]],
            [x_e[i+1], y_e[i+1], base_z],
            [x_e[i], y_e[i], base_z]
        ])
    ax.add_collection3d(Poly3DCollection(verts_e, facecolors='#273549', edgecolors='#0f172a', lw=0.4, alpha=0.98))

def project_to_fig(fig, ax, x, y, z):
    """Accurately projects a 3D data coordinate to 2D figure fraction."""
    x2, y2, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
    disp = ax.transData.transform((x2, y2))
    return fig.transFigure.inverted().transform(disp)

# ==============================================================================
# 1. High-Resolution 3D Perspective Rendering (Single Hero Image)
# ==============================================================================
print('Rendering 1. High-Resolution 3D Topological Perspective Rendering...')
fig = plt.figure(figsize=(19, 11.5), dpi=220, facecolor='#0a0f1d')
ax = fig.add_subplot(111, projection='3d', facecolor='#0a0f1d')

ls = LightSource(azdeg=315, altdeg=42)
rgb = ls.shade(elev, cmap=plt.cm.gist_earth, vert_exag=2.3, blend_mode='overlay', vmin=340, vmax=1650)

surf = ax.plot_surface(LON_GRID, LAT_GRID, elev, facecolors=rgb,
                       rstride=1, cstride=1, antialiased=True, shade=False, lw=0)
add_block_pedestal(ax, LON_GRID, LAT_GRID, elev, base_z=BASE_DATUM)

ax.view_init(elev=30, azim=-68)
ax.set_box_aspect((2.2, 1.3, 0.48))
ax.dist = 7.6

ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.xaxis.pane.set_edgecolor('none')
ax.yaxis.pane.set_edgecolor('none')
ax.zaxis.pane.set_edgecolor('none')
ax.grid(False)
ax.set_axis_off()
ax.set_zlim(BASE_DATUM, 1850)

# Geomorphic Ridge & Gap Pins
geo_pins = [
    {'id': 'mah', 'lon': -76.78, 'lat': 40.640, 'z': 1180, 'color': '#ef4444', 'name': 'Mahantango Ridge'},
    {'id': 'ber', 'lon': -76.78, 'lat': 40.538, 'z': 1460, 'color': '#f97316', 'name': 'Berry Mountain Ridge'},
    {'id': 'val', 'lon': -76.81, 'lat': 40.590, 'z': 560, 'color': '#38bdf8', 'name': 'Lykens Valley Floor'},
    {'id': 'gap', 'lon': -76.96, 'lat': 40.545, 'z': 365, 'color': '#06b6d4', 'name': 'Susquehanna Water Gap'}
]

for p in geo_pins:
    ax.plot([p['lon'], p['lon']], [p['lat'], p['lat']], [p['z'], p['z'] + 90], color=p['color'], lw=2.2, zorder=20)
    ax.scatter([p['lon']], [p['lat']], [p['z'] + 90], color=p['color'], s=50, edgecolors='white', lw=1.2, zorder=21)

# Plot Town Pins on 3D surface
for t in TOWNS:
    tz = t['elev']
    is_b = t['borough']
    col = '#fbbf24' if is_b else '#38bdf8'
    sz = 45 if is_b else 22
    needle_h = 75 if is_b else 45
    ax.plot([t['lon'], t['lon']], [t['lat'], t['lat']], [tz, tz + needle_h], color=col, lw=1.3, alpha=0.90, zorder=18)
    ax.scatter([t['lon']], [t['lat']], [tz + needle_h], color=col, s=sz, edgecolors='#0f172a', lw=0.9, zorder=19)

fig.canvas.draw()
coords_proj = {p['id']: project_to_fig(fig, ax, p['lon'], p['lat'], p['z'] + 90) for p in geo_pins}

# Major callouts around the model
ax.annotate('MAHANTANGO MOUNTAIN (Northern Ridge)\nPeak: ~1,380 ft AMSL | Resistant Sandstone Caprock\nFold Belt Northern Rampart bounding Mahantango Creek',
            xy=coords_proj['mah'], xycoords='figure fraction',
            xytext=(0.56, 0.85), textcoords='figure fraction',
            arrowprops=dict(facecolor='#ef4444', edgecolor='white', arrowstyle='->', lw=1.8, shrinkB=6),
            fontsize=9.2, fontweight='bold', color='#fef2f2',
            bbox=dict(boxstyle='round,pad=0.45', facecolor='#111827', edgecolor='#ef4444', lw=1.6, alpha=0.96))

ax.annotate('LYKENS VALLEY (Intervening Valley Basin)\nFloor: ~500–720 ft AMSL (~800–1,050 ft Relief)\nCatskill Red Shale Agricultural Heartland (Berrysburg / Gratz)',
            xy=coords_proj['val'], xycoords='figure fraction',
            xytext=(0.74, 0.50), textcoords='figure fraction',
            arrowprops=dict(facecolor='#38bdf8', edgecolor='white', arrowstyle='->', lw=1.8, shrinkB=6),
            fontsize=9.2, fontweight='bold', color='#f0f9ff',
            bbox=dict(boxstyle='round,pad=0.45', facecolor='#111827', edgecolor='#38bdf8', lw=1.6, alpha=0.96))

ax.annotate('BERRY MOUNTAIN (Southern Ridge)\nPeak: ~1,614 ft AMSL | Mississippian Pocono Quartz Conglomerate\nFold Belt Southern Rampart bounding Armstrong Valley',
            xy=coords_proj['ber'], xycoords='figure fraction',
            xytext=(0.54, 0.12), textcoords='figure fraction',
            arrowprops=dict(facecolor='#f97316', edgecolor='white', arrowstyle='->', lw=1.8, shrinkB=6),
            fontsize=9.2, fontweight='bold', color='#fff7ed',
            bbox=dict(boxstyle='round,pad=0.45', facecolor='#111827', edgecolor='#f97316', lw=1.6, alpha=0.96))

ax.annotate('SUSQUEHANNA RIVER WATER GAP\nRiver: ~360 ft AMSL | Millersburg Ferry\nAntecedent River Gorge cutting through Folded Ridges',
            xy=coords_proj['gap'], xycoords='figure fraction',
            xytext=(0.04, 0.58), textcoords='figure fraction',
            arrowprops=dict(facecolor='#06b6d4', edgecolor='white', arrowstyle='->', lw=1.8, shrinkB=6),
            fontsize=9.2, fontweight='bold', color='#f0fdfa',
            bbox=dict(boxstyle='round,pad=0.45', facecolor='#111827', edgecolor='#06b6d4', lw=1.6, alpha=0.96))

# Comprehensive Settlement Directory Badge in Lower Left
town_summary = (
    "LYKENS VALLEY & RIDGES SETTLEMENT DIRECTORY\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "★ INCORPORATED BOROUGHS:\n"
    "  • Millersburg (446 ft)   • Elizabethville (663 ft)\n"
    "  • Berrysburg (723 ft)    • Gratz (815 ft)\n"
    "  • Lykens (677 ft)        • Williamstown (757 ft)\n"
    "  • Pillow / Uniontown (546 ft)\n\n"
    "● HISTORIC VILLAGES & COMMUNITIES:\n"
    "  • Dalmatia (490 ft)      • Klingerstown (539 ft)\n"
    "  • Wiconisco (764 ft)     • Spring Glen (715 ft)\n"
    "  • Sacramento (630 ft)    • Loyalton (597 ft)\n"
    "  • Killinger (536 ft)     • Lenkerville (488 ft)\n"
    "  • Hebe (857 ft)          • Hickory Corners (646 ft)\n\n"
    "◄ BORDERING REGIONAL CORRIDORS:\n"
    "  • South: Halifax (6 mi S via PA-147 / River)\n"
    "  • North: Herndon (3 mi N via PA-147)\n"
    "  • East:  Valley View & Hegins (PA-25)\n"
    "  • East:  Tower City & Pottsville (US-209)"
)
fig.text(0.04, 0.10, town_summary, fontsize=7.8, color='#cbd5e1', family='monospace',
         bbox=dict(boxstyle='round,pad=0.55', facecolor='#111827', edgecolor='#fbbf24', lw=1.3, alpha=0.96))

fig.text(0.50, 0.962, '3D TOPOLOGICAL RENDERING: APPALACHIAN RIDGE-AND-VALLEY PROVINCE',
         ha='center', fontsize=14.5, fontweight='bold', color='#f8fafc')
fig.text(0.50, 0.938, 'Berry Mountain (South), Mahantango Mountain (North), and Intervening Lykens Valley Settlements (PA)',
         ha='center', fontsize=10.2, color='#94a3b8')

render_3d_file = os.path.join(OUT_DIR, 'berry_mahantango_3d_render.png')
plt.savefig(render_3d_file, dpi=220, facecolor='#0a0f1d')
plt.close()
print(f'Saved {render_3d_file}')

# ==============================================================================
# 2. Multi-View 3D Analysis Plate
# ==============================================================================
print('Rendering 2. Multi-View 3D Analysis Plate...')
fig = plt.figure(figsize=(23, 14.5), dpi=200, facecolor='#0a0f1d')

views = [
    {
        'elev': 28, 'azim': -68,
        'title': 'A. Down-Valley Oblique View (Looking ENE along Strike of Fold)',
        'subtitle': 'Looking down Lykens Valley between Berry Mtn (Right) and Mahantango Mtn (Left)',
        'pins': [
            {'x': -76.78, 'y': 40.640, 'z': 1180, 'text': 'Mahantango Ridge (~1,380 ft)', 'col': '#ef4444', 'pos': (0.27, 0.88)},
            {'x': -76.8114, 'y': 40.6025, 'z': 723, 'text': 'Berrysburg (723 ft)', 'col': '#fbbf24', 'pos': (0.36, 0.68)},
            {'x': -76.7025, 'y': 40.5694, 'z': 677, 'text': 'Lykens & Wiconisco', 'col': '#fbbf24', 'pos': (0.42, 0.58)},
            {'x': -76.78, 'y': 40.538, 'z': 1460, 'text': 'Berry Mtn Ridge (~1,614 ft)', 'col': '#f97316', 'pos': (0.27, 0.49)}
        ]
    },
    {
        'elev': 48, 'azim': -120,
        'title': 'B. Regional Transverse View (Looking NNW across Fold Belt)',
        'subtitle': 'Broad perspective showing parallel sandstone ridges, agricultural valley, and river corridor',
        'pins': [
            {'x': -76.80, 'y': 40.642, 'z': 1100, 'text': 'Mahantango Ridge & Pillow Gap', 'col': '#ef4444', 'pos': (0.76, 0.88)},
            {'x': -76.7178, 'y': 40.6111, 'z': 815, 'text': 'Gratz & Lykens Valley Basin', 'col': '#fbbf24', 'pos': (0.86, 0.72)},
            {'x': -76.8150, 'y': 40.5489, 'z': 663, 'text': 'Elizabethville (663 ft)', 'col': '#fbbf24', 'pos': (0.78, 0.58)},
            {'x': -76.80, 'y': 40.540, 'z': 1340, 'text': 'Berry Mtn (South Ridge)', 'col': '#f97316', 'pos': (0.74, 0.48)}
        ]
    },
    {
        'elev': 20, 'azim': 115,
        'title': 'C. Water Gap Perspective (Looking WSW toward Susquehanna Gorge)',
        'subtitle': 'Viewing westward down the valley floor toward Millersburg and the river breach',
        'pins': [
            {'x': -76.96, 'y': 40.545, 'z': 365, 'text': 'Susquehanna Water Gap (360 ft)', 'col': '#06b6d4', 'pos': (0.34, 0.32)},
            {'x': -76.9569, 'y': 40.5411, 'z': 446, 'text': 'Millersburg Ferry Terminal', 'col': '#fbbf24', 'pos': (0.39, 0.22)},
            {'x': -76.9036, 'y': 40.5658, 'z': 536, 'text': 'Killinger / Western Valley', 'col': '#38bdf8', 'pos': (0.34, 0.08)}
        ]
    }
]

plt.subplots_adjust(left=0.03, right=0.97, top=0.89, bottom=0.04, wspace=0.10, hspace=0.25)

fig.text(0.50, 0.965, 'COMPREHENSIVE 3D TOPOLOGICAL ANALYSIS: APPALACHIAN RIDGE-AND-VALLEY PROVINCE',
         ha='center', fontsize=14.5, fontweight='bold', color='#ffffff')
fig.text(0.50, 0.940, 'Berry Mountain, Mahantango Mountain, and the Intervening Lykens Valley Settlements (Pennsylvania)',
         ha='center', fontsize=10.5, color='#94a3b8')

for idx, v in enumerate(views, 1):
    ax = fig.add_subplot(2, 2, idx, projection='3d', facecolor='#0a0f1d')
    surf = ax.plot_surface(LON_GRID, LAT_GRID, elev, facecolors=rgb,
                           rstride=1, cstride=1, antialiased=True, shade=False, lw=0)
    add_block_pedestal(ax, LON_GRID, LAT_GRID, elev, base_z=BASE_DATUM)
    
    for t in TOWNS:
        tz = t['elev']
        is_b = t['borough']
        col = '#fbbf24' if is_b else '#38bdf8'
        sz = 30 if is_b else 16
        ax.scatter([t['lon']], [t['lat']], [tz + 60], color=col, s=sz, edgecolors='#0f172a', lw=0.7, zorder=18)

    ax.view_init(elev=v['elev'], azim=v['azim'])
    ax.set_box_aspect((2.2, 1.3, 0.48))
    ax.dist = 7.8
    
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('none')
    ax.yaxis.pane.set_edgecolor('none')
    ax.zaxis.pane.set_edgecolor('none')
    ax.grid(False)
    ax.set_axis_off()
    ax.set_zlim(BASE_DATUM, 1850)
    
    ax.set_title(f"{v['title']}\n{v['subtitle']}", fontsize=9.8, fontweight='bold', color='#f8fafc', pad=10)
    
    for p in v['pins']:
        ax.plot([p['x'], p['x']], [p['y'], p['y']], [p['z'], p['z'] + 90], color=p['col'], lw=1.8, zorder=20)
        ax.scatter([p['x']], [p['y']], [p['z'] + 90], color=p['col'], s=40, edgecolors='white', lw=1.0, zorder=21)

fig.canvas.draw()

for idx, v in enumerate(views, 1):
    ax = fig.axes[idx - 1]
    for p in v['pins']:
        proj_pt = project_to_fig(fig, ax, p['x'], p['y'], p['z'] + 90)
        ax.annotate(p['text'],
                    xy=proj_pt, xycoords='figure fraction',
                    xytext=p['pos'], textcoords='figure fraction',
                    arrowprops=dict(facecolor=p['col'], edgecolor='white', arrowstyle='->', lw=1.5, shrinkB=5),
                    fontsize=8.2, fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.32', facecolor='#111827', edgecolor=p['col'], lw=1.3, alpha=0.94))

# Panel 4: Geological & Cultural Settlement Geography Synthesis
ax4 = fig.add_subplot(2, 2, 4, facecolor='#0a0f1d')
ax4.axis('off')

expl_text = (
    "APPALACHIAN GEOLOGY & SETTLEMENT GEOGRAPHY: BERRY & MAHANTANGO SECTION\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "1. TECTONIC ORIGIN & FOLD BELT GEOMORPHOLOGY:\n"
    "   • Formed during the late Paleozoic Alleghanian Orogeny (~320–280 Ma) by continental\n"
    "     collision during the assembly of Pangea.\n"
    "   • Parallel sandstone ridges (Mahantango to North, Berry to South) strike N70°E,\n"
    "     enclosing the deeply eroded Devonian Catskill red shale valley floor.\n"
    "   • Vertical topographic relief reaches 800 to 1,060 ft from valley to ridge crests.\n\n"
    "2. HISTORIC SETTLEMENT PATTERNS & ECONOMIC CORRIDORS:\n"
    "   • AGRICULTURAL HEARTLAND (Catskill Shale Lowlands):\n"
    "     - Berrysburg (inc. 1819), Gratz (inc. 1805), Spring Glen, and Sacramento form\n"
    "       a productive farming corridor famed for Pennsylvania German culture and soils.\n"
    "   • ANTHRACITE MINING CORRIDOR (Eastern Bear / Short Mountain Flank):\n"
    "     - Lykens (inc. 1872), Wiconisco, and Williamstown (inc. 1887) developed along\n"
    "       Wiconisco Creek around early anthracite collieries (Lykens Valley coal bed).\n"
    "   • SUSQUEHANNA RIVER GATEWAY & WATER GAPS:\n"
    "     - Millersburg (inc. 1807) & Lenkerville anchor the antecedent river gorge;\n"
    "       home to the historic Millersburg wooden paddlewheel ferry (operating since 1817).\n"
    "     - Pillow (Uniontown, inc. 1864) & Klingerstown guard Mahantango Creek gaps.\n"
    "     - Dalmatia (Georgetown) anchors the northern Susquehanna riverfront terrace.\n\n"
    "3. BORDERING REGIONAL CONNECTIONS:\n"
    "   • South: Halifax (6 mi S via PA-147) connects to Dauphin & Harrisburg.\n"
    "   • North: Herndon (3 mi N via PA-147) connects to Sunbury & Northumberland.\n"
    "   • East:  Valley View & Hegins (PA-25) link to Hegins Valley & Schuylkill County.\n"
    "   • East:  Tower City (US-209) links to the Southern Anthracite Coal Field."
)

ax4.text(0.03, 0.95, expl_text, transform=ax4.transAxes, fontsize=8.2, color='#f1f5f9',
         family='monospace', verticalalignment='top',
         bbox=dict(boxstyle='round,pad=0.75', facecolor='#111827', edgecolor='#38bdf8', lw=1.4))

multiview_file = os.path.join(OUT_DIR, 'appalachian_multi_view_3d.png')
plt.savefig(multiview_file, dpi=200, facecolor='#0a0f1d')
plt.close()
print(f'Saved {multiview_file}')

# ==============================================================================
# 3. Geomorphic Elevation Cross-Section Transect
# ==============================================================================
print('Rendering 3. Geomorphic Elevation Cross-Section Transect...')
ilon = np.abs(lons - (-76.8114)).argmin()
transect_lats_descending = lats
transect_elev_raw = elev[:, ilon]

sort_idx = np.argsort(transect_lats_descending)
t_lats = transect_lats_descending[sort_idx]
t_elev = transect_elev_raw[sort_idx]

R_earth = 6371.0
km_from_south = (t_lats - t_lats[0]) * (math.pi / 180.0) * R_earth

fig, ax = plt.subplots(figsize=(14.5, 6.8), dpi=220, facecolor='#ffffff')

ax.fill_between(km_from_south, t_elev, 200, color='#e8dfcc', alpha=0.9, label='Bedrock Strata (Devonian / Mississippian)')
ax.plot(km_from_south, t_elev, color='#0f172a', lw=2.5, label='Topographic Surface (USGS DEM)')

berry_mask = (t_lats >= 40.53) & (t_lats <= 40.56)
berry_crest_i = np.where(berry_mask)[0][np.argmax(t_elev[berry_mask])]

valley_mask = (t_lats >= 40.58) & (t_lats <= 40.62)
valley_floor_i = np.where(valley_mask)[0][np.argmin(t_elev[valley_mask])]

mahantango_mask = (t_lats >= 40.63) & (t_lats <= 40.67)
mahantango_crest_i = np.where(mahantango_mask)[0][np.argmax(t_elev[mahantango_mask])]

# Annotate Berry Mountain
ax.annotate(f'BERRY MOUNTAIN RIDGE\nCrest: {t_elev[berry_crest_i]:.0f} ft AMSL\nPocono Sandstone & Conglomerate',
            xy=(km_from_south[berry_crest_i], t_elev[berry_crest_i]),
            xytext=(km_from_south[berry_crest_i] - 1.5, t_elev[berry_crest_i] + 250),
            arrowprops=dict(facecolor='#ea580c', edgecolor='#9a3412', arrowstyle='->', lw=1.8),
            fontsize=9, fontweight='bold', color='#9a3412', ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#fff7ed', edgecolor='#ea580c', lw=1.5))

# Annotate Elizabethville (Projected in southern foothills)
elizabethville_km = (40.5489 - t_lats[0]) * (math.pi / 180.0) * R_earth
ax.plot(elizabethville_km, 663, '*', color='#f59e0b', markeredgecolor='#0f172a', markersize=12, zorder=10)
ax.annotate('Elizabethville (~663 ft)\nSouthern Foothills / US-209',
            xy=(elizabethville_km, 663), xytext=(elizabethville_km + 1.2, 840),
            arrowprops=dict(facecolor='#f59e0b', edgecolor='#b45309', arrowstyle='->', lw=1.5),
            fontsize=8.2, fontweight='bold', color='#78350f', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffbeb', edgecolor='#f59e0b', lw=1.2))

# Annotate Berrysburg in Lykens Valley Floor
ax.plot(km_from_south[valley_floor_i], 723, '*', color='#f59e0b', markeredgecolor='#0f172a', markersize=12, zorder=10)
ax.annotate(f'LYKENS VALLEY FLOOR\nBerrysburg Borough: 723 ft\nFloor Minimum: {t_elev[valley_floor_i]:.0f} ft (Relief: ~800 ft)\nEroded Catskill Red Shale',
            xy=(km_from_south[valley_floor_i], t_elev[valley_floor_i]),
            xytext=(km_from_south[valley_floor_i], t_elev[valley_floor_i] + 430),
            arrowprops=dict(facecolor='#0284c7', edgecolor='#0369a1', arrowstyle='->', lw=1.8),
            fontsize=8.8, fontweight='bold', color='#0369a1', ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#f0f9ff', edgecolor='#0284c7', lw=1.5))

# Annotate Pillow (Projected in northern gap)
pillow_km = (40.6406 - t_lats[0]) * (math.pi / 180.0) * R_earth
ax.plot(pillow_km, 546, '*', color='#f59e0b', markeredgecolor='#0f172a', markersize=12, zorder=10)
ax.annotate('Pillow (Uniontown, 546 ft)\nMahantango Creek Water Gap',
            xy=(pillow_km, 546), xytext=(pillow_km - 1.2, 790),
            arrowprops=dict(facecolor='#f59e0b', edgecolor='#b45309', arrowstyle='->', lw=1.5),
            fontsize=8.2, fontweight='bold', color='#78350f', ha='right',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffbeb', edgecolor='#f59e0b', lw=1.2))

# Annotate Mahantango Mountain
ax.annotate(f'MAHANTANGO MOUNTAIN RIDGE\nCrest: {t_elev[mahantango_crest_i]:.0f} ft AMSL\nResistant Ridge-Capping Sandstone',
            xy=(km_from_south[mahantango_crest_i], t_elev[mahantango_crest_i]),
            xytext=(km_from_south[mahantango_crest_i] + 1.6, t_elev[mahantango_crest_i] + 250),
            arrowprops=dict(facecolor='#dc2626', edgecolor='#991b1b', arrowstyle='->', lw=1.8),
            fontsize=9, fontweight='bold', color='#991b1b', ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#fef2f2', edgecolor='#dc2626', lw=1.5))

ax.text(0.015, 0.08, '◄ SOUTH\nTo Halifax & Harrisburg (PA-147)', transform=ax.transAxes,
        fontsize=8.5, fontweight='bold', color='#475569', ha='left',
        bbox=dict(boxstyle='square,pad=0.3', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1))
ax.text(0.985, 0.08, 'NORTH ►\nTo Herndon & Sunbury (PA-147)', transform=ax.transAxes,
        fontsize=8.5, fontweight='bold', color='#475569', ha='right',
        bbox=dict(boxstyle='square,pad=0.3', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1))

# Width arrow moved to y=640 to prevent collision with Berrysburg
ax.annotate('', xy=(km_from_south[berry_crest_i], 640), xytext=(km_from_south[mahantango_crest_i], 640),
            arrowprops=dict(arrowstyle='<->', color='#2563eb', lw=1.8))
valley_width_km = km_from_south[mahantango_crest_i] - km_from_south[berry_crest_i]
ax.text((km_from_south[berry_crest_i] + km_from_south[mahantango_crest_i])/2, 605,
        f'Valley Width Crest-to-Crest: ~{valley_width_km:.1f} km ({valley_width_km*0.621371:.1f} miles)',
        color='#1d4ed8', fontsize=8.5, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#eff6ff', edgecolor='#93c5fd', lw=1))

ax.set_ylim(200, 1750)
ax.set_xlim(km_from_south[0], km_from_south[-1])
ax.set_title('Appalachian Geomorphic Cross-Section Profile (South-to-North Transect)\n'
             'Topographic Profile across Berry Mountain, Lykens Valley (Elizabethville & Berrysburg), and Mahantango Mountain (Pillow)',
             fontsize=12, fontweight='bold', pad=14)
ax.set_xlabel('South-to-North Transect Distance (km) along 76.8114°W Meridian', fontsize=10, fontweight='bold')
ax.set_ylabel('Elevation above Sea Level (feet)', fontsize=10, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', framealpha=0.95)

plt.tight_layout()
profile_file = os.path.join(OUT_DIR, 'appalachian_cross_section_profile.png')
plt.savefig(profile_file, dpi=220)
plt.close()
print(f'Saved {profile_file}')

# ==============================================================================
# 4. Polished 2D Topographical Relief Map with Full Settlement Network
# ==============================================================================
print('Rendering 4. Polished 2D Topographical Relief Map with Full Settlement Network...')
fig, ax = plt.subplots(figsize=(16, 10.5), dpi=220, facecolor='#ffffff')
rgb_2d = ls.shade(elev, cmap=plt.cm.terrain, vert_exag=3.0, blend_mode='overlay', vmin=340, vmax=1650)
extent = [lons.min(), lons.max(), lats.min(), lats.max()]

im = ax.imshow(rgb_2d, extent=extent, origin='upper', aspect='auto')

# Elevation Contours
cs = ax.contour(lons, lats, elev, levels=np.arange(400, 1650, 150), colors='#0f172a', alpha=0.30, linewidths=0.55)
ax.clabel(cs, inline=True, fontsize=6.5, fmt='%d ft', colors='#334155')

# Prominent Geomorphic Annotations
ax.annotate('MAHANTANGO MOUNTAIN\n(Northern Sandstone Crest: ~1,380 ft)',
            xy=(-76.76, 40.640), xytext=(-76.76, 40.678),
            arrowprops=dict(facecolor='#b91c1c', edgecolor='white', arrowstyle='->', lw=1.8),
            fontsize=9.2, fontweight='bold', color='#991b1b', ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#fef2f2', alpha=0.92, edgecolor='#b91c1c', lw=1.4))

ax.annotate('BERRY MOUNTAIN\n(Southern Pocono Ridge: ~1,340–1,614 ft)',
            xy=(-76.84, 40.538), xytext=(-76.84, 40.510),
            arrowprops=dict(facecolor='#c2410c', edgecolor='white', arrowstyle='->', lw=1.8),
            fontsize=9.2, fontweight='bold', color='#9a3412', ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#fff7ed', alpha=0.92, edgecolor='#c2410c', lw=1.4))

ax.annotate('LYKENS VALLEY\n(Catskill Red Shale Basin: ~500–620 ft)',
            xy=(-76.855, 40.588), xytext=(-76.855, 40.618),
            arrowprops=dict(facecolor='#0284c7', edgecolor='white', arrowstyle='->', lw=1.8),
            fontsize=9.2, fontweight='bold', color='#0369a1', ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#f0f9ff', alpha=0.92, edgecolor='#0284c7', lw=1.4))

ax.annotate('Susquehanna River\nWater Gap (~360 ft)',
            xy=(-76.960, 40.546), xytext=(-76.995, 40.605),
            arrowprops=dict(facecolor='#0d9488', edgecolor='white', arrowstyle='->', lw=1.6),
            fontsize=8.5, fontweight='bold', color='#0f766e', ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0fdfa', alpha=0.92, edgecolor='#0d9488', lw=1.2))

# Town placement specs: (name, lat, lon, elev, is_borough, dx, dy, ha, va)
towns_specs = [
    # Boroughs (Stars)
    ('Millersburg', 40.5411, -76.9569, 446, True, 0.006, 0.004, 'left', 'bottom'),
    ('Elizabethville', 40.5489, -76.8150, 663, True, 0.006, -0.005, 'left', 'top'),
    ('Berrysburg', 40.6025, -76.8114, 723, True, 0.006, 0.004, 'left', 'bottom'),
    ('Gratz', 40.6111, -76.7178, 815, True, -0.006, 0.004, 'right', 'bottom'),
    ('Lykens', 40.5694, -76.7025, 677, True, 0.006, -0.005, 'left', 'top'),
    ('Williamstown', 40.5817, -76.6186, 757, True, 0.000, -0.006, 'center', 'top'),
    ('Pillow', 40.6406, -76.8033, 546, True, 0.006, -0.005, 'left', 'top'),
    
    # Villages & Settlements (Circles)
    ('Lenkerville', 40.5311, -76.9583, 488, False, 0.006, -0.002, 'left', 'center'),
    ('Killinger', 40.5658, -76.9036, 536, False, 0.006, 0.004, 'left', 'bottom'),
    ('Loyalton', 40.5606, -76.7561, 597, False, 0.000, 0.005, 'center', 'bottom'),
    ('Wiconisco', 40.5753, -76.6781, 764, False, -0.007, 0.005, 'right', 'bottom'),
    ('Spring Glen', 40.6331, -76.6431, 715, False, -0.007, 0.004, 'right', 'bottom'),
    ('Sacramento', 40.6289, -76.6019, 630, False, -0.006, -0.004, 'right', 'top'),
    ('Klingerstown', 40.6558, -76.7386, 539, False, 0.006, 0.004, 'left', 'bottom'),
    ('Dalmatia', 40.6486, -76.9069, 490, False, -0.006, 0.004, 'right', 'bottom'),
    ('Hebe', 40.6625, -76.8208, 857, False, 0.006, 0.004, 'left', 'bottom'),
    ('Hickory Corners', 40.6692, -76.8833, 646, False, 0.006, 0.004, 'left', 'bottom')
]

for name, tlat, tlon, telev, is_bor, dx, dy, ha, va in towns_specs:
    if is_bor:
        ax.plot(tlon, tlat, '*', color='#f59e0b', markeredgecolor='#0f172a', markersize=12, mew=1.3, zorder=15)
        badge_bg = '#fffbeb'
        badge_edge = '#b45309'
        text_color = '#78350f'
        fweight = 'bold'
        fsize = 8.2
    else:
        ax.plot(tlon, tlat, 'o', color='#38bdf8', markeredgecolor='#0f172a', markersize=6.0, mew=1.1, zorder=14)
        badge_bg = '#ffffff'
        badge_edge = '#64748b'
        text_color = '#0f172a'
        fweight = 'bold'
        fsize = 7.4

    lbl = f"{name}\n({telev} ft)"
    ax.text(tlon + dx, tlat + dy, lbl, fontsize=fsize, fontweight=fweight, color=text_color,
            ha=ha, va=va, zorder=16,
            bbox=dict(boxstyle='round,pad=0.22', facecolor=badge_bg, alpha=0.92, edgecolor=badge_edge, lw=0.9))

# Clean Border Corridor Badges
# 1. South border: Halifax
ax.text(-76.920, 40.504, '◄ TO HALIFAX (6 mi) & HARRISBURG (PA-147 / River Corridor)',
        fontsize=7.8, fontweight='bold', color='#1e293b', ha='left', va='bottom',
        bbox=dict(boxstyle='square,pad=0.28', facecolor='#e2e8f0', edgecolor='#475569', lw=1.0, alpha=0.95))

# 2. North border: Herndon
ax.text(-76.905, 40.686, '▲ TO HERNDON (3 mi) & SUNBURY (PA-147)',
        fontsize=7.8, fontweight='bold', color='#1e293b', ha='left', va='top',
        bbox=dict(boxstyle='square,pad=0.28', facecolor='#e2e8f0', edgecolor='#475569', lw=1.0, alpha=0.95))

# 3. East border Route 25: Valley View & Hegins
ax.text(-76.603, 40.655, 'TO HEGINS & VALLEY VIEW (PA-25) ►',
        fontsize=7.8, fontweight='bold', color='#1e293b', ha='right', va='center',
        bbox=dict(boxstyle='square,pad=0.28', facecolor='#e2e8f0', edgecolor='#475569', lw=1.0, alpha=0.95))

# 4. East border Route 209: Tower City
ax.text(-76.603, 40.560, 'TO TOWER CITY & POTTSVILLE (US-209) ►',
        fontsize=7.8, fontweight='bold', color='#1e293b', ha='right', va='center',
        bbox=dict(boxstyle='square,pad=0.28', facecolor='#e2e8f0', edgecolor='#475569', lw=1.0, alpha=0.95))

# Legend
legend_box = (
    "MAP SYMBOLOGY & FEATURES\n"
    "★ Incorporated Borough (Historic Center)\n"
    "● Historic Village / Agricultural Settlement\n"
    "▲ Sandstone Mountain Rampart\n"
    "— Topographic Contours (150-ft Interval)\n"
    "◄ Regional Corridor to Bordering Towns"
)
ax.text(0.015, 0.025, legend_box, transform=ax.transAxes, fontsize=8.0, color='#0f172a',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffffff', edgecolor='#cbd5e1', lw=1.2, alpha=0.96))

ax.set_title('Topographical Shaded Relief & Comprehensive Settlement Map\n'
             'Appalachian Ridge-and-Valley Province: Berry Mountain, Mahantango Mountain, and Lykens Valley (Pennsylvania)',
             fontsize=13, fontweight='bold', pad=14)
ax.set_xlabel('Longitude (°W)', fontsize=10, fontweight='bold')
ax.set_ylabel('Latitude (°N)', fontsize=10, fontweight='bold')
ax.set_xlim(lons.min(), lons.max())
ax.set_ylim(lats.min(), lats.max())
ax.grid(True, linestyle='--', alpha=0.35)

plt.tight_layout()
map_file = os.path.join(OUT_DIR, 'appalachian_topographical_map.png')
plt.savefig(map_file, dpi=220)
plt.close()
print(f'Saved {map_file}')

print('ALL 4 SCIENTIFIC RENDERS GENERATED SUCCESSFULLY WITH COMPLETE TOWN NETWORK!')
