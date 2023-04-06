import pandas as pd
from typing import List, Optional

class Electrification:
    """
    class to implement electrification for loadshapes
    """

    def __init__(self):
        """"""

    @staticmethod
    def apply_electrification(df, elec_percentage, 
                            electric_col: Optional[str] = "Electricity Total", 
                            non_electric_cols: Optional[List[str]] = ["Natural Gas Total", "Propane Total", "Fuel Oil Total"]) -> pd.DataFrame:

        """ Calculates the new electric supply from electrification of non electric fuels (non_electric_cols)
            
            PARAMETERS
            ----------
            df: pd.DataFrame
                sg2t loadshape dataframe format

            elec_percentage: float
                the percentage amount of non-electric supply converted to electric load

            electric_col: str
                the name of the electric load in the df dataframe (default: "Electricity Total")

            non_electric_cols: List[str]
                list of names of the non electric load to be electrified in the df dataframe (default: ["Natural Gas Total", "Propane Total", "Fuel Oil Total"])
        
            RETURNS
            -------
            df: pd.DataFrame
                returns the same dataframe but with two extra columns: 
                    - New Supply: calcultes how much of the existing non electric energy sources are electrified (same unit as the data)
                    - Load Growth: calculates the percentage increase from the current electric load as a result of the New Supply electrification
        """
        df["New Supply"] = (df[non_electric_cols].values * elec_percentage).sum(axis=1)
        df["Load Growth"] = df["New Supply"]/df[electric_col]
        return df
