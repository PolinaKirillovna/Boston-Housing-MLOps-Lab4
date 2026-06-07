#!/usr/bin/env sh
# Initialise the MS SQL database from init-db.sql.
#
# The database-setup commands live here, in a dedicated script, instead of
# being inlined in docker-compose.yml. The script also waits until SQL Server
# is ready to accept logins before applying the schema, which makes startup
# robust against the database container being "healthy" (port open) a moment
# before it can actually authenticate.
set -eu

SQLCMD="/opt/mssql-tools18/bin/sqlcmd"
SERVER="mssql,1433"
INIT_FILE="/init/init-db.sql"
MAX_RETRIES=30

echo "Waiting for SQL Server to accept connections..."
i=1
while [ "$i" -le "$MAX_RETRIES" ]; do
    if "$SQLCMD" -S "$SERVER" -U "$MSSQL_USER" -P "$MSSQL_PASSWORD" -C -Q "SELECT 1" >/dev/null 2>&1; then
        echo "SQL Server is ready."
        break
    fi
    echo "  attempt ${i}/${MAX_RETRIES}: not ready yet, retrying in 2s..."
    i=$((i + 1))
    sleep 2
done

if [ "$i" -gt "$MAX_RETRIES" ]; then
    echo "ERROR: SQL Server did not become ready in time." >&2
    exit 1
fi

echo "Applying ${INIT_FILE}..."
"$SQLCMD" -S "$SERVER" -U "$MSSQL_USER" -P "$MSSQL_PASSWORD" -C -i "$INIT_FILE"
echo "Database initialisation complete."
