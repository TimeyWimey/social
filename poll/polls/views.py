from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import json
import time
#для запроса
import requests
from polls.reques import Request
from polls.settings import api_v

# Create your views here.
#@csrf_exempt
#def home(request):
#	return  TemplateResponse(request, "index.html")
	
def pie(request):
	if request.method == "GET":
		return TemplateResponse(request, "pie.html")
	else:
		return HttpResponseNotFound
@csrf_exempt
def search(request):
	if request.method == "POST":
		response_data = {} #результат 
		searchtext =request.POST["searchtext"]

		searchtext = searchtext.replace('#','')
		
		if len(searchtext)==0:
			return HttpResponseNotFound
		req = Request(api_v)

		r = requests.post(req.request_url('newsfeed.search','q='+searchtext+'&extended=1&count=200&start_time=0&fields=sex,bdate,city,country,can_post,can_see_all_posts,can_see_audio,can_write_private_message')).json()
		#print(req.request_url('newsfeed.search','q='+searchtext+'&extended=1&count=200&start_time=0&fields=sex,bdate,city,country,can_post,can_see_all_posts,can_see_audio,can_write_private_message'))
		
		type_ = count_type(r)
		sex = count_sex(r)
		city = count_city(r)
		date = count_time_pub(r)
		#platfom = count_os(r)

		response_data = {
			'count_type': type_, 
			'count_city': city,
			'count_sex': sex,
			'count_date': date
			#'platfom': platfom
		}
		print(response_data)
		response = HttpResponse(json.dumps(response_data, ensure_ascii=False), content_type="application/json; charset=utf-8")
		response['Access-Control-Allow-Origin'] = '*'
		return response
	else:
		return  HttpResponseRedirect("/")

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
	result = {'nousers':0,'nogroups':0}
	def add_city(i,type_):
		if 'city' in i:
			if i['city']['title'] in result:
				result[i['city']['title']] += 1

			else:
				result[i['city']['title']] = 1
		else:
			if type_=='profiles':
				result['nousers'] += 1
			else:
				result['nogroups'] += 1

	for i in data['response']['profiles']:
		add_city(i,'profiles')
	for i in data['response']['groups']:
		add_city(i,'groups')
	return result

def count_sex(data):
	result = {'man':0,'girl':0,'groups':len(data['response']['groups']),'nosex':0}
	for i in data['response']['profiles']:
		if 'sex' in i:
			if i['sex'] == 1:
				result['girl']+=1
			elif i['sex'] == 2:
				result['man']+=1
			else:
				result['nosex']+=1
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


def count_type(data):
	result = {}
	for i in data['response']['items']:
		if i['post_type'] in result:
			result[i['post_type']] += 1
		else:
			result[i['post_type']] = 1
	return result
def count_time_pub(data):
	result = {}

	def find_sex(id_,data):
		for i in data:
			if i['id'] == id_:
				return i['sex']
		return -1

	for i in range(0,24):
		result[i] = {"man":0,"girl":0,"groups":0}
	for i in data['response']['items']:
		date = i['date']
		type_=''
		if str(i['from_id'])[0]=='-':
			type_ = 'groups'
		else:
			if find_sex(i['from_id'],data['response']['profiles']) == 1:
				type_ = 'girl'
			else:
				type_ = 'man'
		date_pub = int(time.strftime("%H", time.localtime(date)))
		result[date_pub][type_]+=1

	return result