import redis as r
import json
from utils.logger import logger


redis_conn = r.Redis(host='*.*.*.*', port=6379, password='*')


def rpa_report_redis_set(queryDate, depList, responseData, robotList):
    key = ','.join(queryDate)
    val = json.dumps({'depList': depList, 'responseData': responseData, 'robotList': robotList})
    if redis_conn.set(key, val, ex=3600):
        logger.info(f"redis set success:key={key} value={val}")
        return True
    else:
        logger.error(f"redis set fail:key={key} value={val}")
        return False



def rpa_report_redis_get(queryDate):
    key = ','.join(queryDate)
    cacheData = redis_conn.get(key)
    if cacheData:
        logger.info(f"redis get success:key={key} value={cacheData}")
        return json.loads(cacheData)
    else:
        logger.error(f"redis get fail:key={key}")
        return None
