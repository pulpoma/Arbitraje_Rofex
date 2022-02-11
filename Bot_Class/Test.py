from account_details import user, password, account
from log_in import LogIn
from get_data import GetData
from get_tasa import GetTasa


log_in_1 = LogIn(user, password, account)
get_data_1 = GetData(log_in_1, 'GGAL','YPFD','PAMP','DLR')


print(get_data_1.spot)
get_data_1.spot_df
print(get_data_1.spot)

print(get_data_1.instruments)
get_data_1.instruments_load
print(get_data_1.instruments)

print(get_data_1.future_rest)
get_data_1.future_rest_df
print(get_data_1.future_rest)

print(get_data_1.spot)
print(get_data_1.future_rest)

spot = get_data_1.spot
future = get_data_1.future_rest

get_tasa_1 = GetTasa(spot, future)
get_tasa_1.tasas_futuros
print(get_tasa_1.tasas)