import os
import subprocess
import ctypes

def get_short_path_name(long_name):
    try:
        buf = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetShortPathNameW(long_name, buf, 1024)
        return buf.value
    except: return long_name

# Define paths
base_dir = r"F:\Projects\MegaDrive_DEV\SGDK_templates\SimpleGameStates [VER.1.0] [SGDK 211] [GEN] [TEMPLATE] [LOGICA]"
short_dir = get_short_path_name(base_dir)
build_script = os.path.join(short_dir, "build.bat")

print(f"Executing build for: {base_dir}")
print(f"Short path: {short_dir}")

# Run the build script
process = subprocess.Popen(
    [build_script],
    cwd=short_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
    text=True
)

stdout, stderr = process.communicate()

print("--- STDOUT ---")
print(stdout)
print("--- STDERR ---")
print(stderr)
print(f"Exit code: {process.returncode}")

if process.returncode == 0:
    rom_path = os.path.join(short_dir, "out", "rom.bin")
    if os.path.exists(rom_path):
        print(f"SUCCESS: ROM generated at {rom_path}")
    else:
        print("ERROR: Build succeeded but ROM not found in out/")
