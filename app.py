#################################################
# Import Dependencies
#################################################
import numpy as np
import pandas as pd
# import datetime as dt
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#  Import Flask
from flask import Flask, jsonify

# Create a connection to DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define what to do when a user hits the index route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Starter!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br>"
		f"/api/v1.0<start>/<end><br>"
    )


# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using `date` as the key and `tobs` as the value"""
    """Return the JSON representation of dictionary"""
    AllDates_qry = session.query(Measurement.date).distinct().order_by(Measurement.date).all()

    date_tobs = []
    for prcp_data in AllDates_qry: 
        prep_dict = {}
        tobs_query = session.query(Measurement.tobs).filter(Measurement.date == prcp_data.date).all()
        prep_dict[prcp_data.date]= tobs_query
        date_tobs.append(prep_dict)
    
    return jsonify(date_tobs)


# Define what to do when a user hits the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset
    station_qry = session.query(Station.station).all()
    
    return jsonify(station_qry)


# Define what to do when a user hits the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperature():
    # Query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    # Capture the year beginning and end date from the available data to run query for last year

	st_dt = dt.date(2017, 8, 23) - dt.timedelta(days=365)
	TempObs_qry = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= st_dt).all()
	return jsonify(TempObs_qry)

# Define what to do when a user hits the /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def start_mma_temp(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

    min_qry = session.query(func.min(Measurement.tobs)).filter(Measurement.date == start).all()
    max_qry = session.query(func.max(Measurement.tobs)).filter(Measurement.date == start).all()
    avg_qry = session.query(func.avg(Measurement.tobs)).filter(Measurement.date == start).all()
    min_max_avg = "Minimum:"+str(min_qry)+" Maximum:"+str(max_qry)+" Average:"+str(avg_qry)

    return jsonify(min_max_avg)



@app.route("/api/v1.0/<start>/<end>")
def startend_mma_temp(start, end):
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    min_qry = session.query(func.min(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()
    max_qry = session.query(func.max(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()
    avg_qry = session.query(func.avg(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()
    
    min_max_avg = "Minimum:"+str(min_qry)+" Maximum:"+str(max_qry)+" Average:"+str(avg_qry)
    
    return jsonify(min_max_avg)


if __name__ == "__main__":
    app.run(debug=True)
