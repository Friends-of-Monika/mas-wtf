# search.rpy contains logic for locating script file and submod metadata as
# well as processing AST, both Ren'Py and Python.
#
# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init python in _fom_wtf_search:

    import store
    from store import _fom_wtf_util as util

    import os
    import unrpyc, ast
    import zlib

    from repoze_cache import lru_cache


    def __isinstance(v, klass):
        """
        Conducts simplified 'instance of' check comparing only type names.
        Due to how unrpyc operates, normal 'type(x) is y' checks aren't working
        and the only way to somehow is comparing class names.

        IN:
            v -> any:
                Value to check if is an instance of class.
            klass -> type:
                class to check for being an instance of.

        OUT:
            True:
                If value is instance of specified class.
            False:
                If not.
        """

        return v.__class__.__name__ == klass.__name__


    @lru_cache(maxsize=50)
    def scan_headers(path):
        """
        Performs decompilation of .RPYC and embedded Python AST in order to
        locate submod header in the file found at the specified path.

        IN:
            path -> str:
                Path to .RPYC file to scan.

        OUT:
            dict:
                Dictionary containing submod metadata (such as author, name,
                version, description) and field _file containing path to the
                file.
            None:
                If script file contains no submod header.

        NOTE:
            The result of this function execution is LRU-cached with maximum
            amount of cached results of 50 entries.

        RAISES:
            ValueError - in case file has no RPYC bytecode.
        """

        with open(path, "rb") as f:
            try:
                script_ast = unrpyc.read_ast_from_file(f)
            except zlib.error:
                raise ValueError("not a RenPy file")

        for node in script_ast:
            if not __isinstance(node, renpy.ast.Init):
                continue

            for stat in node.block:
                if not __isinstance(stat, renpy.ast.Python):
                    continue

                py_ast = ast.parse(stat.code.source)
                for py_stat in py_ast.body:
                    if not (__isinstance(py_stat, ast.Expr) and
                            __isinstance(py_stat.value, ast.Call) and
                            hasattr(py_stat.value.func, "id") and
                            py_stat.value.func.id == "Submod"):
                        continue

                    metadata = {"_file": path}
                    for keyword in py_stat.value.keywords:
                        if (keyword.arg in ["author", "name",
                                            "version", "description"] and
                            __isinstance(keyword.value, ast.Str)):
                            metadata[keyword.arg] = keyword.value.s

                    return metadata

        return None


    def locate_topic():
        """
        Locates the script file that contains the topic currently executing then
        performs scan for submod headers in it.

        OUT:
            tuple (file, metadata) - tuple of file path and submod metadata for
                the current topic if the script file for it was located and
                submod metadata was found.
            tuple (file, None) - tuple of file path and None if script file was
                located but submod metadata was not found.
            None - if script file for the current topic was not located.

        NOTE:
            Unless current script file is in game/ or game/Submods/ folders (and
            not in its own folder under game/Submods),  this function will
            perform recursive scan of sibling and child .RPYC files for submod
            headers. First header to be located is returned.
        """

        _file = util.get_script_file()
        if _file is None:
            return None

        if _file.endswith(".rpy"):
            _file += "c"

        if not os.path.exists(_file):
            return None

        is_structured = len(_file.split("/")) > 3

        metadata = scan_headers(_file)
        if metadata is None:
            if is_structured:
                _dir = "/".join(_file.split("/")[:-1])
                for curr_dir, _, files in os.walk(_dir):
                    for _sib_file in files:
                        if not _sib_file.endswith(".rpyc"):
                            continue

                        _sib_file = os.path.join(curr_dir, _sib_file)
                        metadata = scan_headers(_sib_file)

                        if metadata is not None:
                            return _file, metadata

        return _file, None