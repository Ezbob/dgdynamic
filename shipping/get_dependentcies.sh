#!/bin/sh

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

LOG="depdency.log"
ERR="dep_err.log"

echo "DEP START" > $LOG

echo "Getting and installing pip dependencies..."
. $CUR_DIR/dgdsl/bin/activate >> $LOG 2>> $ERR
cd ..
pip install -r requirements.txt >> $LOG 2>> $ERR
echo "done."

