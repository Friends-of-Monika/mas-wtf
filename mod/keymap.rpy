init 100 python:
    def _fom_hk_wtf_detect():
        from store import _fom_wtf_search as search
        from store import _fom_wtf_screens as screens

        if mas_globals.this_ev is None:
            return

        res = search.locate_topic()

        if res is None:
            screens.msgbox("Could not locate file that owns this topic.")

        else:
            _file, metadata = res

            if metadata is None:
                if len(_file.split("/")) == 2:
                    screens.msgbox("Could not detect submod that owns this "
                                   "topic, it may be an official MAS topic "
                                   "because its file is located directly in "
                                   "{i}game/{/i} folder.")

                elif (len(_file.split("/")) == 2 and
                      _file.lower().startswith("game/Submods")):
                    screens.msgbox("Could not detect submod that owns this "
                                   "topic, it is impossible to search for its "
                                   "header because its file is located among "
                                   "other submods in {i}game/Submods{/i} "
                                   "folder.")

                else:
                    screens.msgbox("Could not detect what submod owns this "
                                   "topic, but it seems to be located in "
                                   "{{i}}{0}{{/i}}.".format(_file))

            else:
                submod = metadata["name"]
                version = metadata["version"]
                author = metadata["author"]

                screens.msgbox("It seems that this topic is owned by "
                               "{{i}}{0} v{1} by {2}{{/i}} and it seems to be "
                               "located in {{i}}{3}{{/i}}.".format(submod,
                                                                   version,
                                                                   author,
                                                                   _file))

    config.keymap["_fom_wtf_detect"] = ["?"]
    config.underlay.append(renpy.Keymap(_fom_wtf_detect=_fom_hk_wtf_detect))