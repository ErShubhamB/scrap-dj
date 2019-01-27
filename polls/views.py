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
import json
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
		return JsonResponse({'status':'200','session':request.session['user']})
	else:
		return JsonResponse({'status':'500'})
def data_fetch(request):
	url = request.GET.get('url', None)
	#print(url)
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
		#print(part_url)
		r = requests.get(turl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
		html = r.content
		parsed_html = BeautifulSoup(html, 'lxml')
		hotel = parsed_html.find_all('div', {'class': 'sr_item'})
		#tm.sleep(5)
		#print(len(hotel));
		for ho in hotel:
			#print(ho)
			room_array = []
			name = ho.find('span', {'class': 'sr-hotel__name'})
			price = ho.find('strong', {'class': 'availprice'})
			hurl = ho.find('a', {'class': 'hotel_name_link'})['href']
			rating = ho.find('div', {'class': 'bui-review-score__badge'})
			#print(price)
			sub_r = requests.get('https://booking.com'+hurl.replace('\n',''),headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
			sub_html = sub_r.content
			#tm.sleep(5)
			parsed_sub_html = BeautifulSoup(sub_html,'lxml')
			sub_hotels = parsed_sub_html.find('select',{'class':'hprt-nos-select'})
			address = parsed_sub_html.find('span',{'class':'hp_address_subtitle'})
			address = address.text
			sub_rooms = parsed_sub_html.find_all('tr',{'class':'hprt-table-last-row'})
			for rooms in sub_rooms:
				room_type = rooms.find('span',{'class':'hprt-roomtype-icon-link'})
				capacity = rooms.find('span',{'class':'invisible_spoken'})
				occupancy = rooms.find('select',{'class':'hprt-nos-select'})
				imp_text = rooms.find('span',{'class':'important_text'})
				room_obj ={}
				if(room_type):
					rt = room_type.text
				else:
					rt = 'XXX'
				if(capacity):
					cap = capacity.text
				else:
					cap='XXX'
				if(imp_text):
					cop = imp_text.text
					availcheck = 'false'
				else:
					availcheck = 'true'
					if(occupancy):
						cop = occupancy('option')[-1]
						if(cop):
							cop = cop.text
							cop = cop.replace('\n','')
							cop = cop.split('(',1)[0]
							cop = cop.replace(' ','')
							cop = int(cop)
							cop = cop * 10
							cop = str(cop)+'%'
					room_price = rooms.find('span',{'class':'hprt-price-price-rackrate'})
					room_sale_price = rooms.find('span',{'class':'hprt-price-price-actual'})
					wholesale_price = rooms.find('div',{'class':'wholesalers_table__price__number'})
					# print("room price =>"+room_price)
					# print("sale price=>"+room_sale_price)
					# print("normal price=>"+wholesale_price)
					if(room_sale_price and room_price):
						room_pr = room_sale_price.text.replace('\n','')+"( "+room_price.text.replace('\n','')+" )"
					elif(room_price):
						room_pr = room_price.text
					elif(room_sale_price):
						room_pr = room_sale_price.text
					elif(wholesale_price):
						room_pr = wholesale_price.text
					else:
						room_pr = '売り切れ'
				room_obj['room_type'] = rt.replace('\n','')
				room_obj['capacity'] = cap.replace('\n','')
				room_obj['occupancy'] = cop
				room_obj['pricing'] = room_pr
				room_obj['is_available'] = availcheck
				room_array.append(room_obj)
							
			if(rating):
				rating = rating.text
			else:
				rating = parsed_sub_html.find('span',{'class':'bui-review-score__badge'})
				if(rating):
					rating = rating.text
				else:
					rating = "N/A"
			if(price):
				pr = price.text
			else:
				pr = ''
			data = {}
			data['check_in_date'] = dt_from_year+'-'+dt_from_month+'-'+dt_from_day
			data['check_out_date'] = dt_to_year+'-'+dt_to_month+'-'+dt_to_day
			data['name'] = name.text.replace('\n','')
			data['price'] = pr.replace('\n','')
			data['URL'] = 'http://booking.com'+hurl.replace('\n','')
			#rt = rate.replace('\n','')
			#rt = rt.replace(' ','')
			data['rating'] = rating
			data['occupancy'] = '100%'
			data['address'] = address.replace('\n','')
			data['room_data'] =room_array
			hotels.append(data)
			#tm.sleep(5)
	#writer = FileWriter(hotels, out_format='JSON', country='JAPAN')
	#file = writer.output_file()
	return JsonResponse(hotels, safe=False)
def hotel(request):
	return render(request,'core/hotel.html')
def hotel_scrap(request):
	url_list = json.loads(request.POST.get('url', None))
	checkin = request.POST.get('checkin', None)
	checkout = request.POST.get('checkout', None)
	checkin = checkin.split('-',2)
	checkout = checkout.split('-',2)
	d1 = date(int(checkin[0]), int(checkin[1]), int(checkin[2]))  # start date
	d2 = date(int(checkout[0]), int(checkout[1]), int(checkout[2]))  # start date
	#d2 = date(2019, 1, 20)  # end date
	delta = d2 - d1
	# print(url_list)
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
		for url in url_list:
			#print(url)
			room_array = []
			part_url = url.split('checkin',1)
			part_1_url = part_url[0]
			part_2_url = part_url[1].split('dest_id',1)
			part_2_url = part_2_url[1]
			final_url = part_1_url+'checkin='+dt_from_year+'-'+dt_from_month+'-'+dt_from_day+';checkout='+dt_to_year+'-'+dt_to_month+'-'+dt_to_day+';dest_id'+part_2_url
			# print(final_url)
			hotel_html = requests.get(final_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
			hotel_data = hotel_html.content
			parsed_sub_html = BeautifulSoup(hotel_data,'lxml')
			hotel_name = parsed_sub_html.find('h2',{'class':'hp__hotel-name'})
			hotel_address = parsed_sub_html.find('span',{'class':'hp_address_subtitle'})
			hotel_rating = parsed_sub_html.find('span',{'class':'bui-review-score__badge'})
			if(hotel_rating):
				hotel_rating = hotel_rating.text.replace('\n','')
			else:
				hotel_rating='N/A'
			sub_rooms = parsed_sub_html.find_all('tr',{'class':'hprt-table-last-row'})
			for rooms in sub_rooms:
				room_type = rooms.find('span',{'class':'hprt-roomtype-icon-link'})
				capacity = rooms.find('span',{'class':'invisible_spoken'})
				occupancy = rooms.find('select',{'class':'hprt-nos-select'})
				imp_text = rooms.find('span',{'class':'important_text'})
				room_obj ={}
				if(room_type):
					rt = room_type.text
				else:
					rt = 'XXX'
				if(capacity):
					cap = capacity.text
				else:
					cap='XXX'
				if(imp_text):
					cop = imp_text.text
					availcheck = 'false'
				else:
					availcheck = 'true'
					if(occupancy):
						cop = occupancy('option')[-1]
						if(cop):
							cop = cop.text
							cop = cop.replace('\n','')
							cop = cop.split('(',1)[0]
							cop = cop.replace(' ','')
							cop = int(cop)
							cop = cop * 10
							cop = str(cop)+'%'
					room_price = rooms.find('span',{'class':'hprt-price-price-rackrate'})
					room_sale_price = rooms.find('span',{'class':'hprt-price-price-actual'})
					wholesale_price = rooms.find('div',{'class':'wholesalers_table__price__number'})
					# print("room price =>"+room_price)
					# print("sale price=>"+room_sale_price)
					# print("normal price=>"+wholesale_price)
					if(room_sale_price and room_price):
						room_pr = room_sale_price.text.replace('\n','')+"( "+room_price.text.replace('\n','')+" )"
					elif(room_price):
						room_pr = room_price.text
					elif(room_sale_price):
						room_pr = room_sale_price.text
					elif(wholesale_price):
						room_pr = wholesale_price.text
					else:
						room_pr = '売り切れ'
				room_obj['room_type'] = rt.replace('\n','')
				room_obj['capacity'] = cap.replace('\n','')
				room_obj['occupancy'] = cop
				room_obj['pricing'] = room_pr
				room_obj['is_available'] = availcheck
				room_array.append(room_obj)
			hotel_obj ={}
			hotel_obj['hotel_name'] = hotel_name.text
			hotel_obj['hotel_address'] = hotel_address.text
			hotel_obj['room_data'] = room_array
			hotel_obj['rating'] = hotel_rating
			hotel_obj['check_in_date'] = dt_from_year+'-'+dt_from_month+'-'+dt_from_day
			hotel_obj['check_out_date'] = dt_to_year+'-'+dt_to_month+'-'+dt_to_day
			hotels.append(hotel_obj)
	return JsonResponse(hotels, safe=False)
def logout(request):
	del request.session['user']
	return redirect('/login')