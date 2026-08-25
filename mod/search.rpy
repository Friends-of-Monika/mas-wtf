# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init python in _fom_wtf_search:
    from store import _fom_wtf_util as util
    from store import _fom_wtf_metadata as meta
    import store

    # Roots shared by many submods (and MAS itself). A header declared directly
    # in one of these says nothing about its neighbours in the same folder, so
    # it may only claim the very file it was declared in.
    __SHARED_ROOTS = ("game", "game/Submods")

    def __get_dir(path):
        """
        Returns folder part of the given relative script file path.

        IN:
            path -> str:
                Relative (to DDLC folder) script file path, "/"-separated.

        OUT:
            str:
                Folder the file resides in, without trailing slash.
        """

        return "/".join(path.split("/")[:-1])

    def __find_submod(path):
        """
        Looks up the submod that owns the script file at the specified path.

        A header (the submod's Submod(...) declaration) found in the very same
        script file as the topic is taken as proof of ownership outright.

        Failing that, ownership is decided by the folder the header was found
        in: a script file belongs to the submod whose header folder contains
        it. Should several submods match (e.g. a submod shipping another submod
        in a subfolder) the one with the longest, i.e. the most specific
        header folder wins.

        The folder rule does not apply to headers declared directly in game/ or
        game/Submods/, as those roots are shared with MAS itself and with
        unrelated submods respectively: everything sitting next to such a
        header is a neighbour rather than a child of it.

        IN:
            path -> str:
                Relative (to DDLC folder) script file path, "/"-separated.

        OUT:
            tuple (Submod, str):
                Owning submod and relative path to the script file its header
                was declared in.
            None:
                If no submod claims this script file.
        """

        found = None
        found_dir = None

        for submod in store.mas_submod_utils.submod_map.values():
            source = meta.get_source(submod)
            if source is None or source[0] is None:
                # Submod was instantiated before this submod got a chance to
                # patch the Submod class, or its location was undetectable
                continue

            header_file = source[0]
            header_dir = __get_dir(header_file)

            if header_file == path:
                # Header sits in the very file the topic was declared in; this
                # is the only evidence a shared root can ever give us, and it
                # beats any folder guess, so take it and stop looking
                return submod, header_file

            if header_dir in __SHARED_ROOTS:
                # Shared root and the header is elsewhere in it: the topic is
                # a neighbour, not a child, so this submod cannot claim it
                continue

            if not path.startswith(header_dir + "/"):
                continue

            # Most specific (deepest) header folder wins
            if found_dir is None or len(header_dir) > len(found_dir):
                found, found_dir = (submod, header_file), header_dir

        return found

    def locate_topic(ev):
        """
        Locates the script file that declares the specified topic then looks up
        the submod that owns that file.

        IN:
            ev -> Event:
                MAS event object to locate.

        OUT:
            tuple (file, line, metadata) - tuple of file path, line number and
                submod metadata for the given topic if the script file for it
                was located and the owning submod was found.
            tuple (file, line, None) - tuple of file path, line number and None
                if script file was located but no submod claims it.
            None - if script file for the given topic was not located.

            Line number is None whenever it could not be determined; file path
            is never None in any of the tuples above.

        NOTE:
            Script file location comes from _fom_wtf_metadata, which records it
            at the moment the Event object is constructed. When that record is
            missing (e.g. the event was created dynamically at runtime) this
            function falls back to detecting the currently executing script
            file, which is considerably less reliable and yields no line.
        """

        source = meta.get_source(ev)
        if source is not None and source[0] is not None:
            _file, _line = source

        else:
            # No recorded declaration site, guess from current script location
            _file, _line = util.get_script_file(), None

        if _file is None:
            return None

        found = __find_submod(_file)
        if found is None:
            return _file, _line, None

        submod, header_file = found
        return _file, _line, {
            "_file": header_file,
            "name": submod.name,
            "author": submod.author,
            "version": submod.version,
            "description": submod.description
        }
