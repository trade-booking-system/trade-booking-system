from datetime import date, datetime, timedelta
import pandas_market_calendars as market_calendar

cal: market_calendar.MarketCalendar= market_calendar.get_calendar("NYSE")

def get_most_recent_trading_day() -> date:
    date= datetime.now().date()
    date-= timedelta(days= 1)
    trading_days= cal.valid_days(start_date= date - timedelta(days= 5), end_date= date)

    previous_trading_day= trading_days[-1]
    return previous_trading_day.date()

def get_dates(start_date: date, end_date: date):
    if start_date > end_date:
        raise ValueError("start date is later than end date")
    current_date= start_date
    while current_date <= end_date:
        yield current_date
        current_date= current_date +timedelta(1)

# return all dates from starting date to end date that are valid trading days
def get_market_dates(start_date: date, end_date: date) -> list[date]:
    return [date for date in get_dates(start_date, end_date) if is_trading_day(date)]

def is_trading_day(date: date) -> bool:
    trading_days= cal.valid_days(start_date= date, end_date= date)
    return trading_days.size == 1
