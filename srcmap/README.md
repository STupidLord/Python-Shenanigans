# `maps_to_server.py` and `old maps_to_server.py`
As you should be able to guess, `maps_to_server.py` is the new version of `old maps_to_server.py`.
<br>
The latter only exists as a sort of very general basis of what I want the new one to do.

Originally I didn't push the old one because I didn't want it to see the light of day, but I later realized that I might as well push it while it's sitting in this dir. I don't even know if it fully in it's current state since I was preparing to rework it before deciding to just completely redo it as a new file.

## `old maps_to_server.py` is dead
Now that I decided to make `maps_to_server` more like an actual package thing, I decided to rename the folder it is contained in to `srcmap`. Get it? src? Like SrcEngine?

With that rename came my GitHub Desktop[^1] telling me "old folder and files delete, new folder and files created". I decided to use this as an excuse to simply not readd the old file. If the need ever arrises to see it, simply go to the [last commit](https://github.com/STupidLord/Python-Shenanigans/tree/951d921180ab6ba25b5833022db0adeb8a74ce5d) with it.

# PEP 8
I refuse to let a code formatter touch my code, ever. However, I know following some standards might be beneficial in the long run if I want to ever touch other codebases. To remedy my hatred of code formatters; I simply went through my code and made it loosely compliant (loosely doing heavy lifting) with some PEP 8 things.

I'll be honest, I'm not a big fan of following something like PEP 8 as I'm used to being able to format my stuff however I want, but I understand the use case and respect those who follow it.

## Part 2, Electric Boogaloo
Okay... maybe I like formatting a bit more than I suggested before. I've been going through code and making smaller helper functions to reduce the amount of work a single function is doing.

Reading a list of `MapItem`s? Well, before `read_list_of_maps()` would do it all, but now it simply iterates and calls `read()` on the `MapItem`.

Copying a list of maps from one folder to another? `copy_map_files()` used to do that with the help of `get_list_of_maps()` alone, but now it also delegates tasks to `_prepare_dir_as_path()`, `_copy_and_log_map()`, and `_copy_and_log_nav()`.

# Footnotes
[^1]: I am far to lazy to use CLI for this, it's not like I need to do anything other than commits and pushes.