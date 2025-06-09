import re

from quart import Blueprint, abort, g, jsonify, render_template, request, send_from_directory

bp = Blueprint("geocoder", __name__)

# Regex patterns
LON_LAT_PATTERN = re.compile(r"(?P<lon>-?[0-9]+.[0-9]+),\s*(?P<lat>-?[0-9]+.[0-9]+)")
ALPHANUM_PATTERN = re.compile(r"[^A-Za-z0-9\s]+")


@bp.get("/")
async def index():
    return await render_template("index.html")


@bp.get("/api/<int:object_id>")
async def detail(object_id):
    record = await g.connection.fetch_one(
        """SELECT object_id, address_nice, owner, ST_AsText(centroid), ST_AsText(envelope), ST_AsText(boundary), data
        FROM shack_address
        WHERE object_id = :object_id""",
        {"object_id": str(object_id)},
    )

    if record:
        return jsonify(
            {
                "object_id": record[0],
                "address": record[1],
                "owner": record[2],
                "centroid": record[3],
                "envelope": record[4],
                "boundary": record[5],
                "data": record[6],
            }
        )
    else:
        return jsonify({})


@bp.get("/api/geocode")
async def geocode():
    """This route will accept a query parameter (`q` or `point`), and query for matching land parcels.
    `point` must be a string that parses as <float>,<float> and will be used to query for intersection with the `boundary`
    spatial column.
    `q` will be parsed as free text (non-alphanumeric characters will be ignored) and will be used to perform a text search
    against the `tsv` column.
    Query results will be returned as serialised JSON objects.
    An optional `limit` parameter may be passed in to limit the maximum number of results returned, otherwise the route
    defaults to a maximum of five results (no sorting is carried out, so these are simply the first five results from the
    query.
    """
    q = request.args.get("q", "", type=str)
    point = request.args.get("point", "", type=str)
    if not q and not point:
        abort(400, "Invalid request parameters")

    # Point intersection query
    if point:  # Must be in the format lon,lat
        m = LON_LAT_PATTERN.match(point)
        if m:
            lon, lat = m.groups()
            # Validate `lon` and `lat` by casting them to float values.
            try:
                lon, lat = float(lon), float(lat)
            except ValueError:
                abort(400, "Invalid coordinate")

            ewkt = f"SRID=4326;POINT({lon} {lat})"
            record = await g.connection.fetch_one(
                """SELECT object_id, address_nice, owner, ST_AsText(centroid), ST_AsText(envelope), ST_AsText(boundary), data
                FROM shack_address
                WHERE ST_Intersects(boundary, ST_GeomFromEWKT(:ewkt))""",
                {"ewkt": ewkt},
            )
            # Serialise and return any query result.
            if record:
                return jsonify(
                    {
                        "object_id": record[0],
                        "address": record[1],
                        "owner": record[2],
                        "centroid": record[3],
                        "envelope": record[4],
                        "boundary": record[5],
                        "data": record[6],
                    }
                )
            else:
                return jsonify({})
        else:
            abort(400, "Invalid coordinate")

    # Address query
    # Sanitise the input query: remove any non-alphanumeric/whitespace characters.
    q = re.sub(ALPHANUM_PATTERN, "", q)
    words = q.split()  # Split words on whitespace.
    tsquery = "&".join(words)

    # Default to return a maximum of five results, allow override via `limit`.
    if "limit" in request.args:
        limit = request.args.get("limit", type=int)
    else:
        limit = 5

    records = await g.connection.fetch_all(
        """SELECT object_id, address_nice, owner, ST_X(centroid), ST_Y(centroid)
        FROM shack_address
        WHERE tsv @@ to_tsquery(:tsquery)
        LIMIT :limit""",
        {"tsquery": tsquery, "limit": limit},
    )

    # Serialise and return any query results.
    return jsonify(
        [
            {
                "object_id": record[0],
                "address": record[1],
                "owner": record[2],
                "lon": record[3],
                "lat": record[4],
            }
            for record in records
        ]
    )


@bp.get("/livez")
async def liveness():
    return "OK"


@bp.get("/readyz")
async def readiness():
    # Returns a HTTP 500 error if database connection unavailable.
    await g.connection.fetch_val("SELECT 1")
    return "OK"


@bp.get("/favicon.ico")
async def favicon():
    return await send_from_directory("static", "favicon.ico")
