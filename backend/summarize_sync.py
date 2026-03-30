import json

with open('sync_result.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=" * 50)
print("NAVIAID API SYNC RESULTS")
print("=" * 50)
print(f"Total new items synced: {d.get('total_synced', 0)}")
print(f"Timestamp: {d.get('timestamp', 'N/A')}")
print()

for src, info in d.get('sources', {}).items():
    synced = info.get('synced', 0)
    errors = info.get('errors', [])
    print(f"  [{src.upper():12s}]  synced={synced}  errors={len(errors)}")
    for e in errors[:3]:
        print(f"               - {e[:100]}")

print()
top_errors = d.get('errors', [])
if top_errors:
    print(f"All combined errors ({len(top_errors)}):")
    for e in top_errors[:10]:
        print(f"  - {e[:120]}")
else:
    print("No combined errors.")
print("=" * 50)
