# update and changelog

v 1.0
changes:
- game processes run entirely independently of graphics
- different entities with different properties
- basic world generation
- items and inventory (acquired from enemies or chests)
- now with color!
- flight now supported
- not entirely non-functional UI
- enemy ai but currently with no pathing

v 1.1
changes:
- generally cleaned up the RO_gue.py
- new phasing mechanic added to shift between floors with r and f
- small performance optimizations
- enemies now sleep until they've spotted the player
- temporary ASCII map input used until procedural map generation is finished
- added slightly more intelligent ai

v 1.2
changes:
- performance improvements as only entities on the current floor(s) are loaded
- procedural floor generation added

to do:
- procedural generation
- improve enemy ai
- obscure view with obstacles
- add in traps
- add in support for fluid dynamics to support gas spread
- improve phasing mechanics (i.e. require items to use so they can't be spammed, add cooldown, effects when phasing into walls, etc.)
- visualization with something besides terminal (especially to make phasing clearer)