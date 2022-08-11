import sqlite3
from sqlite3 import Error

from . import database_setup

db_name = '/home/trogers/hobie_dashboard/demands.sqlite3'
# db_name = 'demands.sqlite3'


def query_truck_data(conn):

    trucks_query = '''SELECT * FROM trucks'''

    cur = conn.cursor()

    cur.execute(trucks_query)
    trucks = cur.fetchall()

    return trucks


def query_demands_data(conn):

    demands_query = '''SELECT demand_id, address, load, longitude, latitude FROM demands'''

    cur = conn.cursor()

    cur.execute(demands_query)
    demands = cur.fetchall()

    return demands


def query_data():

    database = db_name
    conn = database_setup.create_connection(database)

    trucks = query_truck_data(conn)
    demands = query_demands_data(conn)

    return trucks, demands
