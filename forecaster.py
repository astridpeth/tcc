import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from datetime import timedelta, date

INITIAL_DAY = 18282

class Forecaster:
    
    def __init__(self, data: pd.DataFrame, country: str, fun, region: str = ""):
        self.fun = fun
        self.country = country
        self.region = region
        self.bounds = ((40000,10,0,0),(1000000,150,800,30000))
        self.p0 = [100000., 61, 400.,0]
        self.data = self.__filterAndGroupBy__(data)
        self.sample_size = int(self.data['Date_T'].max().astype(int))
    
    def getP0(self):
        if len(self.p0) == 4:
            return self.p0
        else:
            return self.p0[0:3]
        
    def getBounds(self):
        if len(self.bounds) == 4:
            return self.bounds
        else:
            return self.bounds[0:3]
        
    def plot(self):
       if self.__paramsAreNotNull__():
            self.__plotSimulation__()
       else:
           raise(Exception)
        
    def __filterAndGroupBy__(self, data): 
        ans = data[data['Country/Region'] == self.country]
        if self.__region__is__not_null__():
            ans = ans[ans['Province/State'] == self.region]
        ans = ans.groupby("ObservationDate",as_index=False).sum()
        ans['Date_T'] = pd.to_timedelta(ans['ObservationDate']).dt.days - INITIAL_DAY
        return ans
    
    def __region__is__not_null__(self):
        return self.region != ""
         
    def forecast(self):
        df = self.data.copy()
        x_data = np.array([x for x in df['Date_T'].tolist()])
        y_data = np.array([x for x in df['Confirmed'].tolist()])   
        ans = curve_fit(
                f = self.fun, 
                xdata = np.transpose(x_data),
                ydata = np.transpose(y_data), 
                p0 = self.getP0(),
                bounds = self.getBounds()
               ) 
        c1, c2, c3, c4 = self.__get_params__(ans[0])
        self.c1, self.c2, self.c3, self.c4 = c1, c2, c3, c4
        return c1, c2, c3, c4
    
    def __get_params__(self,ans: np.array):
        if ans.shape[0] == 3:
            c1, c2, c3 = list(ans)
            return c1, c2, c3, 0
        else:
            c1, c2, c3, c4 = list(ans)
            return c1, c2, c3, c4
    
    def __paramsAreNotNull__(self):
        return self.c1 != None and self.c2 != None and self.c3 != None and self.c4 != None
    
    def __plotSimulation__(self, size=(12,8)):
        past_forecast = self.data['ObservationDate'].append(self.data['ObservationDate'] + 
                                                       timedelta(days=self.sample_size))
        forecast = pd.DataFrame()
        forecast['Date_T'] = pd.to_timedelta(past_forecast).dt.days - INITIAL_DAY
        forecast['ObservationDate'] = past_forecast
        forecast['Confirmed'] = forecast['Date_T'].apply(
            lambda t: self.fun([t],self.c1,self.c2,self.c3,self.c4)[0])
        
        to_plot = pd.DataFrame()
        to_plot[['ObservationDate','Confirmed_forecast']] = forecast[['ObservationDate',"Confirmed"]]
        to_plot = to_plot.merge(
            self.data[['ObservationDate','Confirmed']],on='ObservationDate',how='left')
        
        to_plot.plot(x='ObservationDate',
                     y=['Confirmed','Confirmed_forecast'],
                     figsize=size,
                     title=self.country + " - " + self.region)
        plt.show()
    
