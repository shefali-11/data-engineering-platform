# Safe recovery helper for clickhouse-medallion-warehouse.
# Run from the project folder. It does not delete volumes or modify ClickHouse data.
$ErrorActionPreference = 'Continue'

Write-Host "=== ClickHouse Medallion Warehouse: Airflow recovery ===" -ForegroundColor Cyan
Write-Host "Project: $((Get-Location).Path)"

if (-not (Test-Path '.\docker-compose.yaml')) {
    Write-Host "ERROR: docker-compose.yaml not found. Open CMD/PowerShell in clickhouse-medallion-warehouse first." -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/5] Current service status" -ForegroundColor Yellow
docker compose ps

Write-Host "`n[2/5] Recreate only Airflow services (no volume deletion)" -ForegroundColor Yellow
docker compose up -d --force-recreate airflow airflow-scheduler airflow-dag-processor
if ($LASTEXITCODE -ne 0) {
    Write-Host "Airflow services did not recreate successfully. Recent Airflow logs:" -ForegroundColor Red
    docker compose logs --tail 80 airflow airflow-scheduler airflow-dag-processor
    exit 2
}

Write-Host "`n[3/5] Wait for Airflow API health (up to 60 seconds)" -ForegroundColor Yellow
$healthy = $false
for ($i = 1; $i -le 12; $i++) {
    try {
        $r = Invoke-WebRequest -Uri 'http://localhost:8082/api/v2/monitor/health' -TimeoutSec 4 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $healthy = $true; Write-Host $r.Content; break }
    } catch { }
    Start-Sleep -Seconds 5
}
if (-not $healthy) {
    Write-Host "Airflow API did not become healthy. Recent logs follow; no data was deleted." -ForegroundColor Red
    docker compose logs --tail 120 airflow airflow-scheduler airflow-dag-processor
    exit 3
}

Write-Host "`n[4/5] Check DAG is visible" -ForegroundColor Yellow
docker exec medallion-airflow airflow dags list | findstr /i "customer_medallion_pipeline"
if ($LASTEXITCODE -ne 0) {
    Write-Host "DAG not found in Airflow. Recent DAG processor logs:" -ForegroundColor Red
    docker compose logs --tail 100 airflow-dag-processor
    exit 4
}

Write-Host "`n[5/5] Trigger the pipeline and show recent task status" -ForegroundColor Yellow
docker exec medallion-airflow airflow dags trigger customer_medallion_pipeline
Start-Sleep -Seconds 12
docker exec medallion-airflow airflow tasks states-for-dag-run customer_medallion_pipeline --help 2>$null | Out-Null
Write-Host "`nRecent scheduler errors (if any):" -ForegroundColor Yellow
docker compose logs --since 3m airflow-scheduler 2>&1 | Select-String -Pattern 'ConnectError|Connection refused|Traceback|ERROR|Workload execution failed' | Select-Object -Last 30
Write-Host "`nRecovery attempt finished. This script did not delete volumes or touch ClickHouse data." -ForegroundColor Green
Write-Host "If the execution API error remains, the logs above identify the remaining failure; this environment cannot execute the script on your laptop automatically."
