# coding: utf-8

import re, datetime

from pyquery import PyQuery as _
from jzsadmin.models import Entry

is_phone = re.compile(r'((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))$)')
now = datetime.datetime.utcnow

def get_url_set(city, cate):
    print 'Get list of %s' % cate
    urls = set()
    n = 0
    while 1:
        url = r"http://%s.ganji.com/%s/f%d" % (city, cate, n)
        doc = _(url)
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
    print 'Get detail....'
    data = {}
    doc = _(url)

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
    li_list = doc('.contList li')

    # address
    data['address'] = _(li_list[0]).find('.wt2').text()

    # worktime
    data['worktime'] = _(li_list[2]).find('.wt2').text()

    # serviceareas
    data['serviceareas'] = _(li_list[3]).find('.wt2').text()

    # linkman
    data['linkman'] = _(li_list[4]).find('.wt2 strong').text()

    # serviceitems
    item_list = _(li_list[1]).find('.wt2 a')
    items = []
    for e in item_list:
        items.append(_(e).text())
    data['serviceitems'] = items

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
    e.serviceareas = " " if data['serviceareas'] is None else \
            set(data['serviceareas'])
    e.serviceitems = set(data['serviceitems'])
    e.contracts = data['contracts']
    e.linkman = data['linkman'] or " "

    e.save()


def crawl_ganji(cy, city, cate):

    for url in get_url_set(cy, cate):
        url_all = r'http://%s.ganji.com%s' % (cy, url) 
        content_dict = get_detail(url_all)
        if content_dict:
            content_dict['city_label'] = city
            save_content(content_dict)
