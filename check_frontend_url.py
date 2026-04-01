import urllib.request, re

try:
    html = urllib.request.urlopen("https://naviaid.onrender.com/").read().decode()
    js_files = re.findall(r'src="(.*?\.js)"', html)
    print("JS files:", js_files)
    for js in js_files:
        url = js if js.startswith('http') else 'https://naviaid.onrender.com' + js
        content = urllib.request.urlopen(url).read().decode()
        urls = re.findall(r'https://[a-zA-Z0-9-]+\.onrender\.com', content)
        if urls:
            print(f"Found Render URL in {js}:", set(urls))
        if 'localhost:8000' in content:
            print(f"Found localhost in {js}")
except Exception as e:
    print("Error:", e)
