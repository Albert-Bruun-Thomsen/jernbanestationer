from api.wikidata import parse_wikidata, get_results
from database import sql


def update_database():
    wikidata = get_results()
    parsed = parse_wikidata(wikidata)
    sql.clear_station()
    for data in parsed:
        print(data)
        sql.create_record(data)


update_database()
# sql.clear_station()