import marimo

__generated_with = "0.6.22"
app = marimo.App()


@app.cell
def __(mo):
    mo.md("# Accessing NREL's ResStock and ComStock Databases")
    return


@app.cell
def __():
    #import os, sys
    import marimo as mo
    #import pandas as pd
    import matplotlib.pyplot as plt

    from sg2t.io.loadshapes.nrel.nbs import BuildStock, API
    from sg2t.io.loadshapes.nrel.naming import BUILDING_TYPES, HOME_TYPES
    return API, BUILDING_TYPES, BuildStock, HOME_TYPES, mo, plt


@app.cell
def __(mo):
    mo.md("The NREL Building Stock (NBS) `sg2t` module has two classes that deal with the data. The first one is the `API` class to access the data from the S3 bucket. The second is the `BuildStock` class that includes methods for cleaning and post-processing the data (mostly to format it to the `sg2t` standard).")
    return


@app.cell
def __(mo):
    mo.md("## Step 1: Pull the data using the API class")
    return


@app.cell
def __(mo):
    mo.md(
        """
        Currently, the API class (under `sg2t.io.loadshapes.nrel.nbs.API`) provides access to the ResStock and ComStock timeseries aggregates by state, county (for 2021 release year), and climate (Building America and IECC zones).

        You can access each with the following methods:

        ```python
        api = API()
        sector = "resstock"
        btype = "single-family_detached"

        # by state
        state = "CA"
        df = api.get_data_by_state(sector, state=state, building_type=btype)

        # by county
        county = "Alameda"
        df = api.get_data_by_county(sector, state=state, building_type=btype, county_name=county)

        # By climate (Building America)
        climate = "hot-dry"
        df = api.get_data_by_climate_ba(sector, climate=climate, building_type=btype)

        # or for IECC
        climate = "1A"
        df = api.get_data_by_climate_iecc(sector, climate=climate, building_type=btype)
        ```
        """
    )
    return


@app.cell
def __(mo):
    mo.md("The home and building types for both sectors are built into the `sg2t.io.loadshapes.nrel.naming` module as \"HOME_TYPES\" and \"BUILDING_TYPES\", respectively.")
    return


@app.cell
def __(BUILDING_TYPES, HOME_TYPES, mo):
    mo.md(
        f"""
        Residential home types:

        {HOME_TYPES},

        Commercial building types: 

        {BUILDING_TYPES}
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        """
        Working Example

        ```python
        # Create an API instance 
        api = API()

        # Configuration 
        metadata = {
            "sector" : "Resstock",
            "state" : "CA",
            "county_name" : "Alameda",
            "building_type" : HOME_TYPES[1]
            }

        # Pull data
        # Needs:
        # - By state: sector, state and building type
        # - By county: sector, state and county and building type
        # - By climate: sector, climate and building type
        dataset = api.get_data_by_county(**metadata)

        # Raw NREL data
        dataset.head(3)
        ```
        """
    )
    return


@app.cell
def __(API, HOME_TYPES):
    # Create an API instance 
    api = API()

    # Configuration 
    metadata = {
        "sector" : "Resstock",
        "state" : "CA",
        "county_name" : "Alameda",
        "building_type" : HOME_TYPES[1]
        }

    # Pull data
    # Needs:
    # - By state: sector, state and building type
    # - By county: sector, state and county and building type
    # - By climate: sector, climate and building type
    dataset = api.get_data_by_county(**metadata)
    return api, dataset, metadata


@app.cell
def __(dataset):
    # Raw NREL data
    dataset.head(3)
    return


@app.cell
def __(mo):
    mo.md("## Step 2: Using the BuildStock class")
    return


@app.cell
def __(mo):
    mo.md("This step is for when you'd like to do some data cleaning/analysis in `sg2t` (or elsewhere), e.g., normalization, cleaner column names.")
    return


@app.cell
def __(mo):
    mo.md(
        """
        ### Example
        ```python
        blds_dataset = BuildStock(data=dataset, metadata=metadata)

        # To normalize by square footage 
        blds_dataset.normalize_by_sqft();
        ```
        """
    )
    return


@app.cell
def __(BuildStock, dataset, metadata):
    blds_dataset = BuildStock(data=dataset, metadata=metadata)

    # To normalize by square footage 
    blds_dataset.normalize_by_sqft();

    blds_dataset.data_normalized.head(3)
    return blds_dataset,


@app.cell
def __(mo):
    mo.md(
        """
        To plot the energy consumption (raw)
        ```python
        blds_dataset.data.plot(y=["out.site_energy.total.energy_consumption"])
        ```
        """
    )
    return


@app.cell
def __(blds_dataset):
    blds_dataset.data.plot(y=["out.site_energy.total.energy_consumption"])
    return


@app.cell
def __(mo):
    mo.md(
        """
        To plot the normalized energy consumption
        ```python
        blds_dataset.data_normalized.plot(y=["out.site_energy.total.energy_consumption[kW/sf]"])
        ```
        """
    )
    return


@app.cell
def __(blds_dataset):
    blds_dataset.data_normalized.plot(y=["out.site_energy.total.energy_consumption[kW/sf]"])
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
