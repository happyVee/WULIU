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
import xlwt


def findRoads(info):
	title = info['title']
	city = findCitys(title)
	fcity = city[0]
	tocity = city[1]
	pacity = city[2]

	exlistli = []
	exlist = []

	if(len(fcity)>0 and len(tocity)>0):
		addrlist = findAddr(info,fcity,tocity)
		for fcityi in fcity:
			for tocityi in tocity:
				exlistli = biuldLi(info,fcityi,tocityi,pacity,addrlist)
				if exlistli != False:
					exlist.append(exlistli)
		'''
		with open('road.csv','a') as csvfile:
			spamwriter = csv.writer(csvfile, dialect='excel')
			for exl in exlist:
				spamwriter.writerow(exl)
		'''
		#print('找到 : ' + str(len(exlist)))
	return exlist

def findCitys(title):
	title = title[title.find('】')+1:].replace('，','').replace('。','').replace('和','、').replace('及','、').replace('专线','')
	if title.find('中转') > -1:
		pacity = title.split('中转')[1]
		ftaddr = title.split('中转')[0]
	else:
		pacity = ''
		ftaddr = title
	if ftaddr.find('至') > -1:
		fcity = ftaddr.split('至')[0].split('、')
		if '' in fcity:
			fcity.remove('')
		tocity = ftaddr.split('至')[1].split('、')
		if '' in tocity:
			tocity.remove('')
	elif ftaddr.find('直达') > -1:
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

	return [fcity,tocity,pacity]

def findAddr(info,fcity,tocity):
	ctext = info['ctext']
	addrlist = {}
	telline = []
	ctext = ctext.replace('：\n','：').replace(':\n','：').replace('：',':').replace('\xa0',':').replace('\r','\n')
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
						addrflag = 2
						tocity[tocity.index(tocityi)] = city
						break

			if addrflag > 0:
				addrl = [addrflag,city,addr,person,tel,pnum]
				if city not in addrlist.keys():
					addrl = checkAddr(addrl)
					addrlist[city] = addrl
	else:
		city = fcity[0]
		addr = info['faddr']
		person = ''
		tel = ''
		pnum = info['ctel']
		addrl = [1,city,addr,person,tel,pnum]
		addrl = checkAddr(addrl)
		addrlist[city] = addrl
	return addrlist

def checkAddr(addrl):
	addr = addrl
	if addr[4] == '':
		for i in range(1,6):
			m = re.findall(r"1\d{10}",addr[i])
			if m:
				addr[4] = m[0]
				break
	if addr[5] == '':
		for i in range(1,6):
			m = re.findall(r"0\d{2}\d?.?\d{7}\d?",addr[i])
			if m:
				addr[4] = m[0]
				break
	if len(addr[1]) > 4:
		addr[1] = addr[1][0:4]
	if addr[2].startswith(('0','1')):
		addr[2] = ''
	if len(addr[3]) > 3:
		addr[3] = addr[3][0:3]
	m = re.findall(r"1\d{10}",addr[4])
	if m:
		addr[4] = m[0]
	else:
		addr[4] = ''
	m = re.findall(r"0\d{2}\d?.?\d{7}\d?",addr[5])
	if m:
		addr[5] = m[0]
	else:
		addr[5] = ''
	return addr

def biuldLi(info,fcityi,tocityi,pacity,addrlist):
	faddrlist = decCity(fcityi)
	taddrlist = decCity(tocityi)
	if faddrlist == False:
		faddrlist = [fcityi,fcityi,fcityi]
	if taddrlist == False:
		taddrlist = [tocityi,tocityi,tocityi]
	cname = info['cname']
	rinfo =  fcityi + "到" + tocityi
	faddr_p = faddrlist[0]
	faddr_c = faddrlist[1]
	faddr_a = faddrlist[2]
	if fcityi in addrlist.keys():
		faddr = addrlist[fcityi][2]
		fpre = addrlist[fcityi][3]
		ftel = addrlist[fcityi][4]
		fnum = addrlist[fcityi][5]
	else:
		faddr = info['faddr']
		fpre = ''
		ftel = info['tel']
		fnum = info['pnum']
	
	taddr_p = taddrlist[0]
	taddr_c = taddrlist[1]
	taddr_a = taddrlist[2]
	if tocityi in addrlist.keys():
		taddr = addrlist[tocityi][2]
		tpre = addrlist[tocityi][3]
		ttel = addrlist[tocityi][4]
		tnum = addrlist[tocityi][5]
	else:
		taddr = ''
		tpre = ''
		ttel = ''
		tnum = ''
	info['cfig'] = info['cfig'] + [' ',' ',' ',' ']	
	cfig = info['cfig'][0:5]
	exlistli = [cname,rinfo,faddr_p,faddr_c,faddr_a,faddr,fpre,ftel,fnum,taddr_p,taddr_c,taddr_a,taddr,tpre,ttel,tnum,pacity,cfig[0],cfig[1],cfig[2],cfig[3],cfig[4],info['iurl']]
	return exlistli

def saveInfo(infolist):
	print("共有"+ str(len(infolist)) + " 个公司")
	exlist = []
	for i in range(len(infolist)):
		info = infolist[i]
		m = re.findall(r"1\d{10}",info['ctel'])
		if m:
			info['tel'] = m[0]
		else:
			info['tel'] = ''

		m = re.findall(r"0\d{2}\d?.?\d{7}\d?",info['ctel'])
		if m:
			info['pnum'] = m[0]
		else:
			info['pnum'] = ''
		res = findRoads(info)
		exlist = exlist + res
	#print("总有"+ str(len(exlist)) + " 条路线")
	return exlist

def saveToExcel(count,ws,exlist):
	for column in range(len(exlist)):
		exl = exlist[column]
		colVal = count + column
		for row in range(len(exl)):
			value = exl[row]
			ws.write(colVal,row,value)
	return ws

def saveAColmn(column,ws,exl,style0):
	for row in range(len(exl)):
		value = exl[row]
		ws.write(column,row,value,style0)

def decCity(cityname):
	area_code = getAreaCode(cityname)
	p_name=''
	c_name=''
	a_name=''
	if area_code == False:
		return False
	else:
		p_code = area_code[0:2]
		c_code = area_code[2:4]
		a_code = area_code[4:6]
		if c_code == '00':
			c_code = '01'
			a_code = '01'
		if a_code == '00':
			a_code = '01'
		p_name = code2city[p_code]['name']
		if p_code == '71' or p_code == '81' or p_code == '82':
			c_name = p_name
			a_name = p_name
			return [p_name,c_name,a_name]
		c_name = code2city[p_code]['cities'][c_code]['name']
		if a_code not in code2city[p_code]['cities'][c_code]['areas'].keys():
			a_name = '市辖区'
		else:
			a_name = code2city[p_code]['cities'][c_code]['areas'][a_code]
		return [p_name,c_name,a_name]


def getAreaCode(cityname):
	cit = city2code.keys()
	for ci in cit:
		if cityname in ci:
			return city2code[ci]
	return False


if __name__ == '__main__':
	wb = xlwt.Workbook()
	ws = wb.add_sheet('Sheet1')
	with open('city2code.json','r',encoding = 'utf=8') as f:
		city2code= json.load(f)
	with open('code2city.json','r',encoding = 'utf=8') as f:
		code2city = json.load(f)
	exl0 = ['物流公司名称','线路信息','省','市','县/区','详细地址','联系人','手机号码','网点电话','省','市','县/区','详细地址','联系人','手机号码','网点电话','中转区域','图片1','图片2','图片3','图片4','图片5','链接']
	style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on')
	count = 0
	saveAColmn(count,ws,exl0,style0)
	count = 1
	for i in range(0,4):
		fname = 'web1info' + str(i) + '.json'
		#fname = 'web2info' + str(i) + '.json'
		#fname = 'info.json'
		print("打开文件"+ fname)
		with open(fname,'r') as f:
			infolist = json.load(f)
		exlist = saveInfo(infolist)
		saveToExcel(count,ws,exlist)
		print("总有"+ str(len(exlist)) + " 条路线")
		count = count + len(exlist)
	print("总有"+ str(count) + " 条路线")


	ws2 = wb.add_sheet('Sheet2')
	count = 0
	saveAColmn(count,ws2,exl0,style0)
	count = 1
	for i in range(0,4):
		#fname = 'web1info' + str(i) + '.json'
		fname = 'web2info' + str(i) + '.json'
		#fname = 'info.json'
		print("打开文件"+ fname)
		with open(fname,'r') as f:
			infolist = json.load(f)
		exlist = saveInfo(infolist)
		saveToExcel(count,ws,exlist)
		print("总有"+ str(len(exlist)) + " 条路线")
		count = count + len(exlist)
	print("总有"+ str(count) + " 条路线")


	wb.save('AddrItem0.xls')
