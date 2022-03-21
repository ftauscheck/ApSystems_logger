import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup


class ApSystems:

    def __init__(self, domain, useragent, username, password):
        self._logged = False
        self.domain = domain
        self.useragent = useragent
        self.headers = {'user-agent': self.useragent}
        mainpage = requests.get(self.domain + '/ema/index.action', headers=self.headers)
        self.mainpage_cookies = mainpage.cookies
        self.mainpage_cookies.set('loginPageUrl', 'newLogin', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('loginActionUrl', 'index', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('page', '1', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('cookUser', '', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('cookPass', '', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('cookBox', '', domain='apsystemsema.com', path='/')

        soup = BeautifulSoup(mainpage.text, "html5lib")
        form_hidden = soup.find(attrs={'name': 'code'})
        self.code = form_hidden.get('value')

        var_today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pload = {'username': username, 'password': password, 'code': self.code, 'today': var_today}
        login = requests.post(self.domain + '/ema/loginEMA.action', data=pload, headers=self.headers,
                              cookies=self.mainpage_cookies, allow_redirects=False)

        self.mainpage_cookies.update(login.cookies)

        self.mainpage_cookies.set('loginPageUrl', 'newLogin', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('loginActionUrl', 'index', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('page', '1', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('cookUser', '', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('cookPass', '', domain='apsystemsema.com', path='/')
        self.mainpage_cookies.set('cookBox', '', domain='apsystemsema.com', path='/')

        if login.status_code == 302:  # expected here
            url = '/ema/security/optsecondmenu/intoViewOptModule.action'

            res = requests.get(self.domain + url, headers=self.headers, cookies=self.mainpage_cookies)
            if res.status_code == 200:
                page = BeautifulSoup(res.text, "html.parser")
                var_page = page.find(attrs={'id': 'viewname'}).find('option')
                self._sid = var_page.get('sid')
                self._ecu = var_page.get('en')
                self._vid = var_page.get('value')
                self._iid = var_page.get('iid')
                self._logged = True

    def is_logged(self):
        return self._logged

    def get_power(self, date):
        pload = {'sid': self._sid, 'vid': self._vid, 'iid': self._iid, 'date': date}
        res = requests.post(self.domain + "/ema/ajax/getViewAjax/getViewPowerByViewAjax", data=pload,
                            headers=self.headers, cookies=self.mainpage_cookies)

        if res.status_code == 200:
            array_final = {}
            temp_power = {}
            data = json.loads(res.text)
            array_time = data['time'].split(',')

            # Primeiro processa os dados de power:
            array_power = data['power'].split(',')
            x = 0
            for time in array_time:
                temp_power[x] = {
                    'datetime': datetime.fromtimestamp((int(time) + 8 * 60 * 60 * 1000) / 1000),
                    'power': array_power[x]
                }
                x += 1
            array_final['power'] = temp_power

            temp_power = {}
            ecu_list = data['detail'].split('&')
            for ecu_data in ecu_list:
                temp_ecu_power = {}
                sub_ecu = ecu_data.split('/')
                ecu = sub_ecu[0]
                ecu_power = sub_ecu[1].split(',')
                x = 0
                for power in ecu_power:
                    temp_ecu_power[x] = {
                        'datetime': datetime.fromtimestamp((int(array_time[x]) + 8 * 60 * 60 * 1000) / 1000),
                        'power': power
                    }
                    x += 1
                temp_power[ecu] = temp_ecu_power
            array_final['ecu_power'] = temp_power
            return array_final
        return False


'''
    def get_panel_info(self):
        self.inverterInfo = {}
        pload = {'sid': self._sid, 'vid': self._vid, 'iid': self._iid}
        res = requests.post(self.domain + "/ema/ajax/getViewAjax/getViewByViewIdAndSystemIdAjax", data=pload,
                            headers=self.headers, cookies=self.mainpage_cookies)
        optOneLength = 60
        if res.status_code == 200:
            print(len(res.text))
            numofpannel = len(res.text)/optOneLength
            for i in range(numofpannel):
                optString = res.text[i*optOneLength:i*optOneLength+optOneLength]
                inverterInfoId = optString.split("-")[0]
                optString = optString.split("-")[1]
                if optString[12:13] == 0:
                    inverter_dev_id = optString[0:12]
                else:
                    inverter_dev_id = optString[0:12] + "-" + optString[12:13]
                xposition = int(optString[13:16])
                yposition = int(optString[16:19])
                panel_angle = int(optString[19:20])
                panel_info_id = optString[20:24]
                type = int(optString[24:26])
                expand = int(optString[26:27])
                if type == 12:
                    panel_angle = 1
                self.inverterInfo[inverter_dev_id] = {
                    'inverter_info_id' : inverterInfoId,
                    'xposition' : xposition,
                    'yposition' : yposition,
                    'panel_angle' : panel_angle,
                    'panel_info_id' : panel_info_id,
                    'type' : type,
                    'expand' : expand
                }
            return self.inverterInfo
        return False
'''
