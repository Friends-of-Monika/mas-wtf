init python in _fom_wtf_search:

    import store
    from store import _fom_wtf_util as util

    import os
    import unrpyc, ast
    import zlib


    def _isinstance0(v, klass):
        return v.__class__.__name__ == klass.__name__


    def scan_headers(path):
        with open(path, "rb") as f:
            try:
                script_ast = unrpyc.read_ast_from_file(f)
            except zlib.error:
                raise ValueError("not a RenPy file")

        for node in script_ast:
            if not _isinstance0(node, renpy.ast.Init):
                continue

            for stat in node.block:
                if not _isinstance0(stat, renpy.ast.Python):
                    continue

                py_ast = ast.parse(stat.code.source)
                for py_stat in py_ast.body:
                    if not (_isinstance0(py_stat, ast.Expr) and
                            _isinstance0(py_stat.value, ast.Call) and
                            py_stat.value.func.id == "Submod"):
                        continue

                    metadata = dict()
                    for keyword in py_stat.value.keywords:
                        if (keyword.arg in ["author", "name",
                                            "version", "description"] and
                            _isinstance0(keyword.value, ast.Str)):
                            metadata[keyword.arg] = keyword.value.s

                    return metadata

        return None


    def locate_topic():
        _file = util.get_script_file()
        if _file is None:
            return None

        if _file.endswith(".rpy"):
            _file += "c"

        if not os.path.exists(_file):
            return None

        metadata = scan_headers(_file)
        if metadata is None:
            if _file.split("/") > 2:
                store.mas_submod_utils.submod_log.info("{!r}".format(_file.split("/")))

                _dir = "/".join(_file.split("/")[:-1])
                store.mas_submod_utils.submod_log.info("{!r}".format(_dir))
                for curr_dir, _, files in os.walk(_dir):
                    for _sib_file in files:
                        if not _sib_file.endswith(".rpyc"):
                            continue

                        _sib_file = os.path.join(curr_dir, _sib_file)
                        store.mas_submod_utils.submod_log.info("{!r}".format(_sib_file))
                        metadata = scan_headers(_sib_file)

                        if metadata is not None:
                            return _file, metadata

        return (_file, None)