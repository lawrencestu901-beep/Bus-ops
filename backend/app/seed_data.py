"""
Real stop / route / bus / promo data, extracted directly from the
existing frontends (lusaka-bus-ai-app.jsx and the operator dashboard)
so the backend seeds with the same network the UIs already expect.
"""

STOPS = [
    {"key": "town_centre", "name": 'Town Centre Market', "x": 22, "y": 62, "aliases": ['town centre', 'town center', 'cbd', 'market']},
    {"key": "kulima_tower", "name": 'Kulima Tower', "x": 40, "y": 48, "aliases": ['kulima', 'kulima tower']},
    {"key": "city_market", "name": 'City Market', "x": 18, "y": 52, "aliases": ['city market']},
    {"key": "kamwala", "name": 'Kamwala', "x": 24, "y": 58, "aliases": ['kamwala']},
    {"key": "lumumba", "name": 'Lumumba', "x": 30, "y": 60, "aliases": ['lumumba']},
    {"key": "kabwata", "name": 'Kabwata', "x": 34, "y": 78, "aliases": ['kabwata']},
    {"key": "chilenje", "name": 'Chilenje', "x": 36, "y": 70, "aliases": ['chilenje']},
    {"key": "kanyama", "name": 'Kanyama', "x": 8, "y": 42, "aliases": ['kanyama']},
    {"key": "chunga", "name": 'Chunga', "x": 6, "y": 55, "aliases": ['chunga']},
    {"key": "garden", "name": 'Garden Compound', "x": 10, "y": 65, "aliases": ['garden', 'garden compound']},
    {"key": "chawama", "name": 'Chawama', "x": 18, "y": 80, "aliases": ['chawama']},
    {"key": "libala", "name": 'Libala', "x": 22, "y": 86, "aliases": ['libala']},
    {"key": "matero", "name": 'Matero', "x": 15, "y": 30, "aliases": ['matero']},
    {"key": "mandevu", "name": 'Mandevu', "x": 30, "y": 12, "aliases": ['mandevu']},
    {"key": "ngombe", "name": "Ng'ombe", "x": 48, "y": 10, "aliases": ['ngombe', "ng'ombe"]},
    {"key": "mtendere", "name": 'Mtendere', "x": 58, "y": 65, "aliases": ['mtendere']},
    {"key": "kalingalinga", "name": 'Kalingalinga', "x": 50, "y": 52, "aliases": ['kalingalinga']},
    {"key": "unza", "name": 'UNZA', "x": 62, "y": 28, "aliases": ['unza', 'university']},
    {"key": "roma", "name": 'Roma', "x": 55, "y": 18, "aliases": ['roma']},
    {"key": "avondale", "name": 'Avondale', "x": 45, "y": 14, "aliases": ['avondale']},
    {"key": "northmead", "name": 'Northmead', "x": 42, "y": 22, "aliases": ['northmead']},
    {"key": "woodlands", "name": 'Woodlands', "x": 60, "y": 38, "aliases": ['woodlands']},
    {"key": "kabulonga", "name": 'Kabulonga', "x": 55, "y": 26, "aliases": ['kabulonga']},
    {"key": "olympia", "name": 'Olympia', "x": 70, "y": 14, "aliases": ['olympia']},
    {"key": "ibex_hill", "name": 'Ibex Hill', "x": 74, "y": 28, "aliases": ['ibex hill', 'ibex']},
    {"key": "meanwood", "name": 'Meanwood', "x": 66, "y": 42, "aliases": ['meanwood']},
    {"key": "chelstone", "name": 'Chelstone', "x": 82, "y": 20, "aliases": ['chelstone']},
    {"key": "kaunda_square", "name": 'Kaunda Square', "x": 86, "y": 34, "aliases": ['kaunda square', 'kaunda']},
    {"key": "chalala", "name": 'Chalala', "x": 88, "y": 52, "aliases": ['chalala']},
    {"key": "bauleni", "name": 'Bauleni', "x": 80, "y": 58, "aliases": ['bauleni']},
]

ROUTES = [
    {"route_no": "125", "via": 'Great East Road', "stops": ['town_centre', 'kulima_tower', 'chelstone'], "fare": 15, "mins": 35, "traffic": "Low"},
    {"route_no": "102", "via": 'Great East Road', "stops": ['town_centre', 'kabulonga', 'unza'], "fare": 14, "mins": 30, "traffic": "Moderate"},
    {"route_no": "117", "via": 'Chilenje', "stops": ['kulima_tower', 'chilenje', 'kanyama'], "fare": 10, "mins": 42, "traffic": "Moderate"},
    {"route_no": "103", "via": 'Kamwala', "stops": ['kanyama', 'kamwala', 'town_centre'], "fare": 10, "mins": 25, "traffic": "Low"},
    {"route_no": "140", "via": 'Lumumba Road', "stops": ['town_centre', 'lumumba', 'kabwata'], "fare": 8, "mins": 18, "traffic": "Low"},
    {"route_no": "110", "via": 'Freedom Way', "stops": ['town_centre', 'city_market'], "fare": 5, "mins": 8, "traffic": "Low"},
    {"route_no": "118", "via": 'Garden Road', "stops": ['city_market', 'chunga', 'garden'], "fare": 9, "mins": 20, "traffic": "Moderate"},
    {"route_no": "130", "via": 'Mumbwa Road', "stops": ['town_centre', 'matero', 'mandevu'], "fare": 12, "mins": 28, "traffic": "Heavy"},
    {"route_no": "145", "via": 'Zambia-Malawi Road', "stops": ['town_centre', 'northmead', 'ngombe'], "fare": 10, "mins": 22, "traffic": "Moderate"},
    {"route_no": "150", "via": 'Kafue Road', "stops": ['town_centre', 'chawama', 'libala'], "fare": 9, "mins": 24, "traffic": "Heavy"},
    {"route_no": "160", "via": 'Alick Nkhata Road', "stops": ['kulima_tower', 'kalingalinga', 'mtendere'], "fare": 11, "mins": 26, "traffic": "Moderate"},
    {"route_no": "170", "via": 'Great East Road', "stops": ['town_centre', 'roma', 'avondale', 'northmead'], "fare": 13, "mins": 30, "traffic": "Low"},
    {"route_no": "180", "via": 'Great East Road', "stops": ['kulima_tower', 'woodlands', 'kabulonga', 'ibex_hill'], "fare": 15, "mins": 33, "traffic": "Low"},
    {"route_no": "190", "via": 'Great East Road Ext.', "stops": ['chelstone', 'olympia'], "fare": 8, "mins": 15, "traffic": "Low"},
    {"route_no": "200", "via": 'Great East Road', "stops": ['town_centre', 'kulima_tower', 'kaunda_square'], "fare": 14, "mins": 32, "traffic": "Moderate"},
    {"route_no": "210", "via": 'Chalala Road', "stops": ['kaunda_square', 'chalala'], "fare": 6, "mins": 12, "traffic": "Low"},
    {"route_no": "220", "via": 'Kafue Road', "stops": ['town_centre', 'chalala', 'bauleni'], "fare": 16, "mins": 38, "traffic": "Heavy"},
    {"route_no": "230", "via": 'Chindo Road', "stops": ['kulima_tower', 'meanwood', 'woodlands'], "fare": 12, "mins": 26, "traffic": "Moderate"},
    {"route_no": "240", "via": 'Mumbwa Road', "stops": ['matero', 'mandevu', 'chunga'], "fare": 7, "mins": 18, "traffic": "Low"},
]

# driver name -> bus assignment, from the operator dashboard's LIVE_BUSES
BUS_DRIVERS = {
    "125": 'M. Banda',
    "102": 'C. Mwale',
    "117": 'P. Zulu',
    "130": 'R. Phiri',
}

# bus fleet, from the passenger app's NEARBY_BUSES + operator dashboard's LIVE_BUSES
BUSES = [
    {"bus_no": "125", "seats_total": 45, "seats_available": 23, "color": "#16a34a", "status": "On Route"},
    {"bus_no": "102", "seats_total": 45, "seats_available": 18, "color": "#f97316", "status": "On Route"},
    {"bus_no": "117", "seats_total": 45, "seats_available": 15, "color": "#16a34a", "status": "On Route"},
    {"bus_no": "130", "seats_total": 45, "seats_available": 45, "color": "#dc2626", "status": "Delayed"},
]

PROMO_CODES = [
    {"code": "LUSAKA10", "percent": 10, "label": '10% off your trip'},
    {"code": "WELCOME20", "percent": 20, "label": '20% off — welcome offer'},
]
