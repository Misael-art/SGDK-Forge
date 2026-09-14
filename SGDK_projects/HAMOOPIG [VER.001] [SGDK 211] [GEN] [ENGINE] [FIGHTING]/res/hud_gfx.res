ALIGN
// SF HUD bars + KO from user sheet (placeholder / prototype)
SPRITE spr_hud_energy_y  "sprite/hud/energy_yellow.png"  16  2 FAST 0
SPRITE spr_hud_energy_r  "sprite/hud/energy_red.png"     16  2 FAST 0
SPRITE spr_hud_energy_y_p2  "sprite/hud/energy_yellow_p2.png"  16  2 FAST 0
SPRITE spr_hud_energy_r_p2  "sprite/hud/energy_red_p2.png"     16  2 FAST 0
SPRITE spr_hud_ko        "sprite/hud/ko.png"             6  3 FAST 0
// Compact fixed-width cells. The runtime reuses one VRAM tile for all cells.
SPRITE spr_hud_energy_segment "sprite/hud/energy_yellow_segment.png" 2 1 FAST 0
SPRITE spr_hud_clock_digit "sprite/hud/clock_digits_window.png" 2 2 FAST 0
// P1/P2 yellow as plane tiles. NONE/NONE keeps 32 spatial tiles each for WINDOW.
TILESET ts_hud_p1_bar "sprite/hud/energy_yellow_p1_window.png" NONE NONE ROW
TILESET ts_hud_p2_bar "sprite/hud/energy_yellow_p2_window.png" NONE NONE ROW
TILESET ts_hud_clock "sprite/hud/clock_digits_window.png" NONE NONE ROW
TILESET ts_hud_message_font "sprite/hud/message_font.png" NONE NONE ROW
