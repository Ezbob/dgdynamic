#!/bin/sh

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

. $CUR_DIR/setEnvir.sh
echo "Switched to dgdsl virtual environment"
. $CUR_DIR/shipping/dgdsl/bin/activate

