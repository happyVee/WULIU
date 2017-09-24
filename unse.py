class CompyDetial():
	def __init__(self,info):
		self.title = info['title']
		self.cname = info['cname']
		print(self.cname)
		self.ctel = info['ctel']
		self.faddr = info['faddr']
		self.ctext = info['ctext']
		self.content = info['content']
		self.cfig = info['cfig']
		self._info = info
		self.exlist = []
		self.exlistli = []

	def findTrans(self):
		self.title = self.title[self.title.find('】')+1:].replace('，','').replace('。','')
		fcity = self.title.split('直达')[0].split('、')
		taddr = self.title.split('直达')[1]
		tocity = taddr.split('中转')[0].split('、')
		pacity = taddr.split('中转')[1].split('、')
		count = 0
		for fcityi in fcity:
			if len(fcityi) > 0 :
				for tocityi in tocity:
					if len(tocityi) > 0 :
						exlistli = self.biuldLi(fcityi,tocityi,pacity)
						if exlistli != False:
							self.exlist.append(exlistli)
							count = count + 1
		print('Build excel item : ' + str(count))


	def biuldLi(self,fcityi,tocityi,pacity):
		cname = self.cname
		rinfo =  fcityi + "到" + tocityi
		faddr_p = "浙江"
		faddr_c = "杭州"
		faddr_a = fcityi
		faddr = self.faddr
		fpre = ''
		ftel = self.ctel
		fnum = ''
		taddr_p = "江西"
		taddr_c = "南昌"
		taddr_a = tocityi
		taddr = ''
		tpre = ''
		ttel = self.ctext.split('\n')[2]
		tnum = self.ctext.split('\n')[3]
		pacity = str(pacity)
		exlistli = [cname,rinfo,faddr_p,faddr_c,faddr_a,faddr,fpre,ftel,fnum,taddr_p,taddr_c,taddr_a,taddr,tpre,ttel,tnum,pacity]


		#ctextli = self.ctext.
