from PIL import Image
import pytest
from mugen2sgdk_forge.stage_piece_reuse import audit, variants


def test_flip_identity_region_union_and_grid(tmp_path):
    tile = bytes(range(64))
    flip = variants(tile)[1]
    im = Image.new("P", (16,8))
    im.putpalette([v for i in range(256) for v in (i,i,i)])
    im.putdata([v for y in range(8) for v in tile[y*8:y*8+8]+flip[y*8:y*8+8]])
    path=tmp_path/"fixture.png"; im.save(path)
    r=audit(path,{"left":(0,0,8,8),"right":(8,0,8,8)})
    assert r["whole"] == {"cells":2,"unique_exact":2,"unique_hv":1}
    assert r["regions"]["left"]["exclusive_patterns"] == 0
    assert r["regions"]["right"]["patterns_shared_with_outside"] == 1
    assert r["pixels_changed"] == 0
    with pytest.raises(ValueError,match="aligned"):
        audit(path,{"phase4":(4,0,8,8)})
    assert len(set(variants(tile)))==4
    assert variants(variants(tile)[3])[3]==tile
