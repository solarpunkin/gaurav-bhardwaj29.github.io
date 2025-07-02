---
title: "Bypassing macOS code signing for ZIP-appended binaries"
tags: [zip, claude, mac]
slug: "bypassing-code-signing-zip-binaries"
---

I wanted to append a zip data to the end of a binary executable in C to create a single executable server that reads its own zip tail on launch. 

Doing this directly on my mac M2 via `cat repl site.zip > repl.app`  and `chmod +x repl.app` returned a corrupted file which did not run. 

Apparently macOS kills Mach-O binaries with appended data due to [some code signing & notarization rules](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution). 

There is a possible [workaround solution](https://stackoverflow.com/questions/1604673/how-do-i-embed-data-into-a-mac-os-x-mach-o-binary-files-text-section/1605237) that looks like it should work, instead I tried a simpler approach by creating a ‘polyglot file’ (a techie jargon for header files) which is part shell script and part binary. Claude helped me with this. Now doing `cat header.sh repl site.zip > repl.app`  works with a little catch: I have to calculate (#bytes in repl - #bytes in site.zip) and update the header.sh dynamically when either of the two files change.