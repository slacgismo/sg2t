# This module contains data schemas defined for sg2t.
# Each application type (weather, loadshapes, etc) has its own defined
# schema for exports from sg2t.io and inputs for other applications.
import json


weather_schema = {
    "title": "Weather data",
    "type": "object",
    "properties": {
        "date": {"type": "date"},
        "time": {"type": "time"},
        "drybulb": {"type": "float"},
        "humidity": {"type": "float"},
        "wind_spd": {"type": "float"},
    },
    "required": ["date", "time", "drybulb"],
}