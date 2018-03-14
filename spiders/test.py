# -*- coding:utf-8 -*-
from handler import tools
import re
from handler import config

cf = config.get_conf()

start_url = cf.get('web', 'start_url')

source = tools.ungzip_file('imgs_bfed3f42af380aa2d363428af1fe464f.html')
# print source
if source is not None:
    try:
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
        # print s
        re_url = re.compile("<divid=\"bizhiimg\"><p><ahref=\"(.+?)\">")
        url = re_url.search(s)
        url = start_url + url.group(1)
        re_href = re.compile("<imgid=\"imageview\"src=\"(.+?)\"")
        href = re_href.search(s)
        href = href.group(1)
        js = '{"url": "%s","href": "%s"}' % (url, href)
        print js

    except Exception, e:
        print e
