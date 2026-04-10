import os
import subprocess
import time

# List of projects to test (High complexity and representative archetypes)
PROJECTS_TO_TEST = [
    "Mortal Kombat Plus [VER.001] [SGDK 211] [GEN] [ENGINE] [LUTA]",
    "NEXZR MD [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]",
    "BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA]",
    "PlatformerEngine [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]",
    "MegaDriving [VER.1.0] [SGDK 211] [GEN] [ENGINE] [CORRIDA]",
    "RaycastingEngine [VER.1.0] [SGDK 211] [GEN] [ENGINE] [3D]",
    "HAMOOPIG [VER.1.0] [SGDK 211] [GEN] [ENGINE] [LUTA]",
    "Shadow Dancer Hamoopig [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]",
    "SimpleGameStates_Elite" # Our Golden Template
]

BASE_DIR = r"F:\Projects\MegaDrive_DEV"
ENGINES_DIR = os.path.join(BASE_DIR, "SGDK_Engines")
TEMPLATES_DIR = os.path.join(BASE_DIR, "SGDK_templates")

RESULTS = []

def test_project(name, path):
    print(f"\n[TEST] Starting: {name}")
    start_time = time.time()
    
    # Check if build.bat exist
    build_bat = os.path.join(path, "build.bat")
    clean_bat = os.path.join(path, "clean.bat")
    
    if not os.path.exists(build_bat):
        return {"name": name, "status": "SKIPPED", "error": "No build.bat found"}

    try:
        # Clean
        if os.path.exists(clean_bat):
            subprocess.run(["cmd", "/c", "clean.bat"], cwd=path, capture_output=True)
            
        # Build
        proc = subprocess.run(["cmd", "/c", "build.bat"], cwd=path, capture_output=True, text=True, errors="replace")
        
        # Check ROM
        rom_path = os.path.join(path, "out", "rom.bin")
        rom_exists = os.path.exists(rom_path)
        rom_size = os.path.getsize(rom_path) if rom_exists else 0
        
        elapsed = time.time() - start_time
        
        status = "SUCCESS" if (rom_exists and proc.returncode == 0) else "FAILED"
        
        # Capture error snippet if failed
        error_msg = ""
        if status == "FAILED":
            # Check build_output.log for more details
            log_path = os.path.join(path, "out", "logs", "build_output.log")
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        error_msg = f.read()[-1000:] # Last 1000 chars
                except:
                    error_msg = "Could not read log file"
            else:
                error_msg = proc.stderr[-1000:] if proc.stderr else "Return code != 0, no output logged"

        return {
            "name": name,
            "status": status,
            "rom_exists": rom_exists,
            "rom_size": rom_size,
            "time": f"{elapsed:.2f}s",
            "error": error_msg
        }
    except Exception as e:
        return {"name": name, "status": "ERROR", "error": str(e)}

# Main execution
for p_name in PROJECTS_TO_TEST:
    p_path = os.path.join(ENGINES_DIR, p_name)
    if not os.path.exists(p_path):
        p_path = os.path.join(TEMPLATES_DIR, p_name)
    
    if os.path.exists(p_path):
        res = test_project(p_name, p_path)
        RESULTS.append(res)
        print(f"[{res['status']}] {p_name} ({res.get('time', 'N/A')})")
    else:
        print(f"[NOT FOUND] {p_name}")

# Generate Markdown Report
report_path = r"C:\Users\misae\.gemini\antigravity\brain\fc7188d8-f8d4-4bf4-9225-7a2c85b0d2b4\resilience_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# Elite Infrastructure Resilience Report\n\n")
    f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Toolchain:** Persistent Golden Makefile Standard\n\n")
    f.write("| Project | Status | ROM | Size | Time |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for r in RESULTS:
        rom_str = "✅" if r.get("rom_exists") else "❌"
        f.write(f"| {r['name']} | {r['status']} | {rom_str} | {r.get('rom_size', 0)} bytes | {r.get('time', 'N/A')} |\n")
    
    f.write("\n## Failure Analysis\n")
    for r in RESULTS:
        if r['status'] != "SUCCESS":
            f.write(f"### {r['name']}\n")
            f.write(f"```\n{r['error']}\n```\n")

print(f"\nReport generated at: {report_path}")
