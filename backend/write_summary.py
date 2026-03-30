import json

with open('sync_result.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

with open('sync_summary.txt', 'w', encoding='ascii', errors='replace') as out:
    out.write("NAVIAID API SYNC RESULTS\n")
    out.write("=" * 50 + "\n")
    out.write(f"Total new items synced: {d.get('total_synced', 0)}\n")
    out.write(f"Timestamp: {d.get('timestamp', 'N/A')}\n\n")
    for src, info in d.get('sources', {}).items():
        synced = info.get('synced', 0)
        errors = info.get('errors', [])
        out.write(f"  [{src.upper():12s}]  synced={synced}  errors={len(errors)}\n")
        for e in errors[:5]:
            out.write(f"               - {str(e)[:120]}\n")
    out.write("\n")
    top_errors = d.get('errors', [])
    if top_errors:
        out.write(f"Combined errors ({len(top_errors)}):\n")
        for e in top_errors[:15]:
            out.write(f"  - {str(e)[:120]}\n")
    else:
        out.write("No combined errors.\n")
