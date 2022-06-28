# Poor Man's Auto Update

by Chris Bensen

![](images/pexels-miguel-Ã¡-padriÃ±Ã¡n-2882668.jpg)
[Photo by Miguel Á. Padriñán](https://www.pexels.com/photo/close-up-shot-of-keys-on-a-red-surface-2882668/)

If you prefer you can read this blog post on Medium [here](TODO).

Back in the good old day's GitHub allowed anonymous downloads. Now it requires username/password or ssh key. That's no good when the Pi is out of your control. So introducing the Chris Bensen Poor Man's Auto Update. Whatever you do do not do this at home, I am a professional and understand the security vulnerabilities.

The scenario is you have a script that runs on your Raspberry Pi and you need to update it. Let's assume your script is setup to run on boot as a chron job. You can read about setting up a chron job on a Raspberry Pi [here](https://bc-robotics.com/tutorials/setting-cron-job-raspberry-pi/).

## Steps

1. Create the local directory structure on the Pi where 'file.py' is your script.

```
/updater
├── repo
│   ├── file.py
├── file.py
├── updater.py
```

1. Copy this bash script.

[updater.sh](files/updater.sh)
```
#!/bin/bash

curl -X GET \
  <UrlToFile> \
  -o sendvid.py

file1="/users/pi/updater/repo/file.py"
file2="/users/pi/updater/file.py"

if cmp -s "$file1" "$file2"; then
    # same, do nothing
    echo "same"
else
    # different
    echo "different"
    cp $file1 $file2

    reboot
fi
```

1. Create a Oracle Cloud Object Store bucket.
1. Make that bucket public.
1. Copy your file to the bucket.
1. Edit the script by changing the <UrlToFile>. Get the URL from the Object Details and remove the file name from the end so you just have the following parts of the URL: `{accountRestEndpointURL}/{containerName}/{objectName}`
1. Edit the script so the paths are correct.
1. Setup a chron job to run `updater.py` as often as you want to check for updates. Every 5 minutes might be overkill but let's start with that. You can read about setting up a chron job on a Raspberry Pi [here](https://bc-robotics.com/tutorials/setting-cron-job-raspberry-pi/).

You can read the documentation about the downloading a file from Object Store [here](https://docs.oracle.com/en/cloud/cloud-at-customer/occ-get-started/download-file.html).

## Overview

The file `updater/repo/file.py` is the one that gets copied down. The script then compares it to the one in the updater directory. If they are different the updater directory is updated with the new one. `updater/file.py` is the one you want a symlink pointed to.

The **reboot** in `updater.py` will reboot the Pi which starts the updated `file.py` script. I know this is not the absolute best way to do this but it works and is fairly foolproof.

So there you have it, a poor man's auto update.

## Conclusion

Now I do know with OCI Object Store you can use an API for a pre-authenticated request. If you use a REST call from the Pi, you can keep the Object Store Private. However, that is additional work and I'm going to leave that for an excersise for the user, or a future post!
