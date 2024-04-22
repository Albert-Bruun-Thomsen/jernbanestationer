import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from database.data import Station
from datetime import datetime


def parse_date(date: str):
    """
    This function takes a date string as input and returns a datetime.date object.
    The input date string should be in the format "%Y-%m-%dT%H:%M:%SZ".

    Args:
        date (str): The date string to be parsed.

    Returns:
        datetime.date: The parsed date.
    """
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()


def get_results():
    """
    This function sends a SPARQL query to the global endpoint URL and returns the results in JSON format.
    The endpoint URL and the query are defined globally.

    Returns:
        dict: The results of the query in JSON format.
    """
    global endpoint_url
    global query
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def parse_wikidata(results):
    """
    This function takes the results from a SPARQL query to Wikidata and parses the data into a list of Station objects.

    Args:
        results (dict): The results of the SPARQL query in JSON format.

    Returns:
        list: A list of Station objects, each representing a station with its associated data.
    """
    station_data = []
    for result in results["results"]["bindings"]:
        data_dict = {
            "station": result["station"]["value"],
            "name": result["stationLabel"]["value"],
            "uic_code": result["stationID"]["value"] if "stationID" in result else None,
            "transport_network": result["transportNetworkLabel"]["value"] if "transportNetworkLabel" in result else None,
            "address": result["address"]["value"] if "address" in result else None,
            "type": result["BaneTypeLabel"]["value"] if "BaneTypeLabel" in result else None,
            "connecting_line": result["connectingLineLabel"]["value"] if "connectingLineLabel" in result else None,
            "opening_date": parse_date(result["openingDate"]["value"]) if "openingDate" in result else None,
            "geo_latitude": float(result["geoLatitude"]["value"]) if "geoLatitude" in result else None,
            "geo_longitude": float(result["geoLongitude"]["value"]) if "geoLongitude" in result else None
        }
        if data_dict["type"] == "S-tog line F":
            data_dict["type"] = "F line"
        if data_dict["type"] == "S-tog Bx":
            data_dict["type"] = "Bx line"
        if data_dict["type"] is not None:
            if data_dict["type"].lower() in ["a", "b", "c", "e", "h", "bx", "f"]:
                data_dict["type"] += " line"

        station_data.append(data_dict)
        data_dict = None
    stations = [Station(**data) for data in station_data]
    return stations


endpoint_url = "https://query.wikidata.org/sparql"

if __name__ == "__main__":
    with open("wikidata.txt") as file:
        query = file.read()
    results = get_results()
    parsed_results = parse_wikidata(results)
    print(parsed_results)
else:
    with open("api/wikidata/wikidata.txt") as file:
        query = file.read()
