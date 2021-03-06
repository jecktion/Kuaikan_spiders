# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import requests
import time
import random
import re
from multiprocessing.dummy import Pool
import csv
import json
import sys


class Spider(object):
	def __init__(self):
		self.date = '2000-01-01'
	
	def get_headers(self):
		user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
		               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
		               'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
		               'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
		               'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
		               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
		               'Opera/9.52 (Windows NT 5.0; U; en)',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
		               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
		               'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
		user_agent = random.choice(user_agents)
		headers = {'Host': 'www.shilladfs.com', 'Connection': 'keep-alive',
		           'User-Agent': user_agent,
		           'Referer': 'http://www.shilladfs.com/estore/kr/zh/Skin-Care/Basic-Skin-Care/Pack-Mask-Pack/p/3325351',
		           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		           'Accept-Encoding': 'gzip, deflate, br',
		           'Accept-Language': 'zh-CN,zh;q=0.8'
		           }
		return headers
	
	def p_time(self, stmp):  # 将时间戳转化为时间
		stmp = float(str(stmp)[:10])
		timeArray = time.localtime(stmp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		return otherStyleTime

	def remove_emoji(self, text):
		emoji_pattern = re.compile(
			u"(\ud83d[\ude00-\ude4f])|"  # emoticons
			u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
			u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
			u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
			u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
			"+", flags=re.UNICODE)
		return emoji_pattern.sub(r'*', text)

	def replace(self, x):            # 将其余标签剔除
		# 去除img标签,7位长空格
		removeImg = re.compile('<img.*?>| {7}|')
		# 删除超链接标签
		removeAddr = re.compile('<a.*?>|</a>')
		# 把换行的标签换为\n
		replaceLine = re.compile('<tr>|<div>|</div>|</p>')
		# 将表格制表<td>替换为\t
		replaceTD = re.compile('<td>')
		# 把段落开头换为\n加空两格
		replacePara = re.compile('<p.*?>')
		# 将换行符或双换行符替换为\n
		replaceBR = re.compile('<br><br>|<br>')
		# 将其余标签剔除
		removeExtraTag = re.compile('<.*?>', re.S)
		# 将&#x27;替换成'
		replacex27 = re.compile('&#x27;')
		# 将&gt;替换成>
		replacegt = re.compile('&gt;|&gt')
		# 将&lt;替换成<
		replacelt = re.compile('&lt;|&lt')
		# 将&nbsp换成''
		replacenbsp = re.compile('&nbsp;')
		# 将&#177;换成±
		replace177 = re.compile('&#177;')
		replace1 = re.compile(' {2,}')
		x = re.sub(removeImg, "", x)
		x = re.sub(removeAddr, "", x)
		x = re.sub(replaceLine, "\n", x)
		x = re.sub(replaceTD, "\t", x)
		x = re.sub(replacePara, "", x)
		x = re.sub(replaceBR, "\n", x)
		x = re.sub(removeExtraTag, "", x)
		x = re.sub(replacex27, '\'', x)
		x = re.sub(replacegt, '>', x)
		x = re.sub(replacelt, '<', x)
		x = re.sub(replacenbsp, '', x)
		x = re.sub(replace177, u'±', x)
		x = re.sub(replace1, '', x)
		x = re.sub('\n', '', x)
		return x.strip()


	def GetProxies(self):
		# 代理服务器
		proxyHost = "http-dyn.abuyun.com"
		proxyPort = "9020"
		# 代理隧道验证信息
		proxyUser = "HI18001I69T86X6D"
		proxyPass = "D74721661025B57D"
		proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
			"host": proxyHost,
			"port": proxyPort,
			"user": proxyUser,
			"pass": proxyPass,
		}
		proxies = {
			"http": proxyMeta,
			"https": proxyMeta,
		}
		return proxies
	
	def get_detail_page(self, ss):  # 获取某一页的所有评论
		film_url, vod, product_number, plat_number, page = ss
		print '爬取页数：',page, 'vod:',vod
		url = "https://api.kkmh.com/v2/comments/floor_list"
		
		querystring = {"limit": "20", "offset": str(20 * (page - 1)), "order": "score", "source": "0", "target_id": vod,
		               "target_type": "comic", "total": "1"}
		retry = 10
		while 1:
			try:
				headers = {
					'host': "api.kkmh.com",
					'package-id': "com.kuaikan.comic",
					'hw-model': "iPhone10,1",
					'accept-language': "zh-Hans-CN;q=1",
					'accept-encoding': "br, gzip, deflate",
					'accept': "*/*",
					'user-agent': "Kuaikan/5.12.0/512000(iPhone;iOS 11.4;Scale/2.00;WiFi;1334*750)",
					# "User-Agent": "Kuaikan/5.15.1/515001(Android;8.0.0;MHA-AL00;kuaikan9;WIFI;1808*1080)",
					'connection': "keep-alive",
					'lower-flow': "No"

					# "Cookie" : "Expires=Tue, 16-Oct-2018 08:14:34 GMT;uid=124534121;session=v1-GAgAAAAAAAADBRggJkD7e71glTFXZ07zH5LE1HpEg6d1KkwdTcGv3Kv_l78A;Max-Age=86400;kk_s_t=1543912464744;Domain=.kkmh.com;Path=/",
					# "X-Device" : "A:d18b60cb47ed6fac",
					# "User-Agent" : "Kuaikan/5.15.1/515001(Android;8.0.0;MHA-AL00;kuaikan9;WIFI;1808*1080)",
					# "Muid" : "4583fcd3afbfc40503d1161836598da4",
					# "Package-Id" : "com.kuaikan.comic",
					# "Lower-Flow" : "No",
					# "App-Info" : "eyJhbmRyb2lkX2lkIjoiZDE4YjYwY2I0N2VkNmZhYyIsImFwcF9zZWNyZXRfc2lnbiI6IiIsImJkIjoiSFVBV0VJIiwiY2EiOjIwLCJjdCI6MjAsImRldnQiOjEsImRwaSI6NDgwLCJncHMiOiIzOS44NjkzMDIsMTE2LjM4MzQ1MiIsImhlaWdodCI6MTgwOCwiaW1laSI6Ijg2NDIyOTAzMDE0NDc5NCIsImltc2kiOiI0NjAwMzYwMDEwODQ5ODkiLCJtYWMiOiJhNDpjYTphMDphYToyOjkzIiwibW9kZWwiOiJNSEEtQUwwMCIsIm92IjoiOC4wLjAiLCJwaG9uZU51bWJlciI6IiIsIndpZHRoIjoxMDgwfQ==",
					# "Host" : "api.kkmh.com",
					# "Connection" : "Keep-Alive",
					# "Accept-Encoding" : "gzip",
				}
				results = []
				text = requests.get(url, headers=headers, proxies=self.GetProxies(), timeout=10,
									params=querystring).json()
				# print 'text:',text
				items = text['data']['comment_floors']
				last_modify_date = self.p_time(time.time())
				for item in items:
					try:
						nick_name = item['root']['user']['nickname']
						nick_name = self.remove_emoji(nick_name)
					except:
						nick_name = ''
					try:
						tmp1 = self.p_time(item['root']['created_at'])
						cmt_date = tmp1.split()[0]
						cmt_time = tmp1
						# if cmt_date < self.date:
						# 	continue
					except:
						cmt_date = ''
						cmt_time = ''
					try:
						comments = self.replace(item['root']['content'])
						comments = self.remove_emoji(comments)
						comments = self.replace(comments)
					except:
						comments = ''
					try:
						like_cnt = str(item['root']['likes_count'])
					except:
						like_cnt = '0'
					try:
						cmt_reply_cnt = str(item['children_total'])
					except:
						cmt_reply_cnt = '0'
					long_comment = '0'
					source_url = film_url
					tmp = [product_number, plat_number, nick_name, cmt_date, cmt_time, comments, like_cnt,
					       cmt_reply_cnt, long_comment, last_modify_date, source_url]
					print '|'.join(tmp)
					results.append([x.encode('gbk', 'ignore') for x in tmp])
				return results
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
				else:
					continue
	
	def get_total_page(self, product_url):  # 获取总页数
		p = re.compile('topic/(\d+)')
		film_id = re.findall(p, product_url)[0]
		url = "https://api.kkmh.com/v1/topics/%s" % film_id
		querystring = {"is_homepage": "0", "is_new_device": "false", "page_source": "9", "sort": "1", "sortAction": "1"}
		retry = 10
		headers = {
			'host': "api.kkmh.com",
			'package-id': "com.kuaikan.comic",
			'hw-model': "iPhone10,1",
			'accept-language': "zh-Hans-CN;q=1",
			'accept-encoding': "br, gzip, deflate",
			'accept': "*/*",
			'user-agent': "Kuaikan/5.12.0/512000(iPhone;iOS 11.4;Scale/2.00;WiFi;1334*750)",
			'connection': "keep-alive",
			'lower-flow': "No"
		}
		while 1:
			try:
				text = requests.get(url, headers=headers, params=querystring, timeout=10).json()['data']
				comment_num = int(text['comments_count'])
				if comment_num % 20 == 0:
					pagenums = comment_num / 20
				else:
					pagenums = comment_num / 20 + 1
				return pagenums
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_vod(self, film_url):  # 获取电影的VOD
		p = re.compile('topic/(\d+)')
		film_id = re.findall(p, film_url)[0]
		url = "https://api.kkmh.com/v1/topics/%s" % film_id
		querystring = {"is_homepage": "0", "is_new_device": "false", "page_source": "9", "sort": "1", "sortAction": "1"}
		retry = 10
		headers = {
			'host': "api.kkmh.com",
			'package-id': "com.kuaikan.comic",
			'hw-model': "iPhone10,1",
			'accept-language': "zh-Hans-CN;q=1",
			'accept-encoding': "br, gzip, deflate",
			'accept': "*/*",
			'user-agent': "Kuaikan/5.12.0/512000(iPhone;iOS 11.4;Scale/2.00;WiFi;1334*750)",
			'connection': "keep-alive",
			'lower-flow': "No"
		}
		while 1:
			try:
				results = []
				text = requests.get(url, headers=headers, proxies=self.GetProxies(), params=querystring,
				                    timeout=10).json()
				# print '--------',text
				items = text['data']['comics']
				for item in items:
					vod = str(item['id'])
					# print 'vod============',vod
					total = int(item['comments_count'])
					# print 'total============',total
					results.append([vod, total])
				return results
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_all_comments_vod(self, film_url, product_number, plat_number, vod, total):  # 获取某一集的所有评论
		print '每集vod:',vod
		if total % 20 == 0:
			pagenums = total / 20
		else:
			pagenums = total / 20 + 1
		print '总页数:%d' % pagenums
		ss = []
		for page in range(1, pagenums + 1):
			ss.append([film_url, vod, product_number, plat_number, page])
		pool = Pool(4)
		items = pool.map(self.get_detail_page, ss[::-1])
		pool.close()
		pool.join()
		mm = []
		for item in items:
			if item is not None:
				mm.extend(item)
		with open('data_comments.csv', 'a') as f:
			writer = csv.writer(f, lineterminator='\n')
			writer.writerows(mm)
	
	def get_all_comments(self, film_url, product_number, plat_number):  # 获取所有评论
		vods = self.get_vod(film_url)
		if vods is None:
			return None
		else:
			print u'共有 %d 集' % len(vods)
			for item in vods:
				vod, total = item
				self.get_all_comments_vod(film_url, product_number, plat_number, vod, total)


if __name__ == "__main__":
	spider = Spider()
	# spider.get_all_comments('http://www.kuaikanmanhua.com/web/topic/906', 'D0000001', 'P11')
	s = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s.append([i[0], i[2]])
	for j in s:
		print j[0],j[1]
		spider.get_all_comments(j[1], j[0], 'P11')
