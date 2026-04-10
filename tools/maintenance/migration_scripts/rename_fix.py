import os

old_name = r'F:\Projects\MegaDrive_DEV\SGDK_templates\SimpleGameStates [VER.1.0] [SGDK 211] [GEN] [TEMPLATE] [LOGICA]'
new_name = r'F:\Projects\MegaDrive_DEV\SGDK_templates\SimpleGameStates_Elite'

if os.path.exists(old_name):
    print(f"Renaming {old_name} to {new_name}")
    os.rename(old_name, new_name)
else:
    print(f"Old name not found: {old_name}")
    print(f"Available: {os.listdir(r'F:\Projects\MegaDrive_DEV\SGDK_templates')}")
