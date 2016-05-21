# RO_gue

Roguelike implemented entirely within the Python standard library which takes input from and renders in the command line.

All game functions are isolated from both input and rendering so that it can be easily ported to other platforms without changing anything else.

Uses termios as part of a getch() implementation so, as far as I know, it will only function Mac OS. It can be substituted for input(), but will then require newline buffering on input.

Example rendering:

![UI](/sample_images/UI.png?raw=true "UI")
