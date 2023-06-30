import json

class ValidTickers:

    def __init__(self, filename: str):
        self.valid_tickers= self.parse_file(filename)

    def parse_file(self, filename) -> list[str]:
        file= open(filename, "r")
        data= file.read()
        file.close()
        tickers= data.splitlines()
        return tickers

    def get_all_tickers(self) -> list[str]:
        return self.valid_tickers

    def is_valid_ticker(self, stock_ticker: str) -> bool:
        return stock_ticker in self.valid_tickers
