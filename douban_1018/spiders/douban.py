# -*- coding: utf-8 -*-
import scrapy
import urllib
from PIL import Image
from base64 import b64encode
import requests


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['https://accounts.douban.com/login']
    login_url = 'https://accounts.douban.com/login'

    def parse(self, response):
        print 'url:',response.url
        formdata = {'source':'index_nav',
                    'redir': 'https://www.douban.com/',
                    'form_email':'strong0528@aliyun.com',
                    'form_password':'307xiaoqiang608',
                    'remember':'on',
                    'user_login':'登录'
                    }
        captcha_url = response.xpath("//div/img[@id='captcha_image']/@src").extract()
        # captcha_url2 = response.xpath("//div/img[@id='captcha_image']/@src").get()
        print 'captcha_url:',captcha_url
        # print 'captcha_url2:', captcha_url2

        if len(captcha_url):
            captcha = self.regonize_captcha(captcha_url[0])
            formdata['captcha-solution'] = captcha
            captcha_id = response.xpath("//input[@name='captcha-id']/@value").get()
            print 'captcha_id:',captcha_id
            formdata['captcha-id'] = captcha_id

        yield scrapy.FormRequest(
            url = self.login_url,
            formdata = formdata,
            callback=self.parse_login_after
        )
        # yield scrapy.Request('https://www.douban.com/', callback=self.parse_login_after)

    def parse_login_after(self, response):
        # 验证是否成功登录
        print '---------denglu-------'
        print 'response.url:',response.url
        user_name = response.xpath("//li[@class='nav-user-account']/a/span/text()").get()
        print 'user_name:',user_name
        #个人主页url:
        people_index_url = response.xpath("//div[@class='more-items']//tr[1]/td/a/@href").extract()[0]
        print 'people_index_url:',people_index_url

        yield scrapy.Request(people_index_url, callback=self.parse_people_index)

    # 登录个人主页,对个人主页进行操作
    def parse_people_index(self, response):
        print '----登录个人主页-------'
        print '个人主页url:',response.url
        edit_url = response.xpath("//form[@name='edit_sign']/@action").extract()[0]
        edit_url_full = 'https://www.douban.com'+ edit_url
        print 'edit_url:',edit_url
        ck = response.xpath("//input[@name='ck']/@value").extract()[0]
        formdata = {'ck':ck,
                    'signature':'我是最美的花朵'}
        yield scrapy.FormRequest(edit_url_full, formdata=formdata, callback=self.parse_edit_none)

    # 避免二次请求parse处理
    def parse_edit_none(self, response):
        pass

    # 借助阿里云市场的图形验证码识别自动进行输入
    # 该接口的网址:https://market.aliyun.com/products/57124001/cmapi028447.html
    def regonize_captcha(self, image_url):
        urllib.urlretrieve(image_url, 'captcha2.png')
        recognize_url = 'http://yzmplus.market.alicloudapi.com/fzyzm'
        formdata = {'v_type': 'cn'}
        with open('captcha2.png', 'rb') as fp:
            data = fp.read()
            pic = b64encode(data)
            formdata['v_pic'] = pic
        # print 'formdata:', formdata

        # 该接口的appcode,需购买,填写个人的.
        appcode = 'ea63dd28efea4ca98860d2bf972bb907'
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Authorization': 'APPCODE ' + appcode}

        response = requests.post(recognize_url, data=formdata, headers=headers)
        result = response.json()
        print result
        code = result['v_code']
        # 自动识别存在识别不出来,增加人工识别
        if code == '':
            code = self.regonize_captcha_by_hand(image_url)
        print 'code:', code
        return code

     # 显示验证码,手动输入
    def regonize_captcha_by_hand(self, image_url):
        urllib.urlretrieve(image_url, 'captcha.png')
        image = Image.open('captcha.png')
        image.show()
        captcha = raw_input('请输入验证码:')
        return captcha
