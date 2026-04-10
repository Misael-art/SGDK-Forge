import os
import subprocess

# Define paths
base_dir = r"F:\Projects\MegaDrive_DEV\SGDK_templates\SimpleGameStates_Elite"
build_script = os.path.join(base_dir, "build.bat")

print(f"Executing build for: {base_dir}")
print(f"Build script: {build_script}")

# Run the build script
process = subprocess.Popen(
    [build_script],
    cwd=base_dir,
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
