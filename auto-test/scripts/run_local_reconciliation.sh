#!/usr/bin/env bash
set -euo pipefail

business_date=""
log_file="${BATCH_LOG_FILE:-target/batch-logs/reconciliation.log}"

while (($# > 0)); do
    case "$1" in
        --date)
            business_date="${2:-}"
            shift 2
            ;;
        *)
            printf 'Unknown argument: %s\n' "$1" >&2
            exit 64
            ;;
    esac
done

mkdir -p "$(dirname "$log_file")"
: >"$log_file"

log() {
    printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$*" | tee -a "$log_file"
}

log "RECONCILIATION STARTED date=${business_date}"

if [[ "$business_date" == "FAIL" ]]; then
    log "ERROR simulated reconciliation failure"
    log "RECONCILIATION FAILED date=${business_date}"
    exit 2
fi

if [[ ! "$business_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    log "ERROR invalid business date: ${business_date}"
    log "RECONCILIATION FAILED date=${business_date}"
    exit 64
fi

if [[ "${DB_KIND:-}" != "h2" ]]; then
    log "ERROR local fixture only supports DB_KIND=h2"
    log "RECONCILIATION FAILED date=${business_date}"
    exit 3
fi

sql="UPDATE transactions SET status = 'RECONCILED' WHERE status = 'PENDING';
INSERT INTO reconciliation_summary(run_date, reconciled_count, status)
SELECT '${business_date}', COUNT(*), 'COMPLETED'
FROM transactions
WHERE status = 'RECONCILED';"

java \
    -cp "${JDBC_DRIVER_JAR:?JDBC_DRIVER_JAR is required}" \
    org.h2.tools.Shell \
    -url "${JDBC_URL:?JDBC_URL is required}" \
    -user "${JDBC_USER:-sa}" \
    -password "${JDBC_PASSWORD:-}" \
    -sql "$sql" >>"$log_file" 2>&1

log "RECONCILIATION COMPLETED date=${business_date}"
