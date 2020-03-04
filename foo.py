from forecaster import Forecaster
import pandas as pd
import numpy as np

covid = pd.read_csv("covid_19_data.csv")
covid["ObservationDate"] = pd.to_datetime(covid["ObservationDate"])
covid.drop(columns=["SNo"], inplace=True)

def incidence_denv(xdata, c1, c2, c3,c4 = 0):
    ans = [c1 * np.exp(-((t-c2)**2)/c3) + c4 for t in xdata]
    return ans
caster = Forecaster(covid, "Mainland China", incidence_denv)

print("Done 1")

caster.forecast()
caster.plot()