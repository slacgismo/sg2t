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
    # Configuration 
    sector = "ResStock"
    state = "CA"
    county = "Alameda"
    return county, sector, state


@app.cell
def __(API):
    ""# Create an API instance 
    api = API()
    return api,


@app.cell
def __(api, county, state):
    # df = api.get_data_comstock_by_county(state=state, county_name=county, building_type="largehotel")

    df = api.get_data_resstock_by_county(state=state, county_name=county, building_type="single-family_detached")
    return df,


@app.cell
def __():
    #df.plot(y=["out.site_energy.total.energy_consumption"])
    return


@app.cell
def __(api):
    # to get SF for normalization
    meta = api.get_metadata("resstock") # takes a while
    return meta,


@app.cell
def __(df):
    # adjust data cols and index to prep to merge with metadata
    df.rename(columns=
            {
                "in.county": "county",
                "in.geometry_building_type_recs": "building_type", # resstock
                "in.building_type": "building_type", # comstock
            },
                inplace=True
            )
    return


@app.cell
def __(api, county, df, meta, state):
    # get SF per build type
    area = meta.groupby(["county","building_type"]).sum()
    area.columns = ["floor_area[sf]"]
    area.reset_index(inplace=True)

    # get county puma
    puma = api.get_county_gisjoin_name(county, state)

    # sort SF by county and building type
    area_ = area[area["county"]== puma]
    area_.set_index(["county","building_type"],inplace=True)

    # join data with SF metadata 
    df.reset_index(inplace=True)
    df.set_index(["county","building_type"], inplace=True)
    data = df.join(area_)

    # print(df[df["in.county"]==puma]["in.building_type"].unique())

    dt = 0.25
    columns = []
    for column in data.columns:
        if column.endswith("consumption"):
            data[column] = data[column] / data["floor_area[sf]"] / dt
        columns.append(column.replace("consumption","consumption[kW/sf]"))

    data.columns = columns
    data.drop("floor_area[sf]",axis=1,inplace=True)
    data.reset_index(inplace=True)
    data.set_index(["county","building_type","timestamp"],inplace=True)
    data.sort_index(inplace=True)
    return area, area_, column, columns, data, dt, puma


@app.cell
def __(data):
    data["out.site_energy.total.energy_consumption[kW/sf]"]
    return


@app.cell
def __(data):
    # plot and compare
    # y is power intensity
    data.plot(y=["out.site_energy.total.energy_consumption[kW/sf]"])
    return


@app.cell
def __(BuildStock, api, county, sector, state):
    # Pass through kwargs to API
    # Needs:
    # - state and building type
    # - state and county and building type
    # - climate and building type

    # if building type not provided, return all?
    ## for now, take building type and return one by one
    ## if user wants more, loops over method with diff btypes <<<<<------

    res = BuildStock(api=api, 
                     sector=sector, 
                     state=state, 
                     county=county, 
                     building_type="single-family_detached")
    return res,


@app.cell
def __(res):
    res.get_data()
    return


@app.cell
def __(county, res, state):
    res.normalize_by_sqft("resstock", county, state)
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
