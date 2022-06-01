# -*- coding: utf-8 -*- 
# @Time : 2022/6/1 18:07 
# @Author : zhouys618@163.com 
# @File : mongodb.py 
# @desc:
from oslo_config import cfg
for k,v in cfg.CONF.items():
    print(k,v)