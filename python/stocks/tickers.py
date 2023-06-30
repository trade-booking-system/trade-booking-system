import json

class ValidTickers:

    def __init__(self, filename: str):
        self.valid_tickers= self.parse_file(filename)

    def parse_file(self, filename) -> set[str]:
        tickers= set()
        file= open(filename, "r")
        stock_info= json.load(file)
        file.close()
        for stock in stock_info:
            tickers.add(stock["Symbol"])
        return tickers

    def get_all_tickers(self) -> set[str]:
        return self.valid_tickers

    def is_valid_ticker(self, stock_ticker: str) -> bool:
        return stock_ticker in self.valid_tickers
