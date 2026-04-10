/**
 *  \deprecated Use pal.h unit instead
 */

#ifndef _VDP_PAL_H_
#define _VDP_PAL_H_


/**
 *  \deprecated Use #PAL_getColor(..) instead
 */
#define PAL_getColor(index)     _Pragma("GCC error \"This definition is deprecated, use PAL_getColor(..) instead.\"")

/**
 *  \deprecated Use #PAL_getColors(..) instead
 */
#define VDP_getPaletteColors(index, dest, count)     _Pragma("GCC error \"This definition is deprecated, use PAL_getColors(..) instead.\"")
/**
 *  \deprecated Use #PAL_getPalette(..) instead
 */
#define VDP_getPalette(num, pal)     _Pragma("GCC error \"This definition is deprecated, use PAL_getPalette(..) instead.\"")

/**
 *  \deprecated Use #PAL_setColor(..) instead
 */
#define PAL_setColor(index, value)     _Pragma("GCC error \"This definition is deprecated, use PAL_setColor(..) instead.\"")
/**
 *  \deprecated Use #PAL_setColors(..) instead
 */
#define PAL_setColors(index, values, count, DMA)     _Pragma("GCC error \"This definition is deprecated, use PAL_setColors(..) instead.\"")
/**
 *  \deprecated Use #PAL_setPalette(..) instead
 */
#define PAL_setPalette(num, pal, DMA)     _Pragma("GCC error \"This definition is deprecated, use PAL_setPalette(..) instead.\"")

/**
 *  \deprecated Use #PAL_fade(..) instead
 */
#define PAL_fade(fromcol, tocol, palsrc, paldst, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fade(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeTo(..) instead
 */
#define PAL_fadeTo(fromcol, tocol, pal, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeTo(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeOut(..) instead
 */
#define PAL_fadeOut(fromcol, tocol, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeOut(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeIn(..) instead
 */
#define PAL_fadeIn(fromcol, tocol, pal, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeIn(..) instead.\"")

/**
 *  \deprecated Use #PAL_fadePalette(..) instead
 */
#define PAL_fadePalette(numpal, palsrc, paldst, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadePalette(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeToPalette(..) instead
 */
#define PAL_fadeToPalette(numpal, pal, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeToPalette(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeOutPalette(..) instead
 */
#define PAL_fadeOutPalette(numpal, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeOutPalette(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeInPalette(..) instead
 */
#define PAL_fadeInPalette(numpal, pal, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeInPalette(..) instead.\"")

/**
 *  \deprecated Use #PAL_fadeAll(..) instead
 */
#define PAL_fadeAll(palsrc, paldst, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeAll(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeToAll(..) instead
 */
#define PAL_fadeToAll(pal, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeToAll(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeOutAll(..) instead
 */
#define PAL_fadeOutAll(numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeOutAll(..) instead.\"")
/**
 *  \deprecated Use #PAL_fadeInAll(..) instead
 */
#define PAL_fadeInAll(pal, numframe, async)     _Pragma("GCC error \"This definition is deprecated, use PAL_fadeInAll(..) instead.\"")

/**
 *  \deprecated Use #PAL_isDoingFade(..) instead
 */
#define VDP_isDoingFade()     _Pragma("GCC error \"This definition is deprecated, use PAL_isDoingFade(..) instead.\"")
/**
 *  \deprecated Use #PAL_waitFadeCompletion(..) instead
 */
#define PAL_waitFadeCompletion()     _Pragma("GCC error \"This definition is deprecated, use PAL_waitFadeCompletion(..) instead.\"")
/**
 *  \deprecated Use #PAL_interruptFade() instead
 */
#define PAL_interruptFade()     _Pragma("GCC error \"This definition is deprecated, use PAL_interruptFade(..) instead.\"")


#endif // _VDP_PAL_H_
