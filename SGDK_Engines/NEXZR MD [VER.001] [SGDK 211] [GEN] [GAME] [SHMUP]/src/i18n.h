#ifndef I18N_H
#define I18N_H

typedef enum {
    LANG_EN = 0,
    LANG_PT,
    LANG_ES
} Language;

void I18N_setLanguage(Language lang);

extern const char* TXT_START;
extern const char* TXT_OPTIONS;
extern const char* TXT_EXIT;

extern const char* TXT_CURRENT_LANGUAGE;

extern const char* TXT_LANGUAGE;
extern const char* TXT_DIFFICULTY;
extern const char* TXT_CREDITS;
extern const char* TXT_BACK;

extern const char* TXT_ON;
extern const char* TXT_OFF;

extern const char* TXT_PAUSED;

#endif
