#!/usr/bin/python
from bottle import Bottle, static_file, request, response
from caddy.utils import env
import os
import re
import ujson
from sqlalchemy import create_engine
from sqlalchemy.sql import text


dot_env = os.path.join(os.getcwd(), ".env")
if os.path.exists(dot_env):
    from dotenv import load_dotenv
    load_dotenv()
app = application = Bottle()


# Database connection
database_url = env("DATABASE_URL").replace("postgis", "postgresql+psycopg")
DB_ENGINE = create_engine(database_url)

# Regex patterns
LON_LAT_PATTERN = re.compile(r"(?P<lon>-?[0-9]+.[0-9]+),\s*(?P<lat>-?[0-9]+.[0-9]+)")
ALPHANUM_PATTERN = re.compile(r"[^A-Za-z0-9\s]+")


@app.route("/")
def index():
    return static_file("index.html", root="caddy/templates")


@app.route("/favicon.ico")
def favicon():
    return static_file("favicon.ico", root="caddy/static")


@app.route("/livez")
def liveness():
    return "OK"


@app.route("/readyz")
def readiness():
    conn = DB_ENGINE.connect()
    result = conn.execute(text("SELECT 1")).fetchone()

    if result:
        return "OK"


@app.route("/api/<object_id>")
def detail(object_id):
    # Validate `object_id`: this value needs be castable as an integer, even though we use it as a string.
    try:
        int(object_id)
    except ValueError:
        response.status = 400
        return "Bad request"

    response.content_type = "application/json"
    sql = text(f"""SELECT object_id, address_nice, owner, ST_AsText(centroid), ST_AsText(envelope), ST_AsText(boundary), data
               FROM shack_address
               WHERE object_id = :object_id""")
    sql = sql.bindparams(object_id=object_id)
    conn = DB_ENGINE.connect()
    result = conn.execute(sql).fetchone()

    if result:
        return ujson.dumps({
            "object_id": result[0],
            "address": result[1],
            "owner": result[2],
            "centroid": result[3],
            "envelope": result[4],
            "boundary": result[5],
            "data": result[6],
        })
    else:
        return "{}"


@app.route("/api/geocode")
def geocode():
    q = request.query.q or ""
    point = request.query.point or ""
    if not q and not point:
        response.status = 400
        return "Bad request"

    # Point intersection query
    if point:  # Must be in the format lon,lat
        m = LON_LAT_PATTERN.match(point)
        if m:
            lon, lat = m.groups()
            # Validate `lon` and `lat` by casting them to float values.
            try:
                lon, lat = float(lon), float(lat)
            except ValueError:
                return "{}"
            ewkt = f"SRID=4326;POINT({lon} {lat})"
            sql = text("""SELECT object_id, address_nice, owner, ST_AsText(centroid), ST_AsText(envelope), ST_AsText(boundary), data
                       FROM shack_address
                       WHERE ST_Intersects(boundary, ST_GeomFromEWKT(:ewkt))""")
            sql = sql.bindparams(ewkt=ewkt)
            conn = DB_ENGINE.connect()
            result = conn.execute(sql).fetchone()
            response.content_type = "application/json"

            # Serialise and return any query result.
            if result:
                return ujson.dumps({
                    "object_id": result[0],
                    "address": result[1],
                    "owner": result[2],
                    "centroid": result[3],
                    "envelope": result[4],
                    "boundary": result[5],
                    "data": result[6],
                })
            else:
                return "{}"
        else:
            response.status = 400
            return "Bad request"

    # Address query
    # Sanitise the input query: remove any non-alphanumeric/whitespace characters.
    q = re.sub(ALPHANUM_PATTERN, "", q)
    words = q.split()  # Split words on whitespace.
    tsquery = "&".join(words)

    # Default to return a maximum of five results, allow override via `limit`.
    if request.query.limit:
        try:
            limit = int(request.query.limit)
        except ValueError:
            response.status = 400
            return "Bad request"
    else:
        limit = 5

    sql = text(f"""SELECT address_nice, owner, ST_X(centroid), ST_Y(centroid), object_id
               FROM shack_address
               WHERE tsv @@ to_tsquery(:tsquery)
               LIMIT :limit""")
    sql = sql.bindparams(tsquery=tsquery, limit=limit)
    conn = DB_ENGINE.connect()
    result = conn.execute(sql).fetchall()
    response.content_type = "application/json"

    # Serialise and return any query results.
    if result:
        j = []
        for i in result:
            j.append({
                "address": i[0],
                "owner": i[1],
                "lon": i[2],
                "lat": i[3],
                "pin": i[4],
            })
        return ujson.dumps(j)
    else:
        return "[]"


if __name__ == "__main__":
    from bottle import run
    run(application, host="0.0.0.0", port=env("PORT", 8080))
