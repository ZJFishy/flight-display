import requests
import time
from math import sqrt

BOUNDS = "42.04137759484996,41.86483305485586,-87.94425878608439,-87.54647100967044" # N, S, W, E
HOME_COORDS = (41.97526672499893, -87.65515571991378)

URL_HEAD="https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds="
URL_TAIL="&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1"
FULL_URL=URL_HEAD+BOUNDS+URL_TAIL
DETAILS_URL_HEAD="https://data-live.flightradar24.com/clickhandler/?flight="

HEADERS = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
     "cache-control": "no-store, no-cache, must-revalidate, post-check=0, pre-check=0",
     "accept": "application/json"
}

def get_flights() -> dict:
    try:
        response: dict = requests.get(url=FULL_URL, headers=HEADERS).json()
        return {key: value for key, value in response.items() if key not in ("version", "full_count")}

    except Exception as e:
        print(e)
        return {}

def get_distances(flights: dict) -> dict:
    return {key: sqrt((HOME_COORDS[0] - value[1]) ** 2 + (HOME_COORDS[1] - value[2]) ** 2) for key, value in flights.items()}

def get_closest_flight(flights: dict) -> str:
    distances = get_distances(flights)
    return min(distances, key=distances.get)
    
def get_details(flight_id: str) -> dict:
    try:
        response: dict = requests.get(url=DETAILS_URL_HEAD+flight_id, headers=HEADERS).json()
        return response
    
    except Exception as e:
        print(e)
        return {}
    
def parse_details(detail_dict: dict) -> dict:
    details = {}

    if identification := detail_dict.get("identification"):
        details["callsign"] = identification["callsign"]
    else:
        details["callsign"] = "???xxxx"
    details["aircraft_model"] = detail_dict["aircraft"]["model"]["text"]
    details["aircraft_registration"] = detail_dict["aircraft"]["registration"]
    details["airline"] = detail_dict["airline"]["name"]
    airport = detail_dict.get("airport")
    if airport:
        if origin := airport.get("origin"):
            details["origin_name"] = origin["name"]
            details["origin_code"] = origin["code"]["iata"]
        else:
            details["origin_name"] = "Unknown"
            details["origin_code"] = "---"
        if destination := airport.get("destination"):
            details["destination_name"] = destination["name"]
            details["destination_code"] = destination["code"]["iata"]
        else:
            details["destination_name"] = "Unknown"
            details["destination_code"] = "---"
    else:
        details["origin_name"] = "Unknown"
        details["destination_name"] = "Unknown"
        details["origin_code"] = "---"
        details["destination_code"] = "---"
    details["departure_time"] = detail_dict["time"]["real"]["departure"]
    details["altitude"] = detail_dict["trail"][0]["alt"]
    details["speed"] = detail_dict["trail"][0]["spd"]

    return details

def print_flight_info(summary: dict) -> None:
    SEPARATOR = "- " * 20
    print(SEPARATOR)
    print(summary["callsign"])
    print(summary["airline"])
    print(f"{summary["origin_name"]} ({summary["origin_code"]}) -> {summary["destination_name"]} ({summary["destination_code"]})")
    print(f"{summary["aircraft_model"]} ({summary["aircraft_registration"]})")
    print(f"{summary["speed"]} knots, {summary["altitude"]} feet")
    try:
        secs_elapsed = time.time() - summary["departure_time"]
        hours_elapsed = secs_elapsed // 3600
        secs_elapsed %= 3600
        mins_elapsed = secs_elapsed // 60
        print(f"{str(int(hours_elapsed)).zfill(2)}:{str(int(mins_elapsed)).zfill(2)} elapsed")
    except:
        print("Unknown time elapsed")
    print(SEPARATOR)

def get_flight_info(summary: dict) -> str:
    SEPARATOR = "- " * 20
    try:
        secs_elapsed = time.time() - summary["departure_time"]
        hours_elapsed = secs_elapsed // 3600
        secs_elapsed %= 3600
        mins_elapsed = secs_elapsed // 60
        time_string = f"{str(int(hours_elapsed)).zfill(2)}:{str(int(mins_elapsed)).zfill(2)} elapsed"
    except:
        time_string = "Unknown time elapsed"
    return f"""
{SEPARATOR}
{summary["callsign"]}
{summary["airline"]}
{summary["origin_name"]} ({summary["origin_code"]}) -> {summary["destination_name"]} ({summary["destination_code"]})
{summary["aircraft_model"]} ({summary["aircraft_registration"]})
{summary["speed"]} knots, {summary["altitude"]} feet
{time_string}
{SEPARATOR}
"""

def print_closest_flight_details() -> None:
    flights = get_flights()
    closest_flight = get_closest_flight(flights)
    flight_details = get_details(closest_flight)
    summary = parse_details(flight_details)
    print_flight_info(summary)

def print_n_closest_flight_details(n=1) -> None:
    flights = get_flights()
    sorted_flights = sorted(d := get_distances(flights), key = d.get)
    if len(sorted_flights) > n:
        sorted_flights = sorted_flights[:n]
    for flight in sorted_flights:
        flight_details = get_details(flight)
        summary = parse_details(flight_details)
        print_flight_info(summary)

def print_all_flight_details() -> None:
    flights = get_flights()
    sorted_flights = sorted(d := get_distances(flights), key = d.get)
    for flight in sorted_flights:
        flight_details = get_details(flight)
        summary = parse_details(flight_details)
        print_flight_info(summary)

def get_closest_flight_details() -> None:
    flights = get_flights()
    closest_flight = get_closest_flight(flights)
    flight_details = get_details(closest_flight)
    summary = parse_details(flight_details)
    get_flight_info(summary)

def get_n_closest_flight_details(n=1) -> None:
    flights = get_flights()
    sorted_flights = sorted(d := get_distances(flights), key = d.get)
    if len(sorted_flights) > n:
        sorted_flights = sorted_flights[:n]
    for flight in sorted_flights:
        flight_details = get_details(flight)
        summary = parse_details(flight_details)
        get_flight_info(summary)

def get_all_flight_details() -> None:
    flights = get_flights()
    sorted_flights = sorted(d := get_distances(flights), key = d.get)
    for flight in sorted_flights:
        flight_details = get_details(flight)
        summary = parse_details(flight_details)
        get_flight_info(summary)