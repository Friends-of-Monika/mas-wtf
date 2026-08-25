# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init -1000 python in _fom_wtf_metadata:
    from store import renpy
    import store
    import functools

    __SOURCES = {}

    def get_source(obj):
        return __SOURCES.get(obj, None)

    def wrap_set_source(fn):
        @functools.wraps(fn)
        def wrapped_init(self, *args, **kwargs):
            try:
                sourcefile = store._fom_wtf_util.get_script_file()
            except Exception:
                # get_filename_line() is unstable and may give us nothing
                # usable at all; a missing source beats a broken __init__
                sourcefile = None
            sourceline = (renpy.get_filename_line() or (None, None))[1]
            source     = (sourcefile, sourceline)
            try:
                retval = fn(self, *args, **kwargs)
                __SOURCES[self] = source
                return retval
            finally:
                pass
        return wrapped_init

init -998 python in fom_wtf:
    def get_source(obj):
        from store._fom_wtf_metadata import get_source
        return get_source(obj)

init -1000 python in _fom_wtf_metadata:
    from store import Event # python early
    Event.__init__ = wrap_set_source(Event.__init__)

init -991 python in _fom_wtf_metadata:
    def handle_python_execute_init(self):
        # we can't intercept Submod class definition at level -990 before
        # other submods instantiate it, so we have to tap into 'init python'
        # invocations and keep listening until we suddenly find that
        # mas_submod_utils store has Submod class defined
        if hasattr(renpy.store.mas_submod_utils, "Submod"):
            Submod = renpy.store.mas_submod_utils.Submod
            Submod.__init__ = wrap_set_source(Submod.__init__)
            unpatch_python_execute_init() # early exit

    patch_python_execute_init(handle_python_execute_init)

init -989 python in _fom_wtf_metadata:
    unpatch_python_execute_init()

init -999 python in _fom_wtf_metadata:
    __ORIGINAL_python_execute_init = renpy.ast.Python.execute

    def patch_python_execute_init(fn):
        @functools.wraps(__ORIGINAL_python_execute_init)
        def wrapped_python_execute_init(self):
            retval = __ORIGINAL_python_execute_init(self)
            fn(self)
            return retval
        renpy.ast.Python.execute = wrapped_python_execute_init

    def unpatch_python_execute_init():
        renpy.ast.Python.execute = __ORIGINAL_python_execute_init
