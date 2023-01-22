# lib.rpy performs Python module lookup path modifications in order to enable
# Python modules from lib/ folder.
#
# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf


init -99 python in _fom_wtf_lib:

    import store
    from store import _fom_wtf as mod

    import os
    import sys


    sys.path.append(os.path.join(mod.basedir, "lib", "unrpyc"))