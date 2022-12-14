from django.shortcuts import render
import sqlite3
import folium
# Create your views here.

db_name = '/home/trogers/demo_CVRP_dashboard/demands.sqlite3'
# db_name = 'demands.sqlite3'


def logs_index_view(request):
    context = {'segment': 'logs'}
    print("Request:", request, request.method, request.POST.get('spec'))

    if request.method == "POST" and request.POST.get('spec') == 'deauthorize_path':
        id = request.POST.get('dataid')
        print("Deauthorizing path:", id)

        deauthorize_path(id)
        reset_logged_ids()

    context['paths'] = get_logged_paths()

    if len(context['paths']) == 0:
        context['paths_empty'] = True
    else:
        context['paths_empty'] = False

    return render(request, 'logs_index.html', context)


def logged_path_info_view(request, id=id):
    context = {'segment': 'logs'}

    context['total_distance'] = round(get_total_distance(id)*0.000621371, 2)
    context['total_duration'] = round(get_total_duration(id)/3600, 2)
    context['total_load'] = get_total_load(id)
    context['date'] = get_date(id)

    context['id'] = id

    context['num_paths'] = get_num_paths()

    context['locations'] = get_locations(id)

    m = folium.Map([40, -98], tiles='CartoDB positron',
                   zoom_start=4, scroll_wheel_zoom=False)
    # prev_stop = None
    count = 0
    for location in context['locations']:
        address = location['address']
        if count == 0:
            html = folium.Html(("Depot" + " - " + address), script=True)
        else:
            html = folium.Html(
                ("Load Delivered: " + str(location['load']) + " ft" + "\u00b3" + " - " + address), script=True)
        popup = folium.Popup(html, max_width=2650)
        folium.CircleMarker(location=[location['latitude'], location['longitude']],
                            popup=popup, fill_color='blue', radius=5).add_to(m)
        # if prev_stop:
        #     folium.PolyLine([(prev_stop[0], prev_stop[1]), (delivery['latitude'], delivery['longitude'])],
        #                     color='blue', weight=2, opacity=1).add_to(m)
        # prev_stop = (delivery['latitude'], delivery['longitude'])
        count += 1
    m = m._repr_html_()
    context['map'] = m

    return render(request, 'logged_path_info.html', context)


def get_logged_paths():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT logged_path_id, date, time, total_load FROM logged_paths")
    paths = cur.fetchall()

    logged_paths = []
    for path in paths:
        formatted_path = {
            'id': path[0], 'date': path[1], 'time': path[2], 'load': path[3]}
        logged_paths.append(formatted_path)
    conn.close()
    return logged_paths


def get_total_distance(id):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT total_distance FROM logged_paths WHERE logged_path_id = ?", (id,))
    total_distance = cur.fetchall()[0][0]
    conn.close()
    return total_distance


def get_total_duration(id):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT total_duration FROM logged_paths WHERE logged_path_id = ?", (id,))
    total_duration = cur.fetchall()[0][0]
    conn.close()
    return total_duration


def get_total_load(id):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT total_load FROM logged_paths WHERE logged_path_id = ?", (id,))
    total_load = cur.fetchall()[0][0]
    conn.close()
    return total_load


def get_date(id):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT date FROM logged_paths WHERE logged_path_id = ?", (id,))
    date = cur.fetchall()[0][0]
    conn.close()
    return date


def get_locations(id):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT address, load, latitude, longitude FROM logged_deliveries WHERE logged_path_id = ?", (id,))
    locations_data = cur.fetchall()

    locations = []
    for location in locations_data:
        l = {'address': location[0], 'load': location[1], 'latitude': location[2],
             'longitude': location[3]}
        locations.append(l)
    conn.close()
    return locations


def get_num_paths():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM logged_paths")
    num_paths = c.fetchall()[0][0]

    conn.close()
    return num_paths


def deauthorize_path(id):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        "SELECT logged_delivery_id, address, load, longitude, latitude FROM logged_deliveries WHERE logged_path_id = ?", (id,))

    deliveries = cur.fetchall()

    for delivery in deliveries:

        cur.execute(
            "SELECT load FROM demands WHERE address = ?", (delivery[1],))
        check_load = cur.fetchall()

        if check_load:
            cur.execute("UPDATE demands SET load = ? WHERE address = ?",
                        (check_load[0][0] + delivery[2], delivery[1]))
        else:
            cur.execute(
                "INSERT INTO demands (address, load, longitude, latitude) VALUES (?, ?, ?, ?)", (delivery[1], delivery[2], delivery[3], delivery[4]))

        cur.execute(
            "DELETE FROM logged_deliveries WHERE logged_delivery_id = ?", (delivery[0],))

    cur.execute("DELETE FROM logged_paths WHERE logged_path_id = ?", (id,))

    conn.commit()
    conn.close()


def reset_logged_ids():

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    count = 1
    cur.execute("SELECT logged_path_id FROM logged_paths")
    logged_path_ids = cur.fetchall()
    for id in logged_path_ids:
        cur.execute(
            "UPDATE logged_deliveries SET logged_path_id = ? WHERE logged_path_id = ?", (count, id[0]))
        cur.execute(
            "UPDATE logged_paths SET logged_path_id = ? WHERE logged_path_id = ?", (count, id[0]))
        count += 1
    conn.commit()
    conn.close()
