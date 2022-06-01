import datetime
import json
from collections import namedtuple

monthList = {
    'Q1': ['04', '06'],
    'Q2': ['04', '09'],
    'Q3': ['04', '12'],
    'Q4': ['04', '03'],
}
dateList = {
    'Q1': ['04-01', '06-30'],
    'Q2': ['04-01', '09-30'],
    'Q3': ['04-01', '12-31'],
    'Q4': ['04-01', '03-31'],
}


def init_quarter_of_fafiscal(year, timeList):
    yearDur = year.split('/')
    yearTime = {}
    for key in timeList:
        if key == 'Q4':
            currTimeList = []
            currTimeList.append(yearDur[0]+'-'+timeList[key][0])
            currTimeList.append(yearDur[1] + '-' + timeList[key][1])
            yearTime.update({'Q4': currTimeList})
        else:
            currTimeList = []
            for date in timeList[key]:
                currTimeList.append(yearDur[0]+'-'+date)
            yearTime.update({key: currTimeList})
    return yearTime


yearList = {
    'yearSort': ['2022/2023', '2021/2022', '2020/2021'],
}

def last_day_of_month(any_day):
    """
    获取获得一个月中的最后一天
    :param any_day: 任意日期
    :return: string
    """
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)


def get_duration_query(fiscal, quarter=None):
    for year in yearList['yearSort']:
        yearList.update({year: {
        'monthList': init_quarter_of_fafiscal(year, monthList),
        'dateList': init_quarter_of_fafiscal(year, dateList)
         }})
    if fiscal == 'current':
        today = datetime.datetime.today()
        last_month = last_day_of_month(today)

        if last_month.month >= 4:
            fiscal = f'{last_month.year}/{last_month.year+1}'
            current = [f'{last_month.year}-{dateList["Q1"][0]}', last_month.strftime("%Y-%m-%d")]
        else:

            fiscal = f'{last_month.year-1}/{last_month.year}'
            current = [f'{last_month.year-1}-{dateList["Q1"][0]}', last_month.strftime("%y-%m-%d")]

        index = yearList['yearSort'].index(fiscal)
        historyYearStart = yearList['yearSort'][index + 1]
        historyYearEnd = yearList['yearSort'][-1]
        return {
            'current': current,
            'history': [yearList[historyYearEnd]['dateList']['Q1'][0], yearList[historyYearStart]['dateList']['Q4'][1]]
        }


    index = yearList['yearSort'].index(fiscal)
    if index != len(yearList['yearSort'])-1:
        historyYearStart = yearList['yearSort'][index+1]
        historyYearEnd = yearList['yearSort'][-1]
        return {
            'current': yearList[fiscal]['dateList'][quarter],
            'history': [yearList[historyYearEnd]['dateList']['Q1'][0], yearList[historyYearStart]['dateList']['Q4'][1]]
        }
    else:
        return {
            'current': yearList[fiscal]['dateList'][quarter],
            'history': None
        }


def date_compare(enableRange, fiscal):
    if fiscal == 'current':
        today = datetime.datetime.today()
        last_month = datetime.date(today.year, today.month, 1) - datetime.timedelta(1)
        if last_month.month >= 4:
            fiscal = f'{last_month.year}/{last_month.year + 1}'
        else:
            fiscal = f'{last_month.year - 1}/{last_month.year}'
    if enableRange[0]['begind'] < yearList[fiscal]['monthList']['Q1'][0]:
        return 0
    else:
        if enableRange[0]['begind'] > yearList[fiscal]['monthList']['Q4'][1]:
            return -1
        else:
            return 1


def enable_range_preprocessing(enableRange):
    if enableRange != '' and enableRange is not None:
        for timeDur in enableRange:
            timeDur['begind'] = date_add_day(timeDur['begind'])
            timeDur['endd'] = date_add_day(timeDur['endd'])
        return enableRange
    else:
        return None


def cal_date_durations_intersection(duration1, duration2):
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=datetime.datetime.strptime(duration1[0], '%Y-%m-%d'), end=datetime.datetime.strptime(duration1[1], '%Y-%m-%d'))
    r2 = Range(start=datetime.datetime.strptime(duration2[0], '%Y-%m-%d'), end=datetime.datetime.strptime(duration2[1], '%Y-%m-%d'))
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    delta = (earliest_end - latest_start).days + 1
    overlap = max(0, delta)
    return overlap


def cal_date_intersection_month(duration1, duration2):
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=datetime.datetime.strptime(duration1[0], '%Y-%m-%d'),
               end=datetime.datetime.strptime(duration1[1], '%Y-%m-%d'))
    r2 = Range(start=datetime.datetime.strptime(duration2[0], '%Y-%m-%d'),
               end=datetime.datetime.strptime(duration2[1], '%Y-%m-%d'))
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    v_year_end = earliest_end.year
    v_month_end = earliest_end.month
    v_year_start = latest_start.year
    v_month_start = latest_start.month
    interval = (v_year_end - v_year_start)*12 + (v_month_end - v_month_start) + 1
    if interval<0:
        return 0
    return interval


def date_add_day(date):
    if len(date) == 7:
        return date + '-01'
    elif date == '':
        return str(datetime.date.today())
    else:
        return date


if __name__ == '__main__':
    print(yearList)
    print(get_duration_query('current', ''))
    cal_date_durations_intersection(['2018-05-01', '2018-06-01'], ['2018-05-01', '2018-05-15'])
    num = cal_date_intersection_month(['2020-03-01', '2020-06-01'], ['2018-03-01', '2018-04-01'])
    print(num)
