# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Example route to display available routes
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/temp/<start>/<end>"
    )


# route to get a list of stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations_list = [station[0] for station in results]

    return jsonify(stations_list)


# route to get precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query the precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)


# Route to get temperature observations for the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    # Calculate the date one year from the last date in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query the temperature observations for the most active station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list
    temperature_observations = [temp[0] for temp in results]

    return jsonify(temperature_observations)


# route to get temperature data for a given start date
@app.route("/api/v1.0/temp/<start>")
def temp_start(start):
    # Query to get the minimum, maximum, and average temperatures for the given start date
    results = session.query(
        func.min(Measurement.tobs), 
        func.max(Measurement.tobs), 
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    # Convert the results to a list
    temperature_stats = []
    for min_temp, max_temp, avg_temp in results:
        temperature_stats.append({
            "Minimum Temperature": min_temp,
            "Maximum Temperature": max_temp,
            "Average Temperature": avg_temp
        })

    # Return the results as JSON
    return jsonify(temperature_stats)


# route to get temperature data for a given start and end date
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_start_end(start, end):
    results = session.query(
        func.min(Measurement.tobs), 
        func.max(Measurement.tobs), 
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)