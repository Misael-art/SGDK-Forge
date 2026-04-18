import json

try:
    with open('F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/out/logs/visual_aesthetic_report.json', 'r') as f:
        r = json.load(f)
        
    print("ASSETS ISSUES:")
    for a in r.get('assets', []):
        issues = a.get('issues', [])
        if issues:
            print(f"- {a.get('resource_name')}: {len(issues)} issues")
            for i in issues:
                print(f"  * {i.get('code')}: {i.get('message')}")
except Exception as e:
    print("Error:", e)
