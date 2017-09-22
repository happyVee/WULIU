#Coding = 'utf-8'
##filename:wuliu

import requests
import urllib
from urllib import parse as urlparse
from lxml import html
from bs4 import BeautifulSoup


basic_url = 'http://www.chawuliu.com/'
details_url = 'http://www.chawuliu.com/detail/19838'

headers = {
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
