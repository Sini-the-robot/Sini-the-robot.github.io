import requests
import json
import random
import time
import os
from datetime import datetime
from urllib.parse import quote

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
UPDATE_HOURS = 6

CITIES = [
    {"name": "Tokyo", "lat": 35.68, "lon": 139.69, "country": "Japan"},
    {"name": "Tehran", "lat": 35.69, "lon": 51.39, "country": "Iran"},
    {"name": "Amsterdam", "lat": 52.37, "lon": 4.90, "country": "Netherlands"},
    {"name": "Nairobi", "lat": -1.29, "lon": 36.82, "country": "Kenya"},
    {"name": "Buenos Aires", "lat": -34.60, "lon": -58.38, "country": "Argentina"},
    {"name": "Mumbai", "lat": 19.08, "lon": 72.88, "country": "India"},
    {"name": "Oslo", "lat": 59.91, "lon": 10.75, "country": "Norway"},
    {"name": "Cape Town", "lat": -33.93, "lon": 18.42, "country": "South Africa"},
    {"name": "Mexico City", "lat": 19.43, "lon": -99.13, "country": "Mexico"},
    {"name": "Bangkok", "lat": 13.75, "lon": 100.52, "country": "Thailand"},
    {"name": "Istanbul", "lat": 41.01, "lon": 28.95, "country": "Turkey"},
    {"name": "Sydney", "lat": -33.87, "lon": 151.21, "country": "Australia"},
    {"name": "Cairo", "lat": 30.04, "lon": 31.24, "country": "Egypt"},
    {"name": "Vancouver", "lat": 49.25, "lon": -123.12, "country": "Canada"},
    {"name": "Lisbon", "lat": 38.72, "lon": -9.14, "country": "Portugal"},
    {"name": "Kyoto", "lat": 35.01, "lon": 135.77, "country": "Japan"},
    {"name": "Bogota", "lat": 4.71, "lon": -74.07, "country": "Colombia"},
    {"name": "Helsinki", "lat": 60.17, "lon": 24.94, "country": "Finland"},
    {"name": "Marrakech", "lat": 31.63, "lon": -7.99, "country": "Morocco"},
    {"name": "Tbilisi", "lat": 41.69, "lon": 44.83, "country": "Georgia"},
    {"name": "Reykjavik", "lat": 64.13, "lon": -21.94, "country": "Iceland"},
    {"name": "Chengdu", "lat": 30.57, "lon": 104.07, "country": "China"},
    {"name": "Accra", "lat": 5.56, "lon": -0.20, "country": "Ghana"},
    {"name": "Lima", "lat": -12.05, "lon": -77.04, "country": "Peru"},
    {"name": "Vienna", "lat": 48.21, "lon": 16.37, "country": "Austria"},
    {"name": "Lahore", "lat": 31.55, "lon": 74.34, "country": "Pakistan"},
    {"name": "Addis Ababa", "lat": 9.03, "lon": 38.74, "country": "Ethiopia"},
    {"name": "Prague", "lat": 50.08, "lon": 14.44, "country": "Czech Republic"},
    {"name": "Hanoi", "lat": 21.03, "lon": 105.85, "country": "Vietnam"},
    {"name": "Auckland", "lat": -36.86, "lon": 174.76, "country": "New Zealand"},
]

def get_season(month, lat):
    if lat >= 0:
        if 3 <= month <= 5: return "Spring"
        if 6 <= month <= 8: return "Summer"
        if 9 <= month <= 11: return "Autumn"
        return "Winter"
    else:
        if 3 <= month <= 5: return "Autumn"
        if 6 <= month <= 8: return "Winter"
        if 9 <= month <= 11: return "Spring"
        return "Summer"

def weather_code_to_text(code):
    if code == 0: return "Clear sky"
    if code <= 3: return "Partly cloudy"
    if code <= 48: return "Foggy"
    if code <= 67: return "Rainy"
    if code <= 77: return "Snowy"
    if code <= 82: return "Showers"
    if code >= 95: return "Stormy"
    return "Cloudy"

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=auto"
    r = requests.get(url, timeout=10)
    d = r.json()
    return {
        "temp": round(d["current"]["temperature_2m"]),
        "humidity": d["current"]["relative_humidity_2m"],
        "condition": weather_code_to_text(d["current"]["weather_code"])
    }

def get_plant(city, country, lat, temp, humidity, condition, season):
    prompt = f"""You are a botanist. Choose ONE native or naturalized plant species currently active in this location.

Location: {city}, {country} (lat: {lat:.1f})
Season: {season}
Temperature: {temp}°C
Humidity: {humidity}%
Weather: {condition}

Respond ONLY with valid JSON, no markdown, no extra text:
{{
  "latin": "Genus species",
  "common": "Common name",
  "note": "One elegant sentence max 16 words describing what this plant is doing right now, poetic-scientific tone",
  "phenology": "Current stage (Flowering / Dormant / Fruiting / Budding / Seeding)",
  "compound_name": "Name of the key chemical compound (e.g. Thymol, Curcumin, Caffeine)",
  "compound": "One sentence max 12 words: what makes this compound rare or powerful",
  "image_prompt": "Fine botanical illustration of [plant name], traditional ukiyo-e woodblock print style, natural botanical colors, precise ink outlines, ivory paper texture, full plant with stem leaves and flowers, botanically accurate, soft watercolor wash, no text, no labels, museum quality print"
}}"""

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.8
        },
        timeout=20
    )
    raw = r.json()["choices"][0]["message"]["content"]
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

def get_image_url(image_prompt):
    encoded = quote(image_prompt)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=800&seed={seed}&nologo=true"
def get_image_url(image_prompt):
    encoded = quote(image_prompt)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=920&seed={seed}&nologo=true"

import base64 as _b64

def get_watermark_url():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.svg")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64 = _b64.b64encode(f.read()).decode()
        return f"data:image/svg+xml;base64,{b64}"
    fallback = _b64.b64encode(b"<svg xmlns='http://www.w3.org/2000/svg' width='120' height='28' viewBox='0 0 120 28'><text x='8' y='18' font-family='Georgia,serif' font-style='italic' font-size='14' fill='rgba(242,236,224,0.7)'>Florae</text><text x='8' y='27' font-family='monospace' font-size='7' fill='rgba(138,171,122,0.5)' letter-spacing='2'>FLORAE.IO</text></svg>").decode()
    return f"data:image/svg+xml;base64,{fallback}"

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230e0e0c'/%3E%3Cpath d='M16 28 C16 28 16 14 16 11 C16 4 22 2 26 5 C26 5 20 9 19 15' fill='%235a9a6a'/%3E%3Cpath d='M16 20 C16 20 12 15 8 15 C4 15 4 20 7 23 C10 26 16 22 16 20' fill='%232d5a3d'/%3E%3C/svg%3E"

def build_html(city, country, weather, season, plant, image_url, updated_at):
    refresh_seconds = UPDATE_HOURS * 3600
    compound = plant.get('compound', plant.get('trait', plant.get('fact', '')))
    wm_url = get_watermark_url()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="{refresh_seconds}">
<title>Florae · {city}</title>
<link rel="icon" href="{FAVICON}">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
<style>
  *{{ margin:0; padding:0; box-sizing:border-box; }}
  html,body{{ width:100%; background:#0e0e0c; font-family:'DM Serif Display',Georgia,serif; }}

  /* TOP BAR */
  .topbar{{
    position:sticky; top:0; z-index:50;
    display:flex; justify-content:space-between; align-items:center;
    padding:0 1.5rem; height:46px;
    background:#0e0e0c;
    border-bottom:1px solid rgba(255,255,255,0.05);
  }}
  .topbar-left{{ display:flex; align-items:center; gap:0.6rem; }}
  .live-dot{{
    width:6px; height:6px; border-radius:50%; background:#5a9a6a;
    animation:pulse 2.5s ease-in-out infinite;
  }}
  @keyframes pulse{{
    0%,100%{{ opacity:1; box-shadow:0 0 0 0 rgba(90,154,106,0.5); }}
    50%     {{ opacity:0.5; box-shadow:0 0 0 5px rgba(90,154,106,0); }}
  }}
  .brand{{ font-family:'DM Mono',monospace; font-size:0.55rem; letter-spacing:0.22em; text-transform:uppercase; color:rgba(255,255,255,0.28); }}
  .clock{{ font-family:'DM Mono',monospace; font-size:1.3rem; font-weight:300; color:rgba(255,255,255,0.65); letter-spacing:0.08em; font-variant-numeric:tabular-nums; }}
  .topbar-right{{ display:flex; align-items:center; gap:0.7rem; }}
  .date-txt{{ font-family:'DM Mono',monospace; font-size:0.5rem; letter-spacing:0.12em; color:rgba(255,255,255,0.18); text-transform:uppercase; }}
  .icon-btn{{
    background:none; border:1px solid rgba(255,255,255,0.1); color:rgba(255,255,255,0.35);
    width:28px; height:28px; border-radius:4px; cursor:pointer; font-size:0.8rem;
    display:flex; align-items:center; justify-content:center; transition:all 0.2s;
  }}
  .icon-btn:hover{{ border-color:rgba(90,154,106,0.5); color:#5a9a6a; }}

  /* MAIN CARD — centered, max width */
  .card{{
    max-width:540px;
    margin:0 auto;
    padding:0.5rem 0 1rem;
  }}

  /* IMAGE */
  .image-zone{{
    position:relative;
    border-radius:4px;
    margin:0 1rem;
    padding:3px;
    background:linear-gradient(90deg,#2d5a3d,#8aab7a,#c8a96e,#5a9a6a,#2d5a3d);
    background-size:400% 100%;
    animation:borderShimmer 6s linear infinite;
  }}
  @keyframes borderShimmer{{
    0%{{background-position:0% 0;}}
    100%{{background-position:400% 0;}}
  }}
  .image-zone .img-inner{{
    position:relative;
    overflow:hidden;
    background:#111110;
    border-radius:2px;
    height:100%;
  }}
  .image-zone img.main-img{{
    width:100%;
    display:block;
    animation:fadeImg 1.2s ease forwards;
  }}
  @keyframes fadeImg{{ from{{opacity:0;}} to{{opacity:1;}} }}

  .img-overlay{{
    position:absolute; inset:0;
    background:linear-gradient(to bottom, transparent 65%, rgba(14,14,12,0.2) 100%);
    pointer-events:none;
  }}
  .image-badge{{
    position:absolute; top:0.7rem; left:0.7rem;
    background:rgba(14,14,12,0.55); backdrop-filter:blur(6px);
    border:1px solid rgba(255,255,255,0.07);
    padding:0.25rem 0.65rem;
    font-family:'DM Mono',monospace; font-size:0.44rem; letter-spacing:0.16em;
    text-transform:uppercase; color:rgba(255,255,255,0.5);
  }}
  .watermark{{
    position:absolute; bottom:0.7rem; right:0.7rem;
    height:34px; width:auto; opacity:0.55;
    pointer-events:none;
    filter:drop-shadow(0 1px 4px rgba(0,0,0,0.8));
    z-index:5;
  }}
  .image-loading{{
    position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
    flex-direction:column; gap:1rem; background:#111110; z-index:3;
    min-height:300px;
  }}
  .leaf-anim{{ opacity:0.2; animation:leafFloat 3s ease-in-out infinite; }}
  @keyframes leafFloat{{ 0%,100%{{transform:translateY(0) rotate(0deg);}} 50%{{transform:translateY(-7px) rotate(4deg);}} }}
  .loading-txt{{ font-family:'DM Mono',monospace; font-size:0.5rem; letter-spacing:0.2em; color:rgba(255,255,255,0.2); text-transform:uppercase; }}

  /* SHIMMER LINE */


  /* INFO */
  .info{{
    background:#131310;
    margin:0 1rem;
    padding:1rem 1.4rem 1rem;
    border-radius:0 0 3px 3px;
  }}

  /* weather row */
  .weather-row{{
    display:grid; grid-template-columns:repeat(4,1fr);
    gap:0.3rem; margin-bottom:1rem;
    padding-bottom:1rem;
    border-bottom:1px solid rgba(255,255,255,0.05);
  }}
  .w-item{{ display:flex; flex-direction:column; gap:0.1rem; }}
  .w-label{{ font-family:'DM Mono',monospace; font-size:0.38rem; letter-spacing:0.12em; text-transform:uppercase; color:rgba(255,255,255,0.2); }}
  .w-value{{ font-family:'DM Mono',monospace; font-size:0.92rem; color:rgba(242,236,224,0.85); font-variant-numeric:tabular-nums; }}
  .w-value.sm{{ font-size:0.7rem; }}

  /* plant name */
  .plant-latin{{ font-size:1.75rem; font-style:italic; line-height:1.1; color:rgba(242,236,224,0.95); margin-bottom:0.3rem; animation:slideUp 0.7s ease forwards; }}
  .plant-common{{ font-family:'DM Mono',monospace; font-size:0.44rem; letter-spacing:0.22em; text-transform:uppercase; color:#5a9a6a; margin-bottom:0.7rem; animation:slideUp 0.85s ease forwards; }}
  @keyframes slideUp{{ from{{opacity:0;transform:translateY(5px);}} to{{opacity:1;transform:translateY(0);}} }}

  .divider{{ width:24px; height:1px; background:rgba(255,255,255,0.1); margin-bottom:1rem; }}

  .plant-note{{ font-size:0.88rem; font-style:italic; line-height:1.65; color:rgba(242,236,224,0.4); margin-bottom:1rem; animation:slideUp 1s ease forwards; }}

  /* compound */
  .compound-label{{ font-family:'DM Mono',monospace; font-size:0.38rem; letter-spacing:0.2em; text-transform:uppercase; color:rgba(255,255,255,0.18); margin-bottom:0.4rem; }}
  .compound-name{{ font-size:1.1rem; font-style:italic; color:rgba(242,236,224,0.75); margin-bottom:0.3rem; }}
  .compound-desc{{ font-family:'DM Mono',monospace; font-size:0.58rem; line-height:1.55; color:rgba(242,236,224,0.28); margin-bottom:0.9rem; }}

  /* footer */
  .footer-row{{ display:flex; align-items:center; gap:0.6rem; }}
  .phenology-tag{{
    font-family:'DM Mono',monospace; font-size:0.38rem; letter-spacing:0.14em;
    text-transform:uppercase; color:#5a9a6a;
    border:1px solid rgba(90,154,106,0.3); padding:0.2rem 0.55rem;
    background:rgba(90,154,106,0.05);
  }}
  .updated-tag{{ font-family:'DM Mono',monospace; font-size:0.36rem; color:rgba(255,255,255,0.15); margin-left:auto; }}

  /* FULLSCREEN */
  .fs-overlay{{
    display:none; position:fixed; inset:0; background:#0a0a08; z-index:100;
    align-items:center; justify-content:center;
  }}
  .fs-overlay.active{{ display:flex; }}
  .fs-img-wrap{{
    position:relative; max-width:100vw; max-height:100vh;
    display:flex; align-items:center; justify-content:center;
  }}
  .fs-overlay img.fs-main{{ max-width:100vw; max-height:100vh; object-fit:contain; display:block; }}
  .fs-watermark{{
    position:absolute; bottom:0.8rem; right:0.8rem;
    height:34px; width:auto; opacity:0.5;
    pointer-events:none;
    filter:drop-shadow(0 1px 4px rgba(0,0,0,0.8));
    z-index:5;
  }}
  .fs-close{{
    position:fixed; top:1rem; right:1rem;
    background:rgba(14,14,12,0.7); color:rgba(255,255,255,0.6);
    border:1px solid rgba(255,255,255,0.12); width:34px; height:34px;
    border-radius:4px; cursor:pointer; font-size:0.9rem;
    display:flex; align-items:center; justify-content:center; z-index:101;
  }}
  .fs-info{{
    position:fixed; bottom:1.5rem; left:50%; transform:translateX(-50%);
    background:rgba(14,14,12,0.7); backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,0.08);
    padding:0.45rem 1.2rem; text-align:center; white-space:nowrap; z-index:101;
  }}
  .fs-latin{{ font-style:italic; font-size:1rem; color:rgba(242,236,224,0.9); }}
  .fs-city{{ font-family:'DM Mono',monospace; font-size:0.44rem; letter-spacing:0.18em; text-transform:uppercase; color:#5a9a6a; margin-top:0.15rem; }}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-left">
    <div class="live-dot"></div>
    <span class="brand">Florae</span>
  </div>
  <div class="clock" id="clock">00:00:00</div>
  <div class="topbar-right">
    <span class="date-txt">{datetime.now().strftime('%d %b %Y')}</span>
    <button class="icon-btn" onclick="openFS()" title="Fullscreen [F]">⛶</button>
    <button class="icon-btn" id="shareBtn" onclick="shareIt()" title="Share">↗</button>
  </div>
</div>

<div class="card">

  <div class="image-zone">
    <div class="img-inner">
    <div class="image-loading" id="loader">
      <svg class="leaf-anim" width="44" height="44" viewBox="0 0 48 48" fill="none" stroke="#5a9a6a" stroke-width="1.2">
        <path d="M24 44 C24 44 24 18 24 13 C24 4 35 1 42 7 C42 7 31 13 28 23"/>
        <path d="M24 30 C24 30 17 23 10 23 C3 23 2 31 8 36 C14 41 24 36 24 30"/>
        <line x1="24" y1="44" x2="24" y2="37"/>
      </svg>
      <span class="loading-txt">Painting the season</span>
    </div>
    <img class="main-img" src="{image_url}" alt="{plant['common']}"
      onload="document.getElementById('loader').style.display='none'"
      onerror="document.getElementById('loader').style.display='none'"/>
    <div class="img-overlay"></div>
    <div class="image-badge">{city} · {country}</div>
    <img class="watermark" src="{wm_url}" alt="Florae"/>
    </div>
  </div>

  <div class="info">
    <div class="weather-row">
      <div class="w-item"><span class="w-label">Temp</span><span class="w-value">{weather['temp']}°C</span></div>
      <div class="w-item"><span class="w-label">Humidity</span><span class="w-value">{weather['humidity']}%</span></div>
      <div class="w-item"><span class="w-label">Sky</span><span class="w-value sm">{weather['condition']}</span></div>
      <div class="w-item"><span class="w-label">Season</span><span class="w-value sm">{season}</span></div>
    </div>

    <div class="plant-latin">{plant['latin']}</div>
    <div class="plant-common">{plant['common'].upper()}</div>
    <div class="divider"></div>
    <div class="plant-note">{plant['note']}</div>

    <div class="compound-label">Key compound</div>
    <div class="compound-name">{plant.get('compound_name', '')}</div>
    <div class="compound-desc">{compound}</div>

    <div class="footer-row">
      <div class="phenology-tag">{plant['phenology']}</div>
      <span class="updated-tag">{updated_at}</span>
    </div>
  </div>

</div>

<!-- FULLSCREEN -->
<div class="fs-overlay" id="fsOverlay">
  <button class="fs-close" onclick="closeFS()">✕</button>
  <div class="fs-img-wrap">
    <img class="fs-main" src="{image_url}" alt="{plant['common']}"/>
    <img class="fs-watermark" src="{wm_url}" alt="Florae"/>
  </div>
  <div class="fs-info">
    <div class="fs-latin">{plant['latin']}</div>
    <div class="fs-city">{city} · {country} · {season}</div>
  </div>
</div>

<script>
function tick(){{
  const n=new Date(), p=x=>String(x).padStart(2,'0');
  document.getElementById('clock').textContent=p(n.getHours())+':'+p(n.getMinutes())+':'+p(n.getSeconds());
}}
tick(); setInterval(tick,1000);
function openFS(){{ document.getElementById('fsOverlay').classList.add('active'); }}
function closeFS(){{ document.getElementById('fsOverlay').classList.remove('active'); }}
document.getElementById('fsOverlay').addEventListener('click',function(e){{ if(e.target===this) closeFS(); }});
document.addEventListener('keydown',function(e){{ if(e.key==='Escape') closeFS(); if(e.key==='f'||e.key==='F') openFS(); }});
function shareIt(){{
  const btn=document.getElementById('shareBtn');
  if(navigator.share){{ navigator.share({{title:'Florae · {plant["latin"]}',url:window.location.href}}); }}
  else{{ navigator.clipboard.writeText(window.location.href).then(()=>{{
    btn.textContent='✓'; btn.style.color='#5a9a6a';
    setTimeout(()=>{{btn.textContent='↗';btn.style.color='';}},2000);
  }}); }}
}}
</script>
</body>
</html>"""

def run():
    city_data = random.choice(CITIES)
    city, country = city_data["name"], city_data["country"]
    lat, lon = city_data["lat"], city_data["lon"]
    print(f"[{datetime.now().strftime('%H:%M')}] {city}, {country}")
    try:
        weather = get_weather(lat, lon)
        print(f"  Weather : {weather['temp']}°C, {weather['condition']}")
        month = datetime.now().month
        season = get_season(month, lat)
        plant = get_plant(city, country, lat, weather["temp"], weather["humidity"], weather["condition"], season)
        print(f"  Plant   : {plant['latin']} ({plant['common']})")
        print(f"  Compound: {plant.get('compound_name','—')} — {plant.get('compound','—')}")
        image_url = get_image_url(plant.get("image_prompt", f"beautiful botanical illustration of {plant['latin']}, japanese woodblock ukiyo-e style"))
        print(f"  Image   : generating...")
        updated_at = datetime.now().strftime("%H:%M")
        html = build_html(city, country, weather, season, plant, image_url, updated_at)
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "florae.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Saved   : index.html")
    except Exception as e:
        print(f"  Error   : {e}\n"); return
    try:
        os.system('git add index.html')
        os.system(f'git commit -m "florae: {city}"')
        os.system('git push')
        print(f"  GitHub  : pushed\n")
    except Exception as e:
        print(f"  GitHub  : failed — {e}\n")

if __name__ == "__main__":
    UPDATE_HOURS = 2
    print("="*40+"\n  Florae\n"+"="*40+"\n")
    run()
