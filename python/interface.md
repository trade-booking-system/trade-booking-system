## Components

### schema
- contains schemas

### listeners
- profit and loss: from tradeUpdates, positionUpdates and prices to p&l
- position: from tradeInfo to positions, positionUpdates, and p&lStocks
- price: from yahoo api to live prices

### utils
- `booktrade`: books a trade and notifies 2 services
- `booktrades_bulk`: books a list of trades
- `update_trade`: updates a trade and notifies 2 services (can only update trade on the same day it was booked)
- `get_trades`: gets all booked trades
- `query_trades`: gets trades with a specific account, year, month, and day
- `get_trade_history`: gets the full history of a specific trade
- `get_accounts`: gets a list of accounts that have trades

- `get_all_positions`: gets all positions in the database
- `get_positions`: gets all positions for a specific account
- `get_position`: gets a position given an account and tickers pair

- `get_redis_client`: gets a redis client

- `ValidTickers.__init__`: accepts a path to a text file with a ticker symbol on each line
- `ValidTickers.get_all_tickers`: returns the list of tickers
- `ValidTickers.is_valid_ticker`: returns whether the given ticker is on the list

- 'MarketCalander': deals with getting valid market dates (not created yet (subject to change slightly))
- 'get_previous_open_market_date': returns the most recent date where the market was open

### websocket
- listens to positionUpdates or tradeUpdates

## Channels:

### tradesInfo
- Format: `{account}:{ticker}:{amount}`
- Description: used by position_listener to update positions

### tradeUpdatesWS
- Format: `{type}:{json data}`

### positionUpdatesWS
- Format: `position:{json data}`

### tradeUpdates
- Format: '{account}:{ticker}:{amount}:{price}'
- Description: used to calculate trade p&l

### positionUpdates
- Format: '{account}:{ticker}'
- Description: used to calculate position p&l

### pricesUpdates
- Format: `updated`
- Description: notifies pl_listener that it should update position p&l for each stock

## Structures

### p&lStocks
- Type: set
- Data: `{account}:{ticker}`

### pnl
- Type: hash
- Name: `p&l:{account}:{ticker}`
- Key: date
- Value: Profit Loss (JSON)

### trades
- Type: hash
- Name: `trades:{account}:{date}`
- Key: id
- Value: Trade History (JSON)

### positions
- Type: hash
- Name: `positions:{account}`
- Key: ticker
- Value: Position (JSON)

### live prices
- Type: hash
- Name: `livePrices:{ticker}`
- Key: date
- Value: stock price (float)
