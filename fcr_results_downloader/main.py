# main.py

from fcr_results.fcr_results import main, schedule_daily_run

if __name__ == "__main__":
    # Sofortige Ausführung beim Start
    df = main()
    
    # Starten des Schedulers
    schedule_daily_run()
