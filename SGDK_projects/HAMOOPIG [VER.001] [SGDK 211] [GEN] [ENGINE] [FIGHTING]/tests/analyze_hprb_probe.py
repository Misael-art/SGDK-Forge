#!/usr/bin/env python3
"""Decode HAMOOPIG's diagnostic HPRB SRAM block.

The probe samples the DMA queue before VBlank and the active SGDK sprite list;
it is evidence for the captured ROM only, not a synthetic performance claim.

Escritor canonico: src/hamoopig_runtime_probe.c (exportProbe).  Qualquer
mudanca de layout la tem de aparecer em SCHEMA_SIZE e no decode abaixo, e o
--self-check tem de continuar passando.
"""
import argparse, hashlib, json, struct, tempfile
from pathlib import Path

HPRB_OFFSET = 0x500
SIGNATURE = b'HPRB'

# schema -> (size declarado, numero de words).  size = 8 + words*2, igual ao
# HPRB_BYTES do C.  O par e FECHADO: aceitar size de um schema em outro faz o
# decoder ler um layout diferente do que a ROM escreveu, em silencio.
SCHEMA_SIZE = {1: (24, 8), 2: (32, 12), 3: (36, 14), 4: (46, 19), 5: (50, 21)}

STAGE_NAMES = ['clock', 'health_hud', 'message_hud', 'animation', 'fsm']

# Saturacoes do lado C. probeSamples para em 0xFFFF (runtime_probe.c:132) e
# cada linha do histograma de scanline para em 0xFF (runtime_probe.c:44).
SAMPLES_SATURATION = 0xFFFF
SCANLINE_SATURATION = 0xFF


class HprbError(Exception):
    """Entrada invalida. Nunca degrade para zeros: zero e um valor legitimo."""


def decode(data: bytes) -> dict:
    off = HPRB_OFFSET
    if len(data) < off + 8:
        raise HprbError(f'too short for header: {len(data)} bytes, need {off + 8}')
    if data[off:off + 4] != SIGNATURE:
        raise HprbError('HPRB signature missing')

    schema, size = struct.unpack_from('>HH', data, off + 4)
    if schema not in SCHEMA_SIZE:
        raise HprbError(f'unsupported HPRB schema {schema}')
    expected_size, words = SCHEMA_SIZE[schema]
    if size != expected_size:
        raise HprbError(f'schema {schema} declares size {size}, expected {expected_size}')

    # Sem esta checagem uma SRAM truncada decodifica como zeros: int.from_bytes
    # de fatia vazia e 0, e o relatorio sairia "within_nominal" sem dado algum.
    need = off + 8 + words * 2
    if len(data) < need:
        raise HprbError(f'truncated block: {len(data)} bytes, need {need} for schema {schema}')

    vals = list(struct.unpack_from(f'>{words}H', data, off + 8))

    frame = (vals[0] << 16) | vals[1]
    if schema == 1:
        peak_dma_frame = peak_scanline_frame = None
        dma, active, vdp, scanline, samples, scene = vals[2:8]
    else:
        peak_dma_frame = (vals[2] << 16) | vals[3]
        peak_scanline_frame = (vals[4] << 16) | vals[5]
        dma, active, vdp, scanline, samples, scene = vals[6:12]

    pre_sprite_dma = vals[12] if words > 12 else None
    sprite_dma_delta = vals[13] if words > 13 else None
    stage_dma = vals[14:19] if words >= 19 else None
    peak_pre_at_max = vals[19] if words >= 21 else None
    peak_sprite_at_max = vals[20] if words >= 21 else None

    # SGDK 2.11 H40 VBlank envelope from dma.h: NTSC ~7.6 KiB, PAL ~17 KiB.
    region = 'PAL' if (scene & 0x8000) else 'NTSC'
    dma_limit = 17 * 1024 if region == 'PAL' else int(7.6 * 1024)

    warnings = []

    # samples==0 significa que nenhum tick rodou: os picos sao zeros iniciais,
    # nao medicao. Sem isto o relatorio aprovaria um bloco vazio.
    trustworthy = True
    if samples == 0:
        warnings.append('samples==0: nenhum tick foi amostrado; picos nao sao medicao')
        trustworthy = False
    if samples == SAMPLES_SATURATION:
        warnings.append(f'samples saturado em {SAMPLES_SATURATION}: contagem e um piso, nao exata')
    if scanline >= SCANLINE_SATURATION:
        warnings.append(f'sprites_per_scanline saturado em {SCANLINE_SATURATION} no contador de 8 bits')

    # Os dois picos podem vir de frames diferentes: somados nao descrevem um
    # unico pior frame. O plano alerta explicitamente para isso.
    same_frame = None
    if peak_dma_frame is not None and peak_scanline_frame is not None:
        same_frame = peak_dma_frame == peak_scanline_frame
        if not same_frame:
            warnings.append(
                f'pico de DMA (frame {peak_dma_frame}) e pico de scanline '
                f'(frame {peak_scanline_frame}) sao de frames distintos; '
                'nao os some como um pior caso unico')

    # A altura de tela nao e exportada pela sonda, entao PAL224 e PAL240 caem no
    # mesmo envelope. Limitacao conhecida, registrada em vez de mascarada.
    if region == 'PAL':
        warnings.append('envelope PAL unico: a sonda nao exporta altura, '
                        'entao 224 e 240 nao sao distinguidos')

    result = {
        'schema': schema, 'declared_size': size, 'words': words,
        'frame': frame, 'peak_dma_frame': peak_dma_frame,
        'peak_scanline_frame': peak_scanline_frame,
        'peaks_from_same_frame': same_frame,
        # DMA_getQueueTransferSize() e o tamanho ENFILEIRADO antes do VBlank,
        # nao bytes comprovadamente transferidos nem backlog residual.
        'max_dma_queued_bytes': dma,
        'max_active_sprites': active, 'max_vdp_sprites': vdp,
        'max_sprites_per_scanline': scanline, 'samples': samples,
        'max_pre_sprite_dma_bytes': pre_sprite_dma,
        'max_sprite_dma_delta_bytes': sprite_dma_delta,
        'max_stage_dma_delta_bytes': stage_dma,
        'stage_names': STAGE_NAMES,
        'peak_pre_sprite_dma_at_max_bytes': peak_pre_at_max,
        'peak_sprite_dma_delta_at_max_bytes': peak_sprite_at_max,
        'last_scene': scene & 0x7FFF, 'region_inference': region,
        'limits': {'dma_queued_bytes': dma_limit, 'vdp_sprite_links': 80,
                   'sprites_per_scanline': 20},
        'dma_status': 'over_budget' if dma > dma_limit else 'within_nominal',
        'sprite_status': 'within_nominal' if vdp <= 80 and scanline <= 20 else 'over_budget',
        'measurement_trustworthy': trustworthy,
        'warnings': warnings,
        'evidence_scope': 'HPRB SRAM snapshot from BlastEm; same ROM hash required',
    }
    # Sem amostra nao ha veredito. Ausencia de erro nao e aprovacao.
    if not trustworthy:
        result['decision'] = 'indeterminado'
    else:
        result['decision'] = 'cabe com recuo' if dma > dma_limit else 'cabe'
    return result


def _block(schema, values, *, signature=SIGNATURE, size=None, tail_words=None):
    """Monta um bloco HPRB sintetico para as fixtures."""
    expected_size, words = SCHEMA_SIZE[schema]
    vals = list(values) + [0] * (words - len(values))
    n = words if tail_words is None else tail_words
    return (b'\x00' * HPRB_OFFSET + signature
            + struct.pack('>HH', schema, expected_size if size is None else size)
            + struct.pack(f'>{n}H', *vals[:n]))


def _schema5(**kw):
    """Bloco schema 5 plausivel; kw sobrescreve campos por nome."""
    f = {'frame_hi': 0, 'frame_lo': 600, 'pdma_hi': 0, 'pdma_lo': 412,
         'pscan_hi': 0, 'pscan_lo': 412, 'dma': 5688, 'active': 24, 'vdp': 61,
         'scanline': 14, 'samples': 600, 'scene': 10}
    f.update(kw)
    return _block(5, [f['frame_hi'], f['frame_lo'], f['pdma_hi'], f['pdma_lo'],
                      f['pscan_hi'], f['pscan_lo'], f['dma'], f['active'],
                      f['vdp'], f['scanline'], f['samples'], f['scene'],
                      1200, 900, 100, 200, 300, 400, 500, 1100, 850])


def self_check() -> int:
    failures = []

    def expect_ok(name, data, **fields):
        try:
            r = decode(data)
        except HprbError as e:
            failures.append(f'{name}: rejeitou entrada valida ({e})')
            return None
        for k, v in fields.items():
            if r.get(k) != v:
                failures.append(f'{name}: {k}={r.get(k)!r}, esperado {v!r}')
        return r

    def expect_reject(name, data, fragment):
        try:
            decode(data)
        except HprbError as e:
            if fragment not in str(e):
                failures.append(f'{name}: rejeitou por "{e}", esperado conter "{fragment}"')
            return
        failures.append(f'{name}: ACEITOU entrada invalida')

    # --- positivas: round-trip de valores conhecidos ---
    expect_ok('schema5 nominal', _schema5(),
              schema=5, frame=600, max_dma_queued_bytes=5688,
              max_sprites_per_scanline=14, samples=600, last_scene=10,
              region_inference='NTSC', peaks_from_same_frame=True,
              measurement_trustworthy=True, decision='cabe')

    # frame de 32 bits atravessando a fronteira das duas words
    expect_ok('frame 32 bits', _schema5(frame_hi=1, frame_lo=2), frame=65538)

    # bit 15 da scene e a regiao, nao o numero da cena
    expect_ok('regiao PAL', _schema5(scene=0x8000 | 10),
              region_inference='PAL', last_scene=10)

    # schema 1 legado: campos novos ausentes viram None, sem estourar
    expect_ok('schema1 legado', _block(1, [0, 300, 4096, 12, 40, 9, 300, 2]),
              schema=1, frame=300, max_dma_queued_bytes=4096, samples=300,
              max_pre_sprite_dma_bytes=None, max_stage_dma_delta_bytes=None,
              peak_pre_sprite_dma_at_max_bytes=None,
              peak_dma_frame=None, peaks_from_same_frame=None)

    r = expect_ok('over budget NTSC', _schema5(dma=9000),
                  dma_status='over_budget', decision='cabe com recuo')

    # --- negativas: tem de recusar, nunca degradar para zeros ---
    expect_reject('assinatura ausente', _schema5()[:HPRB_OFFSET] + b'XXXX' + _schema5()[HPRB_OFFSET + 4:],
                  'signature missing')
    expect_reject('arquivo curto demais', b'\x00' * (HPRB_OFFSET + 4), 'too short')
    expect_reject('bloco truncado', _block(5, [0, 600], tail_words=6), 'truncated')
    expect_reject('schema desconhecido', _block(5, [0, 1])[:HPRB_OFFSET + 4]
                  + struct.pack('>HH', 99, 50) + _block(5, [0, 1])[HPRB_OFFSET + 8:],
                  'unsupported HPRB schema')
    expect_reject('size cruzado com schema', _block(5, [0, 1], size=32),
                  'expected 50')

    # --- avisos: aceita, mas nao aprova ---
    r = expect_ok('samples zero', _schema5(samples=0),
                  measurement_trustworthy=False, decision='indeterminado')
    if r and not any('samples==0' in w for w in r['warnings']):
        failures.append('samples zero: faltou aviso')

    r = expect_ok('samples saturado', _schema5(samples=SAMPLES_SATURATION))
    if r and not any('saturado' in w for w in r['warnings']):
        failures.append('samples saturado: faltou aviso')

    r = expect_ok('picos de frames distintos', _schema5(pdma_lo=100, pscan_lo=500),
                  peaks_from_same_frame=False)
    if r and not any('frames distintos' in w for w in r['warnings']):
        failures.append('picos distintos: faltou aviso')

    r = expect_ok('scanline saturada', _schema5(scanline=SCANLINE_SATURATION),
                  sprite_status='over_budget')
    if r and not any('scanline saturado' in w for w in r['warnings']):
        failures.append('scanline saturada: faltou aviso')

    if failures:
        print('FAIL:')
        for f in failures:
            print('  -', f)
        return 1
    print('PASS: round-trip, schema legado, truncamento, schema/size cruzado, '
          'assinatura, samples zero/saturado, picos de frames distintos, scanline saturada')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sram', type=Path, nargs='?')
    ap.add_argument('--rom', type=Path)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--self-check', action='store_true')
    a = ap.parse_args()
    if a.self_check:
        raise SystemExit(self_check())
    if a.sram is None:
        ap.error('sram e obrigatorio quando --self-check nao e usado')
    try:
        result = decode(a.sram.read_bytes())
    except HprbError as e:
        raise SystemExit(f'HPRB invalido: {e}')
    if a.rom:
        result['rom_sha256'] = hashlib.sha256(a.rom.read_bytes()).hexdigest()
    out = a.out or a.sram.with_name('hprb_probe_report.json')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
