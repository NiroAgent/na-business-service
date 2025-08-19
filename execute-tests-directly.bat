@echo off
echo ========================================
echo DIRECT PLAYWRIGHT TEST EXECUTION
echo ========================================
echo.

REM Test vf-dashboard-service
echo Testing vf-dashboard-service...
cd /d E:\Projects\VisualForgeMediaV2\vf-dashboard-service\mfe
if exist node_modules (
    npx playwright test --reporter=list
) else (
    echo Installing dependencies first...
    call npm install
    npx playwright install
    npx playwright test --reporter=list
)

REM Test vf-audio-service  
echo.
echo Testing vf-audio-service...
cd /d E:\Projects\VisualForgeMediaV2\vf-audio-service\mfe
if exist node_modules (
    npx playwright test --reporter=list
) else (
    echo Installing dependencies first...
    call npm install
    npx playwright install
    npx playwright test --reporter=list
)

REM Test ns-shell
echo.
echo Testing ns-shell...
cd /d E:\Projects\NiroSubs-V2\ns-shell
if exist node_modules (
    npx playwright test --reporter=list
) else (
    echo Installing dependencies first...
    call npm install
    npx playwright install
    npx playwright test --reporter=list
)

echo.
echo ========================================
echo TEST EXECUTION COMPLETE
echo Check results above for failures
echo ========================================
pause