""" This file includes name mapping and terms used for NREL's Resstock and Comstock Loadshape data anlaysis"""

CLIMATE_ZONES = ("cold", "hot-dry", "hot-humid", "marine", "mixed-dry",
                                "mixed-humid", "very-cold")

BUILDING_TYPES = ("fullservicerestaurant", "quickservicerestaurant", "hospital",
                               "outpatient", "largehotel", "smallhotel", "largeoffice",
                               "mediumoffice", "smalloffice", "secondaryschool", "primaryschool",
                               "retailstripmall", "retailstandalone", "warehouse")
                               
HOME_TYPES = ("mobile_home", "single-family_detached", "single-family_attached",
                             "multi-family_with_2_-_4_units", "multi-family_with_5plus_units")

NREL_COL_MAPPING= {
    "timestamp": "Datetime",
    "out.electricity.cooling.energy_consumption.kwh": "Electricity Cooling",
    "out.electricity.heating.energy_consumption.kwh": "Electricity Heating",
    "out.fuel_oil.heating.energy_consumption.kwh": "Fuel Oil Heating",
    "out.natural_gas.heating.energy_consumption.kwh": "Natural Gas Heating",
    "out.propane.heating.energy_consumption.kwh": "Propane Heating",
    "out.site_energy.total.energy_consumption.kwh": "Site Energy Total",
    "out.electricity.total.energy_consumption.kwh": "Electricity Total",
    "out.fuel_oil.total.energy_consumption.kwh": "Fuel Oil Total",
    "out.natural_gas.total.energy_consumption.kwh": "Natural Gas Total",
    "out.propane.total.energy_consumption.kwh": "Propane Total",
    "out.electricity.cooling.energy_consumption": "Electricity Cooling",
    "out.electricity.heating.energy_consumption": "Electricity Heating",
    "out.fuel_oil.heating.energy_consumption": "Fuel Oil Heating",
    "out.natural_gas.heating.energy_consumption": "Natural Gas Heating",
    "out.propane.heating.energy_consumption": "Propane Heating",
    "out.site_energy.total.energy_consumption": "Site Energy Total",
    "out.electricity.total.energy_consumption": "Electricity Total",
    "out.fuel_oil.total.energy_consumption": "Fuel Oil Total",
    "out.natural_gas.total.energy_consumption": "Natural Gas Total",
    "out.propane.total.energy_consumption": "Propane Total"
}