# clockify-idleless
Very simple clockify script to track time without idle periods. Very opiniated approach serving the way I track my own time. The premise is that whatever time the user spends active on his/her computer correlates well with the time spent on a given project. The idea is to run the script at startup, forget about it and get reports of the approximate time spent working. If running on a workstation which is only used for work then that approximation should be good enough.

## Requirements
* Python >= 3.5

## Quick Setup
1. Install Python 3.5+ if you haven't already
1. On the command line run: `pip install clockify-idleless`
1. Run: `clockify-idleless` (it will exit with an error)
1. Open `[path to user home folder]/.clockify-idleless/config.ini`
    1. Fill in `APIKey` (mandatory), you can get it from [Clockify user settings](https://clockify.me/user/settings)
    1. Fill in `DefaultProjectId` (optional), you can get it from the url of the Clockify project page. Should be a string resembling `4ba584e621c3d66367e2d149`
1. Run `clockify-idleless` (a tray icon should appear on the taskbar)

## Adding to startup on Windows
1. Find the script executable in the Python Scripts folder, something like: `C:\Users\[user]\AppData\Local\Programs\Python\Python35\Scripts\clockify_idleless.exe`
1. Open the startup folder by running (<kbd>⊞ Win</kbd>+<kbd>R</kbd>) `shell:startup` which should take you to a folder similar to: `C:\Users\[user]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
1. Create a shortcut of `clockify_idleless.exe` on the `Startup` folder
1. Forget about the script and track your active time on Clockify's website
