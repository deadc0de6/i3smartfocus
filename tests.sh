#!/bin/sh
# author: deadc0de6 (https://github.com/deadc0de6)
# Copyright (c) 2020, deadc0de6

set -ev

pycodestyle i3smartfocus/
pyflakes i3smartfocus/
