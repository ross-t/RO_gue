# RO_gue

A basic roguelike written in python designed to use only the python standard library.

Current graphics are handled in OS X terminal.

Movement is handled as wasd followed by enter between inputs.

ASCII map input as a current placeholder to procedural generation.

Basic enemy AI with no pathing.

Phasic mechanic to shift between floors, the idea for which being that all of the floors or 'depths' exist in the same space just slightly 'out of phase' with each other. While phasing between floors you are vulnerable to enemies on both floors (though they remain constrained by the bounds of their own floor). You can also walk through walls that only exist on one of the two floors, but not ones that exist on both. The duration of this 'phasing' period is by default 5 player turns.