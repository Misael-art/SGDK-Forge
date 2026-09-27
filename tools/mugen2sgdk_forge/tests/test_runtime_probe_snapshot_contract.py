from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]'
SOURCE = PROJECT / 'src/system/runtime_probe.c'


def _function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    open_brace = source.index('{', start)
    depth = 0
    for index in range(open_brace, len(source)):
        if source[index] == '{':
            depth += 1
        elif source[index] == '}':
            depth -= 1
            if depth == 0:
                return source[open_brace + 1:index]
    raise AssertionError(f'unclosed function body: {signature}')


def test_every_probe_snapshot_exports_both_blocks_at_window_close():
    source = SOURCE.read_text(encoding='utf-8')
    exporter = _function_body(source, 'static void export_probe_snapshot(void)')
    assert 'MDRuntimeProbe_exportToSRAM();' in exporter
    assert 'export_visual_probe_to_sram();' in exporter

    tick = _function_body(source, 'void MDRuntimeProbe_tick(void)')
    assert 'export_probe_snapshot();' in tick
    assert 'g_mdRuntimeProbe[30] >= PROBE_MEASURE_FRAMES' in tick
    assert 's_windowLatched = 1;' in tick

    assert '#define PROBE_VLAB_SCHEMA_VERSION 2' in source
    assert '#define PROBE_VLAB_MEASUREMENT_TRAILER_WORDS 2' in source
    assert 'sram_write_visual_word(&offset, g_mdRuntimeProbe[30]);' in source
    assert 'sram_write_visual_word(&offset, (u16)PROBE_MEASURE_FRAMES);' in source
