# keymap.rpy contains keysym mappings and (currently, subject to change)
# callbacks to these keysym with actions performed on key presses.
#
# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init 100 python:

    def _fom_hk_wtf_detect():
        """
        A callback for W and ? key presses that performs current topic lookup
        and passes info to respective dialog screen.
        """

        from store import _fom_wtf_search as search
        from store import _fom_wtf_screens as screens

        # Get current topic or do nothing if out of topic (in idle mode, etc.)
        ev = mas_globals.this_ev
        if ev is None:
            return

        # Perform topic location routine and pass output to screen (along with
        # event reference)
        res = search.locate_topic()
        screens.topic_info(ev, res)


    # Assign W and ? keys to the keypress callback _fom_hk_wtf_detect
    config.keymap["_fom_wtf_detect"] = ["w", "?"]
    config.underlay.append(renpy.Keymap(_fom_wtf_detect=_fom_hk_wtf_detect))