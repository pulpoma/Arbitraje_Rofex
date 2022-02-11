class GetTasa():

    def __init__(self):
        import pandas as pd

        self.tasas = []
        

    @staticmethod
    def tasas_futuros(spots,futures):
        """Toma las series spot, y el df future y calcula las tasas continuas"""
        import time

        spot = spots.copy(deep=True)
        future = futures.copy(deep=True)

        for activo in future.index:
            for column in future.columns[:-2]:
                spot_t = spot[activo.split('/')[0]]
                future_t = future.loc[activo, column]
                delta_t = GetTasa.delta_days(future.loc[activo, 'year'],
                                               future.loc[activo, 'month'])
                future.loc[activo, column] = GetTasa.tasa(spot_t, future_t, delta_t)

        tasas = future
        return tasas
        
        
        
    @staticmethod
    def tasa(spot, future, t=30):
        """Calculo de Tasa Continua, si es necerario agregar funciones para otras tasas"""
        import numpy as np        

        def tasa_continua_dias(spot, future, t=30):
            tasa = np.log(future / spot) / (t / 365)
            return (tasa)

        return tasa_continua_dias(spot, future, t)

        tasa_continua_dias(spot, future, t)
    

    @staticmethod
    def delta_days(year, month):
        import calendar
        from datetime import date

        """Calculo el ultimo dia habil del mes, teniendo ano y mes como input.
        De la ultima semana del mes, toma el maximo dia de entre 0:5(lun-vier)"""
        last_business_day_in_month = date(year, month, max(calendar.monthcalendar(year, month)[-1:][0][:5]))

        def last_business_day_in_month(year, month):
            return (date(year, month, max(calendar.monthcalendar(year, month)[-1:][0][:5])))

        """Calculo el ultimo dia habil del mes, tomamos la ecuacion anterior"""
        def days_until_last_business_day(year, month):
            delta = last_business_day_in_month(year, month) - date.today()

            return (delta.days)


        return days_until_last_business_day(year, month)