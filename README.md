# spider_solitaire_solver

This is a python tool which will automatically look at and click on the screen to attempt to solve
a game of Spider Solitaire.  


To run:

1.  Make a new virtual environment.

2.  Run `pip install -e .`

2.  Open the page https://www.free-spider-solitaire.com/ so that a game is sitting ready to start, and fully visible
    on the screen.

3.  On the command line, run the entry point `solve`.


Current Status:

The solver can clear a few runs to the top, but hasn't finished a game yet.  Takes around 10-15 mins.


Warning:

This tool uses the package pyautogui to move the mouse and make clicks on the screen.  This means it may be
difficult to exit the program if something is going wrong (it is hard to click on the command window and
`Ctrl + C` if the program is constantly dragging the mouse to different locations).  As the program runs,
it is often possible to use `Ctrl + C` to exit, but if not, the default pyautogui fail-safe can be used,
which at the time of writing is to aggressively move the mouse to a corner of the screen (See
https://pyautogui.readthedocs.io/en/latest/#fail-safes).  Turning the computer off works too.
