# coding:UTF-8

"""
@version: python3.8
@author:yangdc3
@software: PyCharm
@file: rpa.py
@time: 2022/5/17 10:47
"""

import json
import pandas

from db.redis.redisManager import rpa_report_redis_get, rpa_report_redis_set
from utils.toExcel import show_data_robot_detail, show_rpa_report_total
from utils.datetimeUtils import get_duration_query, \
    enable_range_preprocessing, \
    cal_date_durations_intersection, cal_date_intersection_month

from db.role import get_attr, get_qty_role_dict, get_role_list_rpa, get_role_list_by_appadmin, \
    get_qty_role_data_left_comment


def get_dep_list():
    attrDict = get_attr()
    depList = json.loads(attrDict['SumTolTools1.RpaQuaterReportConfig'])
    depRoleList = json.loads(attrDict['CCUserCustomizeReportLS'])
    depRoleDict = {}
    for depRole in depRoleList:
        fliedList = depRole.split(':')
        depRoleDict.update({fliedList[0]: fliedList[1].split('_')})
    for dep in depList:
        dep.update({'depRoles': depRoleDict[dep['descEng']]})
    return depList


def rpa_single_by_day(robotDetail, robotQty, timeDuration):
    if robotDetail['saveType'] == 0:
        saveManDay = float(robotQty)*float(robotDetail['saveManDay'])
        saveCost = float(robotQty)*float(robotDetail['saveCost'])
    else :
        enableRange = enable_range_preprocessing(robotDetail['enablerange'])
        if enableRange is None:
            enableRange = [{
                'begind': timeDuration[0],
                'endd': timeDuration[1],
            }]
        overlap = 0
        for enableDate in enableRange:
            curOverlap = cal_date_durations_intersection(timeDuration, [enableDate['begind'], enableDate['endd']])
            overlap = overlap + curOverlap
        saveManDay = overlap*(float(robotDetail['saveManDay'])/30)
        saveCost = overlap*(float(robotDetail['saveCost'])/30)
    return {
        'saveCost': round(saveCost, 2),
        'saveManDay': round(saveManDay, 2),
    }


def rpa_single_by_month(robotDetail, robotQty, timeDuration):
    if robotDetail['saveType'] == 0:
        saveManDay = float(robotQty)*float(robotDetail['saveManDay'])
        saveCost = float(robotQty)*float(robotDetail['saveCost'])
    else :
        enableRange = enable_range_preprocessing(robotDetail['enablerange'])
        if enableRange is None:
            enableRange = [{
                'begind': timeDuration[0],
                'endd': timeDuration[1],
            }]
        overlap = 0
        for enableDate in enableRange:
            curOverlap = cal_date_intersection_month(timeDuration, [enableDate['begind'], enableDate['endd']])
            overlap = overlap + curOverlap
        saveManDay = overlap*float(robotDetail['saveManDay'])
        saveCost = overlap*float(robotDetail['saveCost'])
    return {
        'saveCost': round(saveCost, 2),
        'saveManDay': round(saveManDay, 2),
    }


def cal_robots_rpa_month(robots, robotDetailDict, roleQtyDict, queryDuration):
    saveManDay = 0
    for roleId in robots:
        if roleQtyDict.__contains__(int(roleId)) and robotDetailDict[roleId]['saveType'] == 0:
            saveManDay = saveManDay + \
                            rpa_single_by_month(robotDetailDict[roleId], roleQtyDict[int(roleId)], queryDuration)[
                                'saveManDay']
        elif robotDetailDict[roleId]['saveType'] == 1:
            saveManDay = saveManDay + \
                            rpa_single_by_month(robotDetailDict[roleId], 0, queryDuration)[
                                'saveManDay']
    return round(saveManDay, 2)


def get_rpa_report_excel(fiscal, quarter):
    queryDate = get_duration_query(fiscal, quarter)
    # cacheData = rpa_report_redis_get(queryDate['current'])
    cacheData = None
    if cacheData is None:
        cacheData = get_rpa_report(fiscal, quarter)
    excelStream = show_rpa_report_total(cacheData)
    return excelStream


def get_rpa_report(fiscal, quarter):
    queryDate = get_duration_query(fiscal, quarter)
    # cacheData = rpa_report_redis_get(queryDate['current'])
    cacheData = None
    if cacheData:
        responseData = cacheData['responseData']
        depList = cacheData['depList']
        robotList = cacheData['robotList']
    else:
        responseData = []
        depList = get_dep_list()
        curQueryDuration = queryDate['current']
        hisQueryDuration = queryDate['history']
        robotDict = get_role_list_rpa(fiscal)
        robotList = []
        curRoleQtyDict = get_qty_role_dict(curQueryDuration)
        if hisQueryDuration is not None:
            hisRoleQtyDict = get_qty_role_dict(hisQueryDuration)
        else:
            hisRoleQtyDict = []

        for dep in depList:
            newRobots = list(set(robotDict['newRobotList']).intersection(set(dep['depRoles'])))
            existedRobots = list(set(robotDict['existedRobotList']).intersection(set(dep['depRoles'])))

            robotList = list(set(robotList).union(set(robotDict['newRobotList']+robotDict['existedRobotList'])))

            newRobotDetailDict = robotDict['newRobotDetailDict']
            existedRobotDetailDict = robotDict['existedRobotDetailDict']

            newSaveManDayFY = cal_robots_rpa_month(newRobots, newRobotDetailDict, curRoleQtyDict, curQueryDuration)
            existedSaveManDayFY = cal_robots_rpa_month(existedRobots, existedRobotDetailDict, curRoleQtyDict, curQueryDuration)
            if hisQueryDuration is not None:
                existedSaveManDayHis = cal_robots_rpa_month(existedRobots, existedRobotDetailDict, hisRoleQtyDict, hisQueryDuration)
            else:
                existedSaveManDayHis = 0
            depDict = {
                'depName': dep['depName'],
                'depHc': dep['depHc'],
                'kpi5preMd': dep['kpi5preMd'],
                'kpi10preMd': dep['kpi10preMd'],
                'newRobotsQty': len(newRobots),
                'existedRobotsQty': len(existedRobots),
                'newSaveManDayFY': newSaveManDayFY,
                'existedSaveManDayFY': existedSaveManDayFY,
                'existedSaveManDayHis': existedSaveManDayHis,
                'existedSaveManDay': round((existedSaveManDayHis + existedSaveManDayFY), 2),
                'saveManDayTotal': round((existedSaveManDayHis + existedSaveManDayFY + newSaveManDayFY), 2),
                'saveManDayTotalFY':  round((existedSaveManDayFY + newSaveManDayFY),2),
                'totleRobotQty': len(newRobots) + len(existedRobots),
                'completionRate': round((existedSaveManDayFY + newSaveManDayFY) / dep['kpi10preMd'], 2)
            }
            responseData.append(depDict)
            dep.update({
                'newRobots': newRobots,
                'existedRobots': existedRobots,
                'newRobotsQty': len(newRobots),
                'existedRobotsQty': len(existedRobots),
                'newSaveManDayFY': newSaveManDayFY,
                'existedSaveManDayFY': existedSaveManDayFY,
                'existedSaveManDayHis': existedSaveManDayHis,
                'existedSaveManDay': existedSaveManDayHis + existedSaveManDayFY,
                'saveManDayTotal': existedSaveManDayHis + existedSaveManDayFY + newSaveManDayFY,
                'saveManDayTotalFY': existedSaveManDayFY + newSaveManDayFY,
                'totleRobotQty': len(newRobots) + len(existedRobots),
                'completionRate': round((existedSaveManDayFY + newSaveManDayFY)/dep['kpi10preMd'], 2)
            })
        rpa_report_redis_set(queryDate['current'], depList, responseData, robotList)

    # show_data_robot_detail(get_role_by_list(robotList))
    return {'responseData': responseData, 'depList': depList, 'robotList': robotList}


def cal_man_day_by_dep(depDetail, robotDict, roleQtyDict, fiscal, quarter=None):
    # queryDuration = yearList[fiscal]['dateList'][quarter]
    queryDuration = ['2022-01-01', '2022-01-30']
    robotDictAll = robotDict['robotDetailDict']
    robotList = depDetail['newRobots'] + depDetail['existedRobots']
    # robotList = depDetail['newRobots']
    # print(depDetail['existedRobots'])
    saveManDay = cal_robots_rpa_month()
    for roleId in robotList:
        curSaveManDay = 0
        if roleQtyDict.__contains__(int(roleId)) and robotDictAll[roleId]['saveType'] == 0:
            curSaveManDay = rpa_single_by_month(robotDictAll[roleId], roleQtyDict[roleId], queryDuration)['saveManDay']
            saveManDay = saveManDay + rpa_single_by_month(robotDictAll[roleId], roleQtyDict[roleId], queryDuration)['saveManDay']
        elif robotDictAll[roleId]['saveType'] == 1:
            curSaveManDay = rpa_single_by_month(robotDictAll[roleId], 0, queryDuration)['saveManDay']
            saveManDay = saveManDay + rpa_single_by_month(robotDictAll[roleId], 0, queryDuration)['saveManDay']
        print(roleId, robotDictAll[roleId]['funname'], round(curSaveManDay, 2))
    print(depDetail['depName'], round(saveManDay, 2))


def get_qty():
    queryDuration = ['2022-04-01', '2022-04-30']
    roleQtyDict = get_qty_role_dict(queryDuration)
    roledataList = get_role_list_by_appadmin()
    roleList = []
    data = []
    qty = 0
    for i in roledataList:
        roleList.append(i[0])
        if roleQtyDict.__contains__(int(i[0])):
            qty = qty + roleQtyDict[i[0]]
        if get_qty_role_data_left_comment(queryDuration, int(i[0])):
            curData = get_qty_role_data_left_comment(queryDuration, int(i[0]))
            data = data + curData


    name = ['id', 'roleId', 'funname', 'qty', 'dbTime', 'duration', 'comment']
    test = pandas.DataFrame(columns=name, data=data)
    test.to_csv('./testcsv.csv', encoding='gbk')
    print(qty)
