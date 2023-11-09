from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import datetime
from datetime import timedelta, datetime

from .platform import ANKI21

# all codes includes repeated presses AND learn/relearns
legend_factors = (0.125, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 4)


class Activity(object):
    def __init__(self, col):
        self.col = col
        self.offset = self._getColOffset()
        self.legend_factors = legend_factors

    def getEverything(self, review_type):
        everything = self._getDataAndLegendAndOffset(review_type)
        return everything

    def _getDataAndLegendAndOffset(self, review_type):
        raw_data = self._fetchRawDataFromDatabase(review_type)
        data_legend = self._setDynamicLegend(self._getAverage(raw_data))

        return {
            'data': raw_data,
            'legend': data_legend,
            'offset': self.offset,
        }

    def _fetchRawDataFromDatabase(self, review_type):
        offset = self.offset * 3600

        two_months_ago_in_unix = self._convertToUnix(datetime.today() - timedelta(days=62))
        if (review_type == "Added"):
            intial_cmd = "SELECT CAST(STRFTIME('%s', id / 1000 - {offset}, 'unixepoch', 'localtime', 'start of day') as int) AS day, COUNT() FROM cards WHERE id > {two_months} GROUP BY DAY"

            cmd = intial_cmd.format(offset=offset, two_months=two_months_ago_in_unix)
        else:
            intial_cmd = "SELECT CAST(STRFTIME('%s', id/1000 - {offset}, 'unixepoch', 'localtime', 'start of day') as int) AS day, COUNT() FROM revlog WHERE (ease = '{ease}' AND id > {two_months} ) GROUP BY DAY"

            reviewCode = {
                'Again': 1,
                'Hard': 2,
                'Good': 3,
                'Easy': 4
            }

            cmd = intial_cmd.format(offset=offset, ease=reviewCode[review_type], two_months=two_months_ago_in_unix)

        raw_data = self.col.db.all(cmd)
        return raw_data

    def _setDynamicLegend(self, average):
        avg = max(20, average)
        return [coefficient * avg for coefficient in self.legend_factors]

    def _getAverage(self, raw_data):
        total = 0
        days_learned = 1
        for idx, item in enumerate(raw_data):
            total += item[1]
            days_learned += 1
        avg = int(round(total / days_learned, 1))
        return avg

    def _getColOffset(self):
        """
        Return daily scheduling cutoff time in hours
        """
        if ANKI21 and self.col.sched_ver() == 2:
            return self.col.conf.get("rollover", 4)
        start_date = datetime.fromtimestamp(self.col.crt)
        return start_date.hour

    def _convertToUnix(self, dt):
        epoch = datetime.utcfromtimestamp(0)
        return (dt - epoch).total_seconds() * 1000.0
