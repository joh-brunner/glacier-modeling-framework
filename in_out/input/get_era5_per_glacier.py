import os
import shutil

import oggm.cfg as cfg
import oggm.utils as utils
import oggm.workflow as workflow
import oggm.tasks as tasks


RGI_ID = "RGI60-07.01044"

TEMP_WD = "temp"

OUT_FOLDER_NAME = "../../data/input"
FILES_TO_STORE = ["climate_historical.nc"]


def main():
    initialize_oggm(TEMP_WD)

    rgi_ids = utils.get_rgi_glacier_entities([RGI_ID], version="62")

    # Init glacier dir
    gdirs = workflow.init_glacier_directories(rgi_ids, reset=True, force=True)
    gdir = gdirs[0]

    cfg.PARAMS["baseline_climate"] = "ERA5"

    tasks.process_climate_data(gdir)

    # Copy the files and delete the temporary gdir
    if not os.path.exists(OUT_FOLDER_NAME):
        os.makedirs(OUT_FOLDER_NAME)
    for file in FILES_TO_STORE:
        shutil.copy(gdir.dir + "/" + file, OUT_FOLDER_NAME + "/" + file)
    shutil.rmtree(TEMP_WD)


def initialize_oggm(WD):
    # Initialize OGGM and set up the default run parameters
    cfg.initialize()

    cfg.PARAMS["continue_on_error"] = False
    cfg.PARAMS["use_multiprocessing"] = False
    cfg.PARAMS["use_intersects"] = False

    # Where to store the data for the run - should be somewhere you have access to
    cfg.PATHS["working_dir"] = WD


main()
