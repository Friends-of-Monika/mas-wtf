# keymap.rpy contains keysym mappings and (currently, subject to change)
# callbacks to these keysym with actions performed on key presses.
#
# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

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
                    message = ("{a=https://github.com/Friends-of-Monika/mas-wtf#-why-does-it-not-detect-the-submod-owning-a-topic}Could not detect submod that owns this topic{/a}, "
                               "it {i}may be{/i} an official MAS topic because "
                               "its file is located directly in {i}game/{/i} "
                               "folder.")

                elif (len(_file.split("/")) == 2 and
                      _file.lower().startswith("game/Submods")):
                    message = ("{a=https://github.com/Friends-of-Monika/mas-wtf#-why-does-it-not-detect-the-submod-owning-a-topic}Could not detect submod that owns this topic{/a}, "
                               "it is impossible to search for its header "
                               "because its file is located among other "
                               "submods in {i}game/Submods{/i} folder.")

                else:
                    message = ("{a=https://github.com/Friends-of-Monika/mas-wtf#-why-does-it-not-detect-the-submod-owning-a-topic}Could not detect what submod owns this topic{/a}, "
                               "but it seems to be located in {{i}}{0}{{/i}}."
                               .format(_file))

            else:
                submod = metadata["name"]
                version = metadata["version"]
                author = metadata["author"]

                message = ("{{a=https://github.com/Friends-of-Monika/mas-wtf#-why-does-it-say-seems-and-might-why-so-uncertain}}It seems{{/a}} that this topic is owned by {{i}}{0} v{1} "
                           "by {2}{{/i}} and it seems to be located in "
                           "{{i}}{3}{{/i}}.".format(submod, version, author,
                                                    _file))

            if bool(ev.prompt) and ev.prompt != ev.eventlabel:
                topic_title = ("The topic is called {{i}}{0}{{/i}}"
                               .format(ev.prompt))

                if ev.random:
                    topic_title += ("\nand it {a=https://github.com/Friends-of-Monika/mas-wtf#-why-does-it-say-seems-and-might-why-so-uncertain}{i}might{/i}{/a} be accessible from "
                                    "{i}Repeat conversation{/i} menu.")
                elif ev.pool:
                    topic_title += ("\nand it {a=https://github.com/Friends-of-Monika/mas-wtf#-why-does-it-say-seems-and-might-why-so-uncertain}{i}might{/i}{/a} be accessible from "
                                    "{i}Hey, [m_name]...{/i} menu.")

                else:
                    topic_title += "."

                screens.msgbox("{0}\n\n{1}".format(message, topic_title))

            else:
                screens.msgbox(message)


    config.keymap["_fom_wtf_detect"] = ["w", "?"]
    config.underlay.append(renpy.Keymap(_fom_wtf_detect=_fom_hk_wtf_detect))