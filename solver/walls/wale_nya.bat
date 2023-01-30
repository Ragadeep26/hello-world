@ECHO OFF
SET WALLS_PATH=C:\ProgXP\Statik\Fides\Walls
echo %WALLS_PATH% > walls.pat

:: Run calculation for the given input in file %1
%WALLS_PATH%\wabbe %1

:: View graphic results
::IF EXIST %1.wpf %WALLS_PATH%\wallsviewer.exe %1.wpf %2
