# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init python in _fom_wtf_screens:
    from store import Return
    import store

    # True while a dialog of ours is on screen. The keymap that brings us here
    # lives in config.underlay and therefore keeps firing inside the context
    # invoke_in_new_context() spawns below, so without this guard every further
    # keypress would stack yet another dialog on top of the visible one.
    _showing = False

    def msgbox(text):
        """
        Convenience function for calling dialog screen with specified text.
        Shows a simple info dialog window with OK button.

        Does nothing if a dialog shown by this function is already visible.
        """

        global _showing
        if _showing:
            return

        _showing = True
        try:
            renpy.invoke_in_new_context(
                renpy.call_screen, "dialog",
                message=text,
                ok_action=Return()
            )
        finally:
            _showing = False

    def topic_info(ev, res):
        """
        Shows a dialog window with respective topic info received.

        IN:
            ev -> Event:
                MAS event object for the current topic.
            res -> 2-tuple or None, see search.locate_topic() output info:
                Output of search.locate_topic() with necessary info about topic.
        """

        if res is None:
            # When output is None, locating routine didn't find a trustworthy
            # script file location and therefore we cannot tell much to user
            msgbox("Could not locate file that owns this topic.")

        else:
            # Obtain file path and metadata (may be None) from result parameter
            _file, metadata = res

            if metadata is None:
                # If no metadata found and file path has just one slash,
                # therefore it must be located directly in game/
                if len(_file.split("/")) == 2:
                    message = (
                        _("Could not detect submod that owns this topic, "
                            "it {{i}}may be{{/i}} an official MAS topic "
                            "because its file is located directly in "
                            "{{i}}game/{{/i}} folder: {{i}}{0}{{/i}}")
                        .format(_file)
                    )

                # Otherwise, check if it's in game/Submods
                elif (len(_file.split("/")) > 2 and
                    _file.lower().startswith("game/Submods")):
                    message = (
                        _("Could not detect submod that owns this topic, "
                            "it is impossible to search for its header "
                            "because its file is located among other "
                            "submods in {{i}}game/Submods{{/i}} folder: {0}")
                        .format(_file)
                    )

                # Or else fall back to some generic message
                else:
                    message = (
                        _("Could not detect what submod owns this topic, "
                            "but it seems to be located in {{i}}{0}{{/i}}.")
                        .format(_file)
                    )

            else:
                # Assign metadata to vars for brevity
                submod = metadata["name"]
                version = metadata["version"]
                author = metadata["author"]

                # Make up an informative message about topic and owning submod
                message = (
                    _("It seems that this topic is owned by {{i}}{0} v{1} "
                        "by {2}{{/i}} and it seems to be located in "
                        "{{i}}{3}{{/i}}.")
                    .format(submod, version, author, _file)
                )

            # Check if topic has event prompt and it's not empty (if it's empty,
            # it is the same as event label)
            if bool(ev.prompt) and ev.prompt != ev.eventlabel:
                # Construct a message with info
                topic_title = (
                    _("The topic is called {{i}}{0}{{/i}}")
                    .format(ev.prompt)
                )

                # If topic is random, tell so
                if ev.random:
                    topic_title += (
                        _("\nand it {i}might{/i} be accessible from "
                            "{i}Repeat conversation{/i} menu.")
                    )

                # If topic is pooled, tell so
                elif ev.pool:
                    topic_title += (
                        _("\nand it {i}might{/i} be accessible from "
                            "{i}Hey, [m_name]...{/i} menu.")
                    )

                # Else just close the message with a dot if topic prompt
                # doesn't end with punctuation
                elif ev.prompt[-1] not in (".!?"):
                    topic_title += "."

                # Show message with space between submod info and topic info
                msgbox("{0}\n\n{1}".format(message, topic_title))

            else:
                msgbox(message)
