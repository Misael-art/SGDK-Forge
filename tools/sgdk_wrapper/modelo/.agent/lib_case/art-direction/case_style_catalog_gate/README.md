# Case: Style Catalog Gate

Use this case when a project wants to generate, source, convert or judge visual art before a canonical art direction exists.

Expected result:

- block with `art_direction_undeclared` when no decision record exists
- block with `style_catalog_not_consulted` when a manifest was invented without `art_style_catalog.json`
- allow legacy projects to report `art_direction_pre_canonical`, but not to claim AAA/stable/release from that legacy state
- require neutral technical prompt descriptors instead of copying artist, studio, brand, game or IP references

