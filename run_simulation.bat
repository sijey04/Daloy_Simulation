@echo off
echo ================================================================
echo         SMART TRAFFIC CONTROL SYSTEM - ZAMBOANGA KCC
echo                     200 HOUR SIMULATION
echo ================================================================
echo.
echo Starting comprehensive traffic simulation...
echo This will collect the following metrics:
echo   - Vehicle Delay and Travel Time
echo   - Queue Length at both intersections  
echo   - Emissions (CO2, NOx, PMx)
echo   - Overall traffic statistics
echo.
echo Simulation will run for 200 hours (720,000 steps)
echo Progress will be reported every hour.
echo.
echo Press Ctrl+C to stop the simulation at any time.
echo ================================================================
echo.

python traffic_controller.py

echo.
echo ================================================================
echo SIMULATION COMPLETE!
echo ================================================================
echo.
echo To analyze the results, install analysis dependencies:
echo   pip install -r requirements.txt
echo.
echo Then run the analysis:
echo   python traffic_analyzer.py
echo.
echo Generated files:
echo   - traffic_metrics.csv (detailed metrics)
echo   - vehicle_details.csv (individual vehicle data)
echo   - intersection_summary.csv (hourly summaries)
echo ================================================================
pause
