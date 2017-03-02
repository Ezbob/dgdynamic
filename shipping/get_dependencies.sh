#!/bin/sh

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

echo "Getting and installing pip dependencies..."
. $CUR_DIR/dgdsl/bin/activate
cd ..
pip install -r requirements.txt
echo "done."

