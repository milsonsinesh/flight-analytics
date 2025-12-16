from etl.airports_etl import run_airport_etl
from etl.flights_etl import run_flights_etl
from etl.aircraft_etl import run_aircraft_etl
from etl.delays_etl import run_delay_etl

def main():
    print("🚀 Running ETL Pipeline...")

    run_airport_etl()
    run_flights_etl()
    run_aircraft_etl()
    run_delay_etl()

    print("🎉 ETL completed successfully!")

if __name__ == "__main__":
    main()
