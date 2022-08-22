# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
import sqlite3


db_name = '/home/trogers/demo_CVRP_dashboard/demands.sqlite3'
# db_name = 'demands.sqlite3'


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                print("Database_populated")
                populate_sample_database()
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def populate_sample_database():
    sql_trucks_table = """ CREATE TABLE IF NOT EXISTS trucks (
                                        truck_id integer PRIMARY KEY,
                                        capacity integer NOT NULL
                                    ); """

    sql_demands_table = """ CREATE TABLE IF NOT EXISTS demands (
                                        demand_id integer PRIMARY KEY,
                                        address text NOT NULL,
                                        load integer NOT NULL,
                                        longitude real NOT NULL,
                                        latitude real NOT NULL
                                    );"""

    sql_processed_demands_table = """ CREATE TABLE IF NOT EXISTS processed_demands (
                                        processed_demand_id integer PRIMARY KEY,
                                        demand_id integer NOT NULL,
                                        address text NOT NULL,
                                        load integer NOT NULL,
                                        FOREIGN KEY(demand_id) REFERENCES demands(demand_id)
                                    );"""

    sql_assignments_table = """ CREATE TABLE IF NOT EXISTS assignments (
                                        assignment_id integer PRIMARY KEY,
                                        processed_demand_id integer NOT NULL,
                                        truck_id integer NOT NULL,
                                        order_number integer NOT NULL,
                                        distance real NOT NULL,
                                        duration real NOT NULL,
                                        FOREIGN KEY(processed_demand_id) REFERENCES processed_demands(processed_demand_id),
                                        FOREIGN KEY(truck_id) REFERENCES trucks(truck_id)
                                    );"""

    sql_dropped_table = """ CREATE TABLE IF NOT EXISTS dropped (
                                        dropped_id integer PRIMARY KEY,
                                        processed_demand_id integer NOT NULL,
                                        FOREIGN KEY(processed_demand_id) REFERENCES processed_demands(processed_demand_id)
                                    );"""

    sql_logged_paths_table = """ CREATE TABLE IF NOT EXISTS logged_paths (
                                        logged_path_id integer PRIMARY KEY,
                                        date text NOT NULL,
                                        time text NOT NULL,
                                        total_load integer NOT NULL,
                                        total_distance integer NOT NULL,
                                        total_duration integer NOT NULL
                                    );"""

    sql_logged_deliveries_table = """ CREATE TABLE IF NOT EXISTS logged_deliveries (
                                        logged_delivery_id integer PRIMARY KEY,
                                        logged_path_id integer NOT NULL,
                                        addresss text NOT NULL,
                                        load integer NOT NULL,
                                        longtitude real NOT NULL,
                                        latitude real NOT NULL,
                                        FOREIGN KEY(logged_path_id) REFERENCES logged_paths(logged_path_id)
                                    );"""

    demands = [('2500 Victory Park Lane, Dallas, TX 75219',
                0, -96.8094517, 32.788927),
               #    ('400 W Church St, Orlando, FL 32805',
               #        300, -81.3993081, 28.5401666),
               #    ('1 AT&T Center Parkway, San Antonio, TX 78219',
               #        400, -98.43750706398404, 29.4270504),
               #    ('1 State Farm Dr, Atlanta, GA 30303',
               #        150, -84.39638483503104, 33.7573698),
               #    ('100 Legends Way, Boston, MA 02114',
               #     200, -71.06216222263835, 42.3662986),
               ('620 Atlantic Ave, Brooklyn, NY 11217',
                320, -73.97527899757287, 40.6826108),
               ('333 E Trade St, Charlotte, NC 28202', 970, -80.8387765, 35.2243234),
               ('1901 W Madison St, Chicago, IL 60612',
                250, -87.67418510441388, 41.88068305),
               ('1 Center Court, Cleveland, OH 44115',  # Safe below
                   80, -81.689202, 41.496952),
               ('1000 Chopper Cir, Denver, CO 80204', 220, -
                   105.00754401780362, 39.748683799999995),
               ('2645 Woodward Ave, Detroit, MI 48201',
                   450, -83.05516216701272, 42.34092995),
               #    ('1 Warriors Way, San Francisco, CA 94158',
               #        720, -122.38740721330376, 37.767892700000004),
               #    ('1510 Polk St, Houston, TX 77003', 320, -
               #        95.3622850612245, 29.751951408163265),
               ('125 S Pennsylvania St, Indianapolis, IN 46204',
                   640, -86.15550794973416, 39.7639331),
               ('1111 S Figueroa St, Los Angeles, CA 90015',
                840, -118.2678206, 34.0430445),
               ('191 Beale St, Memphis, TN 38103',
                340, -90.05069457768097, 35.1382401),
               ('601 Biscayne Blvd, Miami, FL 33132',
                670, -80.18794351626137, 25.781359549999998),
               ('1111 Vel R. Phillips Ave, Milwaukee, WI 53203',
                120, -87.9165053, 43.0451196),
               ('600 N 1st Ave, Minneapolis, MN 55403',
                700, -93.29053650019743, 44.96765379417572),
               ('1501 Dave Dixon Dr, New Orleans, LA 70113',
                330, -90.08207454487426, 29.94927515),
               #    ('4 Pennsylvania Plaza, New York, NY 10001',
               #     320, -73.99351594545152, 40.750512900000004),
               ('100 W Reno Ave, Oklahoma City, OK 73102',
                130, -97.51508150130435, 35.46339605),
               ('400 W Church St Suite 200, Orlando, FL 32801',
                510, -81.37858246470589, 28.54345825),
               ('3601 S Broad St, Philadelphia, PA 19148',
                150, -75.173446, 39.905098),
               ('201 E Jefferson St, Phoenix, AZ 85004',
                270, -112.071153, 33.446675),
               ('1 N Center Ct St, Portland, OR 97227', 820, -122.667893, 45.53221),
               ('500 David J Stern Walk, Sacramento, CA 95814',
                320, -121.49230196230158, 38.58295952976191),
               ('301 S Temple, Salt Lake City, UT 84101',
                130, -111.88269862556707, 40.76943),
               ('601 F St NW, Washington, DC 20004', 100, -77.02093893584933, 38.8980801)]

    # 12100 total
    trucks = [(1500,), (1800,), (1400,), (2000,), (1800,), (1800,), (1800,)]

    conn = sqlite3.connect(db_name)

    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS trucks")
    cur.execute("DROP TABLE IF EXISTS demands")
    cur.execute("DROP TABLE IF EXISTS deliveries")
    cur.execute("DROP TABLE IF EXISTS assignments")
    cur.execute("DROP TABLE IF EXISTS processed_demands")
    cur.execute("DROP TABLE IF EXISTS dropped")
    cur.execute("DROP TABLE IF EXISTS logged_paths")
    cur.execute("DROP TABLE IF EXISTS logged_deliveries")

    cur.execute(sql_trucks_table)
    cur.execute(sql_demands_table)
    cur.execute(sql_processed_demands_table)
    cur.execute(sql_assignments_table)
    cur.execute(sql_dropped_table)
    cur.execute(sql_logged_paths_table)
    cur.execute(sql_logged_deliveries_table)

    for truck in trucks:
        cur.execute("INSERT INTO trucks (capacity) VALUES (?)", truck)

    for demand in demands:
        cur.execute(
            "INSERT INTO demands (address, load, longitude, latitude) VALUES (?, ?, ?, ?)", demand)

    conn.commit()
    conn.close()
