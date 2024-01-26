
import numpy as np
import geopandas as gpd

from datetime import datetime
from metloom.pointdata import SnotelPointData



gpd.read_file()

snotel_point = SnotelPointData("713:CO:SNTL", "MyStation")
df = snotel_point.get_daily_data(
    datetime(2020, 1, 2), datetime(2020, 1, 20),
    [snotel_point.ALLOWED_VARIABLES.SWE]
)
print(df)
