# -*- coding:utf-8 -*-
import logging
import time
import re
from bs4 import BeautifulSoup
from handler import config
from handler import mysqldb
from handler import logger
from handler import redisdb
from handler import tools

cf = config.get_conf()
db = mysqldb.mysqldb()
rdb = redisdb.redisdb()
logger.set_log('parser_html.log')
basic_url = cf.get('web', 'basic_url')
start_url = cf.get('web', 'start_url')


def parser(html):
    source = tools.ungzip_file(html)
    if source is not None:
        s = source.strip()
        s = s.replace('\t', '').replace('\r', '').replace(' ', '')
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # 处理换行
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        blank_line = re.compile('\n+')  # 处理空行
        s = re_cdata.sub('', s)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        s = re_comment.sub('', s)  # 去掉HTML注释
        s = blank_line.sub('\n', s)  # 去掉多余的空行
        return s


def _link(html):
    s = parser(html)
    re_href = re.compile("<divclass=\"bizhiin\"><ahref=\"(.+?)\"target=\"_blank\">")
    hrefs = re_href.findall(s)
    for href in hrefs:
        url = start_url + href
        rdb.producers(cf.get('redis', 'imgs_queue'), url)


def _page(html):
    s = parser(html)
    re_title = re.compile("jpg\"alt=\"(.+?)\"/>")
    re_href = re.compile("<atarget=\"_blank\"href=\"(.+?)\"")
    titles = re_title.findall(s)
    hrefs = re_href.findall(s)
    for title, href in zip(titles, hrefs):
        logging.info(title)
        url = basic_url + href
        rdb.producers(cf.get('redis', 'link_queue'), url)


def _imgs(html):
    s = parser(html)
    re_url = re.compile("<divid=\"bizhiimg\"><p><ahref=\"(.+?)\">")
    url = re_url.search(s)
    url = start_url + url.group(1)
    re_href = re.compile("<imgid=\"imageview\"src=\"(.+?)\"")
    href = re_href.search(s)
    href = href.group(1)
    js = '{"url": "%s","href": "%s"}' % (url, href)
    rdb.producers(cf.get('redis', 'down_queue'), js)


def parser_html():
    try:
        html = rdb.consumers(cf.get('redis', 'html_queue'))
        logging.info('html is: ' + html)
        if 'page_' in html:
            logging.info('parser page is: ' + html)
            _page(html)
        elif 'link_' in html:
            logging.info('parser link is: ' + html)
            _link(html)
        elif 'imgs_' in html:
            logging.info('parser imgs is: ' + html)
            _imgs(html)
    except:
        logging.info('error html is: ' + html)
        rdb.producers(cf.get('redis', 'html_queue'), html)
    finally:
        time.sleep(1)


def main():
    while True:
        parser_html()


if __name__ == '__main__':
    logging.info('start parser htmls')
    main()
