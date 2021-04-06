import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import requests #for extracting API data to python
import xlsxwriter
import math

stocks=pd.read_csv(r'C:\Users\kinye\Downloads\sp_500_stocks.csv')

#Acquire API token
IEX_CLOUD_API_TOKEN = 'Tpk_059b97af715d417d9f49f50b51b1c448'
symbol='AAPL'
api_url=f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}'
data=requests.get(api_url).json() #Status code 200 means successful
print(data)
response=requests.get(api_url)
response.content
response.text # Serialized JSON content
response.json() #Standard Dictionary content
response.headers['Content-type'] #Non-case sensitive
price=data['latestPrice']
market_cap=data['marketCap'] #2 Trillions

#Adding stocks data to pandas DataFrame
my_columns=['Ticker','Stock Price','Market Capitalization','Number of Shares to Buy']
final_dataframe=pd.DataFrame(columns=my_columns)
final_dataframe.append(pd.Series([symbol,price,market_cap,'N/A'],index=my_columns),ignore_index=True)

def append_data(symbol,final_dataframe):
    api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(api_url).json()  # Status code 200 means successful
    price = data['latestPrice']
    market_cap = data['marketCap']
    my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
    final_dataframe=final_dataframe.append(pd.Series([symbol, price, market_cap, 'N/A'], index=my_columns), ignore_index=True)
    return final_dataframe

for symbol in stocks['Ticker']:
    final_dataframe=append_data(symbol,final_dataframe) #takes forever to load

#Batch API Calls to improve performance
def chunks (lst,n): # split a list into sublist
    for i in range(0,len(lst),n):
        yield lst[i:i+n]

symbol_groups=list(chunks(stocks['Ticker'],100))
symbol_strings=[]
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

final_dataframe=pd.DataFrame(columns=my_columns)
for x in symbol_strings:
    batch_api_call_url=f'https://sandbox.iexapis.com/stable/stock/market/batch?types=quote&symbols={x}&token={IEX_CLOUD_API_TOKEN}'
    data=requests.get(batch_api_call_url).json()
    for y in x.split(','):
        final_dataframe=final_dataframe.append(pd.Series([y,data[y]['quote']['latestPrice'],
                                                          data[y]['quote']['marketCap'],'N/A'],index=my_columns)
                                               ,ignore_index=True)
#Calculating Number of shares to buy
portfolio_size=input('Enter the value of your portfolio')
try:
    val=float(portfolio_size)
except ValueError:
    portfolio_size = input('Please enter the value of your portfolio as a number')
    val=float(portfolio_size)
position_size=val/len(final_dataframe.index)
for i in range(0,len(final_dataframe.index)):
    final_dataframe.loc[i,'Number of Shares to Buy']=math.floor(position_size/final_dataframe.loc[i,'Stock Price'])

#Formatting Excel Output
writer=pd.ExcelWriter(r'C:\Users\kinye\Desktop\recommended_trades.xlsx','xlsxwriter')
final_dataframe.to_excel(writer,sheet_name='Recommended Trades',index=False)

#Changing the format for each variable
backgroup_color='#0a0a23'
font_color='#ffffff'
string_format=writer.book.add_format(
    {'font_color': font_color,
    'bg_color': backgroup_color,
     'border': 1}
)
dollar_format=writer.book.add_format(
    {'num_format':'$0.00',
     'font_color': font_color,
     'bg_color': backgroup_color,
     'border': 1}
)
integer_format=writer.book.add_format(
    {'num_format': '0',
     'font_color': font_color,
     'bg_color': backgroup_color,
     'border': 1}
)
writer.sheets['Recommended Trades'].set_column('A:A',18,string_format)
writer.sheets['Recommended Trades'].set_column('B:B',18,dollar_format)
writer.sheets['Recommended Trades'].set_column('C:C',18,dollar_format)
writer.sheets['Recommended Trades'].set_column('D:D',18,integer_format)
writer.save()

#For loop
columns_formats={
    'A':['Ticker',string_format],
    'B':['Stock Price',dollar_format],
    'C':['Market Capitalization',dollar_format],
    'D':['Number of Shares to Buy',integer_format]
}

l = 0
for x in columns_formats.keys():
    writer.sheets['Recommended Trades'].write(f'{x}1',final_dataframe.columns[l],columns_formats[x])
    l+=1
writer.save()

#Project 2
def chunks (lst,n): # split a list into sublist
    for i in range(0,len(lst),n):
        yield lst[i:i+n]
my_columns=['Ticker','Price','One-Year Price Return','Number of Shares to Buy']
symbol_groups=list(chunks(stocks['Ticker'],100))
symbol_strings=[]
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
final_dataframe=pd.DataFrame(columns=my_columns)

for x in symbol_strings:
    batch_api_call_url=f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={x}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
    data=requests.get(batch_api_call_url).json()
    for y in x.split(','):
        final_dataframe=final_dataframe.append(pd.Series([y,data[y]['price'],
                                                          data[y]['stats']["year1ChangePercent"],'N/A'],index=my_columns)
                                               ,ignore_index=True)

final_dataframe.sort_values('One-Year Price Return',ascending=False,inplace=True)
final_dataframe=final_dataframe[:50]
final_dataframe.reset_index(inplace=True)

#Calculate the number of shares to buy
def portfolio_input():
    global portfolio_size
    portfolio_size=input('Please Enter Your Portfolio Value:')
    try:
        float(portfolio_size)
    except:
        portfolio_size=input("Please enter a float or an integer: ")
portfolio_input()
position_size=float(portfolio_size)/len(final_dataframe)
final_dataframe['Number of Shares to Buy']=(position_size/final_dataframe['Price']).apply(math.floor)

#High Quality Momemtum
hqm_columns=[
    'Tickers',
    'Price',
    'Number of Shares to Buy',
    'One-Year Price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'HQM Score'
]
pd.set_option('display.max_columns',12)
hqm_dataframe=pd.DataFrame(columns=hqm_columns)
for x in symbol_strings:
    batch_api_call_url=f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={x}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
    data=requests.get(batch_api_call_url).json()
    for y in x.split(','):
        hqm_dataframe=hqm_dataframe.append(
            pd.Series([
                y,
                data[y]['price'],
                'N/A',
                data[y]['stats']['year1ChangePercent'],
                'N/A',
                data[y]['stats']['month6ChangePercent'],
                'N/A',
                data[y]['stats']['month3ChangePercent'],
                'N/A',
                data[y]['stats']['month1ChangePercent'],
                'N/A','N/A'], index=hqm_columns ),ignore_index=True)

#Calculating Momemtum Percentile
time_periods=[
    'One-Year',
    'Six-Month',
    'Three-Month',
    'One-Month'
]
hqm_dataframe.dropna(inplace=True)
for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row,f'{time_period} Return Percentile']=stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'].astype(np.float64),
                                                                                          hqm_dataframe.loc[row,f'{time_period} Price Return'])

# from statistics import mean
# for x in hqm_dataframe.index:
#     momemtum_score = []
#     for time_period in time_periods:
#         momemtum_score.append(hqm_dataframe.loc[x,f'{time_period} Return Percentile'])
#     hqm_dataframe.loc[x,'HQM Score']=mean(momemtum_score)
# is the same as code below
for x in hqm_dataframe.index:
    hqm_dataframe.loc[x,'HQM Score']=np.mean(hqm_dataframe.loc[x,[f'{time_period} Return Percentile' for time_period in time_periods]])

hqm_dataframe=hqm_dataframe.sort_values('HQM Score',ascending=False)[:50]
hqm_dataframe.reset_index(inplace=True,drop=True)

#Calculate the number of shares to buy
portfolio_input()
position_size=float(portfolio_size)/len(hqm_dataframe)
hqm_dataframe['Number of Shares to Buy']=(position_size/hqm_dataframe['Price']).apply(math.floor)

#Excel Output
writer=pd.ExcelWriter(r'C:\Users\kinye\Desktop\Momemtum_stategy.xlsx',engine="xlsxwriter")
hqm_dataframe.to_excel(writer,sheet_name='Momemtum Strategy',index=False)
writer.save()

#Project 3
def chunks (lst,n): # split a list into sublist
    for i in range(0,len(lst),n):
        yield lst[i:i+n]
symbol_groups=list(chunks(stocks['Ticker'],100))
symbol_strings=[]
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

my_columns=['Ticker','Price','Price-to-Earnings Ratio','Numbers of Shares to Buy']
final_dataframe=pd.DataFrame()
for x in symbol_strings:
    batch_api_call_url=f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={x}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data=requests.get(batch_api_call_url).json()
    for y in x.split(','):
        final_dataframe=final_dataframe.append(pd.Series([
            y,
            data[y]['quote']['latestPrice'],
            data[y]['quote']['peRatio'],
            'N/A'
        ],index=my_columns),ignore_index=True)

#Removing Glamour Stock (Opposite of 'Value stock')
final_dataframe=final_dataframe.sort_values('Price-to-Earnings Ratio')[final_dataframe['Price-to-Earnings Ratio']>0][:50]
final_dataframe.reset_index(inplace=True,drop=True)

#Calculating Number of Shares to Buy
def portfolio_input():
    global portfolio_size
    portfolio_size=input('Enter your portfolio size:')
    try:
        float(portfolio_size)
    except ValueError:
        portfolio_size=input("Please Enter An Interger: ")

portfolio_input()
position_size=float(portfolio_size)/len(final_dataframe)
final_dataframe['Numbers of Shares to Buy']=(position_size/final_dataframe['Price']).apply(math.floor)

#Building a Better Value Strategy
def chunks (lst,n): # split a list into sublist
    for i in range(0,len(lst),n):
        yield lst[i:i+n]
symbol_groups=list(chunks(stocks['Ticker'],100))
symbol_strings=[]
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
rv_columns=['Ticker',
            'Price',
            'Numbers of Shares to Buy',
            'Price-to-Earnings Ratio',
            'PE Percentile',
            'Price-to-Book Ratio',
            'PB Percentile',
            'Price-to-Sale Ratio',
            'PS Percentile',
            'EV/EBITDA',
            'EV/EBITDA Percentile',
            'EV/GP',
            'EV/GP Percentile',
            'RV'] #Robust Value
#Price-Earning Ratio
#Price-to-book Ratio
#Price-to-sales Ratio
#EV-to-EBITDA
#EV-to-Gross Profit
rv_dataframe=pd.DataFrame(columns=rv_columns)
for x in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={x}&types=advanced-stats,quote&token={IEX_CLOUD_API_TOKEN}'
    data=requests.get(batch_api_call_url).json()
    for y in x.split(","):
        try:
            EV_EBITDA=data[y]['advanced-stats']['enterpriseValue']/data[y]['advanced-stats']['EBITDA']
        except TypeError:
            EV_EBITDA=np.nan
        try:
            EV_GP=data[y]['advanced-stats']['enterpriseValue']/data[y]['advanced-stats']['grossProfit']
        except TypeError:
            EV_GP=np.nan
        rv_dataframe=rv_dataframe.append(pd.Series(
            [y,
             data[y]['quote']['latestPrice'],
             "N/A",
             data[y]['quote']['peRatio'],
            "N/A",
             data[y]['advanced-stats']['priceToBook'],
             "N/A",
             data[y]['advanced-stats']['priceToSales'],
             'N/A',
             EV_EBITDA,
             'N/A',
             EV_GP,
             'N/A',
             'N/A'
            ],index=rv_columns
        ),ignore_index=True)

rv_dataframe.dropna(inplace=True)

rvs=[
    'PE',
    'PB',
    'PS',
    'EV/EBITDA',
    'EV/GP'
]

rv_columns1=['Ticker',
            'Price',
            'Numbers of Shares to Buy',
            'PE Ratio',
            'PE Percentile',
            'PB Ratio',
            'PB Percentile',
            'PS Ratio',
            'PS Percentile',
            'EV/EBITDA Ratio',
            'EV/EBITDA Percentile',
            'EV/GP Ratio',
            'EV/GP Percentile',
            'RV']
rv_dataframe.columns=rv_columns1
for x in rv_dataframe.index:
    for y in rvs:
        rv_dataframe.loc[x,f'{y} Percentile']=stats.percentileofscore(rv_dataframe[f'{y} Ratio'].astype(np.float64),rv_dataframe.loc[x,f'{y} Ratio'])

rv_dataframe['RV']=rv_dataframe[[f'{y} Percentile' for y in rvs]].apply(np.mean,axis=1)
rv_dataframe.columns=rv_columns
rv_dataframe.sort_values('RV',ascending=True,inplace=True)
rv_dataframe.reset_index(inplace=True,drop=True)
rv_dataframe=rv_dataframe[:50]

#Calculating Number of Shares to Buy
def portfolio_input():
    global portfolio_size
    portfolio_size=input('Please Enter Your Portfolio Value:')
    try:
        float(portfolio_size)
    except:
        portfolio_size=input("Please enter a float or an integer: ")
portfolio_input()
position_size=float(portfolio_size)/len(rv_dataframe)
rv_dataframe['Numbers of Shares to Buy']=(position_size/rv_dataframe['Price']).apply(math.floor)

#Formatting Excel
writer=pd.ExcelWriter(r'C:\Users\kinye\Desktop\RobustValue.xlsx',engine='xlsxwriter')
rv_dataframe.to_excel(writer,'Value',index=False)
writer.save()


#Stock Price Prediction Using LSTM
import pandas as pd
import numpy as np
import pandas_datareader as web
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense,LSTM
import requests #for extracting API data to python
import xlsxwriter
import math

df=web.DataReader('AAPL','yahoo',start='2012-01-01', end='2019-12-17')
df
data=df.filter(['Adj Close'])
dataset=data.values
training_data_len=math.ceil(len(dataset)*0.8)
#Scale the data
scaler=MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(list(dataset))

#Split the data into x_train and y_train
train_data=scaled_data[0:training_data_len,:]
x_train=[]
y_train=[]
for i in range(60,len(train_data)):
    x_train.append(train_data[i-60:i,0])
    y_train.append(train_data[i,0])
x_train,y_train=np.array(x_train),np.array(y_train)

#Reshape the data
x_train.shape #LSTM requires 3 dimensional
x_train=np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))
model=Sequential()
model.add(LSTM(50,return_sequences=True,input_shape=(x_train.shape[1],1)))
model.add(LSTM(50,return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

#Compile the model
model.compile(optimizer='adam',loss='mean_squared_error')

#Train the model
model.fit(x_train,y_train,batch_size=1,epochs=1)

#Create the testing dataset
#Create a new array containing scaled values from index 1543 to 2003
test_data=scaled_data[training_data_len-60:,:]
x_test=[]
y_test=dataset[training_data_len:,:]
for i in range(60,len(test_data)):
    x_test.append(test_data[i-60:i,0])

#Convert the data to a numpy array
x_test=np.array(x_test)
x_test.shape
x_test=np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))

#Get the models predicted price value
predictions=model.predict(x_test)
predictions=scaler.inverse_transform(predictions)

#Get root mean squared error
rmse = np.sqrt(((predictions - y_test) ** 2).mean())

train=data[:training_data_len]
valid=data[training_data_len:]
valid['Predictions']=predictions

#Visualize
plt.figure(figsize=(16,8))
plt.title("Model")
plt.plot(train['Adj Close'])
plt.plot(valid[['Adj Close','Predictions']])
plt.legend(loc='best')
plt.show()

#Show the valid and predicted price
valid

#Get the quote
apple_quote=web.DataReader('AAPL','yahoo','2012-01-01','2019-12-17')
new_df=apple_quote.filter(['Adj Close'])
last_60_days=new_df[-60:].values
last_60_days_scaled=scaler.transform(last_60_days)
#Create an empty list
X_test=[]
X_test.append(last_60_days_scaled)
X_test=np.array(X_test)
X_test=np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
#Get the predicted scaled price
pred_price=model.predict(X_test)
pred_price=scaler.inverse_transform(pred_price)
print(pred_price)
apple_quote2=web.DataReader('AAPL','yahoo','2019-12-18','2019-12-18')
apple_quote2['Adj Close']


