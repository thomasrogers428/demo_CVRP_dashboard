from django.shortcuts import render
import sqlite3


def trucks_index_view(request):
    context = {"segment": "trucks"}
    print(request)

    if request.method == "POST":
        t = request.POST.get('type')
        print(t, request.POST.get('truck_id'))

        if t == "Add":
            capacity = request.POST.get('capacity')

            print("capacity", capacity)
            add_truck(capacity)

        elif t == "Delete":
            truck_id = request.POST.get('truck_id')

            print("truck_id", truck_id)

            delete_truck(truck_id)
            renumber_trucks()

    context['trucks'] = get_trucks()

    context['num_trucks'] = len(context['trucks'])

    context['total_capacity'] = get_total_capacity(context['trucks'])

    if context['num_trucks'] != 0:
        context['average_capacity'] = round(
            context['total_capacity']/context['num_trucks'], 2)
    else:
        context['average_capacity'] = 0

    return render(request, 'trucks_index.html', context)


def trucks_add_view(request):
    context = {"segment": "trucks"}

    return render(request, 'trucks_add.html', context)


def trucks_delete_view(request):
    context = {"segment": "trucks"}

    context['trucks'] = get_trucks()

    return render(request, 'trucks_delete.html', context)


def get_trucks():
    conn = sqlite3.connect('demands.sqlite3')
    cur = conn.cursor()
    cur.execute("SELECT truck_id, capacity FROM trucks")

    trucks = []
    trucks_info = cur.fetchall()

    for truck in trucks_info:
        trucks.append({"truck_id": truck[0], "capacity": truck[1]})

    return trucks


def get_total_capacity(trucks):
    total_capacity = 0

    for truck in trucks:
        total_capacity += truck['capacity']

    return total_capacity


def add_truck(capacity):
    conn = sqlite3.connect('demands.sqlite3')
    cur = conn.cursor()

    cur.execute("INSERT INTO trucks (capacity) VALUES (?)", (capacity,))

    conn.commit()
    conn.close()


def delete_truck(truck_id):
    conn = sqlite3.connect('demands.sqlite3')
    cur = conn.cursor()

    print("delete truck:", truck_id)

    cur.execute("DELETE FROM trucks WHERE truck_id = ?", (truck_id,))

    conn.commit()
    conn.close()


def renumber_trucks():
    conn = sqlite3.connect('demands.sqlite3')
    cur = conn.cursor()

    cur.execute("SELECT truck_id FROM trucks")

    truck_ids = cur.fetchall()

    rowid = 1
    for truck_id in truck_ids:
        cur.execute(
            "UPDATE trucks SET truck_id = ? WHERE truck_id = ?", (rowid, truck_id[0]))
        rowid += 1

    conn.commit()
    conn.close()
