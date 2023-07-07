### endpoints
    -websocket requests /ws/
    -api requests /api/
### json
    - trade input - {
        "account":"account name",
        "type":"buy / sell /etc",
        "stock_ticker":"ticker name (see listOfStocks.txt in python/utils)",
        "amount": int of shares,
        "user": "user name",
        "price":float of price
        }
    - position returned - {
        account: ,
        stock_ticker: ,
        amount: ,
        last_aggregation_time: ,
        last_aggregation_host:
        }