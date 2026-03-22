#!/usr/bin/env python3
"""
CP77 Command Builder - Build Script
Parses data/commands.txt and generates index.html
Usage: python src/build.py
"""

import re
import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'commands.txt')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'index.html')


def parse_commands(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = []
    current_section = None
    current_sub = None

    def extract_entry(line):
        s = line.strip()
        # Game.AddToInventory("Items/Ammo.XXX", N) | description
        m = re.match(r'Game\.AddToInventory\("([^"]+)",\s*([^)]+)\)\s*\|\s*(.+)', s)
        if m:
            return {'cmd': f'Game.AddToInventory("{m.group(1)}", {m.group(2).strip()})',
                    'id': m.group(1), 'desc': m.group(3).strip(), 'qty': m.group(2).strip()}
        # Bare: Items.XXX | description
        m = re.match(r'(Items\.[A-Za-z0-9_]+)\s*\|\s*(.+)', s)
        if m:
            return {'cmd': f'Game.AddToInventory("{m.group(1)}", 1)',
                    'id': m.group(1), 'desc': m.group(2).strip(), 'qty': '1'}
        # Bare: Ammo.XXX | description
        m = re.match(r'(Ammo\.[A-Za-z0-9_]+)\s*\|\s*(.+)', s)
        if m:
            return {'cmd': f'Game.AddToInventory("{m.group(1)}", 1)',
                    'id': m.group(1), 'desc': m.group(2).strip(), 'qty': '1'}
        # Other Game.* commands | description
        m = re.match(r'(Game\.[^\|]+)\s*\|\s*(.+)', s)
        if m:
            cmd = m.group(1).strip()
            if 'AddToInventory' not in cmd:
                return {'cmd': cmd, 'id': re.sub(r'[^A-Za-z0-9_]', '_', cmd)[:60],
                        'desc': m.group(2).strip(), 'qty': None}
        return None

    def is_subsection_header(line):
        s = line.strip()
        return (re.match(r'^[A-Z][A-Z0-9\s/\-()+]+$', s)
                and 4 < len(s) < 60
                and '|' not in s
                and not s.startswith('===')
                and not s.startswith('COMMAND')
                and not s.startswith('SECTION')
                and not s.startswith('USE')
                and not s.startswith('NOTE'))

    for line in lines:
        s = line.strip()
        if not s or s.startswith('===') or s.startswith('---') or s.startswith('-'):
            continue
        if 'COMMAND' in s and 'WHAT IT DOES' in s:
            continue
        if s.startswith('Use:') or s.startswith('NOTE') or s.startswith('http'):
            continue

        # Section header
        m = re.match(r'SECTION\s+\d+\s+[—\-]+\s+(.+)', s)
        if m:
            current_section = {'name': m.group(1).strip(), 'items': []}
            sections.append(current_section)
            current_sub = None
            continue

        if current_section is None:
            continue

        # Subsection header
        if is_subsection_header(s):
            current_sub = s
            continue

        entry = extract_entry(line)
        if entry:
            entry['sub'] = current_sub or ''
            current_section['items'].append(entry)

    # Manually fix ATTRIBUTES section (complex multi-line commands)
    attrs = next((s for s in sections if 'ATTRIBUTES' in s['name']), None)
    if attrs and not attrs['items']:
        attrs['items'] = [
            {'cmd': 'PlayerDevelopmentSystem.GetInstance(Game.GetPlayer()):GetDevelopmentData(Game.GetPlayer()):SetAttribute("Strength", X)',
             'id': 'SetAttribute_Strength', 'desc': 'Set Body attribute to X', 'qty': None, 'sub': 'SET ATTRIBUTES'},
            {'cmd': 'PlayerDevelopmentSystem.GetInstance(Game.GetPlayer()):GetDevelopmentData(Game.GetPlayer()):SetAttribute("Reflexes", X)',
             'id': 'SetAttribute_Reflexes', 'desc': 'Set Reflexes attribute to X', 'qty': None, 'sub': 'SET ATTRIBUTES'},
            {'cmd': 'PlayerDevelopmentSystem.GetInstance(Game.GetPlayer()):GetDevelopmentData(Game.GetPlayer()):SetAttribute("TechnicalAbility", X)',
             'id': 'SetAttribute_TechnicalAbility', 'desc': 'Set Technical Ability to X', 'qty': None, 'sub': 'SET ATTRIBUTES'},
            {'cmd': 'PlayerDevelopmentSystem.GetInstance(Game.GetPlayer()):GetDevelopmentData(Game.GetPlayer()):SetAttribute("Intelligence", X)',
             'id': 'SetAttribute_Intelligence', 'desc': 'Set Intelligence to X', 'qty': None, 'sub': 'SET ATTRIBUTES'},
            {'cmd': 'PlayerDevelopmentSystem.GetInstance(Game.GetPlayer()):GetDevelopmentData(Game.GetPlayer()):SetAttribute("Cool", X)',
             'id': 'SetAttribute_Cool', 'desc': 'Set Cool attribute to X', 'qty': None, 'sub': 'SET ATTRIBUTES'},
            {'cmd': 'PlayerDevelopmentSystem.GetInstance(Game.GetPlayer()):GetDevelopmentData(Game.GetPlayer()):AddDevelopmentPoints(X, gamedataDevelopmentPointType.Attribute)',
             'id': 'AddDevelopmentPoints_Attribute', 'desc': 'Add X Attribute (skill) points', 'qty': None, 'sub': 'ADD POINTS'},
            {'cmd': 'PlayerDevelopmentSystem.GetInstance(Game.GetPlayer()):GetDevelopmentData(Game.GetPlayer()):AddDevelopmentPoints(X, gamedataDevelopmentPointType.Primary)',
             'id': 'AddDevelopmentPoints_Primary', 'desc': 'Add X Perk points', 'qty': None, 'sub': 'ADD POINTS'},
        ]

    # Manually fix TELEPORT section
    tele = next((s for s in sections if 'TELEPORT' in s['name']), None)
    if tele and not tele['items']:
        tp = 'Game.GetTeleportationFacility():Teleport(GetPlayer(), ToVector4{{x={x}, y={y}, z={z}, w=1}}, ToEulerAngles{{roll=0, pitch=0, yaw=0}})'
        locations = [
            ("V's Apartment (Megabuilding H10)", -823.92, -1216.7, 22.93),
            ("Afterlife Bar",                    1132.87, -1161.7,  8.02),
            ("Arasaka Tower (exterior)",          680.66,  -659.26,  5.0),
            ("Misty's Esoterica",                -861.2,  -1265.0,  8.0),
            ("Tom's Diner",                       862.48, -1006.0,   8.4),
            ("Rogue's Ranch (Badlands)",          1272.7,  2200.5,  14.5),
            ("Panam's Camp (Aldecaldos)",         2062.4,  2448.0,   7.5),
            ("Dogtown (Phantom Liberty area)",   -2100.0,  2700.0,  10.0),
        ]
        tele['items'] = [
            {'cmd': 'print(Game.GetPlayer():GetWorldPosition())',
             'id': 'GetWorldPosition', 'desc': "Print V's current coordinates to console", 'qty': None, 'sub': 'UTILITIES'},
            {'cmd': 'Game.LogPlayerPositionAndName()',
             'id': 'LogPlayerPosition', 'desc': 'Save current position so you can return', 'qty': None, 'sub': 'UTILITIES'},
        ] + [
            {'cmd': tp.format(x=x, y=y, z=z),
             'id': f'Teleport_{name.split()[0]}', 'desc': name, 'qty': None, 'sub': 'LOCATIONS'}
            for name, x, y, z in locations
        ]

    return sections


def build_html(sections, output_path):
    data_json = json.dumps(sections, separators=(',', ':'))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CP2077 Command Builder</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0f0f1e;color:#dde;min-height:100vh;display:flex;flex-direction:column}}
#topbar{{background:#090916;border-bottom:1px solid #2a2a4a;padding:10px 14px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;flex-shrink:0}}
#topbar h1{{color:#00d4ff;font-size:17px;letter-spacing:.5px;white-space:nowrap;margin-right:4px}}
#topbar h1 span{{color:#ff4466}}
#search{{flex:1;min-width:180px;padding:7px 12px;border-radius:6px;border:1px solid #444;background:#1a1a30;color:#dde;font-size:13px}}
#search:focus{{outline:none;border-color:#00d4ff}}
#qtyWrap{{display:flex;align-items:center;gap:6px;font-size:13px;color:#888;white-space:nowrap}}
#qty{{width:70px;padding:6px 8px;border-radius:6px;border:1px solid #444;background:#1a1a30;color:#dde;font-size:13px;text-align:center}}
.btn{{padding:7px 13px;border-radius:6px;border:none;cursor:pointer;font-size:12px;font-weight:600;transition:background .1s,transform .1s}}
.btn:active{{transform:scale(.97)}}
.btn-cyan{{background:#00d4ff;color:#000}}.btn-cyan:hover{{background:#33ddff}}
.btn-green{{background:#00cc77;color:#000}}.btn-green:hover{{background:#00ee88}}
.btn-ghost{{background:transparent;border:1px solid #444;color:#999;font-size:12px}}.btn-ghost:hover{{border-color:#ff4466;color:#ff4466}}
#selBadge{{background:#0d2a3a;color:#00d4ff;border-radius:10px;padding:3px 10px;font-size:12px;font-weight:600;white-space:nowrap}}
#main{{display:flex;flex:1;overflow:hidden;min-height:0}}
#left{{width:55%;border-right:1px solid #2a2a4a;overflow-y:auto;padding:8px 0}}
.section-block{{margin-bottom:2px}}
.section-head{{display:flex;align-items:center;gap:8px;padding:8px 14px;cursor:pointer;background:#13132a;border-bottom:1px solid #1e1e3a;user-select:none;position:sticky;top:0;z-index:2}}
.section-head:hover{{background:#1a1a38}}
.section-arrow{{font-size:11px;color:#555;transition:transform .2s;width:12px;text-align:center}}
.section-arrow.open{{transform:rotate(90deg);color:#00d4ff}}
.section-title{{font-size:13px;font-weight:600;color:#cce;flex:1}}
.section-count{{font-size:11px;color:#555;margin-left:auto}}
.section-items{{display:none}}.section-items.open{{display:block}}
.sub-head{{padding:5px 14px 3px;font-size:10px;font-weight:700;color:#556;letter-spacing:.8px;background:#0c0c1e;border-bottom:1px solid #161628;margin-top:2px}}
.item-row{{display:flex;align-items:flex-start;gap:9px;padding:7px 14px;border-bottom:1px solid #161628;cursor:pointer;transition:background .1s}}
.item-row:hover{{background:#181830}}
.item-row.checked{{background:#0d2035;border-left:3px solid #00d4ff}}
.item-row input[type=checkbox]{{accent-color:#00d4ff;width:15px;height:15px;flex-shrink:0;margin-top:1px}}
.item-label{{flex:1;min-width:0}}
.item-desc{{font-size:12px;color:#ccd}}
.item-id{{font-size:10px;color:#556;font-family:monospace;margin-top:1px;word-break:break-all}}
.no-match{{padding:30px;text-align:center;color:#445;font-size:13px}}
#right{{width:45%;display:flex;flex-direction:column;min-height:0}}
#rhead{{padding:9px 13px;background:#090916;border-bottom:1px solid #2a2a4a;display:flex;justify-content:space-between;align-items:center;flex-shrink:0}}
#rhead span{{font-size:13px;color:#778}}
#selList{{flex:1;overflow-y:auto;padding:8px 10px;display:flex;flex-direction:column;gap:5px;min-height:0}}
.sel-item{{display:flex;align-items:center;gap:7px;background:#12122a;border:1px solid #222244;border-radius:5px;padding:5px 9px}}
.sel-name{{font-size:11px;color:#aac;flex:1;font-family:monospace;word-break:break-all}}
.sel-qty{{font-size:12px;color:#00d4ff;font-weight:700;min-width:24px;text-align:right}}
.sel-rm{{background:none;border:none;color:#ff4466;cursor:pointer;font-size:15px;padding:0 3px;line-height:1}}
.empty-msg{{padding:30px;text-align:center;color:#334;font-size:13px;line-height:1.8}}
#outWrap{{border-top:1px solid #2a2a4a;flex-shrink:0}}
#outHead{{padding:8px 13px;background:#090916;border-bottom:1px solid #1a1a30;display:flex;justify-content:space-between;align-items:center}}
#outHead span{{font-size:12px;color:#556}}
#output{{width:100%;height:180px;background:#070713;color:#00ff99;font-family:'Courier New',monospace;font-size:11.5px;padding:10px 12px;border:none;resize:none;outline:none;line-height:1.65}}
</style>
</head>
<body>
<div id="topbar">
  <h1>CP2077 <span>Command Builder</span></h1>
  <input id="search" type="text" placeholder="Search any item, ID, or description..." oninput="onSearch()">
  <div id="qtyWrap">Qty: <input id="qty" type="number" value="1" min="1" max="999999"></div>
  <span id="selBadge">0 selected</span>
  <button class="btn btn-ghost" onclick="deselectAll()">Clear</button>
  <button class="btn btn-cyan" onclick="generate()">Generate &#9654;</button>
</div>
<div id="main">
  <div id="left"></div>
  <div id="right">
    <div id="rhead">
      <span>Selected items</span>
      <div style="display:flex;gap:6px">
        <button class="btn btn-green" id="copyBtn" onclick="copyOut()">Copy all</button>
        <button class="btn btn-ghost" onclick="clearOut()">Clear output</button>
      </div>
    </div>
    <div id="selList"><div class="empty-msg">Search and check items on the left.<br>Hit <strong style="color:#00d4ff">Generate &#9654;</strong> to build your commands.</div></div>
    <div id="outWrap">
      <div id="outHead"><span id="cmdCount">0 commands ready</span></div>
      <textarea id="output" readonly placeholder="// Commands appear here after Generate&#10;// Paste directly into CET console in-game"></textarea>
    </div>
  </div>
</div>
<script>
const SECTIONS = {data_json};
let selected = {{}};

function getQty(){{ return parseInt(document.getElementById('qty').value)||1; }}

function buildLeft(){{
  const left = document.getElementById('left');
  left.innerHTML = '';
  SECTIONS.forEach((sec,si)=>{{
    const block = document.createElement('div');
    block.className = 'section-block';
    const head = document.createElement('div');
    head.className = 'section-head';
    head.innerHTML = `<span class="section-arrow" id="arr-${{si}}">&#9658;</span>
      <span class="section-title">${{sec.name}}</span>
      <span class="section-count">${{sec.items.length}} items</span>`;
    head.onclick = ()=>toggleSection(si);
    const body = document.createElement('div');
    body.className = 'section-items';
    body.id = 'body-'+si;
    renderItems(body, sec.items);
    block.appendChild(head);
    block.appendChild(body);
    left.appendChild(block);
  }});
}}

function renderItems(container, items){{
  container.innerHTML = '';
  if(!items.length){{ container.innerHTML='<div class="no-match">No items in this section.</div>'; return; }}
  let lastSub = null;
  items.forEach(item=>{{
    if(item.sub && item.sub !== lastSub){{
      const sh = document.createElement('div');
      sh.className = 'sub-head';
      sh.textContent = item.sub;
      container.appendChild(sh);
      lastSub = item.sub;
    }}
    const row = document.createElement('div');
    row.className = 'item-row'+(selected[item.id]?' checked':'');
    row.innerHTML = `<input type="checkbox" ${{selected[item.id]?'checked':''}} onclick="event.stopPropagation();toggleItem(${{JSON.stringify(item)}})">
      <div class="item-label">
        <div class="item-desc">${{item.desc||item.id}}</div>
        <div class="item-id">${{item.id}}</div>
      </div>`;
    row.onclick = ()=>toggleItem(item);
    container.appendChild(row);
  }});
}}

function toggleSection(si){{
  const body = document.getElementById('body-'+si);
  const arr = document.getElementById('arr-'+si);
  body.classList.toggle('open');
  arr.classList.toggle('open', body.classList.contains('open'));
}}

function toggleItem(item){{
  if(selected[item.id]){{ delete selected[item.id]; }}
  else {{ selected[item.id] = {{...item, selectedQty: getQty()}}; }}
  updateBadge(); updateSelList();
  document.querySelectorAll('.item-id').forEach(el=>{{
    if(el.textContent===item.id){{
      const row = el.closest('.item-row');
      const cb = row.querySelector('input');
      cb.checked = !!selected[item.id];
      row.classList.toggle('checked', !!selected[item.id]);
    }}
  }});
}}

function deselectAll(){{
  selected = {{}};
  updateBadge(); updateSelList();
  document.querySelectorAll('.item-row').forEach(r=>{{
    r.classList.remove('checked');
    const cb = r.querySelector('input[type=checkbox]');
    if(cb) cb.checked = false;
  }});
}}

function updateBadge(){{
  document.getElementById('selBadge').textContent = Object.keys(selected).length+' selected';
}}

function updateSelList(){{
  const keys = Object.keys(selected);
  const panel = document.getElementById('selList');
  if(!keys.length){{
    panel.innerHTML='<div class="empty-msg">Search and check items on the left.<br>Hit <strong style="color:#00d4ff">Generate &#9654;</strong> to build your commands.</div>';
    return;
  }}
  panel.innerHTML = keys.map(id=>{{
    const s = selected[id];
    const safeId = id.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
    return `<div class="sel-item">
      <span class="sel-name">${{s.desc||s.id}}</span>
      <span class="sel-qty">x${{s.selectedQty}}</span>
      <button class="sel-rm" onclick="removeOne('${{safeId}}')">x</button>
    </div>`;
  }}).join('');
}}

function removeOne(id){{
  delete selected[id];
  updateBadge(); updateSelList();
  document.querySelectorAll('.item-id').forEach(el=>{{
    if(el.textContent===id){{
      const row = el.closest('.item-row');
      row.classList.remove('checked');
      const cb = row.querySelector('input[type=checkbox]');
      if(cb) cb.checked = false;
    }}
  }});
}}

function generate(){{
  const keys = Object.keys(selected);
  if(!keys.length){{ document.getElementById('output').value='// No items selected.'; return; }}
  const lines = keys.map(id=>{{
    const s = selected[id];
    if(s.qty===null) return s.cmd;
    const m = s.cmd.match(/^Game\\.AddToInventory\\("([^"]+)",/);
    return m ? `Game.AddToInventory("${{m[1]}}", ${{s.selectedQty}})` : s.cmd;
  }});
  document.getElementById('output').value = lines.join('\\n');
  document.getElementById('cmdCount').textContent = lines.length+' command'+(lines.length!==1?'s':'')+' ready';
}}

function copyOut(){{
  const v = document.getElementById('output').value;
  if(!v||v.startsWith('//')) return;
  navigator.clipboard.writeText(v).then(()=>{{
    const btn = document.getElementById('copyBtn');
    btn.textContent = 'Copied!';
    setTimeout(()=>btn.textContent='Copy all', 2000);
  }});
}}

function clearOut(){{
  document.getElementById('output').value='';
  document.getElementById('cmdCount').textContent='0 commands ready';
}}

function onSearch(){{
  const q = document.getElementById('search').value.toLowerCase().trim();
  if(!q){{ buildLeft(); return; }}
  const left = document.getElementById('left');
  left.innerHTML = '';
  let total = 0;
  SECTIONS.forEach((sec,si)=>{{
    const matched = sec.items.filter(item=>
      (item.desc||'').toLowerCase().includes(q)||
      (item.id||'').toLowerCase().includes(q)||
      (item.sub||'').toLowerCase().includes(q)
    );
    if(!matched.length) return;
    total += matched.length;
    const block = document.createElement('div');
    block.className = 'section-block';
    const head = document.createElement('div');
    head.className = 'section-head';
    head.innerHTML = `<span class="section-arrow open">&#9658;</span>
      <span class="section-title">${{sec.name}}</span>
      <span class="section-count">${{matched.length}} match${{matched.length!==1?'es':''}}</span>`;
    const body = document.createElement('div');
    body.className = 'section-items open';
    renderItems(body, matched);
    block.appendChild(head);
    block.appendChild(body);
    left.appendChild(block);
  }});
  if(!total) left.innerHTML='<div class="no-match" style="margin-top:60px">No items match &ldquo;'+q+'&rdquo;</div>';
}}

buildLeft();
</script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Built {output_path}")


if __name__ == '__main__':
    print("Parsing data/commands.txt ...")
    sections = parse_commands(DATA_FILE)
    total = sum(len(s['items']) for s in sections)
    print(f"  {len(sections)} sections, {total} items found")
    for s in sections:
        print(f"    [{len(s['items']):3d}] {s['name']}")
    print("Generating index.html ...")
    build_html(sections, OUTPUT_FILE)
    print("Done.")
