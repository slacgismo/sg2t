import marimo

__generated_with = "0.2.13"
app = marimo.App()


@app.cell
def __():
    # Requirements
    import os, sys
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt

    from sg2t.io.loadshapes.nrel.nbs import BuildStock, API
    return API, BuildStock, mo, os, pd, plt, sys


@app.cell
def __():
    from sg2t.io.loadshapes.nrel.naming import BUILDING_TYPES, HOME_TYPES
    return BUILDING_TYPES, HOME_TYPES


@app.cell
def __(BUILDING_TYPES):
    BUILDING_TYPES
    return


@app.cell
def __():
    # Configuration 
    metadata = {
        "sector" : "ResStock",
        "state" : "CA",
        "county_name" : "Alameda",
        "building_type" : "single-family_detached"
        }
    return metadata,


@app.cell
def __(API):
    ""# Create an API instance 
    api = API()
    return api,


@app.cell
def __(api, metadata):
    # Pull data first
    # Needs:
    # - By state: sector, state and building type
    # - By county: sector, state and county and building type
    # - By climate: sector, climate and building type
    dataset = api.get_data_by_county(**metadata)
    return dataset,


@app.cell
def __(BuildStock, dataset, metadata):
    res = BuildStock(data=dataset, metadata=metadata) # instantiate with dataframe with index as dt timestamp
    return res,


@app.cell
def __(res):
    res.data.head(1)
    return


@app.cell
def __(res):
    res.normalize_by_sqft() # can only do for county data (for now?)
    return


@app.cell
def __(res):
    res.data.plot(y=["out.site_energy.total.energy_consumption"])
    return


@app.cell
def __(res):
    res.data_normalized.plot(y=["out.site_energy.total.energy_consumption[kW/sf]"])
    return


@app.cell
def __():
    # by climate
    return


@app.cell
def __():
    metadata_com = {
        "sector" : "comstock",
        "climate" : "hot-dry",
        "building_type" : "largehotel"
    }

    # metadata_res = {
    #     "sector" : "ResStock",
    #     "climate" : "hot-dry",
    #     "building_type" : "single-family_detached"
    #     }
    return metadata_com,


@app.cell
def __(api, metadata_com):
    data_com_cli = api.get_data_by_climate_ba(**metadata_com)
    return data_com_cli,


@app.cell
def __(data_com_cli):
    data_com_cli
    return


@app.cell
def __(BuildStock, data_com_cli, metadata_com):
    com = BuildStock(data=data_com_cli, metadata=metadata_com)
    return com,


@app.cell
def __(com):
    com.normalize_by_sqft()
    return


@app.cell
def __():
    metadata_test = {
        "sector" : "comstock",
        "building_type" : "largehotel"
    }
    return metadata_test,


@app.cell
def __(BuildStock, data_com_cli, metadata_test):
    com_test = BuildStock(data=data_com_cli, metadata=metadata_test)
    return com_test,


@app.cell
def __():
    # the way I'm planning to do it doesn't work because I can't pass a new kwarg to get data now, can I? or maybe I can make it a new kwargs... ugh

    # doesn't make sense to have incompatible climate, but i either ask users to fix it by setting up a check (either county/state or climate in there) or I change the system
    return


app._unparsable_cell(
    r"""
    # by state
    com_state_meta = {
        \"sector\" : \"comstock\",
        \"state\" : \"MI\",
        \"building_type\" : \"largehotel\"
    }
    com_state = 
    """,
    name="__"
)


if __name__ == "__main__":
    app.run()
