import xlsxwriter
import pandas
from io import BytesIO

from db.role import get_role_by_list


def show_data_robot_detail(robotDatas, writer):
    columns = []
    dataDict = {}
    # print(json.dumps(robotDatas, indent=4, sort_keys=True, default=str))
    for key in robotDatas[0]:
        columns.append(key)
        dataDict.update({key: []})

    for robot in robotDatas:
        for key, val in robot.items():
            dataDict[key].append(val)

    df = pandas.DataFrame(dataDict)
    df.to_excel(writer, columns=columns, index=False, encoding='utf-8', sheet_name='Robots', engine=xlsxwriter)
    writer.save()


def show_rpa_report_total(cacheData):
    columns = []
    rowsDict = {
        '部门': [],
        'HC': [],
        'KIP 5% MD Saving': [],
        'KIP 10% MD Saving': [],
        'Existed Robot Save MD (FY)': [],
        'Existed Robot Save MD (His)': [],
        'Existed Robot Save MD': [],
        'New Robot Save MD (FY)': [],
        'Save MD Total': [],
        'Save MD Total(FY)': [],
        'newRobotsQty': [],
        'existedRobotsQty': [],
        'Total Active Robot Qty': [],
        'Completion Rate(New Robots Base on 10%)': [],
    }
    for key in rowsDict:
        columns.append(key)
    for depDetail in cacheData['depList']:
        rowsDict['部门'].append(depDetail['depName'])
        rowsDict['HC'].append(depDetail['depHc'])
        rowsDict['KIP 5% MD Saving'].append(depDetail['kpi5preMd'])
        rowsDict['KIP 10% MD Saving'].append(depDetail['kpi10preMd'])
        rowsDict['Existed Robot Save MD (FY)'].append(depDetail['existedSaveManDayFY'])
        rowsDict['Existed Robot Save MD (His)'].append(depDetail['existedSaveManDayHis'])
        rowsDict['Existed Robot Save MD'].append(depDetail['existedSaveManDayHis'] + depDetail['existedSaveManDayFY'])
        rowsDict['New Robot Save MD (FY)'].append(depDetail['newSaveManDayFY'])
        rowsDict['Save MD Total'].append(depDetail['newSaveManDayFY']+depDetail['existedSaveManDayFY']+depDetail['existedSaveManDayHis'])
        rowsDict['Save MD Total(FY)'].append(depDetail['newSaveManDayFY']+depDetail['existedSaveManDayFY'])
        rowsDict['newRobotsQty'].append(depDetail['newRobotsQty'])
        rowsDict['existedRobotsQty'].append(depDetail['existedRobotsQty'])
        rowsDict['Total Active Robot Qty'].append(depDetail['newRobotsQty'] + depDetail['existedRobotsQty'])
        rowsDict['Completion Rate(New Robots Base on 10%)'].append(
            round(depDetail['newSaveManDayFY']/depDetail['kpi10preMd'], 2)*100)

    df = pandas.DataFrame(rowsDict)
    output = BytesIO()  # 在内存中创建一个缓存流

    writer = pandas.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, columns=columns, index=False, encoding='utf-8', sheet_name='Total')
    show_data_robot_detail(get_role_by_list(cacheData['robotList']), writer)
    writer.save()

    output.seek(0)
    return output



