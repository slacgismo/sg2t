""" This file includes name mapping and terms used for NREL's Resstock and Comstock Loadshape data anlaysis"""

CLIMATE_ZONES_BA = ("cold", "hot-dry", "hot-humid", "marine", "mixed-dry",
                                "mixed-humid", "very-cold")

CLIMATE_ZONES_IECC = ("1A", "2A", "2B", "3A", "3B", "3C", "4A", "4B", "4C", "5A", "5B", "5C", "6A", "6B", "7A", "7B", "7", "8") # https://basc.pnnl.gov/images/iecc-climate-zone-map

BUILDING_TYPES = ("fullservicerestaurant", "quickservicerestaurant", "hospital",
                               "outpatient", "largehotel", "smallhotel", "largeoffice",
                               "mediumoffice", "smalloffice", "secondaryschool", "primaryschool",
                               "retailstripmall", "retailstandalone", "warehouse")
                               
HOME_TYPES = ("mobile_home", "single-family_detached", "single-family_attached",
                             "multi-family_with_2_-_4_units", "multi-family_with_5plus_units")

NREL_COL_MAPPING= {
    "timestamp": "Datetime",
    "out.electricity.cooling.energy_consumption.kwh": "Electricity Cooling [kWh]",
    "out.electricity.heating.energy_consumption.kwh": "Electricity Heating [kWh]",
    "out.fuel_oil.heating.energy_consumption.kwh": "Fuel Oil Heating [kWh]",
    "out.natural_gas.heating.energy_consumption.kwh": "Natural Gas Heating [kWh]",
    "out.propane.heating.energy_consumption.kwh": "Propane Heating [kWh]",
    "out.natural_gas.hot_water.energy_consumption.kwh": "Natural Gas Water Heating [kWh]",
    "out.natural_gas.water_systems.energy_consumption": "Natural Gas Water Heating",
    "out.propane.hot_water.energy_consumption.kwh": "Propane Water Heating [kWh]",
    "out.propane.water_systems.energy_consumption": "Propane Water Heating",
    "out.fuel_oil.hot_water.energy_consumption.kwh": "Fuel Oil Water Heating [kWh]",
    "out.fuel_oil.water_systems.energy_consumption": "Fuel Oil Water Heating",
    "out.natural_gas.clothes_dryer.energy_consumption.kwh": "Natural Gas Clothes Dryer [kWh]",
    "out.natural_gas.clothes_dryer.energy_consumption": "Natural Gas Clothes Dryer",
    "out.propane.clothes_dryer.energy_consumption.kwh": "Propane Clothes Dryer [kWh]",
    "out.propane.clothes_dryer.energy_consumption": "Propane Clothes Dryer",
    "out.natural_gas.range_oven.energy_consumption.kwh": "Natural Gas Oven [kWh]",
    "out.natural_gas.cooking_range.energy_consumption": "Natural Gas Oven",
    "out.propane.range_oven.energy_consumption.kwh": "Propane Oven [kWh]",
    "out.propane.cooking_range.energy_consumption": "Propane Oven",
    "out.site_energy.total.energy_consumption.kwh": "Site Energy Total [kWh]",
    "out.electricity.total.energy_consumption.kwh": "Electricity Total [kWh]",
    "out.fuel_oil.total.energy_consumption.kwh": "Fuel Oil Total [kWh]",
    "out.fuel_oil.total.energy_consumption": "Fuel Oil Total",
    "out.natural_gas.total.energy_consumption.kwh": "Natural Gas Total [kWh]",
    "out.propane.total.energy_consumption.kwh": "Propane Total [kWh]",
    "out.electricity.cooling.energy_consumption": "Electricity Cooling",
    "out.electricity.heating.energy_consumption": "Electricity Heating",
    "out.fuel_oil.heating.energy_consumption": "Fuel Oil Heating",
    "out.natural_gas.heating.energy_consumption": "Natural Gas Heating",
    "out.other_fuel.heating.energy_consumption": "Other Fuel Heating",
    "out.propane.heating.energy_consumption": "Propane Heating",
    "out.natural_gas.water_systems.energy_consumption": "Natural Gas Water Heating",
    "out.other_fuel.water_systems.energy_consumption": "Other Fuel Water Heating",
    "out.site_energy.total.energy_consumption": "Site Energy Total",
    "out.district_heating.total.energy_consumption": "District Heating Total",
    "out.district_cooling.total.energy_consumption": "District Cooling Total",
    "out.electricity.total.energy_consumption": "Electricity Total",
    "out.natural_gas.total.energy_consumption": "Natural Gas Total",
    "out.other_fuel.total.energy_consumption": "Other Fuel Total",
    "out.natural_gas.interior_equipment.energy_consumption.kwh": "Natural Gas Interior Equipment [kWh]",
    "out.natural_gas.interior_equipment.energy_consumption": "Natural Gas Interior Equipment",
    "out.natural_gas.water_systems.energy_consumption.kwh": "Natural Gas Water Heating [kWh]",
    "out.other_fuel.cooling.energy_consumption.kwh": "Other Fuel Cooling [kWh]",
    "out.natural_gas.cooling.energy_consumption.kwh": "Natural Gas Cooling [kWh]",
    "out.other_fuel.cooling.energy_consumption": "Other Fuel Cooling",
    "out.natural_gas.cooling.energy_consumption": "Natural Gas Cooling",
    "out.other_fuel.interior_equipment.energy_consumption.kwh": "Other Fuel Interior Equipment [kWh]",
    "out.other_fuel.interior_equipment.energy_consumption": "Other Fuel Interior Equipment",
    "out.other_fuel.water_systems.energy_consumption.kwh": "Other Fuel Water Heating [kWh]",
    "out.other_fuel.heating.energy_consumption.kwh": "Other Fuel Heating [kWh]"
}
