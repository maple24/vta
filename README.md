<p align='center'>
Vite Automation Test Framework<b>(VAT)</b><br>
</p>

<p align='center'>
<b>English</b> | <a href="README.zh-cn.md">简体中文</a>
</p>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features
- ⚙️Python code formatter with [Black](https://black.readthedocs.io/en/stable/)
- 🤖Run test cases with [Robot Framework](https://robotframework.org/)
- 🤝Interacting database with [SQLModel](https://sqlmodel.tiangolo.com/) [Engine](https://docs.sqlalchemy.org/en/20/core/engines.html#mysql)
- 🌽Run keywords asynchronously [GeventLibrary]https://github.com/eldaduzman/robotframework-gevent
- ⚡️An extremely fast Python linter [Ruff](https://beta.ruff.rs/docs/)
- 📤Out-of-box RQM API
- 📧Mail with smpt server
- 🏃‍♂️Delete logs automatically
- 🍉Light-weighted, less than 2MB

## Movitation
1. Run functional test with RF, which has sudo-code like sytax and can generate beautiful report automatically.
2. A pressure test is just running one functional test multiple times with no extra effort.
3. Easy to debug with out-of-box logger tools, and can be easily parsed or data-analysed afterwards.
4. Test cases are compatiable with both RF or Python.
5. Hardwares are seperated from framework which can be called with APIs.
6. Email and RQM APIs are well structured for efficient-first purpose.
7. Use built-in modules, to keep it as light-weighted as possible.
8. Remove database and data statistics from robot to let user focus on test only.

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
5. (optional) set your pythonpath for robotframework

Go to the Robot Framework Language Server extension and go to extension settings
In there you'll find: Robot > Language-server: Python

## Structure
- Helpers: pure functions/classes/apis in independent files, no relative import needed
- Managers: higher level functions which use Helpers to buildup

## Contributing
1. Fork it (https://github.com/maple24/vat.git)
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create a new Pull Request