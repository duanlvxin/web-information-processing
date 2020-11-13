# -*- coding: utf-8 -*-
import scrapy
from mySpider.items import MyspiderItem

class teacherInfoSpider(scrapy.Spider):
    name = 'teacherInfo'
    allowed_domains = ['cs.hitsz.edu.cn']
    start_urls = ['http://cs.hitsz.edu.cn/szll/qzjs.htm']
    offset = 5
    url = 'http://cs.hitsz.edu.cn/szll/qzjs/'

    def parse(self, response):
       for each in response.xpath('/html/body/div[2]/div/div/div[2]/div/div[2]/div/ul/li'):
           item = MyspiderItem()

           name = each.xpath('./div[1]/p/text()').extract()
           item['name'] = name[0] if len(name)>0 else ''
           work = each.xpath('./div[2]/dl[1]/dd/text()').extract()
           item['work'] = work[0] if len(work)>0 else ''
           tellphone = each.xpath('./div[2]/dl[2]/dd/text()').extract()
           item['tellphone'] = tellphone[0] if len(tellphone)>0 else ''
           fax = each.xpath('./div[2]/dl[3]/dd/text()').extract()
           item['fax'] = fax[0] if len(fax)>0 else ''
           email = each.xpath('./div[2]/dl[4]/dd/a/text()').extract()
           item['email'] = email[0] if len(email)>0 else ''
           researchDirection = each.xpath('./div[2]/dl[5]/dd/text()').extract()
           item['researchDirection'] = researchDirection[0] if len(researchDirection)>0 else ''
           yield item

       if self.offset>1:
           self.offset -= 1

       yield scrapy.Request(self.url + str(self.offset) + '.htm', callback = self.parse)