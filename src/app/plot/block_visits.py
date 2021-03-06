import datetime
import functools

from bokeh.models import Range1d
from app import db
from app.plot.plot import DialPlot
from app.plot.queries import DateRangeQueries
from app.plot.util import daily_bar_plot, day_range, day_running_average,\
                          monthly_bar_plot, month_range, month_running_average,\
                          value_last_night, value_last_week


class BlockVisitPlots:
    """Plots displaying the number of block visits.

    Params:
    -------
    date : datetime.date
        The date for which to generate the plots.
    **kwargs: keyword arguments
        Additional keyword arguments are passed on to the function or constructor creating a plot.
    """

    def __init__(self, date, **kwargs):
        self.date = date
        start = self.date - datetime.timedelta(days=300)
        end = self.date + datetime.timedelta(days=150)

        self.kwargs = kwargs

        self.df = DateRangeQueries(start, end, db.engine).block_visits()

    def last_night_plot(self):
        """Dial plot displaying the number of block visits for the date preceding `self.date`.

        Returns:
        --------
        app.plot.plot.DialPlot
            Plot for last night's number of block visits.
        """

        block_visits = value_last_night(df=self.df, date=self.date, date_column='Date', value_column='BlockCount')
        return DialPlot(values=[block_visits],
                        label_values=range(0, 13),
                        dial_color_func=lambda d: '#7f7f7f',
                        display_values=[str(block_visits)],
                        **self.kwargs)

    def week_to_date_plot(self):
        """Dial plot displaying the number of block visits in the seven days leading up to but excluding `self.date`.

        Returns:
        --------
        app.plot.plot.DialPlot
            Plot displaying the number of block visits for the last seven days.
        """

        block_visits = value_last_week(df=self.df, date=self.date, date_column='Date', value_column='BlockCount')
        return DialPlot(values=[block_visits],
                        label_values=range(0, 71, 10),
                        dial_color_func=lambda d: '#7f7f7f',
                        display_values=[str(block_visits)],
                        **self.kwargs)

    def daily_plot(self, days):
        """Bar plot displaying the number of block visits per day.

        The number of block visits is shown for the `days` days leading to but excluding `self.date`. A day here refers
        to the time from noon to noon. For example, 22 May 2016 refers to the period from 22 May 2016, 12:00 to 23 May
        2016, 12:00.

        Params:
        -------
        days : int
            Number of days.

        Returns:
        --------
        app.plot.plot.TimeBarPlot
            Plot of number of block visits as a function of the day.
        """

        start_date, end_date = day_range(self.date, days)
        trend_func = functools.partial(day_running_average, ignore_missing_values=False)

        return daily_bar_plot(df=self.df,
                              start_date=start_date,
                              end_date=end_date,
                              date_column='Date',
                              y_column='BlockCount',
                              y_range=Range1d(start=0, end=30),
                              trend_func=trend_func,
                              **self.kwargs)

    def monthly_plot(self, months):
        """Bar plot displaying the number of block visits per momth.

        The number of block visits is shown for the `months` months leading to but excluding the month containing
        `self.date`. A month here refers start at noon of the first of the month. For example,  May 2016 refers to the
        period from 1 May 2016, 12:00 to 1 June 2016, 12:00.

        Params:
        -------
        months : int
            Number of months.

        Returns:
        --------
        app.plot.plot.TimeBarPlot
            Plot of number of block visits as a function of the month.
        """

        start_date, end_date = month_range(self.date, months)
        trend_func = functools.partial(month_running_average, ignore_missing_values=False)
        return monthly_bar_plot(df=self.df,
                                start_date=start_date,
                                end_date=end_date,
                                date_column='Date',
                                month_column='Month',
                                y_column='BlockCount',
                                y_range=Range1d(start=0, end=300),
                                trend_func=trend_func,
                                **self.kwargs)
