# AllStars

## Development
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
### Updating dependency packages to newest release
```
pip-compile -U
pip install -r requirements.txt
```
## Start the main application server
```
python visual/main.py
```

###
Open your browser and goto:
`localhost:9999`(Recommended)
or
`127.0.0.1:9999`
