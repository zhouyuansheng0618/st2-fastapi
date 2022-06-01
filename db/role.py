# coding:UTF-8

"""
@version: python3.8
@author:yangdc3
@software: PyCharm
@file: rpa.py
@time: 2022/5/17 10:47
"""
import json

from db.dbManager import DbManager
from utils.datetimeUtils import date_compare





def get_attr():
    dbManager = DbManager()
    sql = 'SELECT ROLEKEY, rolevalue, KEYDESC FROM role_attr WHERE ROLEID IN (199,1009)'
    attrDatas = dbManager.fetchall(sql)
    attrDict = {}
    for item in attrDatas:
        attrDict[item['ROLEKEY']] = item['rolevalue']
    dbManager.close()
    return attrDict


def get_role_by_list(roleIdList):
    dbManager = DbManager()
    sql = "SELECT * FROM role_tab WHERE id in (%s) ORDER BY id ASC;" % ','.join(roleIdList)
    data = dbManager.fetchall(sql)
    dbManager.close()
    return data


def get_qty_role_dict(timeDuration=None):
    dbManager = DbManager()
    sql = "SELECT roleId, COALESCE(sum(qty),0) QTY FROM sys_logsummary WHERE dbTime >= '%s' and dbTime <= '%s' group by roleId ORDER BY roleId ASC;" \
          % (timeDuration[0], timeDuration[1])
    data = dbManager.fetchall(sql)
    dbManager.close()
    roleDit = {}
    for item in data:
        roleDit.update({item['roleId']: item['QTY']})
    return roleDit


def get_role_list_rpa(fiscal):
    dbManager = DbManager()
    newRobotList = []
    newRobotDetailDict = {}
    existedRobotList = []
    existedRobotDetailDict = {}
    robotDetailDict = {}
    sql = "SELECT id, saveManDay, saveCost, saveType, enablerange, COMMENT FROM role_tab WHERE ROLESTATUS=1  ORDER BY id ASC;"
    robotData = list(dbManager.fetchall(sql))
    dbManager.close()
    for i, val in enumerate(robotData):
        if val['enablerange'] is not None and val['enablerange'] != '':
            compareResult = date_compare(json.loads(val['enablerange']), fiscal)
            itemDict = {
                'saveManDay': val['saveManDay'],
                'saveCost': val['saveCost'],
                'saveType': val['saveType'],
                'enablerange': json.loads(val['enablerange']),
                'comment': val['COMMENT'],
            }
            roleDict = {
                str(val['id']): itemDict
            }
            robotDetailDict.update(roleDict)
            if compareResult == 1:
                newRobotList.append(str(val['id']))
                newRobotDetailDict.update(roleDict)
            elif compareResult == 0:
                existedRobotList.append(str(val['id']))
                existedRobotDetailDict.update(roleDict)
    return {
        'newRobotList': newRobotList,
        'existedRobotList': existedRobotList,
        'newRobotDetailDict': newRobotDetailDict,
        'existedRobotDetailDict': existedRobotDetailDict,
        'robotDetailDict': robotDetailDict,
    }


def get_qty_role_data(timeDuration, roleId):
    dbManager = DbManager()
    sql = "SELECT * FROM sys_logsummary WHERE dbTime >= '%s' and dbTime <= '%s' and roleId = %d ORDER BY roleId ASC;" \
          % (timeDuration[0], timeDuration[1], roleId)
    data = dbManager.fetchall(sql)
    dbManager.close()
    return data


def get_qty_role_data_left_comment(timeDuration, roleId):
    dbManager = DbManager()
    sql = "SELECT s1.*, r1.comment FROM sys_logsummary s1 left join role_tab r1 on r1.id = s1.roleId WHERE s1.dbTime >= '%s' and s1.dbTime <= '%s' and s1.roleId = %d ORDER BY s1.roleId ASC;" \
          % (timeDuration[0], timeDuration[1], roleId)
    data = dbManager.fetchall(sql)
    dbManager.close()
    return data


def get_role_list_by_appadmin():
    dbManager = DbManager()
    sql = "SELECT id, comment FROM role_tab WHERE ROLESTATUS=1 and appAdmin='liuyan2' ORDER BY id ASC;"
    robotData = dbManager.fetchall(sql)
    dbManager.close()
    roleList = []
    for item in robotData:
        roleList.append([item['id'], item['comment']])
    return roleList
