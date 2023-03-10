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
        and the only way to somehow check instance of is comparing class names.

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
                # Use UNRPYC to read Ren'Py AST from the .RPYC file
                script_ast = unrpyc.read_ast_from_file(f)
            except zlib.error:
                # .RPYC files are GZip compressed, hence the error
                raise ValueError("not a RenPy file")

        for node in script_ast:
            # Looking for 'init python' nodes only
            if not __isinstance(node, renpy.ast.Init):
                continue

            for stat in node.block:
                # Init blocks may be Ren'Py inits, we only need Python
                if not __isinstance(stat, renpy.ast.Python):
                    continue

                # Parse Python AST
                py_ast = ast.parse(stat.code.source)
                for py_stat in py_ast.body:
                    # Look for call expressions like Submod(...) which are
                    # submod header declarations
                    if not (__isinstance(py_stat, ast.Expr) and
                            __isinstance(py_stat.value, ast.Call) and
                            hasattr(py_stat.value.func, "id") and
                            py_stat.value.func.id == "Submod"):
                        continue

                    # Loop over keyword parameters passed to it
                    # TODO: See if there is a possibility of them being
                    # positional, in which case account for that too
                    metadata = {"_file": path}
                    for keyword in py_stat.value.keywords:
                        # Only author, name, version and description are
                        # strings, ignore all the rest and those of them
                        # that aren't simply string literals
                        if (keyword.arg in ["author", "name",
                                            "version", "description"] and
                            __isinstance(keyword.value, ast.Str)):
                            # Save the value of string literal
                            metadata[keyword.arg] = keyword.value.s

                    # Return first found header
                    return metadata

        # No submod headers found
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

        # Only working with .RPYC
        if _file.endswith(".rpy"):
            _file += "c"

        # If the file we look for doesn't exist we cannot work with it obviously
        if not os.path.exists(_file):
            return None

        # Structured are those submods that are located under game/Submods/ in
        # their own folder
        is_structured = len(_file.split("/")) > 3

        # Try to scan header from the script file itself, if not found and
        # submod is well structured try to look around for them recursively
        metadata = scan_headers(_file)
        if metadata is None:
            if is_structured:
                # Get folder of the script file and walk around it
                _dir = "/".join(_file.split("/")[:-1])
                for curr_dir, _, files in os.walk(_dir):
                    for _sib_file in files:
                        # Only need .RPYC files
                        if not _sib_file.endswith(".rpyc"):
                            continue

                        # Join file paths and scan for headers in it
                        _sib_file = os.path.join(curr_dir, _sib_file)
                        metadata = scan_headers(_sib_file)

                        # If file contains a valid header return it right away
                        if metadata is not None:
                            return _file, metadata

        # If .RPY source file exists for this .RPYC, return path to original
        # file (.RPY not .RPYC) for user's reading/editing convenience
        if os.path.exists(_file[:-1]):
            return _file[:-1], None

        # Or else return bytecode file
        return _file, None