#Coding = 'utf-8'
##filename:wuliu

import requests
import urllib
from urllib import parse as urlparse
from lxml import html
from bs4 import BeautifulSoup
import json
import wuliu
import csv
import re


def findTrans(info):
	#title = self.title
	title = info['title']
	title = title[title.find('】')+1:].replace('，','').replace('。','').replace('和','、').replace('及','、')
	if title.find('中转') > -1:
		pacity = title.split('中转')[1]
		ftaddr = title.split('中转')[0]
	else:
		pacity = ''
		ftaddr = title
	if ftaddr.find('直达') > -1:
		fcity = ftaddr.split('直达')[0].split('、')
		if '' in fcity:
			fcity.remove('')
		tocity = ftaddr.split('直达')[1].split('、')
		if '' in tocity:
			tocity.remove('')
	elif ftaddr.find('往返') > -1:
		fcity = ftaddr.split('往返')[0].split('、')
		if '' in fcity:
			fcity.remove('')
		tocity = ftaddr.split('往返')[1].split('、')
		if '' in tocity:
			tocity.remove('')
	else:
		fcity = []
		tocity = []
	#self.fcity = fcity
	#self.tocity = tocityi
	#self.pacity = pacity
	count = 0
	exlistli = []
	exlist = []

	if(len(fcity)>0 and len(tocity)>0):
		addrlist = fmtCtext(info,fcity,tocity)
		print("应该有：" + str(len(fcity)*len(tocity)))
		for fcityi in fcity:
			for tocityi in tocity:
				exlistli = biuldLi(info,fcityi,tocityi,pacity,addrlist)
				if exlistli != False:
					exlist.append(exlistli)
					count = count + 1
					#print(exlistli)
					#print(exlistli[1])
		with open('road.csv','a') as csvfile:
			spamwriter = csv.writer(csvfile, dialect='excel')
			for exl in exlist:
				spamwriter.writerow(exl)
		print('实际有 : ' + str(len(exlist)))
		return count
	else:
		return count


def fmtCtext(info,fcity,tocity):
	ctext = info['ctext']
	addrlist = {}
	telline = []
	ctext = ctext.replace('：\n','：').replace(':\n','：').replace('：',':').replace('\xa0',':')
	ctlist = ctext.split('\n')
	if '' in ctlist:
		ctlist.remove('')
	tel_count = ctext.count('电话')
	for line in ctlist:
		if '电话' in line or '手机' in line:
			ind = ctlist.index(line)
			if ind >0 and '电话' not in ctlist[ind-1]:
				telline.append(ind)
	if len(telline) > 1:
		for i in range(len(telline)):
			addrflag = 0
			ind = telline[i]
			if ind == 0:
				continue

			if '联系人' in ctlist[ind]:
				person = ctlist[ind][ctlist[ind].find('联系人')+4:]
			elif '联系人' in ctlist[ind-1]:
				person = ctlist[ind-1][ctlist[ind-1].find('联系人')+4:]
			elif '联系人' in ctlist[ind+1]:
				person = ctlist[ind+1][ctlist[ind+1].find('联系人')+4:]
			else:
				person = ''

			if '手机' in ctlist[ind]:
				tel = ctlist[ind][ctlist[ind].find('手机')+3:]
			elif '手机' in ctlist[ind-1]:
				tel = ctlist[ind-1][ctlist[ind-1].find('手机')+3:]
			elif '手机' in ctlist[ind+1]:
				tel = ctlist[ind+1][ctlist[ind+1].find('手机')+3:]
			else:
				tel = ''

			if '电话' in ctlist[ind]:
				pnum = ctlist[ind][ctlist[ind].find('电话')+3:]
			else:
				pnum = ''
			
			if ('联系人' in ctlist[ind-1] or '手机' in ctlist[ind-1]) and ind > 2 and ('地' in ctlist[ind-2] or ':' in ctlist[ind-2]):
				addr = ctlist[ind-2][ctlist[ind-2].find(':')+1:]
				city = ctlist[ind-2][:ctlist[ind-2].find(':')]
			elif '地' in ctlist[ind-1] or (':' in ctlist[ind-1] and '联系人' not in ctlist[ind-1] and '手机' not in ctlist[ind-1]and '电话' not in ctlist[ind-1]):
				addr = ctlist[ind-1][ctlist[ind-1].find(':')+1:]
				city = ctlist[ind-1][:ctlist[ind-1].find(':')]
			elif '地' in ctlist[ind] or (':' in ctlist[ind] and '联系人' not in ctlist[ind] and '手机' not in ctlist[ind] and '电话' not in ctlist[ind]):
				addr = ctlist[ind][ctlist[ind].find(':')+1:]
				city = ctlist[ind][:ctlist[ind].find(':')]
			elif '地' in ctlist[ind+1] or (':' in ctlist[ind+1] and '联系人' not in ctlist[ind+1] and '手机' not in ctlist[ind+1] and '电话' not in ctlist[ind+1]):
				addr = ctlist[ind+1][ctlist[ind+1].find(':')+1:]
				city = ctlist[ind+1][:ctlist[ind+1].find(':')]
			else:
				addr = ''
				city = ''

			for fcityi in fcity:
				if fcityi in city or fcityi in addr:
					addrflag = 1
					city = fcityi
					break
				if city in fcityi:
					addrflag = 1
					fcity[fcity.index(fcityi)] = city
					break

			if addrflag == 0:
				for tocityi in tocity:
					if tocityi in city or tocityi in addr:
						addrflag = 2
						city = tocityi
						break
					if city in tocityi:
						addrflag = 1
						tocityi[tocityi.index(tocityi)] = city
						break

			if addrflag > 0:
				addrl = [addrflag,city,addr,person,tel,pnum]
				if city not in addrlist.keys():
					addrlist[city] = addrl
				#print(addr)
	else:
		city = fcity[0]
		addr = info['faddr']
		person = ''
		tel = ''
		pnum = info['ctel']
		addrl = [1,city,addr,person,tel,pnum]
		addrlist[city] = addrl
	print('找到地址: ' + str(len(addrlist)))
	return addrlist

def checkAddr(addr):
	if addr[4] == '':
		for line in addr:
			m = re.findall(r"1\d{10}",addr[i])
			if m:
				addr[4] = m[0]
				break
	if addr[5] == '':
		for i in range(5):
			m = re.findall(r"0\d{3}.*\d{8}",addr[i])
			if m:
				addr[4] = m[0]
				break
	if len(addr[1]) > 4:
		addr[1] = addr[1][0:4]
	if addr[2].startswith(('0','1')):
		addr[2] = ''
	if len(addr[3]) > 3:
		addr[3] = addr[3][0:3] 
	return

def biuldLi(info,fcityi,tocityi,pacity,addrlist):
	cname = info['cname']
	rinfo =  fcityi + "到" + tocityi
	faddr_p = "待写"
	faddr_c = "待写"
	faddr_a = fcityi
	if faddr_a in addrlist.keys():
		faddr = addrlist[faddr_a][2]
		fpre = addrlist[faddr_a][3]
		ftel = addrlist[faddr_a][4]
		fnum = addrlist[faddr_a][5]
	else:
		faddr = info['faddr']
		fpre = ''
		ftel = ''
		fnum = info['ctel']
	taddr_p = "待写"
	taddr_c = "待写"
	taddr_a = tocityi
	if taddr_a in addrlist.keys():
		taddr = addrlist[taddr_a][2]
		tpre = addrlist[taddr_a][3]
		ttel = addrlist[taddr_a][4]
		tnum = addrlist[taddr_a][5]
	else:
		taddr = ''
		tpre = ''
		ttel = ''
		tnum = ''
	cfig = info['cfig']
	exlistli = [cname,rinfo,faddr_p,faddr_c,faddr_a,faddr,fpre,ftel,fnum,taddr_p,taddr_c,taddr_a,taddr,tpre,ttel,tnum,pacity,"cfig"]
	return exlistli



if __name__ == '__main__':
	with open('info.json','r') as f:
		infolist = json.load(f)
	count = 0
	#findTrans(infolist[9])
	for i in range(len(infolist)):
		print('NO.' + str(i))

		count = count + findTrans(infolist[i])

	print("Finish the Job! Find " + str(count) + " Road")