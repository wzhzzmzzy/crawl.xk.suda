urls = {
    'index': "http://xk.suda.edu.cn/",                  # 首页
    'home': "http://xk.suda.edu.cn/default_szdx.aspx",  # 用户首页
    'kb': "http://xk.suda.edu.cn/xskbcx.aspx",          # 课表
    'cj': "http://xk.suda.edu.cn/xscjcx_dq.aspx",       # 成绩
    'jh': "http://xk.suda.edu.cn/pyjh.aspx",            # 培养计划（每年推荐选课）
    'xk': "http://xk.suda.edu.cn/xsxkqk.aspx",          # 选课情况
    'ks': "http://xk.suda.edu.cn/xskscx.aspx"           # 考试时间
}

urls_tao = {
    'index': "http://xk.liontao.xin/",                  # 首页
    'home': "http://xk.liontao.xin/default_szdx.aspx",  # 用户首页
    'kb': "http://xk.liontao.xin/xskbcx.aspx",          # 课表
    'cj': "http://xk.liontao.xin/xscjcx_dq.aspx",       # 成绩
    'jh': "http://xk.liontao.xin/pyjh.aspx",            # 培养计划（每年推荐选课）
    'xk': "http://xk.liontao.xin/xsxkqk.aspx",          # 选课情况
    'ks': "http://xk.liontao.xin/xskscx.aspx"           # 考试时间
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Host': "xk.liontao.xin"
}

post_data = {
    "__VIEWSTATE":"",       # CSRF
    "__EVENTTARGET": "",    # 修改字段名 固定
    "__EVENTARGUMENT": "",  # 未知字段 固定
    "ddlXN": "",            # 学年
    "ddlXQ": "",            # 学期
    "btnCx": " 查  询 "      # 按钮 固定
}

params = {
    'kb': {'xh': "", "xm": "", 'gnmkdm': "N121603"},
    'cj': {'xh': "", "xm": "", 'gnmkdm': "N121604"},
    'jh': {'xh': "", "xm": "", 'gnmkdm': "N121607"},
    'xk': {'xh': "", "xm": "", 'gnmkdm': "N121610"},
    'ks': {'xh': "", "xm": "", 'gnmkdm': "N121615"}
}


def wttn():
    """
    What's the time now?
    :return: int(%yymmdd)
    """
    import datetime

    now = datetime.datetime.now()
    return int(str(now.year) + str(now.month) + str(now.day))


def headless_chrome():
    """
    Chrome Headless Mode With Selenium
    :return: Selenium Chrome Driver
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    chrome_opt = Options()
    chrome_opt.add_argument('--headless')
    chrome_opt.add_argument('--disable-gpu')
    return webdriver.Chrome(chrome_options=chrome_opt)


def get_code(browser, filename):
    """
    在 browser 当前界面获取截图
    :return: Pillow Image
    """
    from PIL import Image
    browser.save_screenshot(filename)
    code_ele = browser.find_element_by_id('icode')
    left = code_ele.location['x']
    top = code_ele.location['y']
    right = code_ele.location['x'] + code_ele.size['width']
    bottom = code_ele.location['y'] + code_ele.size['height']
    img = Image.open(filename).crop((left, top, right, bottom))
    img.save(filename, format='PNG')
    return img


def save_cookies(xh, cookies):
    import json
    import sys
    with open(sys.path[0] + '/cookies/' + xh + '.json', "w") as json_f:
        json.dump(cookies, json_f)


def read_cookies(xh):
    from json import load
    from sys import path
    from os.path import exists
    from os import stat
    from datetime import datetime
    import time
    cookie_path = path[0] + '/cookies/' + xh + '.json'
    if not exists(cookie_path):
        return False
    loc_t = datetime.now()
    modi_t = time.localtime(stat(cookie_path).st_mtime)
    modi_t = datetime(modi_t.tm_year, modi_t.tm_mon, modi_t.tm_mday, modi_t.tm_hour, modi_t.tm_min, modi_t.tm_sec)
    if (loc_t-modi_t).seconds > 1200:
        return False
    with open(cookie_path) as json_f:
        return load(json_f)


def get_referer(user, page_flag):
    from urllib import parse

    data = params[page_flag].copy()
    data['xh'] = user['xh']
    data['xm'] = user['xm']
    return urls_tao[page_flag] + '?' + parse.urlencode(data, encoding='gbk')


def save_to_csv(filename, header, table):
    import csv
    with open(filename, "w", encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(table)


def login_prepare(capt_path):
    """
    获取验证码截图、当时 Cookies 以及 CSRF
    :param capt_path: 验证码存储位置
    :return: (csrf, cookies)
    """
    from bs4 import BeautifulSoup
    browser = headless_chrome()
    browser.get(urls_tao['index'])
    get_code(browser, capt_path)
    chrome_cookies = browser.get_cookies()
    html = browser.page_source
    browser.close()
    cookies = {}
    for cookie in chrome_cookies:
        cookies[cookie['name']] = cookie['value']
    csrf = BeautifulSoup(html, 'lxml').find("input", type="hidden")['value']
    return csrf, cookies


def init_session(form):
    import json
    import requests
    session = requests.Session()
    requests.utils.cookiejar_from_dict(json.loads(form['xk_cookies']), session.cookies)
    headers = {
        'Host': 'xk.liontao.xin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Referer': 'http://xk.liontao.xin/',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        '__VIEWSTATE': form['xk_csrf'],
        'Button1': '',
        'TextBox1': form['xh'],
        'TextBox2': form['pwd'],
        'TextBox3': form['auth']
    }
    res = session.post(urls_tao['home'], headers=headers, data=data)
    return res.text, session


def login_prepare_splash(capt_path):
    from urllib.parse import quote
    import requests
    import base64
    with open('xk_crawler/login_prepare.lua') as lua_f:
        lua_source = lua_f.read()
    url = 'http://wzhzzmzzy.xyz:8888/execute?lua_source=' + quote(lua_source)
    res = requests.get(url).json()
    with open(capt_path, 'wb') as capt_f:
        capt_f.write(base64.b64decode(res['icode']))
    cookies = dict(((i['name'], i['value']) for i in res['cookies']))
    return res['csrf'], cookies


if __name__ == '__main__':
    login_prepare_splash('app/static/test.png')
