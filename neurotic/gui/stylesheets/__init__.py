# -*- coding: utf-8 -*-
"""

"""

# based on https://github.com/Alexhuszagh/BreezeStyleSheets

# import this first to get my customizations of the stylesheets, which need to
# be rebuilt after each change using make_resources.py
from ...gui.stylesheets import stylesheets

# this module is needed for embedded assets but should be imported second so
# that embedded copies of stylesheet files do not override my changes
from ...gui.stylesheets import breeze_resources
