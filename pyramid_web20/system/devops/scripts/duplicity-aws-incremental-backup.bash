#!/bin/bash
#
# Backup installation, PostgreSQL database, Redis databases and media files to S3 bucket
#
# Usage:
#
#   bin/incremental-backup.bash AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY BACKUP_ENCRYPTION_KEY
#
# Installation in Python 2.7 virtualenv
#
#    virtualenv -p python2.7 duplicity-venv
#    source duplicity-venv/bin/activate
#    apt-get install -y librsync-dev
#    pip install https://launchpad.net/duplicity/0.7-series/0.7.01/+download/duplicity-0.7.01.tar.gz
#    pip install boto lockfile
#
# Recovering the backup:
#
#    gpg --batch --decrypt --passphrase xyz mysite-dump-20150213.sql.bzip2.gpg | bunzip2 > dump.sql
#
# Note: The user running this script must have sudo -u postgres acces to run pg_dump
#
# Note: This script is safe to run only on a server where you have 100% control and there are no other UNIX users who could see process command line or environment
#
# Note: Do **not** use AWS Frankfurt region - it uses unsupported authentication scheme - https://github.com/s3tools/s3cmd/issues/402
#
# Further reading:
#
#   http://www.janoszen.com/2013/10/14/backing-up-linux-servers-with-duplicity-and-amazon-aws/
#   http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteEndpoints.html


set -e

# Assume we are /srv/django/mysite
PWD=`pwd`
SITENAME=`basename $PWD`

# Use duplicity + boto installed in specific Python 2.7 virtualenv
source duplicity-venv/bin/activate

# Our S3 bucket where we drop files
DUPLICITY_TARGET=s3://s3-us-west-2.amazonaws.com/liberty-backup3/$SITENAME

# Tell credentials to Boto
export AWS_ACCESS_KEY_ID=$1
export AWS_SECRET_ACCESS_KEY=$2
export BACKUP_ENCRYPTION_KEY=$3

if [ -z "$BACKUP_ENCRYPTION_KEY" ]; then
    echo "You must give AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and BACKUP_ENCRYPTION_KEY on the command line"
    exit 1
fi

# Create daily dump of the database, suitable for drop in restore
sudo -u postgres pg_dumpall --clean | bzip2 | gpg --batch --symmetric --passphrase $BACKUP_ENCRYPTION_KEY > backups/$SITENAME-dump-$(date -d "today" +"%Y%m%d").sql.bzip2.gpg

# Dump the system Redis database, encrypt a copy of it
redis-cli save
cat /var/lib/redis/dump.rdb | bzip2 | gpg --batch --symmetric --passphrase $BACKUP_ENCRYPTION_KEY > backups/$SITENAME-dump-$(date -d "today" +"%Y%m%d").redis.bzip2.gpg


# Use cheap RSS S3 storage, exclude some stuff we know is not important.
# Also we do not need to encrypt media files as in our use case they are not sensitive, SQL dump is encrypted separately.
# Use 1024 MB volumes, as we are going to backup > 10 GB
duplicity --volsize 1024 --s3-use-rrs --exclude=`pwd`/logs --exclude=`pwd`/.git --exclude=`pwd`/venv --exclude=`pwd`/duplicity-venv --no-encryption --full-if-older-than 1M `pwd` $DUPLICITY_TARGET


# Clean up old backups
duplicity remove-older-than 6M $DUPLICITY_TARGET

