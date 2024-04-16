import sqlite3
import re
import time

from sqlalchemy import Date

from api.wikidata import parse_wikidata, get_results
from database import sql
import tkinter as tk
from tkinter import ttk
import tkintermapview
from database import *
from database.data import Station
from database.sql import select_all


class ExistingStation:
    station = str
    station_name = str
    station_types = list
    connecting_lines = list
    transport_networks = list
    geo_latitude = float
    geo_longitude = float
    description = str

    def __init__(self, station, station_name, geo_latitude: float, geo_longitude: float, station_type: str = None,
                 connecting_line: str = None, transport_network: str = None):
        self.station = station
        self.station_name = station_name
        self.geo_latitude = geo_latitude
        self.geo_longitude = geo_longitude
        self.station_types = []
        self.connecting_lines = []
        self.transport_networks = []
        if station_type is not None:
            self.station_types.append(station_type)
        if connecting_line is not None:
            self.connecting_lines.append(connecting_line)
        if transport_network is not None:
            self.transport_networks.append(transport_network)
        self.__update_description()

    def get_name(self):
        return f"{self.station_name}"

    def __repr__(self):
        return f"ExistingStation({self.station}, {self.station_name}, {self.geo_latitude}, {self.geo_longitude}, {self.station_types}, {self.connecting_lines}, {self.transport_networks}, {self.description})"

    def add_attribute(self, station_type: str = None, connecting_line: str = None, transport_network: str = None):
        if station_type is not None:
            if station_type not in self.station_types:
                self.station_types.append(station_type)
        if connecting_line is not None:
            if connecting_line not in self.connecting_lines:
                self.connecting_lines.append(connecting_line)
        if transport_network is not None:
            if transport_network not in self.transport_networks:
                self.transport_networks.append(transport_network)
        self.__update_description()

    def __update_description(self):
        stripped_types = ""
        stripped_lines = ""
        stripped_networks = ""
        if len(self.station_types) > 0:
            stripped_types = f",{str(self.station_types).strip("[]")}"

        if len(self.connecting_lines) > 0:
            stripped_lines = f", {str(self.connecting_lines).strip("[]")}"
        if len(self.connecting_lines) > 0:
            stripped_networks = f", {str(self.transport_networks).strip("[]")}"

        self.description = f"{self.station_name} {stripped_types}{stripped_lines}{stripped_networks}"


def filter_stations(stations, search):
    if len(search) == 0:
        return stations
    filtered_stations = []
    filters = [x.lower() for x in search]
    for filter in filters:
        for station in stations:
            print(f"station: {station.transport_network.lower() if station.transport_network is not None else "None"}, filter: {filter}")
            if re.search(filter, station.name.lower()):
                filtered_stations.append(station)
            elif station.type is not None and re.search(filter, station.type.lower()):
                    filtered_stations.append(station)

            elif station.connecting_line is not None and re.search(filter, station.connecting_line.lower()):
                    filtered_stations.append(station)

            elif station.transport_network is not None and re.search(filter, station.transport_network.lower()):
                    filtered_stations.append(station)
            elif station.opening_date is not None and re.search(filter, str(station.opening_date)):
                filtered_stations.append(station)
    return filtered_stations


def parse_stations(stations):
    existing_stations = []
    for station in stations:
        new_station = True
        station = station.convert_to_dict()
        for existing_station in existing_stations:
            if existing_station.station_name == station["name"]:
                existing_station.add_attribute(station["type"], station["connecting_line"],
                                               station["transport_network"])
                new_station = False
                continue
        if new_station:
            existing_stations.append(
                ExistingStation(station["station"], station["name"], station["geo_latitude"], station["geo_longitude"],
                                station["type"], station["connecting_line"], station["transport_network"]))
    return existing_stations


def line_check(values):
    if values["type"] is None:
        return ""
    return f", {values["type"]}"


def update_database():
    wikidata = get_results()
    parsed = parse_wikidata(wikidata)
    sql.clear_station()
    for data in parsed:
        print(data)
        try:
            sql.create_record(data)
        except Exception:
            pass


def fill_coordinates(filter=None):
    if filter is None:
        filter = []
    global map_widget
    # map_widget.delete_all_marker()
    stations = sql.select_all(Station)
    stations = filter_stations(stations, filter)
    stations = parse_stations(stations)

    existing_markers = set(map_widget.canvas_marker_list)
    for marker in existing_markers:
        if marker.position not in [(station.geo_latitude, station.geo_longitude) for station in stations]:
            map_widget.delete(marker)
    for station in stations:
        if (station.geo_latitude, station.geo_longitude) not in [marker.position for marker in existing_markers]:
            map_widget.set_marker(station.geo_latitude, station.geo_longitude, station.description)


root = tk.Tk()
root.geometry("900x800")

my_label = tk.LabelFrame(root)
my_label.pack(pady=20)

map_widget = tkintermapview.TkinterMapView(my_label, width=800, height=600, corner_radius=0)
map_widget.set_position(55.668308, 12.384060)
fill_coordinates()
map_widget.set_zoom(8)
map_widget.pack()

search_label = tk.Label(root, text="Search for station, type, line or network. Separated by comma(c line,aarhus)")
search_label.pack()
search_entry = ttk.Entry(root)
search_entry.pack()

submit_button = tk.Button(root, text="Search", command=lambda: fill_coordinates(search_entry.get().split(",")))
submit_button.pack()

if __name__ == "__main__":
    # root.mainloop()
    update_database()
else:
    pass
