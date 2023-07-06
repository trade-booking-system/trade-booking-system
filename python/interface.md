## Components

### schema
- contains schemas

### listeners
- profit and loss: from tradeInfo and prices to pnl
- position: from updatePositions to positions, positionUpdates, and p&lStocks
- price: from yahoo api to live prices and snapshot prices

### utils
- `booktrade`: books a trade and notifies services
- `booktrades_bulk`: books a list of trades
- `update_trade`: updates a trade and notifies services
- `get_trades`: gets all booked trades
- `query_trades`: gets trades with a specific account, year, month, and day
- `get_trade_history`: gets the full history of a specific trade
- `get_accounts`: gets a list of accounts that have trades

- `get_all_positions`: gets all positions in the database
- `get_positions`: gets all positions for a specific account
- `get_position`: gets a position given an account and tickers pair

- `get_redis_client`: gets a redis client (use this in the listeners as well?)

- `ValidTickers.__init__`: accepts a path to a text file with a ticker symbol on each line
- `ValidTickers.get_all_tickers`: returns the list of tickers
- `ValidTickers.is_valid_ticker`: returns whether the given ticker is on the list

### websocket
- listens to positionUpdates or tradeUpdates

## Channels:

### updatePositions
- Format: `{account}:{ticker}:{amount}:{price}`
- (Alias: tradeInfo)

### tradeUpdates
- Format: `{type}: {json data}`

### positionUpdates
- Format: `position:{json data}`

### prices
- Format: `updated`

## Structures

### p&lStocks
- Type: set
- Data: `{account}:{ticker}`

### pnl
- Type: hash
- Name: `p&l:{account}:{ticker}`
- Key: realize | unrealized
- Value: pnl (float)

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
- Type: flat
- Key: `livePrices:{ticker}`
- Value: stock price (float)

### snapshot prices
- Type: hash
- Name: `snapshotPrices:{ticker}:{date}`
- Key: time
- Value: stock price (float)
