init 100 python:
    def _fom_hk_wtf_detect():
        from store import _fom_wtf_search as search
        from store import _fom_wtf_screens as screens

        ev = mas_globals.this_ev
        if ev is None:
            return

        res = search.locate_topic()

        if res is None:
            screens.msgbox("Could not locate file that owns this topic.")

        else:
            _file, metadata = res

            if metadata is None:
                if len(_file.split("/")) == 2:
                    message = ("Could not detect submod that owns this topic, "
                               "it {i}may be{/i} an official MAS topic because "
                               "its file is located directly in {i}game/{/i} "
                               "folder.")

                elif (len(_file.split("/")) == 2 and
                      _file.lower().startswith("game/Submods")):
                    message = ("Could not detect submod that owns this topic, "
                               "it is impossible to search for its header "
                               "because its file is located among other "
                               "submods in {i}game/Submods{/i} folder.")

                else:
                    message = ("Could not detect what submod owns this topic, "
                               "but it seems to be located in {{i}}{0}{{/i}}."
                               .format(_file))

            else:
                submod = metadata["name"]
                version = metadata["version"]
                author = metadata["author"]

                message = ("It seems that this topic is owned by {{i}}{0} v{1} "
                           "by {2}{{/i}} and it seems to be located in "
                           "{{i}}{3}{{/i}}.".format(submod, version, author,
                                                    _file))

            if bool(ev.prompt) and ev.prompt != ev.eventlabel:
                topic_title = ("The topic is called {{i}}{0}{{/i}}"
                               .format(ev.prompt))

                if ev.random:
                    topic_title += ("\nand it {i}might{/i} be accessible from "
                                    "{i}Repeat conversation{/i} menu.")
                elif ev.pool:
                    topic_title += ("\nand it {i}might{/i} be accessible from "
                                    "{i}Hey, [m_name]...{/i} menu.")

                else:
                    topic_title += "."

                screens.msgbox("{0}\n\n{1}".format(message, topic_title))

            else:
                screens.msgbox(message)

    config.keymap["_fom_wtf_detect"] = ["?"]
    config.underlay.append(renpy.Keymap(_fom_wtf_detect=_fom_hk_wtf_detect))