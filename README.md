# PyUpdatr

This awesome python script makes sure your mac apps are up-to-date. It works by checking the installed version of your apps in your /Applications folder and it compares with what is on MacUpdate.

This script uses libraries such as requests, BeautifulSoup and tqdm so be sure to have those installed.

Also, some known issues:

1. Some applications might have weird versions showing from MacUpdate. This most likely means the app was not found on MacUpdate and it took the first result it could find.

2. Some developers suck at keeping consistant versions with online and installed version, so you may get apps that are actually up-to-date on your computer but it doesn't show online.
