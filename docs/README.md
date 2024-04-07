# Docs

docs
├── build
├── make.bat
├── Makefile
└── source
   ├── conf.py
   ├── index.rst
   ├── _static
   └──_templates
The purpose of each of these files is:

build/
The directory holds the rendered documentation.

make.bat and Makefile
Convenience scripts to simplify some common Sphinx operations, such as rendering the content.

source/conf.py
A Python script holding the configuration of the Sphinx project. It contains the project name and release you specified to sphinx-quickstart, as well as some extra configuration keys.

source/index.rst
The root document of the project, which serves as welcome page and contains the root of the “table of contents tree” (or toctree).

## How to build docs

```sh
sphinx-build -M html docs/source/ docs/build/
```
