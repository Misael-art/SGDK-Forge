import json

try:
    with open('F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/out/logs/visual_aesthetic_report.json', 'r') as f:
        r = json.load(f)
        
    print("ASSETS IN NEEDS_REVIEW:")
    for a in r.get('assets', []):
        if a.get('status') == 'needs_review':
            issues = [i.get('code') for i in a.get('issues', [])]
            print(f"- {a.get('resource_name')} (Issues: {', '.join(issues)})")
except Exception as e:
    print("Error:", e)
