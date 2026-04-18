#include "entitymanager.h"

Entity entities[MAX_ENTITIES];
u8 entityCount = 0;

Entity* Entity_add(void* ctx, Func func) {
    if (entityCount >= (MAX_ENTITIES)) return NULL;

    entities[entityCount].context = ctx;
    entities[entityCount].func = func;
    entities[entityCount].active = true;
    entities[entityCount].index = entityCount;

    entityCount++;

    return &entities[entityCount - 1];
}

void Entity_removeEntity(unsigned index) {
    if (index >= entityCount && entityCount <= 0) return;

    entities[index].active = false;
    entities[index] = entities[entityCount - 1];
    entityCount--;
}

void Entity_removeByContext(void* ctx) {
    for (unsigned i = 0; i < entityCount; i++) {
        if (entities[i].context == ctx) {
            Entity_removeEntity(i);
            return;
        }
    }
}

void Entity_executeAll() {
    for (unsigned i = 0; i < entityCount; i++) {
        if (entities[i].func && entities[i].active) entities[i].func(entities[i].context);
    }
}

void Entity_executeByContext(void* context) {
    Entity *e = Entity_search(0, context);

    e->func(e->context);
}

void Entity_executeByIndex(unsigned index) {
    entities[index].func(entities[index].context);
}

Entity* Entity_search(unsigned index, void* context) {
    if (index == 0 && context == NULL) {
        return NULL;
    }

    if (index > 0 && index < entityCount) return &entities[index];

    if (context != NULL) {
        for (unsigned i = 0; i < entityCount; i++) {
            if (entities[i].context == context) return &entities[i];
        }
    }

    return NULL;
}