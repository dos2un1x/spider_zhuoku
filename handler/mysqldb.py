# -*- coding:utf-8 -*-
import logging

import pymysql
from DBUtils.PooledDB import PooledDB

import config

cf = config.get_conf()


class mysqldb:
    def connect_mysql(self):
        try:
            dbpool = PooledDB(pymysql, host=cf.get('db', 'dbhost'), port=cf.getint('db', 'dbport'),
                              user=cf.get('db', 'dbuser'), passwd=cf.get('db', 'dbpasswd'),
                              db=cf.get('db', 'dbname'), charset=cf.get('db', 'dbcharset'),
                              mincached=cf.getint('db', 'mincached'), maxcached=cf.getint('db', 'maxcached'),
                              maxshared=cf.getint('db', 'maxshared'), maxconnections=cf.getint('db', 'maxconnections'),
                              blocking=cf.getboolean('db', 'blocking'), maxusage=cf.getboolean('db', 'maxusage'))
            return dbpool.connection()
        except Exception, e:
            logging.info(e)
            logging.info('mysql connect error !')

    def insert_mysql(self, _sql):
        try:
            conn = self.connect_mysql()
            cur = conn.cursor()
            cur.execute(_sql)
            conn.commit()
            return True
        except Exception, e:
            logging.info(e)
            logging.info(_sql)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def update_mysql(self, _sql):
        try:
            conn = self.connect_mysql()
            cur = conn.cursor()
            cur.execute(_sql)
            conn.commit()
            return True
        except Exception, e:
            logging.info(e)
            logging.info(_sql)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def select_mysql(self, _sql):
        try:
            conn = self.connect_mysql()
            cur = conn.cursor()
            cur.execute(_sql)
            res = cur.fetchall()
            return res
        except Exception, e:
            logging.info(e)
            logging.info(_sql)
        finally:
            cur.close()
            conn.close()
