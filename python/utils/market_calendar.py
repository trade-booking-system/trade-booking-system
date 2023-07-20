from datetime import date, time, datetime, timedelta
import pandas_market_calendars as market_calendar

cal: market_calendar.MarketCalendar= market_calendar.get_calendar("NYSE")

def get_most_recent_trading_day() -> date:
    date= datetime.now().date()
    date-= timedelta(days= 1)
    trading_days= cal.valid_days(start_date= date - timedelta(days= 5), end_date= date)

    previous_trading_day= trading_days[-1]
    return previous_trading_day.date()

# return all dates from starting date to end date that are valid trading days
def get_market_dates(start_date: date, end_date: date) -> list[date]:
    dates: list[date]= list()
    if start_date > end_date:
        raise ValueError("start date is later than end date")
    current_date= start_date
    while current_date <= end_date:
        if is_trading_day(current_date):
            dates.append(current_date)
        current_date= current_date +timedelta(1)
    return dates

def is_trading_day(date: date) -> bool:
    trading_days= cal.valid_days(start_date= date, end_date= date)
    return trading_days.size == 1

def default_opening_time() -> time:
    return cal.open_time

def default_closing_time() -> time:
    return cal.close_time
