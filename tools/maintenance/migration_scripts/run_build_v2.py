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
log_file = os.path.join(short_dir, "build_log_p.txt")

print(f"Executing build for: {base_dir}")
print(f"Short path: {short_dir}")
print(f"Log file: {log_file}")

# Run the build script
with open(log_file, "w") as f:
    process = subprocess.Popen(
        [build_script, short_dir],
        cwd=short_dir,
        stdout=f,
        stderr=f,
        shell=True,
        text=True
    )
    process.wait()

print(f"Exit code: {process.returncode}")
if os.path.exists(log_file):
    print(f"Log file created at: {log_file}")
