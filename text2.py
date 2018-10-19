# coding=utf-8

import urllib
from base64 import b64encode
import requests

captcha_url = 'https://www.douban.com/misc/captcha?id=3fb7zhFK8Inin8Gb5L5noRxd:en&size=s'
urllib.urlretrieve(captcha_url, 'captcha2.png')

recognize_url = 'http://yzmplus.market.alicloudapi.com/fzyzm'

formdata = {'v_type':'cn'}
# formdata = {}

with open('captcha2.png', 'rb') as fp:
    data = fp.read()
    pic = b64encode(data)
    formdata['v_pic'] = pic

print 'formdata:',formdata

appcode = 'ea63dd28efea4ca98860d2bf972bb907'
headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'Authorization': 'APPCODE ' + appcode}

response = requests.post(recognize_url, data=formdata, headers=headers)
result = response.json()
print result
code = result['v_code']
print 'code:',code


