@echo off
echo.
echo ========================================
echo   Raspberry Pi Day Planner - Pi Simulation
echo ========================================
echo.
echo This simulates exactly how your Pi will behave!
echo.
echo Controls:
echo - SPACE: Simulate task notification
echo - Mouse: Click DONE/SKIP buttons  
echo - ESC: Exit simulation
echo.
echo Press any key to start the simulation...
pause >nul

python pi_simulation.py

echo.
echo Simulation completed. Press any key to exit...
pause >nul 