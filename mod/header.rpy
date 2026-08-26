# This file is part of Where is That From (see link below):
# https://github.com/friends-of-monika/mas-wtf

init -990 python in mas_submod_utils:
    Submod(
        author="Friends of Monika",
        name="Where is That From",
        description=_("Easily find out what submod owns a topic"),
        version="1.1.1",
        version_updates={
            "friends_of_monika_where_is_that_from_v1_0_1": "friends_of_monika_where_is_that_from_v1_1_0",
            "friends_of_monika_where_is_that_from_v1_1_0": "friends_of_monika_where_is_that_from_v1_1_1"
        }
    )

init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Where is That From",
            user_name="friends-of-monika",
            repository_name="mas-wtf",
            extraction_depth=2
        )

init -100 python in _fom_wtf:
    from store import _fom_wtf_util as util
    import store
    import os

    basedir = os.path.join(
        renpy.config.basedir,
        *util.get_script_file(fallback="game/Submods/Where is That From/mod.rpy").split("/")[:-1]
    )
