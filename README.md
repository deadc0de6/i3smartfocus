[![Build Status](https://travis-ci.org/deadc0de6/i3smartfocus.svg?branch=master)](https://travis-ci.org/deadc0de6/i3smartfocus)
[![PyPI version](https://badge.fury.io/py/i3smartfocus.svg)](https://badge.fury.io/py/i3smartfocus)
[![Python](https://img.shields.io/pypi/pyversions/i3smartfocus.svg)](https://pypi.python.org/pypi/i3smartfocus)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

# i3smartfocus

`i3smartfocus` can be used in place of the default i3wm focus in order
to be able to focus in directions and bypass any the default behavior of
moving focus to the last focused window inside a container.

# Installation

**TODO**

# Usage

**TODO**

Edit i3 config `~/.config/i3/config` and replace the default focus tool
```
bindsym Mod1+Left  exec --no-startup-id "i3smartfocus left"
bindsym Mod1+Down  exec --no-startup-id "i3smartfocus down"
bindsym Mod1+Up    exec --no-startup-id "i3smartfocus up"
bindsym Mod1+Right exec --no-startup-id "i3smartfocus right"

#bindsym Mod1+Left focus left
#bindsym Mod1+Down focus down
#bindsym Mod1+Up focus up
#bindsym Mod1+Right focus right
```

# Contribution

If you are having trouble installing or using `i3smartfocus`, open an issue.

If you want to contribute, feel free to do a PR (please follow PEP8).

# License

This project is licensed under the terms of the GPLv3 license.
