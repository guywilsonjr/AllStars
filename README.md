# AllStars

## Development Setup
From the root directory of this repository do the following:
1. Create a python virtual env (venv)

`python3.10 -m venv .venv`

2. Activate the virtual env

`source .venv/bin/activate`

3. Install dev and regular requirements


```
pip install -U pip setuptools wheel
pip install -r requirements-dev.txt
pip install -r requirements.txt
```
### [VERY OPTIONAL] Updating dependency packages to newest release
Before messing around here I highly recommend reading or understanding the material in the article [Pip-tools for Cross-OS development](https://medium.com/@crawftv/pip-tools-for-cross-os-development-194b33da9c0d)
```
pip-compile -U
pip install -r requirements.txt
```

4.
### Start the main application server
```
python visual/main.py
```

Open your browser and goto:
`localhost:80`(Recommended)
or
`127.0.0.1:80`

## Non-Development Instructions for Server start
We make use of the **important** screen to keep our terminal session commands from dying when we disconnect. [Why we use screen and why it's important!](https://linuxize.com/post/how-to-use-linux-screen/)
**For only code updates skip to last step**
2. Run steps 1-3 of the Development setup
3. [Only needed once]Move the service config file called `allstars.service` to the folder `/etc/systemd/system`. The command **might** be something like:
`sudo cp allstars.service /etc/systemd/system`
4. Refresh systemd whenever you make a change to the file and want to update that file
`sudo systemctl daemon-reload`
5. Start the service
`sudo service allstars restart`
