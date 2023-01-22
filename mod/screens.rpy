init python in _fom_wtf_screens:

    import store
    from store import Return

    def msgbox(text):
        renpy.invoke_in_new_context(renpy.call_screen, "dialog",
                                    message=text, ok_action=Return())