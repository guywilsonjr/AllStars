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
1. Run steps 1-3 of the Development setup
2. Check to see if a screen session is already running:
`screen -ls`
The output should either be no other screens running or something starting with the **5-digit** SESSION_ID:
`[SESSION_ID].pts-0.linuxize-desktop   (Detached)`
ex:
`10835.pts-0.linuxize-desktop   (Detached)`

3. If the screen session already exists go into it:
`screen -r [SESSION_ID]`
4. Start the program in sudo mode so we can also use port 80

5. 

