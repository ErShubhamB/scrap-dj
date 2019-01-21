from django.shortcuts import render
import urllib.request as urllib2
from bs4 import BeautifulSoup
import requests
from django.shortcuts import redirect
#from file_writer import FileWriter
from datetime import date, timedelta
import time as tm
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
# Create your views here.
def login(request):
	#template = loader.get_template('core/index.html')
    # return HttpResponse("Hello, world. You're at the dashboard.")
	if 'user' not in request.session:
		return render(request, 'core/login.html')
	else:
		return redirect('/')
def index(request):
	if 'user' not in request.session:
		return redirect('/login')
	else:
		return render(request,'core/index.html')
	return render(request,'core/index.html')
def user_login(request):
	username = request.POST.get('username', None)
	password = request.POST.get('password', None)
	if(username == 'admin' and password == 'password'):
		#s = SessionStore()
		request.session['user'] = '200'
		request.session.set_expiry(5000)
		return JsonResponse({'status':'200','session':request.session['user']})
	else:
		return JsonResponse({'status':'500'})
def data_fetch(request):
	url = request.GET.get('url', None)
	print(url)
	checkin = request.GET.get('checkin', None)
	checkout = request.GET.get('checkout', None) 
	part_url = url.split('&checkin_year',1)[0]
	#part_url = part_url+'&checkin_year=2019&checkin_month=4&checkin_monthday=12&checkout_year=2019&checkout_month=4&checkout_monthday=13'
	checkin = checkin.split('-',2)
	checkout = checkout.split('-',2)
	d1 = date(int(checkin[0]), int(checkin[1]), int(checkin[2]))  # start date
	d2 = date(int(checkout[0]), int(checkout[1]), int(checkout[2]))  # start date
	#d2 = date(2019, 1, 20)  # end date
	delta = d2 - d1
	hotels = []
	for i in range(delta.days):
		dt_from = d1 + timedelta(i)
		dt_to = d1 + timedelta(i+1)
		#[0] => Year [1] => month [2] => day
		split_from = str(dt_from).split('-',2)
		split_to = str(dt_to).split('-',2)
		dt_to_year = split_to[0]
		dt_to_month = split_to[1]
		dt_to_day = split_to[2]

		dt_from_year = split_from[0]
		dt_from_month = split_from[1]
		dt_from_day = split_from[2]
		turl = part_url+'&checkin_year='+dt_from_year+'&checkin_month='+dt_from_month+'&checkin_monthday='+dt_from_day+'&checkout_year='+dt_to_year+'&checkout_month='+dt_to_month+'&checkout_monthday='+dt_to_day+'&no_rooms=1&group_adults=2&group_children=0&sb_travel_purpose=business&b_h4u_keep_filters=&from_sf=1'
		r = requests.get(turl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
		html = r.content
		# print(html)
		parsed_html = BeautifulSoup(html, 'lxml')
		hotel = parsed_html.find_all('div', {'class': 'sr_item'})
		#tm.sleep(5)
		print(len(hotel));
		for ho in hotel:
			#print(ho)
			name = ho.find('span', {'class': 'sr-hotel__name'})
			price = ho.find('strong', {'class': 'availprice'})
			hurl = ho.find('a', {'class': 'hotel_name_link'})['href']
			#rating = ho.find('div', {'class': 'bui-review-score__badge'})
			#print(price)
			sub_r = requests.get('http://booking.com'+hurl.replace('\n',''),headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
			sub_html = sub_r.content
			#tm.sleep(5)
			parsed_sub_html = BeautifulSoup(sub_html,'lxml')
			sub_hotels = parsed_sub_html.find('select',{'class':'hprt-nos-select'})
			address = parsed_sub_html.find('span',{'class':'hp_address_subtitle'})
			address = address.text
			rating = parsed_sub_html.find('span',{'class':'bui-review-score__badge'})
			if(rating):
				rating = rating.text 
			else:
				rating = ''
			if(sub_hotels):
				opt = sub_hotels('option')[-1]
				if(opt):
					#print(opt.text)
					occupancy = opt.text
					occupancy = occupancy.replace('\n','')
					occupancy = occupancy.split('(',1)[0]
					occupancy = occupancy.replace(' ','')
					occupancy = int(occupancy)
					occupancy = occupancy * 10
					occupancy = str(occupancy)+'%'
				else:
					occupancy = 0
			if(price):
				pr = price.text
			else:
				pr = ''
			if(rating):
				rate = rating.text
			else:
				rate = ''
			data = {}
			data['check_in_date'] = dt_from_year+'-'+dt_from_month+'-'+dt_from_day
			data['check_out_date'] = dt_to_year+'-'+dt_to_month+'-'+dt_to_day
			data['name'] = name.text.replace('\n','')
			data['price'] = pr.replace('\n','')
			data['URL'] = 'http://booking.com'+hurl.replace('\n','')
			rt = rate.replace('\n','')
			rt = rt.replace(' ','')
			data['rating'] = rate.replace('\n','')
			data['occupancy'] = occupancy
			data['address'] = address.replace('\n','')
			hotels.append(data)
			#tm.sleep(5)
	#writer = FileWriter(hotels, out_format='JSON', country='JAPAN')
	#file = writer.output_file()
	return JsonResponse(hotels, safe=False)
def logout(request):
	del request.session['user']
	return redirect('/login')