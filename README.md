<p align='center'>
Robotic Process Automation Framework<b>(RPAF)</b><br>
</p>

<p align='center'>
<b>English</b> | <a href="https://github.com/antfu/vitesse/blob/main/README.zh-cn.md">简体中文</a>
</p>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Prerequisites
- python >= 3.8

## Quick start
1. clone project
```sh
git clone https://github.com/maple24/vat.git
```
2. create python virtual environment
```sh
cd vat
python -m venv .venv
```
3. activate venv and install dependencies
```sh
.venv/scripts/activate
pip install -r requirements.txt
```
4. run HelloWorld.bat and check logs in /log

## Features
- ⚙️Python code formatter with [Black](https://black.readthedocs.io/en/stable/)
- ⚡️An extremely fast Python linter [Ruff](https://beta.ruff.rs/docs/)
- 📤RQM API
- 📧Mail with smpt server
- 🤖Run test cases with [Robot Framework](https://robotframework.org/)