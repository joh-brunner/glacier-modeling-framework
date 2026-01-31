import xarray as xr
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import numpy as np

# ChatGPT script

def thickness_to_gif(
    nc_path,
    out_gif="glacier_thickness.gif",
    var="ice_thickness",
    fps=5,
    vmin=None,
    vmax=None,
    every_n=1,
):
    """
    Create a looping GIF from a 3D (t, y, x) thickness field in a NetCDF.

    Parameters
    ----------
    nc_path : str
        Path to NetCDF file.
    out_gif : str
        Output GIF filename.
    var : str
        Name of thickness variable in the NetCDF.
    fps : int
        Frames per second in the GIF.
    every_n : int
        Take every n-th timestep (for large files).
    vmin, vmax : float or None
        Optional fixed color limits for consistency.
    """

    ds = xr.open_dataset(nc_path)
    da = ds[var]

    # ensure we have a time dimension first
    if "t" not in da.dims:
        raise ValueError(f"Expected time dimension 't' in {var}")

    frames = []
    times = da["t"].values

    # set color limits if not provided
    if vmin is None:
        vmin = float(da.min())
    if vmax is None:
        vmax = float(da.max())

    for i in range(0, da.sizes["t"], every_n):
        fig, ax = plt.subplots(figsize=(6, 5))

        im = ax.imshow(
            da.isel(t=i),
            origin="lower",
            vmin=vmin,
            vmax=vmax,
            cmap="viridis",
        )

        ax.set_title(f"Larsbreen at year = {i}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        plt.colorbar(im, ax=ax, label="Ice thickness")

        # ---- FIXED CAPTURE HERE ----
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()

        buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
        buf = buf.reshape(h, w, 4)

        image = buf[:, :, [1, 2, 3]]  # drop alpha, keep RGB
        # ----------------------------

        frames.append(image)
        plt.close(fig)


    # write looping GIF
    imageio.mimsave(out_gif, frames, fps=fps, loop=0)

    print(f"Saved GIF to {out_gif}")
    ds.close()


thickness_to_gif(
    "data/output_larsbreen.nc",
    out_gif="thickness_evolution.gif",
    var="ice_thickness",
    fps=6,
    every_n=1,      # use 2, 5, ... if you have many timesteps
)
