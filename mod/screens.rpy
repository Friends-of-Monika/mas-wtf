# screens.rpy contains convenience functions for working with MAS screens
# and code that performs GUI related tasks such as dialog window showing.
#
# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init python in _fom_wtf_screens:

    import store
    from store import Return


    def msgbox(text):
        renpy.invoke_in_new_context(renpy.call_screen, "dialog",
                                    message=text, ok_action=Return())


    def topic_info(ev, res):
        if res is None:
            msgbox("Could not locate file that owns this topic.")

        else:
            _file, metadata = res

            if metadata is None:
                if len(_file.split("/")) == 2:
                    message = ("Could not detect submod that owns this topic, "
                               "it {{i}}may be{{/i}} an official MAS topic "
                               "because its file is located directly in "
                               "{{i}}game/{{/i}} folder: {{i}}{0}{{/i}}"
                               .format(_file))

                elif (len(_file.split("/")) == 2 and
                      _file.lower().startswith("game/Submods")):
                    message = ("Could not detect submod that owns this topic, "
                               "it is impossible to search for its header "
                               "because its file is located among other "
                               "submods in {{i}}game/Submods{{/i}} folder: {0}"
                               .format(_file))

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

                msgbox("{0}\n\n{1}".format(message, topic_title))

            else:
                msgbox(message)