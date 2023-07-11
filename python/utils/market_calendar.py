from datetime import date, time, datetime, timedelta
import pandas_market_calendars as market_calendar

cal: market_calendar.MarketCalendar= market_calendar.get_calendar("NYSE")

def get_most_recent_trading_day() -> date:
    date= datetime.now().date()
    date-= timedelta(days= 1)
    trading_days= cal.valid_days(start_date= date - timedelta(days= 5), end_date= date)

    previous_trading_day= trading_days[-1]
    return previous_trading_day.date()

def is_trading_day(date: date) -> bool:
    trading_days= cal.valid_days(start_date= date, end_date= date)
    return trading_days.size == 1

def is_market_open() -> bool:
    return cal.is_open_now()

def default_closing_time() -> time:
    return cal.close_time
