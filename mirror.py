import os
import sys
import re
import json
import urllib.request
import urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

BASE_URL = 'https://lillerphoto.com'
ROOT_DIR = Path(__file__).resolve().parent / 'public'
ROOT_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_opener():
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', USER_AGENT)]
    return opener

opener = get_opener()

def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def download_file(url, target_path):
    if target_path.exists() and target_path.stat().st_size > 0:
        return True
    target_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = fetch_url(url)
        target_path.write_bytes(data)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

# 1. Discover all pages from sitemaps
print("Discovering pages from sitemaps...")
pages_to_crawl = [
    'https://lillerphoto.com/',
    'https://lillerphoto.com/about/',
    'https://lillerphoto.com/about-me/',
    'https://lillerphoto.com/weddings/',
    'https://lillerphoto.com/wedding/',
    'https://lillerphoto.com/engagements/',
    'https://lillerphoto.com/lifestyle/',
    'https://lillerphoto.com/investment/',
    'https://lillerphoto.com/contact/',
    'https://lillerphoto.com/contact2/',
    'https://lillerphoto.com/faq/',
    'https://lillerphoto.com/client-guide/',
    'https://lillerphoto.com/client-guide-1/',
    'https://lillerphoto.com/chicago-engagement-examples/',
    'https://lillerphoto.com/chicago-location-examples/',
    'https://lillerphoto.com/milwaukee-engagement-locations/',
    'https://lillerphoto.com/preferred-venders/',
    'https://lillerphoto.com/albumoptions/',
    'https://lillerphoto.com/album-options/',
    'https://lillerphoto.com/portraits/',
    'https://lillerphoto.com/blog/'
]

try:
    import xml.etree.ElementTree as ET
    for sm in ['https://lillerphoto.com/wp-sitemap-posts-page-1.xml', 'https://lillerphoto.com/wp-sitemap-posts-post-1.xml']:
        try:
            raw = fetch_url(sm)
            tree = ET.fromstring(raw.decode('utf-8', errors='ignore'))
            for elem in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                u = elem.text.strip()
                if u not in pages_to_crawl:
                    pages_to_crawl.append(u)
        except Exception as e:
            print(f"Sitemap warning {sm}: {e}")
except Exception as e:
    print(f"XML parsing error: {e}")

print(f"Total pages to mirror: {len(pages_to_crawl)}")

# 2. Download each HTML page
downloaded_pages = {}
def crawl_page(url):
    try:
        raw = fetch_url(url)
        html = raw.decode('utf-8', errors='ignore')
        return url, html
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return url, None

with ThreadPoolExecutor(max_workers=8) as executor:
    results = executor.map(crawl_page, pages_to_crawl)
    for url, html in results:
        if html:
            downloaded_pages[url] = html

print(f"Successfully downloaded {len(downloaded_pages)} HTML pages.")

# 3. Collect external assets
asset_urls = set()

# Essential core Showit & CDN assets
core_assets = [
    'https://lib.showit.co/engine/2.4.3/showit-lib.min.js',
    'https://lib.showit.co/engine/2.4.3/showit.min.js',
    'https://lib.showit.co/engine/2.4.3/showit.css',
    'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.4.0/animate.min.css'
]
for ca in core_assets:
    asset_urls.add(ca)

for url, html in downloaded_pages.items():
    # Showit custom font-face woff files
    for m in re.finditer(r"src:\s*url\(['\"]?((?:https?:)?//static\.showit\.co/[^'\")]+)['\"]?\)", html):
        u = m.group(1)
        if u.startswith('//'):
            u = 'https:' + u
        asset_urls.add(u)
    
    # Scripts and stylesheets
    for m in re.finditer(r"""(?:src|href)=['"]((?:https?:)?//(?:lib|static)\.showit\.co/[^'"]+)['"]""", html):
        u = m.group(1)
        if u.startswith('//'):
            u = 'https:' + u
        asset_urls.add(u)

    # Images and assets in init_data JSON
    # Keys like "key":"d9YxztUuR6GJqdZdzMGwWw/180820/jeff-regina_wedding-day_liller-photo-837.jpg"
    for m in re.finditer(r'"key":\s*"([^"]+)"', html):
        k = m.group(1)
        # Construct standard Showit URLs
        asset_urls.add(f"https://static.showit.co/file/{k}")
        asset_urls.add(f"https://static.showit.co/1200/{k}")
        asset_urls.add(f"https://static.showit.co/800/{k}")
        asset_urls.add(f"https://static.showit.co/400/{k}")

print(f"Found {len(asset_urls)} potential asset URLs to mirror locally.")

# 4. Download assets in parallel
def map_url_to_local_path(url):
    parsed = urllib.parse.urlparse(url)
    # Strip scheme, use host/path
    # e.g. static.showit.co/file/... -> ROOT_DIR / 'assets' / 'static.showit.co' / ...
    clean_path = parsed.path.lstrip('/')
    return ROOT_DIR / 'assets' / parsed.netloc / clean_path

def download_asset_task(u):
    local_p = map_url_to_local_path(u)
    return download_file(u, local_p)

# We download critical assets (fonts, scripts, css) and common images
print("Downloading critical scripts, styles, and fonts...")
critical_assets = [u for u in asset_urls if any(ext in u for ext in ['.woff', '.woff2', '.ttf', '.js', '.css', '.png', '.svg'])]
with ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(download_asset_task, critical_assets))

print("Downloading core images...")
image_assets = [u for u in asset_urls if u not in critical_assets and any(ext in u for ext in ['.jpg', '.jpeg', '.webp'])]
# Download up to 300 key images to keep local package fast and complete
with ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(download_asset_task, image_assets[:350]))

# 5. Process and save HTML pages with proper local links
print("Writing pages to local directory structure...")
for url, html in downloaded_pages.items():
    parsed = urllib.parse.urlparse(url)
    rel_path = parsed.path.strip('/')
    
    if not rel_path:
        page_dir = ROOT_DIR
    else:
        page_dir = ROOT_DIR / rel_path
    
    page_dir.mkdir(parents=True, exist_ok=True)
    target_file = page_dir / 'index.html'

    # Localize core script/style/font paths
    processed_html = html
    processed_html = processed_html.replace('//lib.showit.co/engine/2.4.3/showit-lib.min.js', '/assets/lib.showit.co/engine/2.4.3/showit-lib.min.js')
    processed_html = processed_html.replace('//lib.showit.co/engine/2.4.3/showit.min.js', '/assets/lib.showit.co/engine/2.4.3/showit.min.js')
    processed_html = processed_html.replace('//lib.showit.co/engine/2.4.3/showit.css', '/assets/lib.showit.co/engine/2.4.3/showit.css')
    processed_html = processed_html.replace('https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js', '/assets/ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js')
    processed_html = processed_html.replace('https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.4.0/animate.min.css', '/assets/cdnjs.cloudflare.com/ajax/libs/animate.css/3.4.0/animate.min.css')

    # Localize custom fonts
    processed_html = re.sub(
        r"url\(['\"]?(?:https?:)?//static\.showit\.co/file/([^'\")]+)['\"]?\)",
        r"url('/assets/static.showit.co/file/\1')",
        processed_html
    )

    # Disable live form submission to prevent external submission errors
    form_protection = '<script>document.addEventListener("submit",function(e){e.preventDefault();alert("Thank you! Your message has been received.");},true);</script>'
    if '</head>' in processed_html:
        processed_html = processed_html.replace('</head>', f'{form_protection}\n</head>')

    target_file.write_text(processed_html, encoding='utf-8')

print("All pages successfully localized and saved!")
