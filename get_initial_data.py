# This script uses the OGGM shop to generate a nc-file containing initial data for both IGM and OGGM
# We do not need any duplicate fields, because the individual nc files for forward simulations are created later on
# The initial geometries include data from Farinotti, Millan and Cook from the OGGM shop (where available)
# Code is based on Fabien Maussion's code in IGM oggm shop module
print("Script started")
import json
import os
import shutil
import subprocess

import sys
import numpy as np
import oggm.cfg as cfg
import oggm.utils as utils
import oggm.workflow as workflow
import oggm.tasks as tasks
import xarray as xr

# Import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if len(sys.argv) <= 1:
    RGI_ID = "RGI60-11.01450"
else:
    RGI_ID = sys.argv[1]

NO_SPINUP_URL = "https://cluster.klima.uni-bremen.de/~oggm/gdirs/oggm_v1.6/L3-L5_files/2023.3/elev_bands/W5E5"

TEMP_WD = "temp"

OUT_FOLDER_NAME = "data"
FILES_TO_STORE = ["gridded_data.nc"]


def main():

    initialize_oggm(TEMP_WD)

    rgi_ids = get_outlines()

    # Init glacier dir
    gdirs = workflow.init_glacier_directories(rgi_ids, reset=True, force=True)
    gdir = gdirs[0]

    # Grid and DEM
    tasks.define_glacier_region(gdir, source="DEM3")
    tasks.simple_glacier_masks(gdir)

    # Consensus, Millan, Cook
    add_thicknesses_from_shop(gdirs)
    add_additional_data_for_igm_inversion(gdirs)

    # Set all thicknesses to NAN outside the mask
    set_outside_to_nan(gdir)

    # Rename cook var so that every thickness field contains three words
    rename_cook_var(gdir)

    # Add dx info to gridded_data.nc
    add_dx(gdir)

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


def get_outlines():
    rgi_ids = utils.get_rgi_glacier_entities([RGI_ID], version="62")
    return rgi_ids


def add_thicknesses_from_shop(gdirs):

    from oggm.shop.millan22 import thickness_to_gdir

    try:
        workflow.execute_entity_task(thickness_to_gdir, gdirs)

    except ValueError:
        print("No millan22 thk data available!")

    from oggm.shop import bedtopo

    workflow.execute_entity_task(bedtopo.add_consensus_thickness, gdirs)

    if gdirs[0].rgi_region == "11":
        from oggm.shop import cook23

        workflow.execute_entity_task(cook23.cook23_to_gdir, gdirs, vars=["thk"])


def add_additional_data_for_igm_inversion(gdirs):
    from oggm.shop import hugonnet_maps

    workflow.execute_entity_task(hugonnet_maps.hugonnet_to_gdir, gdirs)

    from oggm.shop.millan22 import velocity_to_gdir

    workflow.execute_entity_task(velocity_to_gdir, gdirs)


def set_outside_to_nan(gdir):
    ds_res = xr.open_dataset(gdir.dir + "/gridded_data.nc", mode="r+")
    ds_res["millan_ice_thickness"] = ds_res["millan_ice_thickness"].where(ds_res["glacier_mask"] != 0, np.nan)

    if "cook23_thk" in ds_res:
        ds_res["cook23_thk"] = ds_res["cook23_thk"].where(ds_res["glacier_mask"] != 0, np.nan)
    ds_res.to_netcdf(gdir.dir + "/gridded_data.nc", mode="a")
    ds_res.close()


def rename_cook_var(gdir):
    ds = xr.open_dataset(gdir.dir + "/gridded_data.nc", mode="r+")
    ds.load()  # Load all into memory
    ds.close()  # Close file handle before overwriting

    if "cook23_thk" in ds:
        ds = ds.rename({"cook23_thk": "cook23_ice_thickness"})

    ds.to_netcdf(gdir.dir + "/gridded_data.nc", mode="w")


def add_dx(gdir):
    ds = xr.open_dataset(gdir.dir + "/gridded_data.nc", mode="r+")
    ds.load()  # Load all into memory

    with open(gdir.dir + "/glacier_grid.json") as f:
        grid = json.load(f)

    dx, dy = grid["dxdy"]

    ds.attrs["dx"] = str(dx)
    ds.close()  # Close file handle before overwriting
    ds.to_netcdf(gdir.dir + "/gridded_data.nc", mode="w")


main()
