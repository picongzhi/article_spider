# -*- coding: utf-8 -*-

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re


session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookie未能加载')

agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
header = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': agent
}


# 通过个人中心页面返回状态码来判断是否登录
def is_login():
    inbox_url = 'https://www.zhihu.com/inbox'
    response = session.get(inbox_url, headers=header, allow_redirect=False)
    if response.status_code != '200':
        return False
    else:
        return True


# 获取首页
def get_index():
    response = session.get('https://www.zhihu.com', headers=header)
    with open('index_page.html', 'wb') as f:
        f.write(response.text.encode('utf-8'))


# 获取xsrf code
def get_xsrf():
    response = session.get('https://www.zhihu.com',
                            headers=header)
    text = response.text
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', text)
    if match_obj:
        return match_obj.group(1)
    else:
        return ''


# 知乎登录
def zhihu_login(account, password):
    if re.match('1\d{10}', account):
        print('手机号码登录')
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            '_xsrf': get_xsrf(),
            'phone_num': account,
            'password': password
        }
    else:
        if '@' in account:
            print('邮箱登录')
            post_url = 'https://www.zhihu.com/login/email'
            post_data = {
                '_xsrf': get_xsrf(),
                'email': account,
                'password': password
            }
    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()

