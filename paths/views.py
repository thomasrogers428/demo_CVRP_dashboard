from django.shortcuts import render, get_object_or_404
import sqlite3
import folium
from . import CVRP_TD
from datetime import date, datetime

db_name = '/home/trogers/demo_CVRP_dashboard/demands.sqlite3'
# db_name = 'demands.sqlite3'


def path_index(request):
    print("Request:", request, request.method, "Auth:", request.POST.get('auth_spec'),
          "Calc:", request.POST.get('calc_spec'), "reset:", request.POST.get('reset_spec'))
    context = {'segment': 'paths'}

    context['total_shipped'] = get_total_shipped()
    context['total_capacity'] = get_total_capacity()
    context['percent_capacity'] = round(
        context['total_shipped']/context['total_capacity']*100, 2)

    context['loaded'] = False

    if request.method == "POST" and request.POST.get('calc_spec') == 'calculate_path':
        CVRP_TD.solve()
        context['loaded'] = True

    if request.method == "POST" and request.POST.get('reset_spec') == 'path_reset':
        path_reset()

    context['paths'] = handle_paths()

    print("Context:", context)

    context['drops'], context['dropped_load_total'] = handle_dropped_loads()

    if request.method == "POST" and request.POST.get('auth_spec') == 'authorize_path':
        log_path(context['paths'])
        clear_demands(context['paths'])
        context['paths'] = []

    if len(context['paths']) == 0:
        context['paths_empty'] = True
    else:
        context['paths_empty'] = False

    if len(context['drops']) == 0:
        context['drops_empty'] = True
    else:
        context['drops_empty'] = False

    return render(request, 'paths_index.html', context)


def truck_info_view(request, id=id):
    context = {'segment': 'paths'}

    print("id", id)
    deliveries, distance, duration, load = handle_truck_info(id)
    context['deliveries'] = deliveries
    context['paths'] = handle_paths()
    context['num_trucks'] = len(context['paths'])
    context['total_distance'] = round(distance*0.000621371, 2)
    context['total_duration'] = round(duration/3600, 2)
    context['total_load'] = load

    # context['id'] = context['paths'][id]['count']
    context['id'] = id
    for path in context['paths']:
        if path['truck_id'] == id:
            context['truck_num'] = path['count']
            break

    m = folium.Map([40, -98], tiles='CartoDB positron',
                   zoom_start=4, scroll_wheel_zoom=False)
    prev_stop = None
    count = 0
    for delivery in context['deliveries']:
        address = delivery['address']
        if count == 0:
            html = folium.Html(("Depot" + " - " + address), script=True)
        else:
            html = folium.Html(
                ("Stop : " + str(count) + " - " + address), script=True)
        popup = folium.Popup(html, max_width=2650)
        folium.CircleMarker(location=[delivery['latitude'], delivery['longitude']],
                            popup=popup, fill_color='blue', radius=5).add_to(m)
        if prev_stop:
            folium.PolyLine([(prev_stop[0], prev_stop[1]), (delivery['latitude'], delivery['longitude'])],
                            color='blue', weight=2, opacity=1).add_to(m)
        prev_stop = (delivery['latitude'], delivery['longitude'])
        count += 1
    m = m._repr_html_()
    context['map'] = m

    return render(request, 'truck_info.html', context)


def load_paths():

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT processed_demand_id, truck_id, order_number FROM assignments")
    assignments = cur.fetchall()

    truck_paths = {}

    for assignment in assignments:
        processed_demand_id = assignment[0]
        truck_id = assignment[1]
        order_number = assignment[2]

        # c.execute("SELECT * FROM processed_demands WHERE id = ?", (processed_demand_id,))

        if truck_id not in truck_paths:
            truck_paths[truck_id] = [(processed_demand_id, order_number)]
        else:
            truck_paths[truck_id].append((processed_demand_id, order_number))

    for truck_id in truck_paths:
        path = truck_paths[truck_id]

        truck_paths[truck_id] = sorted(path, key=lambda x: x[1])

    conn.close()
    return truck_paths


def handle_paths():
    truck_paths = load_paths()

    path_info = []
    count = 1
    for truck_id in truck_paths:
        deliveries = truck_paths[truck_id]

        total_load = 0
        total_stops = 0

        for delivery in deliveries:

            processed_demand_id = delivery[0]

            conn = sqlite3.connect(db_name)
            cur = conn.cursor()

            cur.execute("SELECT load FROM processed_demands WHERE processed_demand_id = ?",
                        (processed_demand_id,))

            demand = cur.fetchall()[0]

            total_load += demand[0]

            total_stops += 1

        if total_stops != 1:
            path_info.append(
                {"truck_id": truck_id, "count": count, "total_load": total_load, "total_stops": total_stops-1})
            count += 1

    return path_info


def handle_truck_info(id):

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT processed_demand_id, distance, duration FROM assignments WHERE truck_id = ?", (id,))
    delivery_ids = cur.fetchall()

    all_deliveries = []
    count = 1

    total_distance = 0
    total_duration = 0
    total_load = 0

    print("delivery_ids", delivery_ids)

    for delivery_id in delivery_ids:
        processed_demand_id = delivery_id[0]
        id_distance = delivery_id[1]
        id_duration = delivery_id[2]

        cur.execute("SELECT address, load FROM processed_demands WHERE processed_demand_id = ?",
                    (processed_demand_id,))

        deliveries = cur.fetchall()

        for delivery in deliveries:
            print(delivery, count)

            address, load = delivery[0], delivery[1]

            print(address)

            cur.execute(
                "SELECT longitude, latitude FROM demands WHERE address = ?", (address,))

            location = cur.fetchall()[0]

            print("location", location)
            longitude = location[0]
            latitude = location[1]

            all_deliveries.append(
                {"id": count, "address": address, "load": load, 'longitude': longitude, 'latitude': latitude})

            total_load += load

        count += 1
        total_distance += id_distance
        total_duration += id_duration

    conn.close()
    print("output", all_deliveries)
    return all_deliveries, total_distance, total_duration, total_load


def get_total_shipped():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT processed_demand_id FROM assignments")
    ids = c.fetchall()

    total_shipment = 0
    for id in ids:
        c.execute(
            "SELECT load FROM processed_demands WHERE processed_demand_id = ?", (id[0],))
        load = c.fetchall()[0][0]
        total_shipment += load

    conn.close()
    return total_shipment


def get_total_capacity():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT capacity FROM trucks")
    capacities = c.fetchall()

    total_capacity = 0
    for capacity in capacities:
        total_capacity += capacity[0]

    conn.close()
    return total_capacity


def get_num_trucks():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM trucks")
    num_trucks = c.fetchall()[0][0]

    conn.close()
    return num_trucks


def handle_dropped_loads():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT processed_demand_id FROM dropped")

    ids = c.fetchall()

    print("Ids", ids)

    drops = []
    dropped_load_total = 0

    for id in ids:
        id = id[0]
        c.execute(
            "SELECT address, load FROM processed_demands WHERE processed_demand_id = ?", (id,))

        dropped = c.fetchall()
        drops.append(
            {'id': id, 'address': dropped[0][0], 'load': dropped[0][1]})

        dropped_load_total += (dropped[0][1])

    return drops, dropped_load_total


def log_path(paths):
    # Part 1: Add paths to the log db
    today = date.today().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M:%S")
    total_load = total_duration = total_distance = 0
    for path in paths:
        total_load += path['total_load']

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("SELECT distance, duration FROM assignments")

    assignments = cur.fetchall()

    for assignment in assignments:
        total_distance += assignment[0]
        total_duration += assignment[1]

    print("Ex1:", today, time, total_load, total_distance, total_duration)
    cur.execute(
        "INSERT INTO logged_paths (date, time, total_load, total_distance, total_duration) VALUES (?, ?, ?, ?, ?)", (today, time, total_load, total_distance, total_duration))

    path_id = cur.lastrowid

    for path in paths:
        print(path)

        truck_id = path['truck_id']

        cur.execute(
            "SELECT processed_demand_id FROM assignments WHERE truck_id = ?", (truck_id,))
        ids = cur.fetchall()

        for id in ids:
            print(id)
            cur.execute(
                "SELECT address, load FROM processed_demands WHERE processed_demand_id = ?", (id[0],))
            delivery = cur.fetchall()[0]
            address = delivery[0]
            load = delivery[1]

            cur.execute(
                "SELECT longitude, latitude FROM demands WHERE address = ?", (address,))

            location = cur.fetchall()[0]
            longitude = location[0]
            latitude = location[1]

            cur.execute(
                "SELECT load FROM logged_deliveries WHERE address= ? AND logged_path_id= ?", (address, path_id))

            print("EX2:", path_id, address, load)
            check_load = cur.fetchall()

            if check_load:
                new_load = check_load[0][0] + load
                cur.execute(
                    "UPDATE logged_deliveries SET load= ? WHERE address= ? AND logged_path_id= ?", (new_load, address, path_id))
            else:
                cur.execute("INSERT INTO logged_deliveries (logged_path_id, address, load, longitude, latitude) VALUES (?, ?, ?, ?, ?)",
                            (path_id, address, load, longitude, latitude))

    conn.commit()
    conn.close()


def clear_demands(paths):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    for path in paths:
        truck_id = path['truck_id']

        cur.execute(
            "SELECT processed_demand_id FROM assignments WHERE truck_id = ?", (truck_id,))
        processed_ids = cur.fetchall()

        for processed_id in processed_ids:

            if processed_id == 1:
                continue

            processed_id = processed_id[0]

            cur.execute(
                "SELECT demand_id FROM processed_demands WHERE processed_demand_id = ?", (processed_id,))

            demand_id = cur.fetchall()

            demand_id = demand_id[0][0]

            cur.execute(
                "SELECT load FROM demands WHERE demand_id = ?", (demand_id,))

            full_load = cur.fetchall()

            full_load = full_load[0][0]

            cur.execute(
                "SELECT load FROM processed_demands WHERE processed_demand_id = ?", (processed_id,))

            delivered_load = cur.fetchall()[0][0]

            remaining_load = full_load - delivered_load

            cur.execute("UPDATE demands SET load = ? WHERE demand_id = ?",
                        (remaining_load, demand_id,))

            # cur.execute(
            #     "DELETE FROM processed_demands WHERE processed_demand_id = ?", (id[0],))

    cur.execute("DELETE FROM demands WHERE load = 0 AND NOT demand_id = 1")

    cur.execute("DELETE FROM processed_demands")
    cur.execute("Delete FROM assignments")
    cur.execute("Delete FROM dropped")

    cur.execute("SELECT demand_id FROM demands")

    demand_ids = cur.fetchall()

    count = 1
    for demand_id in demand_ids:
        demand_id = demand_id[0]
        cur.execute(
            "UPDATE demands SET demand_id = ? WHERE demand_id = ?", (count, demand_id))
        count += 1

    conn.commit()
    conn.close()

    return paths


def path_reset():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("DELETE FROM assignments")
    cur.execute("DELETE FROM processed_demands")
    cur.execute("DELETE FROM dropped")

    conn.commit()
    conn.close()
