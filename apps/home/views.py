# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
import sqlite3
import folium


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    context['total_demand'] = get_total_demand()

    context['total_capacity'] = get_total_capacity()

    context['shippable'] = min(
        context['total_demand'], context['total_capacity'])

    if context['total_demand'] != 0:
        context['percent_aval'] = round(((context['shippable'] /
                                          context['total_demand']) * 100), 2)
    else:
        context['percent_aval'] = 0

    context['delivery_locations'] = get_delivery_locations()

    m = folium.Map([40, -98], tiles='cartodbpositron',
                   zoom_start=4, scroll_wheel_zoom=False)
    count = 0
    for delivery in context['delivery_locations']:
        address = delivery['address']
        if count == 0:
            html = folium.Html(("Depot" + " - " + address), script=True)
        else:
            html = folium.Html(
                address, script=True)
        popup = folium.Popup(html, max_width=2650)
        print(delivery['longitude'], delivery['latitude'])
        folium.CircleMarker(location=[delivery['latitude'], delivery['longitude']],
                            popup=popup, fill_color='blue', radius=5).add_to(m)
        count += 1
    m = m._repr_html_()
    context['map'] = m

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def get_total_demand():
    conn = sqlite3.connect('demands.sqlite3')
    c = conn.cursor()
    c.execute("SELECT load FROM demands")
    demands = c.fetchall()

    total_demand = 0
    for demand in demands:
        total_demand += demand[0]

    conn.close()
    return total_demand


def get_total_capacity():
    conn = sqlite3.connect('demands.sqlite3')
    c = conn.cursor()
    c.execute("SELECT capacity FROM trucks")
    capacities = c.fetchall()

    total_capacity = 0
    for capacity in capacities:
        total_capacity += capacity[0]

    conn.close()
    return total_capacity


def get_delivery_locations():

    conn = sqlite3.connect('demands.sqlite3')
    cur = conn.cursor()
    cur.execute(
        "SELECT address, longitude, latitude FROM demands")
    delivery_details = cur.fetchall()

    all_deliveries = []

    for details in delivery_details:
        address = details[0]
        longitude = details[1]
        latitude = details[2]

        all_deliveries.append(
            {'address': address, 'longitude': longitude, 'latitude': latitude})

    conn.close()
    return all_deliveries
