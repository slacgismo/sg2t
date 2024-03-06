"""Class for obtaining loadshapes from the SPEECh model.
https://github.com/slacgismo/speech/tree/main.
"""

import pandas as pd
from sg2t.transportation.speech import DataSetConfigurations
from sg2t.transportation.speech import SPEECh
from sg2t.transportation.speech import SPEEChGeneralConfiguration
from sg2t.transportation.speech import Scenarios


class EV:
    def __init__(self, total_evs):
        self.total_evs = total_evs # Input number of EVs in simulation
        self.weekday_option = 'weekday'
        self.dataset = 'Original16' # 'NewData' not implemented yet
        self.path_to_data = 'inputs/'
        self.ng = 16 # default number of groups for Original16 dataset
        self.g_weights = None # weight for each group
        # self.b_weights = None # weight for each behavior
        self.config = None
        self.loadshapes = None

    def create_config(self):
        data = DataSetConfigurations(self.dataset, ng=self.ng,
                                     path_to_data=self.path_to_data)
        model = SPEECh(data)
        self.config = SPEEChGeneralConfiguration(model)
        return self.config

    def change_pg(self, new_weights=None):
        if self.config and (self.g_weights or new_weights):
            self.config.change_pg(new_weights=new_weights, dend=True)

        elif not (self.g_weights or new_weights):
            # Use a pre-set weighting:
            scenario = Scenarios('BaseCase')
            self.config.change_pg(new_weights = scenario.new_weights)

        else:
            raise("Make sure a config has been created, and g_weights have "
                  "been defined (otherwise default with be used).")

        return self.config

    def change_ps_zg(self, group, cat, weekday, new_weights):
        if self.config:
            self.config.change_ps_zg(group, cat, weekday, new_weights)

        else:
            raise("Make sure a config has been created.")

        return self.config

    def generate_loads(self, config=None):
        if not config:
            self.config = self.create_config()
        else:
            self.config = config

        self.config.num_evs(self.total_evs)
        self.config.groups()

        # Reweigh if new weights have been set
        if self.g_weights:
            self.change_pg()
        # if self.b_weights: # TODO
        #     self.change_ps_zg()

        self.config.run_all(weekday=self.weekday_option)

        self.loadshapes = self._format_data(self.config.total_load_dict)

        return self.loadshapes

    def _format_data(self, loadshapes):
        loadshapes = pd.DataFrame.from_dict(loadshapes)
        loadshapes["Datetime"] = (
                pd.Timestamp('2023-3-01') +
                pd.to_timedelta(loadshapes.index, unit='m')
        )
        loadshapes.set_index('Datetime', inplace=True)
        loadshapes = loadshapes.resample('h').mean()
        loadshapes["Hour"] = pd.date_range("00:00", "23:45", freq="1H").hour
        loadshapes.set_index('Hour', inplace=True)
        return loadshapes
