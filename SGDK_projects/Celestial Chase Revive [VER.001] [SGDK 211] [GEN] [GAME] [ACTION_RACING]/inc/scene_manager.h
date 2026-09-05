#ifndef SCENE_MANAGER_H
#define SCENE_MANAGER_H

#include "scene_types.h"

void SM_init(SceneId initialScene);
void SM_requestTransition(SceneId nextScene);
void SM_update(void);
SceneId SM_getCurrentScene(void);

#endif /* SCENE_MANAGER_H */
