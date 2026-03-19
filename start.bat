@echo off
echo Starting Video Encoder Base Container...
docker-compose up --build -d
echo.
echo ==============================================================
echo The server should now be running in the background!
echo You can access the Web UI at: http://localhost:5000
echo.
echo Note: drop your video files into the "input" folder.
echo The encoded videos will appear in the "output" folder.
echo ==============================================================
echo.
pause