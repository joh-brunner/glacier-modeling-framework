import xarray as xr

# A script to compare the output of GlacierWrite and the GlacierHistory Database

# (adjust names as needed)
thickness_file = "data/input/output_larsbreen.nc"
change_file = "debug_change.nc"
output_file = "updated_thickness.nc"

# ----------------------------
# Load datasets
# ----------------------------
ds_thickness = xr.open_dataset(thickness_file)
ds_change = xr.open_dataset(change_file)

# Assume variable names (adjust if needed)
ice_thickness_slice0 = ds_thickness["ice_thickness"].isel(t=0)
change = ds_change["dhdt"]  # or "total" if you used that earlier

# ----------------------------
# Apply change
# ----------------------------
updated_thickness = ice_thickness_slice0 + change

# ----------------------------
# Store result
# ----------------------------
ds_out = ds_thickness.copy()
ds_out["ice_thickness_updated"] = updated_thickness

# Save to disk
ds_out.to_netcdf(output_file)

print(f"Saved updated dataset to {output_file}")