import re
import tkinter as tk
from tkinter import ttk
import tkintermapview
from api.wikidata import parse_wikidata, get_results
from database import sql
from database.data import Station


class ExistingStation:
    """
    The ExistingStation class represents a station with various attributes.

    Attributes:
        station (str): The station identifier.
        station_name (str): The name of the station.
        station_types (list): The types of the station.
        connecting_lines (list): The connecting lines of the station.
        transport_networks (list): The transport networks of the station.
        opening_date (str): The opening date of the station.
        geo_latitude (float): The geographical latitude of the station.
        geo_longitude (float): The geographical longitude of the station.
        description (str): The description of the station.
    """
    station = str
    station_name = str
    station_types = list
    connecting_lines = list
    transport_networks = list
    opening_date = str
    geo_latitude = float
    geo_longitude = float
    description = str

    def __init__(self, station, station_name, opening_date: str, geo_latitude: float, geo_longitude: float, station_type: str = None,
             connecting_line: str = None, transport_network: str = None):
        """
        The constructor for ExistingStation class.

        Args:
            station (str): The station identifier.
            station_name (str): The name of the station.
            opening_date (str): The opening date of the station.
            geo_latitude (float): The geographical latitude of the station.
            geo_longitude (float): The geographical longitude of the station.
            station_type (str, optional): The type of the station. Defaults to None.
            connecting_line (str, optional): The connecting line of the station. Defaults to None.
            transport_network (str, optional): The transport network of the station. Defaults to None.
        """
        self.station = station
        self.station_name = station_name
        self.opening_date = opening_date
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

    def __repr__(self):
        """
        This method is used to provide a string representation of the ExistingStation object.
        It returns a formatted string that includes all the attributes of the ExistingStation object.

        Returns:
            str: A string representation of the ExistingStation object.
        """
        return f"ExistingStation({self.station}, {self.station_name}, {str(self.opening_date)},{self.geo_latitude}, {self.geo_longitude}, {self.station_types}, {self.connecting_lines}, {self.transport_networks}, {self.description})"

    def add_attribute(self, station_type: str = None, connecting_line: str = None, transport_network: str = None):
        """
        This method is used to add attributes to the ExistingStation object.
        It checks if the station_type, connecting_line, and transport_network are not None and not already in their respective lists.
        If they are not, it adds them to their respective lists.
        After adding the attributes, it calls the __update_description method to update the description of the ExistingStation object.

        Args:
            station_type (str, optional): The type of the station. Defaults to None.
            connecting_line (str, optional): The connecting line of the station. Defaults to None.
            transport_network (str, optional): The transport network of the station. Defaults to None.
        """
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
        """
        This private method is used to update the description of the ExistingStation object.
        It first checks if there are any station types, connecting lines, and transport networks.
        If there are, it strips the brackets from their string representations and adds them to the description.
        The description is a formatted string that includes the station name, station types, connecting lines, transport networks, and the opening date.
        If the opening date is not available, it adds "Missing date" to the description.

        Note:
            This method is called internally whenever an attribute is added to the ExistingStation object.
        """
        stripped_types, stripped_lines, stripped_networks = "", "", ""
        if len(self.station_types) > 0:
            stripped_types = f",{str(self.station_types).strip('[]')}"

        if len(self.connecting_lines) > 0:
            stripped_lines = f", {str(self.connecting_lines).strip('[]')}"
        if len(self.connecting_lines) > 0:
            stripped_networks = f", {str(self.transport_networks).strip('[]')}"

        self.description = f"{self.station_name} {stripped_types}{stripped_lines}{stripped_networks}{str(self.opening_date) if self.opening_date is not None else 'Missing date'}"


def filter_stations(stations, search):
    """
    This function is used to filter stations based on search criteria.
    It first checks if the search list is empty, if so, it returns all stations.
    If the search list is not empty, it converts each search term to lowercase and iterates over them.
    For each search term, it iterates over all stations and checks if the search term matches any attribute of the station.
    If a match is found, the station is added to the list of filtered stations.

    Args:
        stations (list): A list of Station objects.
        search (list): A list of search criteria.

    Returns:
        list: A list of filtered Station objects.
    """
    if len(search) == 0:
        return stations
    filtered_stations = []
    filters = [x.lower() for x in search]
    for filter in filters:
        for station in stations:
            print(f"station: {station.transport_network.lower() if station.transport_network is not None else 'None'}, filter: {filter}")
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
    """
    This function is used to combine stations with the same name.
    It first converts each station to a dictionary and checks if a station with the same name already exists in the list of existing stations.
    If a station with the same name exists, it adds the attributes of the current station to the existing station.
    If a station with the same name does not exist, it creates a new ExistingStation object and adds it to the list of existing stations.

    Args:
        stations (list): A list of Station objects.

    Returns:
        list: A list of ExistingStation objects with unique station names.
    """
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
                ExistingStation(station["station"], station["name"], station["opening_date"],station["geo_latitude"], station["geo_longitude"],
                                station["type"], station["connecting_line"], station["transport_network"]))
    return existing_stations


def update_database(refresh_markers: bool = False):
    """
    This function is used to update the database with new data from wikidata.
    It first fetches the results from wikidata, parses the results, and then clears the existing stations in the database.
    After that, it iterates over the parsed data and tries to create a new record for each data in the database.
    If the refresh_markers argument is set to True, it will also refresh the markers on the map based on the search entry.

    Args:
        refresh_markers (bool, optional): A flag to determine whether to refresh the markers on the map. Defaults to False.

    Global:
        search_entry: A global variable representing the search entry.
    """
    wikidata = get_results()
    parsed = parse_wikidata(wikidata)
    sql.clear_station()
    for data in parsed:
        print(data)
        try:
            sql.create_record(data)
        except Exception:
            pass
    if refresh_markers:
        fill_coordinates(search_entry.get().split(","))


def fill_coordinates(search=None):
    """
    This function is used to load all stations from the database and display them on the map.
    It first fetches all stations from the database, filters them based on the search criteria,
    and then parses the stations to combine stations with the same name.
    After that, it checks the existing markers on the map and removes any that do not correspond to a station.
    Finally, it adds markers for all stations that do not already have a marker on the map.

    Args:
        search (list, optional): A list of search criteria. If no search criteria are provided, all stations are loaded. Defaults to None.

    Global:
        map_widget: A global variable representing the map widget.
    """
    if search is None:
        search = []
    global map_widget
    # map_widget.delete_all_marker()
    stations = sql.select_all(Station)
    stations = filter_stations(stations, search)
    stations = parse_stations(stations)

    # Check existing markers on the map
    existing_markers = set(map_widget.canvas_marker_list)
    for marker in existing_markers:
        # If the marker's position does not correspond to a station, remove the marker
        if marker.position not in [(station.geo_latitude, station.geo_longitude) for station in stations]:
            map_widget.delete(marker)
    # Add a marker for each station that does not already have a marker
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

update_button = tk.Button(root, text="Update database (may take a while.)", command=lambda: update_database(refresh_markers=True))
update_button.pack()

if __name__ == "__main__":
    root.mainloop()
else:
    pass
