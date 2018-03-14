# -*- coding:utf-8 -*-
import logging
import urllib2
import json
from handler import config
from handler import mysqldb
from handler import logger
from handler import redisdb
from handler import tools

cf = config.get_conf()
db = mysqldb.mysqldb()
rdb = redisdb.redisdb()
logger.set_log('spider_down.log')


def spider_down():
    try:
        down = rdb.consumers(cf.get('redis', 'down_queue'))
        js = json.loads(down)
        url = js['url']
        href = js['href']
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0',
                   'Referer': url}
        req = urllib2.Request(url=href, headers=headers)
        openurl = urllib2.urlopen(req, timeout=5)
        binary_data = openurl.read()
        filename = tools.get_md5(href) + '.jpg'
        status = tools.save_to_file(filename, binary_data)
        if status:
            logging.info('img download ok !')
        else:
            rdb.producers(cf.get('redis', 'down_queue'), down)
    except Exception, e:
        logging.info(e)
        rdb.producers(cf.get('redis', 'down_queue'), down)
    finally:
        openurl.close()


def main():
    while True:
        spider_down()


if __name__ == '__main__':
    logging.info('start spider')
    main()
