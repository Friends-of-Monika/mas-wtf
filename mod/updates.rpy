label friends_of_monika_where_is_that_from_v1_0_1(version="v1_0_1"):
    return

label friends_of_monika_where_is_that_from_v1_1_0(version="v1_1_0"):
    # we messed up here :c
    return

label friends_of_monika_where_is_that_from_v1_1_1(version="v1_1_1"):
    python:
        # this should never under any circumstances possibly return
        # any other folder than: "game/Submods/Where is That From/lib"
        lib_dir = os.path.join(_fom_wtf.basedir, "lib")

        # so basically it's SAFE, HOWEVER, for good measure let's
        # make sure that we aren't targeting something too broad
        # by checking how many files will be affected:
        try:
            import os
            aff_files = sum(len(files) for _, _, files in os.walk(lib_dir))
        except Exception as e:
            # access error/whatever, we can live with some leftovers
            # than otherwise mess up the entire install for someone
            aff_files = None

        # there's exactly 13 files (excl. folders) under lib/ in v1.0.1
        if not (aff_files is None or aff_files != 13):
            # 'safe enough' to try to remove leftovers
            import shutil
            shutil.rmtree(lib_dir)

    return
