#ifndef SYSTEM_QA_BOOTSTRAP_H
#define SYSTEM_QA_BOOTSTRAP_H

#include <genesis.h>
#include "scene_types.h"

#define PROJECT_QA_BOOTSTRAP_SRAM_OFFSET 0x120u
#define QA_BOOTSTRAP_FLAG_HOLD_SCENE 0x0001u
#define QA_BOOTSTRAP_FLAG_FORCE_RACE_FAILURE 0x0002u

SceneId QA_bootstrapResolve(SceneId fallback_scene);
bool QA_bootstrapWasApplied(void);
SceneId QA_bootstrapGetTargetScene(void);
u16 QA_bootstrapGetHoldFrame(void);
u16 QA_bootstrapGetFlags(void);
bool QA_bootstrapConsumeFlag(u16 flag);

#endif
