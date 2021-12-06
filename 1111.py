import FinanceDataReader as fdr 
import pandas as pd
import csv

stocks = fdr.StockListing('KOSPI')

print(stocks.info())

stock = stocks.iloc[:,0:3]
stock.to_csv('C:\work\kospi.csv', index=False, encoding='cp949')

#js = stock.to_json("C:\work\kosdaq.json",orient = 'columns',  ensure_ascii=False)


#print(stock)
#f = open("Kosdaq.csv", "w")
#writer = csv.writer(f)



"""
for row in stock:
    writer.writerow(row) ## 여기 주목!

f.close()
"""