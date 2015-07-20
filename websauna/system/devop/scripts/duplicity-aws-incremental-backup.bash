#!/bin/bash
#
# Backup code files, PostgreSQL database, Redis databases and media files to S3 bucket
#
# Recovering the backup:
#
#    gpg --batch --decrypt --passphrase xyz mysite-dump-20150213.sql.bzip2.gpg | bunzip2 > dump.sql
#
# Note: Do **not** use AWS Frankfurt region - it uses unsupported authentication scheme - https://github.com/s3tools/s3cmd/issues/402
#
# This script never users passwords on a command line.
#
# Further reading:
#
#   http://www.janoszen.com/2013/10/14/backing-up-linux-servers-with-duplicity-and-amazon-aws/
#   http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteEndpoints.html

set -e
set -x

# Check we have duplicity installed
command -v duplicity >/dev/null 2>&1 || { echo >&2 "I require duplicity but it's not installed.  Aborting."; exit 1; }

DUPLICITY=`which duplicity`

# Read .ini settings to bash variables

[[ "$MAIN_WEBSAUNA_SITE_ID" ]] || { echo "websauna.site_id missing";  exit 1; }

[[ "$MAIN_WEBSAUNA_BACKUP_S3_BUCKET_URL" ]] || { echo "Backup S3 bucket missing"; exit 1; }

[[ "$SECRET_BACKUP_ENCRYPTION_KEY" ]] || { echo "backup.encryption_key secrets passphare missing"; exit 1; }

[[ "$SECRET_AWS_ACCESS_KEY_ID" ]] || { echo "aws.access_key_id secrets.ini entry missing"; exit 1; }

[[ "$SECRET_AWS_SECRET_ACCESS_KEY" ]] || { echo "aws.secret_access_key secrets.ini entry missing"; exit 1; }

[[ "$MAIN_WEBSAUNA_BACKUP_S3_BUCKET_URL" ]] || { echo "websauna.backup_s3_bucket_url ini entry missing"; exit 1; }

# Our S3 bucket where we drop files
DUPLICITY_TARGET=$MAIN_WEBSAUNA_BACKUP_S3_BUCKET_URL/$MAIN_WEBSAUNA_SITE_ID

# Tell credentials to Boto
export AWS_ACCESS_KEY_ID=$SECRET_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$SECRET_AWS_SECRET_ACCESS_KEY

# Assume we store backups in the same folder as project
LOCAL_BACKUP_DIR=$PWD/backups/$MAIN_WEBSAUNA_SITE_ID
install -d $LOCAL_BACKUP_DIR

# We need to export passphrase for GPG piping
# http://stackoverflow.com/a/7082184/315168
TEMP_FOLDER=$(mktemp -d)
PASSPHRASE_FILE=$TEMP_FOLDER/passphrase
trap "rm -rf $TEMP_FOLDER" EXIT
echo $SECRET_BACKUP_ENCRYPTION_KEY > $PASSPHRASE_FILE


# Create daily dump of the database, suitable for drop in restore
export PGPASSWORD=$MAIN_SQL_PASSWORD

[[ "$MAIN_SQL_USERNAME" ]] && UARG="-U $MAIN_SQL_USERNAME" || UARG=""
[[ "$MAIN_SQL_HOST" ]] && HARG="-h $MAIN_SQL_HOST" || HARG=""

# Dump PostgreSQL database
pg_dump $UARG $HARG -d $MAIN_SQL_DATABASE --clean | bzip2 | gpg --no-use-agent --batch --passphrase-file $PASSPHRASE_FILE --symmetric > $LOCAL_BACKUP_DIR/dump-$(date -d "today" +"%Y%m%d").sql.bzip2.gpg

# Dump the system Redis database, encrypt a copy of it
redis-cli --rdb $TEMP_FOLDER/redis-dump.rdb
cat $TEMP_FOLDER/redis-dump.rdb | bzip2 | gpg --no-use-agent --batch --passphrase-file $PASSPHRASE_FILE  --symmetric > $LOCAL_BACKUP_DIR/dump-$(date -d "today" +"%Y%m%d").redis.bzip2.gpg

rm -rf $TEMP_FOLDER

# Export passphrase to Duplicity
export PASSPHRASE=$SECRET_BACKUP_ENCRYPTION_KEY

# Incrementally copy sql dump, redis dump and everything in the project folder to S3 bucket
duplicity --volsize 1024 \
    --s3-use-rrs \
    --exclude=`pwd`/logs \
    --exclude=`pwd`/.git \
    --exclude=`pwd`/venv \
    --full-if-older-than 1M \
    `pwd` \
    $DUPLICITY_TARGET

# Clean up old backups
duplicity remove-older-than 6M $DUPLICITY_TARGET

