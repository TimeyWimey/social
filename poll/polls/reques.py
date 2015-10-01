import requests
import sys
import random

class Request:
	class Meta:
		pass
	def __init__(self,*pargs):
		self.api_v = pargs 

	def request_url(self,method_name, parameters): #универсальный метод запроса к API
		"""read https://vk.com/dev/api_requests"""
		req_url = 'https://api.vk.com/method/{method_name}?{parameters}&v={api_v}'.format( #строим строку запроса
			method_name=method_name, api_v=self.api_v, parameters=parameters)

		return req_url
