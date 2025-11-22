import requests


PORTFOLIO = {
    "GAZP": 40,
    "SBER": 75,
    "TATN": 17
}


url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{"TATN"}.json"
data = requests.get(url).json()
last = data["marketdata"]["data"][0][12] or data["marketdata"]["data"][1][12] 
print(last)
