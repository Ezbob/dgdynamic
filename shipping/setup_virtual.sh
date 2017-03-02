#!/bin/bash

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
N_THREADS=4
LOG=$CUR_DIR"/dump.log"
ERR=$CUR_DIR"/err.log"

SRC_DIR=$CUR_DIR/src
PY_DIR=$CUR_DIR/python353

rm -rf $SRC_DIR
rm -rf $PY_DIR
mkdir -p $SRC_DIR
mkdir -p $PY_DIR

echo "Extracting Python 3.5.3..."
tar --extract -f Python-3.5.3.tgz -C $SRC_DIR
echo "done."

echo "Compiling Python 3.5.3 from source..."
cd $SRC_DIR/Python-3.5.3/
./configure --prefix=$PY_DIR >> $LOG 2>> $ERR
make -j$N_THREADS >> $LOG 2>> $ERR
make install >> $LOG 2>> $ERR
echo "done."

echo "Setting up virtual environment in "$CUR_DIR"/dgdsl..."
cd $CUR_DIR
virtualenv --python=$PY_DIR/bin/python3 dgdsl
echo "done."

rm -rf $SRC_DIR

