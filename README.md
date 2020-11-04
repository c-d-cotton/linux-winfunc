# Introduction
The purpose of the functions is to extend standard window managers with more shortcut options regarding window placement.

Although some of the options do not require configuration, most do. I hope to include an example later of how one might configure the files but I have not had time to do so yet.

# Installation
The functions have the following dependencies: xrandr, xdotool, wmctrl, python3.

# Terminology
Window class can be found by running `wmctrl -lx` and looking at the third column. For example, the window class of urxvt is `urxvt.URxvt` on Debian (they sometimes vary by distribution).

# Functionality
## No configuration
Before you begin using the script and each time you change your monitor setup, you should run:
- getmondim() to get the monitor dimensions.

Basic options (which require no configuration) are:
- Cycle through windows on a workspace by placement.
- Cycle through windows on a workspace by type.

## Configuration

I find it useful to have specific instances of windows which I give a unique id, for example a browser devoted to videos or a terminal devoted to displaying my tasks. I include functions to select and assign these ids. The specific functions are as follows:
- Open a window with a specific id.
- Select a window with a specific id.
- Open a window with a specific id if it's not open or select it if it is open.
- Assign a specific id to a window that's already open.
- Move back to the previous workspace after selecting/opening a window with a specific id.

I like to use more than one monitor but find it frustrating to move windows around when I move from one monitor setup to another (for example working with an additional external monitor to unplugging my laptop when I go out and just working with my laptop screen). Thus, I also include scripts that allow me to set default positions for windows for different monitor configurations. The specific functions are as follows:
- Place open windows in their default location if they have one.
- Open a new window and place it in its default location.

# Configuration
To use all the options, you'll need to define four elements:
- getdefaultposdict: A function returning two dictionaries. The first dictionary gives the default positions of different window classes and the second gives the default positions of different window ids. It might be sensible to call the function nummonitors during this function since that allows you to vary the default positions according to the number of monitors.
- idwmclass: A dictionary giving the class of an id.
- idworkspace: A dictionary giving the default workspace of an id. If 99 is specified or a number is not specified, it will be opened on the current workspace.
- newwincommand: A dictionary specifying the command to run to open a new window.
