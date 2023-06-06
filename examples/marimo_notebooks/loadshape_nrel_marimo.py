import marimo

__generated_with = "0.0.5"
app = marimo.App()


@app.cell
def __(mo):
    mo.md("# Loadshape Interactive Tool")
    return


@app.cell
def __(by, mo, sector, view):
    mo.md(
        f"""
    ## **Sector**
        This tool supports loadshape analysis for residential and commercial buildings generated through NREL Resstock and Comstock models.


        - View by {view}{by}

        - Sector {sector}

        - View by Building Type {type} <br />

        """
    )
    return


@app.cell
def __(
    aggregation,
    by_month,
    clothes_AR,
    clothes_year,
    cooking_AR,
    cooking_year,
    day_type,
    fig1,
    heater_AR,
    heater_year,
    mo,
    study_year,
    target_year,
    timezone,
    view_month,
    water_AR,
    water_year,
):
    mo.md(
        f"""
    ## **Electrification**

        A sigmoid function is used to model the electrification adoption rates for end-uses, because it gives a characteristic 'S' shape which tends to start slow, then accelerate, and finally slow down again as it approaches an asymptote. 

        The target year, peak adoption rate year, and peak adoption rates can be changed to fit the sigmoid function. The default peak adoption rate is set to 50% at the year midway between target and initial year. 

        - **Target year to achieve 100% electrification:** {target_year}
        {mo.as_html(fig1)}

            <table style="width:30%">
      <tr>
        <th>End-use appliance</th>
        <th>Peak Adoption Year</th>
        <th>Peak Adoption Rate </th>
      </tr>
      <tr>
        <td>Space heater</td>
        <td>{heater_year} </td>
        <td>{heater_AR}%  </td>
      </tr>
      <tr>
        <td>Water heater</td>
        <td>{water_year} </td>
        <td>{water_AR}% </td>
      </tr>
      <tr>
        <td>Clothes dryer</td>
        <td>{clothes_year} </td>
        <td>{clothes_AR}% </td>
      </tr>
      <tr>
        <td>Cooking</td>
        <td>{cooking_year} </td>
        <td>{cooking_AR}% </td>
      </tr>
    </table>
        ------------------------------------------

    ## **Loadshape**
    Timezone {timezone}

    Year to get loadshape for: {study_year}

    ### Aggregation parameters

        - Season {view_month}{by_month}

        - daytype {day_type}

        - Aggregation {aggregation}
        """
    )

    return


@app.cell
def __(API, NREL_COL_MAPPING, by, checkbox_run, sector, view):
    def _format_columns_df(df):
         # rename columns using NREL_COL_MAPPING and drop the rest of the columns
        df.rename(columns=NREL_COL_MAPPING, inplace = True)
        df = df[df.columns.intersection([*NREL_COL_MAPPING.values()])]
        return df

    # Import annual energy data
    api = API()
    if sector.value == 'Resstock' and checkbox_run.value == True:
        if view.value == 'state':      
            df = api.get_data_resstock_by_state(by.value, type.value)
        elif view.value == 'climate zone - building America':
            df = api.get_data_resstock_by_climatezone(by.value, type.value)
        elif view.value == 'climate zone - iecc':
            df = api.get_data_resstock_by_climatezone_iecc(by.value, type.value)

    elif sector.value == 'Comstock' and checkbox_run.value == True:
        if view.value == 'state':      
            df = api.get_data_comstock_by_state(by.value, type.value)
        elif view.value == 'climate zone - building America':
            df = api.get_data_comstock_by_climatezone(by.value, type.value)
        elif view.value == 'climate zone - iecc':
            df = api.get_data_comstock_by_climatezone_iecc(by.value, type.value)      
    df = _format_columns_df(df)
    df = df[:-1]
    return api, df


@app.cell
def __(df):
    # step #1: calculate the total annual non-electric energy use for the different end-uses
    resstock_heating = df[['Fuel Oil Heating', 'Natural Gas Heating', 'Propane Heating']].sum(axis=1)
    resstock_water_heating = df[['Fuel Oil Hot Water','Natural Gas Hot Water','Propane Hot Water']].sum(axis=1)
    resstock_clothes_dryer = df[['Natural Gas Clothes Dryer', 'Propane Clothes Dryer']].sum(axis=1)
    resstock_oven = df[['Natural Gas Oven', 'Propane Clothes Dryer']].sum(axis=1)
    #----------------------------------------------------------------------------#
    appliance = [resstock_heating, resstock_water_heating, resstock_clothes_dryer, resstock_oven]
    return (
        appliance,
        resstock_clothes_dryer,
        resstock_heating,
        resstock_oven,
        resstock_water_heating,
    )


@app.cell
def __(
    appliance,
    clothes_AR,
    clothes_year,
    cooking_AR,
    cooking_year,
    heater_AR,
    heater_year,
    np,
    plt,
    target_year,
    water_AR,
    water_year,
):
    # implementing sigmoid function for end-uses
    def sigmoid(x, L, k, x0):
        return L / (1 + np.exp(-k*(x-x0)))

    initial_year = 2018
    new_sup = np.zeros((100,4))
    final_val = np.zeros((100,4))
    X0 = [heater_year.value, water_year.value, clothes_year.value, cooking_year.value]
    K = [heater_AR.value, water_AR.value, clothes_AR.value, cooking_AR.value]
    # applying arthemtric or geometric growth rate to achieve electrification
    for i in range(len(appliance)):
        # Initial and target value
        initial_value = appliance[i].sum()
        target_value = 1

        # Calculate parameters
        L = target_value - initial_value
        x0 = X0[i]
        k = K[i]/100  # adjust this to suit your needs

        # Generate x values
        x = np.linspace(initial_year, target_year.value, 100)

        final_val[:,i] = sigmoid(x, L, k, x0) + initial_value
        new_sup[:,i] = -sigmoid(x, L, k, x0)


    plt.plot(x, new_sup[:,0]/1e9)
    plt.axvline(x=X0[0], color='b', ls=':', label='Peak Adoption Year')
    plt.ylabel('New Supply (billion kWh)')
    plt.xlabel('year')
    plt.title('Sigmoid Adoption Rate for Space Heater End-Use Electrification')
    plt.legend()
    plt.grid()

    fig1 = plt.gca()
    return (
        K,
        L,
        X0,
        fig1,
        final_val,
        i,
        initial_value,
        initial_year,
        k,
        new_sup,
        sigmoid,
        target_value,
        x,
        x0,
    )


@app.cell
def __(
    K,
    X0,
    df,
    elec_col,
    np,
    resstock_clothes_dryer,
    resstock_heating,
    resstock_oven,
    resstock_water_heating,
    study_year,
):
    # Calculating the new supply for a given year
    year = int(study_year.value)
    new_supply = resstock_heating*(1/(1+np.exp(-K[0]/100*(year - X0[0])))) +  resstock_water_heating*(1/(1+np.exp(-K[1]/100*(year - X0[1])))) + resstock_clothes_dryer*(1/(1+np.exp(-K[2]/100*(year - X0[2])))) + resstock_oven*(1/(1+np.exp(-K[3]/100*(year - X0[3]))))

    df['New Supply'] = new_supply
    df['New Electricity Total'] = new_supply  + df[elec_col]

    return new_supply, year


@app.cell
def __(sector):
    elec_col = "Electricity Total"
    if sector.value == 'Resstock':
        non_elec_cols = ["Natural Gas Total", "Fuel Oil Total", "Propane Total"]
    elif sector.value == 'Comstock':
        non_elec_cols = ["Natural Gas Total", "District Heating Total",
                         "District Cooling Total", "Other Fuel Total"]
    return elec_col, non_elec_cols


@app.cell
def __(
    Timeseries,
    aggregation,
    day_type,
    df,
    elec_col,
    loadshape_analysis,
    mo,
    month_end,
    month_start,
    new_supply,
    np,
    pd,
    plt,
    timezone,
):
    # Aggregation loadshape
    run_this = new_supply
    df_agg = Timeseries.timeseries_aggregate(df, aggregation.value, month_start, month_end, day_type.value)

    # Time zone adjusting
    if timezone.value != 'EST':
        if timezone.value == 'CST':
            shift = -1 # hrs
        elif timezone.value == 'MST':
            shift = -2 # hrs
        elif timezone.value == 'PST':
            shift = -3 # hrs
        df_old_values = df_agg[:-shift*4]
        df_agg = df_agg.shift(periods=shift*4)
        df_agg[shift*4:] = df_old_values.values

    df_agg['hour'] = pd.date_range("00:00", "23:45", freq="15min").hour
    df_agg['minute'] = pd.date_range("00:00", "23:45", freq="15min").minute
    df_agg["Load Growth"] = (df_agg["New Supply"]/df_agg[elec_col]).values

    t = np.linspace(0,24,len(df_agg))
    # Plotting elec
    plt.plot(t, df_agg['Electricity Total']/1e3 *(60/15), label = 'Current Loadshape')
    plt.plot(t, df_agg['New Electricity Total']/1e3 *(60/15), 
             label = 'Loadshape with Electrification')
    plt.ylim(bottom=0)
    plt.xlabel('Hour (hr)')
    plt.ylabel('Power demand (MW)')
    # plt.title(str(by.value) + ' ' + str(sector.value) + ' Loadshape with Electrification - ' + str(aggregation.value) + ' over ' + str(by_month.value))
    plt.grid()
    plt.legend()

    # loadshape analysis
    # Loadshape analysis
    peak, peak_time, new_peak, new_peak_time, load_growth, supply_peak, supply_peak_time = loadshape_analysis(df_agg)

    mo.md(
        f"""
        {mo.as_html(plt.gca())}

    **Total Energy supply added from current energy consumption** = {np.round(df['New Supply'].values.sum()/1e9,1)}  TWh
    #### Loadshape Peak Analysis for Post Aggregation

    <table style="width:50%">
      <tr>
        <th>Load</th>
        <th>value</th>
        <th>unit</th>
        <th>time</th> 
      </tr>
      <tr>
        <td>current peak</td>
        <td>{np.round(peak[0],0)} </td>
        <td> MW </td>
        <td>{peak_time}</td>

      </tr>
      <tr>
        <td>new peak</td>
        <td>{np.round(new_peak[0],0)} </td>
        <td>MW </td>
        <td>{new_peak_time} </td>
      </tr>
      <tr>
        <td>new supply</td>
        <td>{np.round(supply_peak[0],0)} </td>
        <td>MW </td>
        <td>{supply_peak_time}</td>
      </tr>
      <tr>
        <td>load growth</td>
        <td>{np.round(load_growth,2)} </td>
        <td>% </td>
        <td>{new_peak_time} </td>
      </tr>
    </table>
        ------------------------------------------

        """
    )
    return (
        df_agg,
        df_old_values,
        load_growth,
        new_peak,
        new_peak_time,
        peak,
        peak_time,
        run_this,
        shift,
        supply_peak,
        supply_peak_time,
        t,
    )


@app.cell
def __():
    # Loadshape Analysis
    def loadshape_analysis(df):

        # Current peak value and timing
        current_peak = df[df['Electricity Total'] == df['Electricity Total'].max()]
        val = current_peak['Electricity Total'].values/1e3 *(60/15)
        current_peak_time = str(current_peak.hour.values[0]) + ':' +str(current_peak.minute.values[0])

        # New peak value and timing
        new_peak = df[df['New Electricity Total'] == df['New Electricity Total'].max()]
        new_val = new_peak['New Electricity Total'].values/1e3 *(60/15)
        new_peak_time = str(new_peak.hour.values[0]) + ':' + str(new_peak.minute.values[0])
        load_growth = new_peak['Load Growth'].values[0]*100
        print('New peak load value = ' + str(new_val[0]) + ' MW')
        print('New peak load time: ' + new_peak_time)

        # Greatest New Supply value and timing
        new_supply_peak = df[df['New Supply'] == df['New Supply'].max()]
        supply_val = new_supply_peak['New Supply'].values/1e3 *(60/15)
        supply_peak_time = str(new_supply_peak.hour.values[0]) + ':' + str(new_supply_peak.minute.values[0])

        return val, current_peak_time, new_val, new_peak_time, load_growth, supply_val, supply_peak_time
    return loadshape_analysis,


@app.cell
def __(BUILDING_TYPES, CLIMATE_ZONES, CLIMATE_ZONES_IECC, HOME_TYPES, mo):
    # Dropdown for main dataframe 
    climate_zone = mo.ui.dropdown(CLIMATE_ZONES, value = CLIMATE_ZONES[0])
    climate_zone_iecc = mo.ui.dropdown(CLIMATE_ZONES_IECC, value = CLIMATE_ZONES_IECC[0])
    sector =  mo.ui.dropdown(['Resstock', 'Comstock'], value = 'Resstock')
    building_type = mo.ui.dropdown(BUILDING_TYPES, value = BUILDING_TYPES[1])
    home_type =  mo.ui.dropdown(HOME_TYPES, value = HOME_TYPES[1])
    states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
               'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
               'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
               'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
               'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    state = mo.ui.dropdown(states, value = 'CA')
    view =  mo.ui.dropdown(['state', 'climate zone - building America', 
                            'climate zone - iecc'], value = 'state')
    checkbox_run = mo.ui.checkbox(True)
    return (
        building_type,
        checkbox_run,
        climate_zone,
        climate_zone_iecc,
        home_type,
        sector,
        state,
        states,
        view,
    )


@app.cell
def __(mo):
    # dropdown for electrification stuff
    target_year = mo.ui.slider(2023,2080, value=2045)
    return target_year,


@app.cell
def __(target_year):
    targ_year = target_year.value
    curr_year = 2018
    return curr_year, targ_year


@app.cell
def __(curr_year, mo, targ_year):
    heater_year = mo.ui.number(2018,2100, value=(targ_year + curr_year)/2)
    water_year = mo.ui.number(2018,2100, value=(targ_year + curr_year)/2)
    clothes_year = mo.ui.number(2018,2100, value=(targ_year + curr_year)/2)
    cooking_year = mo.ui.number(2018,2100, value=(targ_year + curr_year)/2)

    heater_AR = mo.ui.number(1,100, value=50)
    water_AR = mo.ui.number(1,100, value=50)
    clothes_AR = mo.ui.number(1,100, value=50)
    cooking_AR = mo.ui.number(1,100, value=50)
    return (
        clothes_AR,
        clothes_year,
        cooking_AR,
        cooking_year,
        heater_AR,
        heater_year,
        water_AR,
        water_year,
    )


@app.cell
def __(mo):
    # dropdown for aggregation parameters
    timezone = mo.ui.dropdown(['EST', 'CST', 'MST', 'PST'], value = 'EST')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    month = mo.ui.dropdown(months, value = months[0])
    season = mo.ui.dropdown(['winter', 'spring', 'summer', 'fall'], value = 'winter')
    view_month = mo.ui.dropdown(['by month', 'by season', 'all-year'], value = 'by month')
    day_type = mo.ui.dropdown(['weekday', 'weekend'])
    aggregation = mo.ui.dropdown(['avg', 'sum', 'peak_day'], value = 'avg')
    return (
        aggregation,
        day_type,
        month,
        months,
        season,
        timezone,
        view_month,
    )


@app.cell
def __(initial_year, mo, target_year):
    study_year = mo.ui.text(value = str(target_year.value))
    study_year = mo.ui.slider(initial_year, target_year.value)
    return study_year,


@app.cell
def __(
    building_type,
    climate_zone,
    climate_zone_iecc,
    home_type,
    sector,
    state,
    view,
):
    # Dropdown option depedency
    if view.value == 'state':
        by = state
    elif view.value == 'climate zone - building America':
        by = climate_zone
    elif view.value == 'climate zone - iecc':
        by = climate_zone_iecc

    if sector.value == 'Resstock':
        type = home_type
    elif sector.value == 'Comstock':
        type = building_type
    return by, type


@app.cell
def __(month, season, view_month):
    # month dependency 
    if view_month.value == 'by month':
        by_month = month
    elif view_month.value == 'by season':
        by_month = season
    elif view_month.value == 'all-year':
        by_month = 'all-year'
    return by_month,


@app.cell
def __(by_month, calendar, view_month):
    if view_month.value == 'by month':
        month_start = list(calendar.month_name).index(by_month.value)
        month_end = month_start + 1
    elif view_month.value == 'by season':
        if by_month.value == 'winter':
            month_start = 1
            month_end = 3
        elif by_month.value == 'spring':
            month_start = 3
            month_end = 6
        elif by_month.value == 'summer':
            month_start = 6
            month_end = 9 
        elif by_month.value == 'fall':
            month_start = 9
            month_end = 12
    elif view_month.value == 'all-year':
        month_start = 1
        month_end = 12
    return month_end, month_start


@app.cell
def __():
    # Imported packages and modules
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import marimo as mo
    import calendar

    from sg2t.io.loadshapes.nrel.api import API
    from sg2t.io.loadshapes.nrel.naming import BUILDING_TYPES, HOME_TYPES, CLIMATE_ZONES, CLIMATE_ZONES_IECC, NREL_COL_MAPPING
    from sg2t.utils.timeseries import Timeseries
    return (
        API,
        BUILDING_TYPES,
        CLIMATE_ZONES,
        CLIMATE_ZONES_IECC,
        HOME_TYPES,
        NREL_COL_MAPPING,
        Timeseries,
        calendar,
        mo,
        np,
        pd,
        plt,
    )


if __name__ == "__main__":
    app.run()
