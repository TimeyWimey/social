from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import Context
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time
#для запроса
import requests
from polls.reques import Request
from polls.settings import api_v

# Create your views here.
@csrf_exempt
def home(request):
	return  TemplateResponse(request, "index.html")
	
def pie(request):
	if request.method == "GET":
		return TemplateResponse(request, "Chart/samples/pie.html")
	else:
		return HttpResponseNotFound
@csrf_exempt
def search(request):
	if request.method == "POST":
		response_data = {} #результат 

		searchtext =request.POST["searchtext"]

		req = Request(api_v)

		r = requests.post(req.request_url('newsfeed.search','q='+searchtext+'&extended=1&count=200&start_time=0&fields=sex,bdate,city,country,can_post,can_see_all_posts,can_see_audio,can_write_private_message')).json()

		type_ = count_type(r)
		sex = count_sex(r)
		city = count_city(r)
		date = count_time_pub(r)
		#platfom = count_os(r)

		response_data = {
			#'count_type': type_, 
			'count_city': city,
			'count_sex': sex,
			'count_date': date
			#'platfom': platfom
		}
		#f = open('log.txt','w')ываыва
		#f.write(str(r))
		#f.close()
		response = HttpResponse(json.dumps(response_data, ensure_ascii=False), content_type="application/json; charset=utf-8")
		response['Access-Control-Allow-Origin'] = '*'
		return response
	else:
		return HttpResponseNotFound

def con_json(a,b):
	for i in b:
		a[i] = b[i]
	return a
def search_json(st, data,result):
	for i in data:
		if(type(data[i]).__name__ == "dict"):
			con_json(result,search_json(st,data[i],result))
		elif i == st:
			if data[i] in result:
				result[data[i]]+=1
			else:
				result[data[i]]=1
	return result

def count_city(data):
	result = {'nouser':0,'nogroup':0}
	for i in range(1,len(data['response'])-1):
		try:
			js = data['response'][i]
			if ('user' in js) and (js['user']!=None):
				if ('city' in js['user']):
					if js['user']['city'] in result:
						result[js['user']['city']]+=1
					else:
						result[js['user']['city']]=1
				else:
					result['nouser'] += 1
			else:
				if ('city' in js['group']):
					if js['group']['city'] in result:
						result[js['group']['city']]+=1
					else:
						result[js['group']['city']]=1
				else:
					result['nogroup'] += 1
		except:
			pass
	result = load_city(result)
	"""s = str(result.keys())
	print(s)"""
	return result

def count_sex(data):
	result = {'man':0,'girl':0,'groups':0,'nosex':0}
	for i in range(1,len(data['response'])-1):
		try:
			js = data['response'][i]
			if ('user' in js) and (js['user']!=None):
				if ('sex' in js['user']):
					if js['user']['sex']==1:
						result['girl']+=1
					else:
						result['man']+=1
				else:
					result['nosex']+=1

			else:
				result['groups']+=1
		except:
			pass
	return result

def count_os(data):
	result = {'Android':0,'iOS':0,'fullvk':0,'mobilevk':0,'otherapp':0,'wphone':0}
	for i in range(1,len(data['response'])-1):
		try:
			js = data['response'][i]
			if ('post_source' in js):
				if ('platfom' in js['post_source']):
					if js['post_source']['platfom']=='android':
						result['Android']+=1
					elif (js['post_source']['platfom']=='iphone'):
						result['iOS']+=1
					else:
						result['wphone']+=1
				else:
					if 'type' in js['post_source']:
						if js['post_source']['type'] == 'vk':
							result['fullvk']+=1
						elif js['post_source']['type'] == 'mvk':
							result['mobilevk']+=1
						elif js['post_source']['type'] == 'api':
							result['otherapp']+=1
		except:
			print('error!')
	return result

def load_city(data):
	city_ids = []
	nouser = data['nouser']
	if '0' in data:
		nouser += data['0']
	nogroup = data['nogroup']
	for i in data:
		city_ids.append(i)
	city_ids = str(city_ids).replace('[\'','').replace('\']','').replace('\'','')
	req = Request(api_v)
	r = requests.get(req.request_url('database.getCitiesById','city_ids='+city_ids)).json()
	
	result2 = {}
	for i in r['response']:
		result2[i['name']] = data[i['cid']]

	result2['nouser'] = nouser
	result2['nogroup'] = nogroup
	return result2

def count_type(data):
	result = {}
	for i in range(1,len(data['response'])-1):
		result = search_json('type',data['response'][i],result)
	return result
def count_time_pub(data):
	result = {}
	for i in range(0,24):
		result[i] = {"man":0,"girl":0,"groups":0}
	for i in range(1,len(data['response'])-1):
		date = data['response'][i]['date']
		if ('user' in data['response'][i]):
			if (data['response'][i]['user'] != None):
				if (data['response'][i]['user']['sex']==1):
					type_ = 'girl'
				else:
					type_ = 'man'
		elif ('group' in data['response'][i]):
			type_ = 'groups'
		date_pub = int(time.strftime("%H", time.localtime(date)))
		result[date_pub][type_]+=1

	return result