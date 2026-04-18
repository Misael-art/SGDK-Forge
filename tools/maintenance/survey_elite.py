import os

projects = [
    r'NEXZR MD [VER.001] [SGDK 211] [GEN] [GAME] [SHMUP]',
    r'Jogo de Nave [VER.0.5] [SGDK 211] [GEN] [GAME] [SHMUP]',
    r'Shadow Dancer Hamoopig [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]',
    r'HAMOOPIG [VER.1.0 CPU6.2] [SGDK 211] [GEN] [ENGINE] [LUTA]',
    r'HAMOOPIG main [VER.001] [SGDK 211] [GEN] [ENGINE] [LUTA]',
    r'BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA]',
    r'PlatformerEngine [VER.1.0] [SGDK 211] [GEN] [ENGINE] [PLATAFORMA]',
    r'KOF94 HAMOOPIG MINIMALIST [VER.001] [SGDK 211] [GEN] [ENGINE] [LUTA]',
    r'HAMOOPIG [VER.1.0] [SGDK 211] [GEN] [ENGINE] [LUTA]',
    r'MegaDriving [VER.1.0] [SGDK 211] [GEN] [ENGINE] [CORRIDA]'
]
base = r'F:\Projects\MegaDrive_DEV\SGDK_Engines'

with open('elite_survey.txt', 'w', encoding='utf-8') as f:
    for p in projects:
        p_path = os.path.join(base, p)
        f.write(f'--- {p} ---\n')
        if not os.path.exists(p_path):
            f.write('NOT FOUND\n\n')
            continue
            
        doc_dir = os.path.join(p_path, 'doc')
        if os.path.exists(doc_dir):
            f.write(f'Docs: {os.listdir(doc_dir)}\n')
        else:
            f.write('No doc dir\n')
            
        src_dir = os.path.join(p_path, 'src')
        if os.path.exists(src_dir):
            src_content = os.listdir(src_dir)
            f.write(f'Src structure: {src_content}\n')
            for item in src_content:
                item_path = os.path.join(src_dir, item)
                if os.path.isdir(item_path):
                    f.write(f'  - {item}/: {os.listdir(item_path)}\n')
                    
        root_files = os.listdir(p_path)
        f.write(f'Root files: {[rf for rf in root_files if rf.lower().endswith(".md") or rf.lower().endswith(".txt")]}\n\n')
