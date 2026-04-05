import re
import urllib.request
import urllib.error
import socket
import ssl
from seed import OPPORTUNITIES

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=context, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return f"URL Error: {e.reason}"
    except Exception as e:
        return f"Error: {e}"

urls = set()
for opp in OPPORTUNITIES:
    if opp.get('source_url'): urls.add(opp['source_url'])
    if opp.get('apply_url'): urls.add(opp['apply_url'])

results = []
for url in sorted(urls):
    status = check_url(url)
    results.append((url, status))

for url, status in results:
    if str(status) != '200' and 'HTTP 403' not in str(status):
        print(f"FAILED: {url} - {status}")
