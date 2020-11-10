from data_base_setup import DBEngine  # noqa:D100

DATABASE = DBEngine


def get_years_opening_hotels():
    dates = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute("SELECT open_date FROM hotels")
        dates = open_dates.fetchall()
    return [date[0].split('.')[2] for date in dates]
