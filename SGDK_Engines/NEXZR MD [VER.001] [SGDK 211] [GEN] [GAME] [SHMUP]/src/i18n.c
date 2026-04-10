#include "i18n.h"
#include "lang_pt.h"
#include "lang_en.h"
#include "lang_es.h"

const char* TXT_START;
const char* TXT_OPTIONS;
const char* TXT_EXIT;

const char* TXT_LANGUAGE;
const char* TXT_DIFFICULTY;
const char* TXT_CREDITS;
const char* TXT_BACK;
const char* TXT_CURRENT_LANGUAGE;

const char* TXT_ON;
const char* TXT_OFF;
const char* TXT_PAUSED;

void I18N_setLanguage(Language lang) {
    switch (lang) {
        case LANG_PT:
            TXT_START   = LANG_PT_TXT_START;
            TXT_OPTIONS = LANG_PT_TXT_OPTIONS;
            TXT_EXIT    = LANG_PT_TXT_EXIT;
            TXT_LANGUAGE = LANG_PT_TXT_LANGUAGE;
            TXT_DIFFICULTY = LANG_PT_TXT_DIFFICULTY;
            TXT_CREDITS = LANG_PT_TXT_CREDITS;
            TXT_BACK = LANG_PT_TXT_BACK;
            TXT_CURRENT_LANGUAGE = LANG_PT_TXT_CURRENT_LANG;
            TXT_ON = LANG_PT_TXT_ON;
            TXT_OFF = LANG_PT_TXT_OFF;
            TXT_PAUSED = LANG_PT_TXT_PAUSED;
            break;
        case LANG_EN:
            TXT_START   = LANG_EN_TXT_START;
            TXT_OPTIONS = LANG_EN_TXT_OPTIONS;
            TXT_EXIT    = LANG_EN_TXT_EXIT;
            TXT_LANGUAGE = LANG_EN_TXT_LANGUAGE;
            TXT_DIFFICULTY = LANG_EN_TXT_DIFFICULTY;
            TXT_CREDITS = LANG_EN_TXT_CREDITS;
            TXT_BACK = LANG_EN_TXT_BACK;
            TXT_CURRENT_LANGUAGE = LANG_EN_TXT_CURRENT_LANG;
            TXT_ON = LANG_EN_TXT_ON;
            TXT_OFF = LANG_EN_TXT_OFF;
            TXT_PAUSED = LANG_EN_TXT_PAUSED;
            break;
        case LANG_ES:
            TXT_START   = LANG_ES_TXT_START;
            TXT_OPTIONS = LANG_ES_TXT_OPTIONS;
            TXT_EXIT    = LANG_ES_TXT_EXIT;
            TXT_LANGUAGE = LANG_ES_TXT_LANGUAGE;
            TXT_DIFFICULTY = LANG_ES_TXT_DIFFICULTY;
            TXT_CREDITS = LANG_ES_TXT_CREDITS;
            TXT_BACK = LANG_ES_TXT_BACK;
            TXT_CURRENT_LANGUAGE = LANG_ES_TXT_CURRENT_LANG;
            TXT_ON = LANG_ES_TXT_ON;
            TXT_OFF = LANG_ES_TXT_OFF;
            TXT_PAUSED = LANG_ES_TXT_PAUSED;
            break;
    }
}
