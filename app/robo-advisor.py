from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as ticker
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()

import datetime
now = datetime.datetime.now()
import json
import csv
import requests
import os
import dotenv as de

def to_usd(my_price):
    return "${0:,.2f}".format(my_price)

def compile_URL(stock_symbol):
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + str(stock_symbol)
    return url

stock_symbol = input("Please enter the stock symbol you have in mind: ")
api_key = os.environ.get("ALPHAVANTAGE_API_KEY")

while True:
    datatype_req = True
    program_req = True
    symbol_length_req = True
    

#Input validation
    if not stock_symbol.isalpha():
        print("Please check your input. Let's try again.")
        datatype_req = False
        break
    if datatype_req == True:
        if int(len(stock_symbol)) not in range(1, 6):
            print("Please ensure that the symbol length is between 1 and 5 characters. Let's try again.")
            symbol_length_req = False
            break
        if symbol_length_req == True:
            data = requests.get(compile_URL(stock_symbol)+"&apikey={api_key}")
            if "Error" in data.text:
                print("Sorry. The symbol you have entered cannot be found online.")
                program_req = False
                break
            else:
                program_req = True
                break


request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={api_key}"
response = requests.get(request_url)
parsed_response = json.loads(response.text)
last_refreshed = parsed_response["Meta Data"]["3. Last Refreshed"]

if __name__ == "__main__":
  de.load_dotenv()
 
tsd = parsed_response["Time Series (Daily)"]

dates = list(tsd.keys())
dates.reverse()

latest_day = dates[0]
latest_close = tsd[latest_day]["4. close"]

high_prices = []
low_prices = []
close_prices = []

for date in dates:
    high_price = tsd[date]["2. high"]
    low_price = tsd[date]["3. low"]
    close_price = tsd[date]["4. close"]
    high_prices.append(float(high_price))
    low_prices.append(float(low_price))
    close_prices.append(float(close_price))

recent_high = max(high_prices)
recent_low = min(low_prices)

csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "prices.csv")

csv_headers = ["timestamp", "open", "high", "low", "close", "volume"]

with open(csv_file_path, "w") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader()
    for date in dates:
        daily_prices = tsd[date]
        writer.writerow({
            "timestamp": date,
            "open": daily_prices["1. open"],
            "high": daily_prices["2. high"],
            "low": daily_prices["3. low"],
            "close": daily_prices["4. close"],
            #"adjusted close": daily_prices["5. adjusted close"],
            "volume": daily_prices["5. volume"],
            #"dividend amount": daily_prices["7. dividend amount"],
            #"split coefficient": daily_prices["8. split coefficient"]
        })

#Recommendation
average_high = np.mean(high_prices)
if float(latest_close) >= average_high:
    decision = "DON'T BUY!"
    explanation = "The stock is overvalued - the latest closing price is equal to or higher than the average high price for the past four months."
else:
    decision = "BUY!"
    explanation = "The stock is undervalued - the latest closing price is lower than the average high price for the past four months."

print("-------------------------")
print(f"SELECTED SYMBOL: {stock_symbol}")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print("REQUEST AT: " + str(now.strftime("%Y-%m-%d %H:%M:%S")))
print("-------------------------")
print(f"LATEST DAY: {last_refreshed}")
print(f"LATEST CLOSE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")
print("-------------------------")
print("RECOMMENDATION: " + decision) 
print("RECOMMENDATION  REASON: " + explanation)
print("-------------------------")
print(f"WRITING DATA TO CSV: {csv_file_path}...")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")


#Further Challenge: Plotting Prices over Time / Data Visualization

fig = plt.figure()

ax = plt.axes()
ax.plot(dates, close_prices)
ax.xaxis.set_major_locator(MaxNLocator(4))

plt.xlabel("Dates")
plt.ylabel("Prices")

formatttt = ticker.FormatStrFormatter('$%1.2f')
ax.yaxis.set_major_formatter(formatttt)
ax.set_ylim([recent_low, recent_high])

plt.title("Stock Prices Over the Past Four Months")
plt.tight_layout()
plt.show()
