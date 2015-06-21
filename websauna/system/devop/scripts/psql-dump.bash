#!/bin/bash
# Run a database for PostgreSQL database
#
set -e
export PGPASSWORD=$MAIN_SQL_PASSWORD

[[ "$MAIN_SQL_USERNAME" ]] && UARG="-U $MAIN_SQL_USERNAME" || UARG=""
[[ "$MAIN_SQL_HOST" ]] && HARG="-h $MAIN_SQL_HOST" || HARG=""

# Dump PostgreSQL database
pg_dump $UARG $HARG -d $MAIN_SQL_DATABASE --clean $@