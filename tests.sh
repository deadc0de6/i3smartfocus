#!/bin/sh
# author: deadc0de6 (https://github.com/deadc0de6)
# Copyright (c) 2020, deadc0de6

set -ev

pycodestyle i3smartfocus/
pycodestyle setup.py

pyflakes i3smartfocus/
pyflakes setup.py

pylint \
  --disable=E0012 \
  i3smartfocus/
pylint \
  --disable=E0012 \
  setup.py
