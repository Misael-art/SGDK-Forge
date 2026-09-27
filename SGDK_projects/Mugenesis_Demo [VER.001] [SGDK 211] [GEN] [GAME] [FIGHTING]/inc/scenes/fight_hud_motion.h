#ifndef FIGHT_HUD_MOTION_H
#define FIGHT_HUD_MOTION_H

/* Integer-only presentation state. Never writes the fighter's actual power. */
#define HUD_POWER_TILES 5
#define HUD_POWER_PX 40
#define HUD_POWER_ROW 26
#define HUD_POWER_LABEL_ROW 25
#define HUD_WIN_ROW 3
#define HUD_COMBO_ROW 5
#define HUD_POWER_DRAIN_FRAMES 24

typedef struct {
    unsigned short shown, target, start, remaining;
} HudPowerMotion;

static inline unsigned short hud_power_x(unsigned short side, unsigned short column)
{
    return side ? 38 - column : 1 + column;
}

static inline unsigned short hud_power_step(HudPowerMotion *m, unsigned short target)
{
    if (target > HUD_POWER_PX) target = HUD_POWER_PX;
    if (target != m->target) {
        m->target = target;
        if (target < m->shown) {
            m->start = m->shown;
            m->remaining = HUD_POWER_DRAIN_FRAMES;
        } else { m->shown = target; m->remaining = 0; }
    }
    if (m->remaining) {
        unsigned long r = --m->remaining;
        m->shown = m->target + (m->start - m->target) * r * r /
                  (HUD_POWER_DRAIN_FRAMES * HUD_POWER_DRAIN_FRAMES);
    }
    return m->shown;
}
#endif
