#ifndef ENTITY_MANAGER_H
#define ENTITY_MANAGER_H

#include <genesis.h>
#include "callback.h"

#define MAX_ENTITIES 10

typedef struct {
    void* context;
    Func func;
    bool active;
    u8 index;
} Entity;

Entity* Entity_add(void* ctx, Func func);
void Entity_removeEntity(unsigned index);
void Entity_removeByContext(void* context);
void Entity_executeAll();
void Entity_executeByContext(void* context);
void Entity_executeByIndex(unsigned index);
Entity* Entity_search(unsigned index, void* context);

#endif