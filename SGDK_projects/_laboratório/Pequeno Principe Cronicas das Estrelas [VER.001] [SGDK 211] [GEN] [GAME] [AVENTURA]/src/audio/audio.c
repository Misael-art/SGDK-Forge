#include "project.h"
#include "resources.h"

void Audio_init(void)
{
}

void Audio_playDialogueVoice(PlanetId planet)
{
    switch (planet)
    {
        case PLANET_B612:
        case PLANET_B612_RETORNO:
        case PLANET_JARDIM:
            XGM2_playPCMEx(sfx_voice_rose, sizeof(sfx_voice_rose), SOUND_PCM_CH2, 6, FALSE, FALSE);
            break;

        case PLANET_KING:
        case PLANET_VAIDOSO:
        case PLANET_BEBADO:
        case PLANET_HOMEM_NEG:
        case PLANET_GEOGRAFO:
            XGM2_playPCMEx(sfx_voice_king, sizeof(sfx_voice_king), SOUND_PCM_CH2, 7, FALSE, FALSE);
            break;

        case PLANET_ACENDEDOR:
            XGM2_playPCMEx(sfx_voice_lamp, sizeof(sfx_voice_lamp), SOUND_PCM_CH2, 7, FALSE, FALSE);
            break;

        case PLANET_DESERTO:
        case PLANET_SERPENTE:
        case PLANET_POCO:
            XGM2_playPCMEx(sfx_voice_wind, sizeof(sfx_voice_wind), SOUND_PCM_CH2, 6, FALSE, FALSE);
            break;

        default:
            break;
    }
}

void Audio_playSolveFx(PlanetId planet)
{
    switch (planet)
    {
        case PLANET_B612:
        case PLANET_B612_RETORNO:
        case PLANET_JARDIM:
            XGM2_playPCMEx(sfx_bloom, sizeof(sfx_bloom), SOUND_PCM_CH3, 10, FALSE, FALSE);
            break;

        case PLANET_KING:
        case PLANET_VAIDOSO:
        case PLANET_HOMEM_NEG:
            XGM2_playPCMEx(sfx_throne, sizeof(sfx_throne), SOUND_PCM_CH3, 10, FALSE, FALSE);
            break;

        case PLANET_ACENDEDOR:
        case PLANET_BEBADO:
        case PLANET_GEOGRAFO:
            XGM2_playPCMEx(sfx_lamp, sizeof(sfx_lamp), SOUND_PCM_CH3, 10, FALSE, FALSE);
            break;

        case PLANET_DESERTO:
        case PLANET_SERPENTE:
        case PLANET_POCO:
            XGM2_playPCMEx(sfx_star, sizeof(sfx_star), SOUND_PCM_CH3, 10, FALSE, FALSE);
            break;

        default:
            break;
    }
}
