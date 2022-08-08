import sqlite3
from sqlite3 import Error

from . import database_setup


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

    database = "demands.sqlite3"
    conn = database_setup.create_connection(database)

    trucks = query_truck_data(conn)
    demands = query_demands_data(conn)

    return trucks, demands
