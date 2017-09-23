#Coding = 'utf-8'
##filename:wuliu

import requests
import urllib
from urllib import parse as urlparse
from lxml import html
from bs4 import BeautifulSoup
import json

class wuliu():
	def __init__(self,params):
		self.host = params['host']
		self.basic_url = params['basic_url']
		self.index_url = params['index_url']
		self._headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate, sdch',
		'Accept-Language':'zh-CN,zh;q=0.8',
		'Connection':'keep-alive',
		'Host':self.host,
		'Referer':self.basic_url,
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
		}
		self.se = requests.Session()
		self.se.headers = self._headers
		self.re = self.se.get(self.index_url)
		self.soup = BeautifulSoup(self.re.text, 'lxml')
		self.findPageParams()
		self.itemlist = []
		self.pnum = 1
		self.purl = ''
		self.inum = 0
		self.iurl = ''
		self.page_flag = False


	def findPageParams(self):
		self.pagation = self.soup.find(id = 'pagation')
		fanilpage = self.pagation.find(title = '尾页')['href']
		index = fanilpage.find('&')
		self.page_be = fanilpage[0:6]
		self.page_af = fanilpage[index:]
		self.page_num = int(fanilpage[6:index])

	def findPageUrl(self,pnum=0):
		if pnum == 0:
			self.purl = self.basic_url + self.page_be + str(self.pnum) + self.page_af
			print('Now we are findding Page NO.' + str(self.pnum))
			self.pnum = self.pnum + 1
			if self.pnum > self.page_num:
				print('All pages are finished!!!')
				self.page_flag = True
			return self.purl
		else:
			purl = self.basic_url + self.page_be + str(pnum) + self.page_af
			return purl

	def parsePage(self,purl):
		print(purl)
		self.re = self.se.get(purl,headers = self._headers)
		self.soup = BeautifulSoup(self.re.text, 'lxml')
		tuanitem = self.soup.find_all(class_ = "tuanitem")
		i = 0
		for item in tuanitem:
			item_href = item.find(class_ = 'tuanitem-meta-title').a['href']
			self.itemlist.append(item_href)

	def findAllItem(self):
		print('totle pagenum:'+ str(self.page_num))
		#self.page_num = 10
		while self.page_flag == False:
			purl = self.findPageUrl()
			self.parsePage(purl)
		print('Totle items: ' + str(len(self.itemlist)))

	def saveItems(self):
		with open('item.txt','w') as f:
			json.dump(self.itemlist,f)
		with open('item.json','w') as f:
			json.dump(self.itemlist,f)

	def readItems(self):
		with open('item.txt','r') as f:
			self.itemlist = json.load(f)

	def parseItem(self):
		self.iurl = self.basic_url + self.itemlist[self.inum]
		print(self.iurl)
		self.re = self.se.get(self.iurl)
		self.soup = BeautifulSoup(self.re.text, 'lxml')
		title = self.soup.find(class_ = "page_title").text
		print(title)
		company_name = title[title.find('【')+1:title.find('】')]
		print(company_name)
		phonenum = self.soup.find(class_ = 'linkman_msg').find_all('span')[0].text
		print(phonenum)
		faddress = self.soup.find(class_ = 'linkman_msg').find_all('span')[1].text
		print(faddress)
		
		content = self.soup.find(class_ = "ml15").text
		print(content)


if __name__ == '__main__':
	params = {}
	params['host'] = 'www.wbtrans.com'
	params['basic_url'] = 'http://www.wbtrans.com/'
	params['index_url'] = 'http://www.wbtrans.com/index.asp?ty=130'
	wl = wuliu(params)
	#wl.findAllItem()
	#wl.saveItems()
	wl.readItems()

'''
	params = {}
	params['host'] = 'www.chawuliu.com'
	params['basic_url'] = 'http://www.chawuliu.com/'
	params['index_url'] = 'http://www.wbtrans.com/index.asp?ty=130'
	wl = wuliu(params)
	wl.findAllItem()
	wl.saveItems()
'''


'''
basic_url = 'http://www.wbtrans.com'
details_url = 'http://www.chawuliu.com/detail/19838'
details_url = 'http://www.wbtrans.com/detail.asp?code=9902'

s.headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate',
	'Accept-Language':'zh-CN,zh;q=0.8',
	'Connection':'keep-alive',
	'Host':'www.chawuliu.com',
	'Referer':'http://www.chawuliu.com/',
	'Upgrade-Insecure-Requests':'1',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
	}

cookies = requests.get(basic_url, headers= headers).cookies

req = requests.get (details_url, headers = headers,  cookies = cookies)

soup = BeautifulSoup(req.text, 'lxml')

title = soup.find(class_ = "page_title").text

content = soup.find(class_ = "ml15").text

page_url = 'http://www.chawuliu.com/?page=2'

page_req = requests.get (page_url, headers = headers,  cookies = cookies)

page_soup = BeautifulSoup(page_req.text, 'lxml')

page_items = page_soup.find_all(class_ = "tuanitem")

i = 0
for item in page_items:
	item_title = item.find(class_ = 'tuanitem-meta-title')
	item_href =  item.find(class_ = 'tuanitem-meta-title').a['href']
	req = requests.get (item_href, headers = headers,  cookies = cookies)
	soup = BeautifulSoup(req.text, 'lxml')
	title = soup.find(class_ = "page_title").text
	print(title)
	i = i + 1

print(i)

item_content = soup.find(class_ = "ml15").text
'''