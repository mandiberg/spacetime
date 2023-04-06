# spacetime

Python script that extracts spatial location from EXIF data, and outputs to CSV. This implementation is meant to be used in a pipeline with NICK (https://addons.mozilla.org/en-GB/firefox/addon/nyc-idling-complaint-knowledge/)

**This is alpha software. I make absolute zero guarantees about its reliability. I was scratching my own itch. It might scratch yours, if you know how to scratch with Python.**

## what the scripts do 

gps_to_csv.py just extracts the data, and saves to CSV. It has less dependencies than gps_to_timestamp.py. 

gps_to_timestamp.py also stamps images and videos with spatial location and time. This has some kind of grumpy dependencies to ffmpeg and ImageMagick, which I found to be annoyingly difficult to set up on MacOS. This component is maybe 98% complete, but I realized I wasn't going to use that workflow, so I didn't finish it completely. It calculates and does add the stamp, but it isn't formatted, and it seems remarkably slow to export (I didn't look into ways of speeding it up). I also don't didn't address output quality/compression. 

## Okay, how do I use this?

First, I use the renameIDLEvideos.command to use exiftool to rename the files. You don't have to do this, but if you do want to, you will need to change the paths in the command (you will also have to install exiftool, but you would have to do that for spacetime anyway)

To extract address info, run "python gps_to_csv.py" from the command line. It will tell you which dependencies you need to install. If that last sentence means nothing to you, I would discourage you from trying this, as it will likely just leave you frustrated. Once you get through the dependencies, it will look for your uncompressed .MOV files into the inbox folder. If you want to keep your files somewhere else, just delete or rename the inbox folder and it will prompt you to select a folder elsewhere (this is actually how I use it -- I rename it inboxx, and then select the files from the folder I store them in.) 

## Known issues

- The timestamp is sometimes outputted in GMT. I haven't quite wrapped my head around this, but it is fairly easy to adjust for in excel. 
- Sometimes it throws an `AttributeError: 'NoneType' object has no attribute 'get'` -- this seems to happen when the Nominatum API is cranky? I banged my head against this for a while, gave up, and came back a few hours later and the script worked fine. So I think this might be some kind of externality. I could be totally wrong. 
- Open Street Map is only 95% reliable for NICK/IDLE purposes. Sometimes it will return placename information, especially for monuments, parks, named buildings -- not the street address. It will sometimes return locations that are logically correct in OSM worldview, but not what we need for NICK/IDLE workflows. And sometimes it is just wrong. Always check its work. I have included a URL to the actual OSM pin drop, so you can fix it. I find that most of these I end up fixing by specifying an intersection of two streets. 
