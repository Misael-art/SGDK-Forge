import os
import subprocess

resolve_script = r"F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\resolve_project.ps1"
bracket_dir = r"F:\Projects\MegaDrive_DEV\SGDK_templates\SimpleGameStates [VER.1.0] [SGDK 211] [GEN] [TEMPLATE] [LOGICA]"

print(f"Testing resolution for: {bracket_dir}")

cmd = [
    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", resolve_script,
    "-EntryDir", bracket_dir,
    "-OutputFormat", "Batch"
]

process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate()

print("--- STDOUT ---")
print(stdout)
print("--- STDERR ---")
print(stderr)
print(f"Exit code: {process.returncode}")
