#!/usr/bin/env python
# coding:UTF-8


"""
@version: python3.8
@author:yangdc3
@software: PyCharm
@file: dbManager.py
@time: 2022/5/17 10:47
"""

import pymysql
from pymysql.cursors import DictCursor
from utils.logger import logger
import yaml


class DbManager:
    # 构造函数
    def __init__(self,  charset='utf8'):
        # 读取配置文件
        yamlPath = './db/config.yaml'
        with open(yamlPath, 'rb') as f:
            date = yaml.load(f, Loader=yaml.FullLoader)
        self.host = date['host']
        self.port = date['port']
        self.user = date['user']
        self.passwd = date['passwd']
        self.db = date['db']
        self.charset = charset
        self.conn = None
        self.cur = None

    # 连接数据库
    def connectDatabase(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
                                        charset=self.charset, cursorclass=DictCursor)
        except:
            logger.error("connectDatabase failed")
            return False
        self.cur = self.conn.cursor()
        return True

    # 关闭数据库
    def close(self):
        # 如果数据打开，则关闭；否则没有操作
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()
        return True

    # 执行数据库的sq语句,主要用来做插入操作
    def execute(self, sql, params=None, commit=False, ):
        # 连接数据库
        res = self.connectDatabase()
        if not res:
            return False
        try:
            if self.conn and self.cur:
                # 正常逻辑，执行sql，提交操作
                rowcount = self.cur.execute(sql, params)
                # print(rowcount)
                if commit:
                    self.conn.commit()
                else:
                    pass
        except:
            logger.error("execute failed: " + sql)
            logger.error("params: " + str(params))
            self.close()
            return False
        return rowcount

    # 查询所有数据
    def fetchall(self, sql, params=None):
        res = self.execute(sql, params)
        if not res:
            logger.info("查询失败")
            self.close()
            return False

        results = self.cur.fetchall()
        logger.info("查询成功" + str(results))
        return results

    # 查询一条数据
    def fetchone(self, sql, params=None):
        res = self.execute(sql, params)
        if not res:
            logger.info("查询失败")
            self.close()
            return False

        result = self.cur.fetchone()
        logger.info("查询成功" + str(result))
        return result

    # 增删改数据
    def edit(self, sql, params=None):
        res = self.execute(sql, params, True)
        if not res:
            logger.info("操作失败")
            return False
        self.conn.commit()
        self.close()
        logger.info("操作成功" + str(res))
        return res


if __name__ == '__main__':
    dbManager = DbManager()
    """
    sql = "select * from bandcard WHERE money>%s;"
    values = [1000]
    result = dbManager.fetchall(sql, values)
    """
    sql = "insert into bandcard values %s,%s,%s;"
    values = [(0, 100), (0, 200), (0, 300)]
    result = dbManager.edit(sql, values)