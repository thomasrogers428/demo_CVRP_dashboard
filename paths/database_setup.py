import sqlite3
from sqlite3 import Error
from geopy.geocoders import Nominatim


def create_connection(db_file):
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, sql_table_statement):
    try:
        c = conn.cursor()
        c.execute(sql_table_statement)

    except Error as e:
        print(e)


def add_truck(conn, truck):
    sql = ''' INSERT INTO trucks(capacity)
              VALUES(?) '''

    cur = conn.cursor()
    cur.execute(sql, truck)
    conn.commit()

    return cur.lastrowid


def add_demand(conn, demand):
    sql = ''' INSERT INTO demands(address, load, longitude, latitude)
              VALUES(?, ?, ?, ?) '''

    cur = conn.cursor()
    cur.execute(sql, demand)
    conn.commit()

    return cur.lastrowid


def add_processed_demand(conn, processed_demand):
    sql = '''INSERT INTO processed_demands(demand_id, address, load)
                VALUES(?,?,?)'''

    cur = conn.cursor()
    cur.execute(sql, processed_demand)
    conn.commit()

    return cur.lastrowid


def add_assignment(conn, assignment):
    sql = ''' INSERT INTO assignments(processed_demand_id, truck_id, order_number, distance, duration)
              VALUES(?, ?, ?, ?, ?) '''

    cur = conn.cursor()
    cur.execute(sql, assignment)
    conn.commit()

    return cur.lastrowid


def add_dropped(conn, assignment):
    sql = ''' INSERT INTO dropped(processed_demand_id)
              VALUES(?) '''

    cur = conn.cursor()
    cur.execute(sql, assignment)
    conn.commit()

    return cur.lastrowid


def main():
    # database = r"C:\sqlite\db\pythonsqlite.sqlite"
    database = "exampledb.sqlite"

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

    demands = [('4925 Oceanside Blvd, Oceanside, CA 92056', 0),
               ('420 S Coast Hwy, Oceanside, CA 92054', 1),
               ('34671 Puerto Pl, Dana Point, CA 92629', 1),
               ('883 Sebastopol Rd, Santa Rosa, CA 95407', 2),
               ('7812 Auburn Blvd, Citrus Heights, CA 95610', 4),
               ('159 Paseo del Sol Ave, Lake Havasu City, AZ 86403', 2),
               ('1601 N Lincoln Ave, Loveland, CO 80538', 4),
               ('4351 S 89th St, Omaha, NE 68127', 32),
               ('11110 N Stemmons Fwy, Dallas, TX 75229', 13),
               ('3959 US-61 White Bear Lake, MN 55110', 1),
               ('32 Weber Rd, Central Square, NY 13036', 1),
               ('5211 Old Post Rd, Charlestown, RI 02813', 27),
               ('1400 S Federal Hwy, Fort Lauderdale, FL 33316', 2),
               ('3 Varney Point Rd, Gilford, NH 03049', 20), ]

    trucks = [(15,), (15,), (15,), (15,), (15,), (15,), (15,)]

    conn = create_connection(database)

    if conn is not None:

        create_table(conn, sql_trucks_table)
        create_table(conn, sql_demands_table)
        create_table(conn, sql_processed_demands_table)
        create_table(conn, sql_assignments_table)
        create_table(conn, sql_dropped_table)

        for truck in trucks:
            add_truck(conn, truck)

        locator = Nominatim(user_agent="myGeocoder")

        for demand in demands:
            address = demand[0]
            print(address)
            location = locator.geocode(address)
            if location == None:
                split = address.split(' ')
                zip = split[len(split) - 1]
                location = locator.geocode(zip)
            longitude, latitude = location.longitude, location.latitude
            print(longitude, latitude)

            located_demand = (address, demand[1], longitude, latitude)

            add_demand(conn, located_demand)

        # cur = conn.cursor()
        # cur.execute("DELETE FROM trucks")
        # cur.execute("DELETE FROM demands")

        # cur.execute("DROP TABLE IF EXISTS trucks")
        # cur.execute("DROP TABLE IF EXISTS demands")
        # cur.execute("DROP TABLE IF EXISTS deliveries")
        # cur.execute("DROP TABLE IF EXISTS assignments")
        # cur.execute("DROP TABLE IF EXISTS processed_demands")
        # cur.execute("DROP TABLE IF EXISTS dropped")

        # print(cur.fetchall())

        conn.commit()
        conn.close()

    else:
        print("Error! cannot create the database connection.")


if __name__ == "__main__":
    main()
