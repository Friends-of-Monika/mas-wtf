# screens.rpy contains convenience functions for working with MAS screens.
#
# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init python in _fom_wtf_screens:

    import store
    from store import Return


    def msgbox(text):
        renpy.invoke_in_new_context(renpy.call_screen, "dialog",
                                    message=text, ok_action=Return())