# TODO List
Tasks that need to be completed



## Logger
The logger could use the following improvements:
- We could potentially use a keydown node to allow the "enter" key to submit a log message
- In order to do so we must:
    - have a condition to only process the enter key if the logger is enabled
    - have some script or node to strip the newline character off the end of the string before it is written to csv
- I don't think it's possible to autoselect the textbox upon starting a log due to native bonsai limitations.

## Ephys
- Bonsai files must be built for all combinations
- hitting enter on the configureheadstage node pulls up a gui with a lot of options, I don't think it is accessible from anywhere other than the editor. Not sure what to do about that yet

## Visualizers
- Rebuilding the visualizer every time the node count changes is really annoying. Try to see if there is a better way.

## Selector Gui
- See if it can be organized to be prettier. 
- Code could probably be cleaned up a little.
- Eventually want to add a custom icon for the shortcut
- Adjust color/font scheme if desired.