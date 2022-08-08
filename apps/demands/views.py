from django.shortcuts import render
import sqlite3
from . import forms
from geopy.geocoders import Nominatim
from django.template import loader

# Create your views here.
from django.http import HttpResponse


def demand_index(request):
    context = {'segment': 'demands'}

    # context['demands'] = [{"id": 1, "address": "Address 1", "load": 5}, {
    #     "id": 2, "address": "Address 2", "load": 5}, {"id": 3, "address": "Address 3", "load": 10}]

    print(request.method)
    if request.method == "POST":
        t = request.POST.get('type')

        if t == "Add":

            address = request.POST.get('address')
            load = request.POST.get('load')

            locator = Nominatim(user_agent="myGeocoder")
            location = locator.geocode(address)
            if location == None:
                split = address.split(' ')
                zip = split[len(split) - 1]
                location = locator.geocode(zip)
            longitude, latitude = location.longitude, location.latitude

            print(address, load)

            conn = sqlite3.connect('demands.sqlite3')
            c = conn.cursor()
            c.execute("INSERT INTO demands (address, load, longitude, latitude) VALUES (?, ?, ?, ?)",
                      (address, load, longitude, latitude))
            conn.commit()
            conn.close()
        elif t == "Delete":
            address = request.POST.get('address')
            print("Address: ", address)
            conn = sqlite3.connect('demands.sqlite3')
            c = conn.cursor()
            c.execute("DELETE FROM demands WHERE address = ?",
                      (address,))
            conn.commit()
            conn.close()

    else:
        print("failed")

    context['demands'] = process_demands()

    # return render(request, loader.get_template('demands/demands_index.html'), context)

    html_template = loader.get_template('demands/demands_index.html')
    return HttpResponse(html_template.render(context, request))


def add(request):
    context = {}
    # return render(request, loader.get_template('demands/demands_add.html'), context)

    html_template = loader.get_template('demands/demands_add.html')
    return HttpResponse(html_template.render(context, request))


def delete(request):

    conn = sqlite3.connect('demands.sqlite3')
    c = conn.cursor()
    c.execute("SELECT address FROM demands")
    as_fetched = c.fetchall()

    context = {'addresses': []}

    for a_fetched in as_fetched:
        context['addresses'].append({"address": a_fetched[0]})

    context['test'] = "This is a test"

    print(context)
    # return render(request, loader.get_template('demands/demands_delete.html'), context)
    html_template = loader.get_template('demands/demands_delete.html')
    return HttpResponse(html_template.render(context, request))


def get_demands():
    conn = sqlite3.connect('demands.sqlite3')
    c = conn.cursor()
    c.execute("SELECT * FROM demands")
    demands = c.fetchall()

    conn.close()
    return demands


def process_demands():
    demands = get_demands()
    context_demands = []
    for demand in demands:
        context_demands.append({
            "id": demand[0],
            "address": demand[1],
            "load": demand[2]
        })
    return context_demands
