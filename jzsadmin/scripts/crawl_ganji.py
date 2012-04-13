# coding: utf-8

import re, datetime, urllib, urllib2

from pyquery import PyQuery as _
from jzsadmin.models import Entry

is_phone = re.compile(r'((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))$)')
now = datetime.datetime.utcnow
headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) \
                AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 \
                Safari/535.19",
        }


def request(url, data=dict()):
    
    data = urllib.urlencode(data) if data else None
    req = urllib2.Request(
            url=url,
            data=data,
            headers=headers
            )
    try:
        request = urllib2.urlopen(req)
        source = request.read()
        request.close()
    except:
        source = None
        print "Connect timeout"

    return source


def get_url_set(city):
    cates = ('banjia', 'baomu', 'baojie', 'weixiu', 'jiadianweixiu',
            'shumashoujiweixiu', 'kongtiaoyiji', 'jiazheng', 'zhongdiangong',
            'yuesao', 'guandao', 'bianminfuwu')
    for cate in cates:
        print 'Get list of %s' % cate
        n = 0
        while 1:
            url = r"http://%s.ganji.com/%s/f%d" % (city, cate, n)
            content = request(url)
            if content:
                doc = _(content)
                nodes = doc('.list .ft-14')
                if not nodes:
                    break
                for node in nodes:
                    url_ = _(node).attr('href')
                    text = _(node).text()
                    if not Entry.query.filter_by(title=text).first():
                        print url_
                        yield url_
            n += 32


def get_detail(url):
    data = {}
    content = request(url)
    if not content: return

    doc = _(content)

    # check 
    check_list = doc('.bd-box .rz-icon span')
    is_ok = False
    for e in check_list:
        if _(e).text() in (u'手机已认证', u'个人实名已认证', u'企业已认证'):
            is_ok = True
            break;

    if not is_ok:
        print 'no auth one'
        return None

    # desc
    desc_list = doc('.pr-cont .nbd')
    data['desc'] = _(desc_list[0]).text()

    # brief
    brief_list = doc('.box-cont p')
    data['brief'] = _(brief_list[1]).text()

    # title
    brief_list = doc('.box-cont h1')
    data['title'] = _(brief_list[0]).text()

    #
    c1_list, c2_list = doc('.contList')[:2] 

    # address
    data['address'] = _(c1_list[0]).find('.wt2').text()

    # serviceitems
    item_list = _(c1_list[1]).find('.wt2 a')
    items = []
    for e in item_list:
        items.append(_(e).text())
    data['serviceitems'] = items

    # worktime
    if len(c1_list) >= 3:
        data['worktime'] = _(c1_list[2]).find('.wt2').text()
    else:
        data['worktime'] = u" "

    # serviceareas
    if len(c1_list) >= 4:
        data['serviceareas'] = _(c1_list[3]).find('.wt2').text()
    else:
        data['serviceareas'] = set()

    # linkman
    if len(c2_list) >= 1:
        data['linkman'] = _(c2_list[0]).find('.wt2 strong').text()
    else:
        data['linkman'] = u" "

    # ontracts
    tel_list = doc('.tel-box span')
    tels = []
    for e in tel_list:
        maybe_tel = _(e).text()
        if is_phone.match(maybe_tel):
            tels.append(maybe_tel)
    data['contracts'] = tels

    return data


def save_content(data):
    print 'Saving...'

    e = Entry()
    e.location = '0.0,0.0'
    e.tags = set()
    e.updated = now()
    e.created = now()
    e.grades = []
    e.city_label = data['city_label']
    e.title = data['title']
    e.brief = data['brief'] or " "
    e.desc = data['desc']
    e.address = data['address']
    e.worktime = data['worktime']
    e.serviceareas = data['serviceareas'] or set()
    e.serviceitems = set(data['serviceitems'])
    e.contracts = data['contracts']
    e.linkman = data['linkman'] or " "
    e.status = 'block'

    e.save()


def crawl_ganji(cy, city):

    for url in get_url_set(cy):
        url_all = r'http://%s.ganji.com%s' % (cy, '/'.join(url.split('/')[:3])) 
        content_dict = get_detail(url_all)
        if content_dict:
            content_dict['city_label'] = city
            save_content(content_dict)
