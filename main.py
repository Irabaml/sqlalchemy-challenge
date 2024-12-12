# Import the dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup

app = Flask(__name__)


# Flask Routes


@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Starting from the most recent data point in the database. 
    last_12_months = dt.date(2017,8,23) - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
    precipitation_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_12_months).order_by(Measurement.date).all()
    session.close()
# Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation_query}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()

    session.close()
# Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    last_12_months = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    result = (
    session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= last_12_months).all()
)
    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(result))

    # Return the results
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    try:
        # Handle only start date
        if not end:
            start_date = dt.datetime.strptime(start, "%m%d%Y")
            results = session.query(*sel).filter(Measurement.date >= start_date).all()
            session.close()
            temps = list(np.ravel(results))
            return jsonify(temps)

        # Handle both start and end dates
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        end_date = dt.datetime.strptime(end, "%m%d%Y")
        results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use MMDDYYYY."}), 400

  



if __name__ == '__main__':
    app.run()
