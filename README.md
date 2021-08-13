# ExprRename
![Tested on Win10-x64 with Python 3.9.6](https://img.shields.io/badge/tested-python%203.9.6%20%7C%20win10--x64-blue)

Crappy Python script to rename files with a name and a number, with the possibility to substract something from the number.  
Uses RegEx to parse filename. Allows only for 2 groups (name and number like mentioned above).  
Output filename can be slightly modified (in form: `group[separator]group`).

##Usage
1. The script can be placed anywhere and can be run from anywhere, as long as reading and writing permissions are given (unhandled error right now).  
Simply run it from the `command line/terminal` or use a `batch file` for easy use.
2. The renaming will be done in the current working dictionary.
    1. Running the script the first time will copy the `default configuration file` into the working directory. How the configuration works can be seen [below](#configuration-file).
    2. Running it with a configuration file in the working directory will execute the renaming process ([attention!](#warning)).

##Configuration file
#####Default file
```{attr.source='.numberLines'}
#~ <RegEx for file names, two groups allowed>
#~ <Formating for output: namegroup, numbergroup, "group[separator]group">
#renaming rules begin here ({} means optional)
#Form (names without extention): {[substraction number]}oldname|{subdirs/}newname
```

#####RegEx
Should cover the whole filename with extention included (`.*` at the end is enough).  
If RegEx is new to you [regexr.com](https://regexr.com/) is a good starting point.
#####Output formating
The possible groups consist of 1 and 2. In the following statement `namegroup` and `numbergroup` are a pair, as well as the two groups between the `""`. In each pair the groups should be used only once:

`namegroup, numbergroup, "group[separator]group"`  
- `namegroup`: regex group with the name used in the renaming rules
- `numbergroup`: regex group with a number. Could also be string if no substraction is planned.
- `"group[separator]group"`: The way the new filename looks without the extention. Should be pretty self-explanatory.

##Warning
I'm pretty new to Python, so it wouldn't suprise me if the code is not that good.  
It's probably also missing some exeptions and it was writen for a specific purpose, so any semblance of extensibility is only halfheartedly there and not really tested.  
(When using it, better test it on similarly named files in a test directory first before trying to rename important stuff...)