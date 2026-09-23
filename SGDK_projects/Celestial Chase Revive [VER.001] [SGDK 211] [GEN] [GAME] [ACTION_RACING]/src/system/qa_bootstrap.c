#include "system/qa_bootstrap.h"

#define QA_BOOTSTRAP_VERSION 1u
#define QA_BOOTSTRAP_LENGTH 12u
#define QA_BOOTSTRAP_HOLD_VERSION 2u
#define QA_BOOTSTRAP_HOLD_LENGTH 16u
#define QA_BOOTSTRAP_CHECKSUM_SEED 0xA55Au

static bool s_applied = false;
static SceneId s_target_scene = APP_SCENE_COUNT;
static u16 s_hold_frame = 0u;
static u16 s_flags = 0u;

static u16 read_u16be(u32 offset)
{
    return (u16)(((u16)SRAM_readByte(offset) << 8) |
                 (u16)SRAM_readByte(offset + 1u));
}

static void clear_magic(u32 offset)
{
    SRAM_writeByte(offset + 0u, 0u);
    SRAM_writeByte(offset + 1u, 0u);
    SRAM_writeByte(offset + 2u, 0u);
    SRAM_writeByte(offset + 3u, 0u);
}

SceneId QA_bootstrapResolve(SceneId fallback_scene)
{
    const u32 offset = PROJECT_QA_BOOTSTRAP_SRAM_OFFSET;
    u16 version;
    u16 length;
    u16 scene_id;
    u16 hold_frame = 0u;
    u16 flags = 0u;
    u16 checksum;
    u16 expected;

    s_applied = false;
    s_target_scene = APP_SCENE_COUNT;
    s_hold_frame = 0u;
    s_flags = 0u;

    SRAM_enable();
    if ((SRAM_readByte(offset + 0u) != (u8)'S') ||
        (SRAM_readByte(offset + 1u) != (u8)'B') ||
        (SRAM_readByte(offset + 2u) != (u8)'I') ||
        (SRAM_readByte(offset + 3u) != (u8)'S'))
    {
        SRAM_disable();
        return fallback_scene;
    }

    version = read_u16be(offset + 4u);
    length = read_u16be(offset + 6u);
    scene_id = read_u16be(offset + 8u);

    if ((version == QA_BOOTSTRAP_HOLD_VERSION) &&
        (length == QA_BOOTSTRAP_HOLD_LENGTH))
    {
        hold_frame = read_u16be(offset + 10u);
        flags = read_u16be(offset + 12u);
        checksum = read_u16be(offset + 14u);
    }
    else
    {
        checksum = read_u16be(offset + 10u);
    }

    expected = QA_BOOTSTRAP_CHECKSUM_SEED ^ version ^ length ^
               scene_id ^ hold_frame ^ flags;
    clear_magic(offset);
    SRAM_disable();

    if (!(((version == QA_BOOTSTRAP_VERSION) &&
           (length == QA_BOOTSTRAP_LENGTH)) ||
          ((version == QA_BOOTSTRAP_HOLD_VERSION) &&
           (length == QA_BOOTSTRAP_HOLD_LENGTH))) ||
        (checksum != expected) ||
        !(scene_id < APP_SCENE_COUNT))
    {
        return fallback_scene;
    }

    s_applied = true;
    s_target_scene = (SceneId)scene_id;
    s_hold_frame = hold_frame;
    s_flags = flags;
    return s_target_scene;
}

bool QA_bootstrapWasApplied(void)
{
    return s_applied;
}

SceneId QA_bootstrapGetTargetScene(void)
{
    return s_target_scene;
}

u16 QA_bootstrapGetHoldFrame(void)
{
    return s_hold_frame;
}

u16 QA_bootstrapGetFlags(void)
{
    return s_flags;
}

bool QA_bootstrapConsumeFlag(u16 flag)
{
    if ((s_flags & flag) == 0u)
    {
        return false;
    }

    s_flags &= (u16)(~flag);
    return true;
}
