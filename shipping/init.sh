#!/bin/sh

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

echo "Wellcome to the Deviation Graph Dynamic Simulation Liberary, or:"
echo "       __          __     __"
echo "  ____/ /___ _____/ /____/ /"
echo " / __  / __ \`/ __  / ___/ / "
echo "/ /_/ / /_/ / /_/ (__  ) /  "
echo "\__,_/\__, /\__,_/____/_/   "
echo "     /____/                 "

echo "By Anders Busch, 2017. Check the LICENSE file for licensing information."

echo "Setting up virtual environment..."

N_THREADS=4
LOG=$CUR_DIR"/dump.log"
ERR=$CUR_DIR"/err.log"

mkdir src >> $LOG 2>> $ERR
mkdir python353 >> $LOG 2>> $ERR

SRC_DIR=$CUR_DIR/src
PY_DIR=$CUR_DIR/python353

echo "Extracting Python 3.5.3..."
tar --extract -f Python-3.5.3.tgz -C $SRC_DIR >> $LOG 2>> $ERR
echo "done."

echo "Compiling Python 3.5.3 from source..."
cd $SRC_DIR/Python-3.5.3/
./configure --prefix=$PY_DIR >> $LOG 2>> $ERR
make -j$N_THREADS >> $LOG 2>> $ERR
make install >> $LOG 2>> $ERR
echo "done."

echo "Setting up virtual environment in "$CUR_DIR"/dgdsl..."
cd $CUR_DIR
virtualenv --python=$PY_DIR/bin/python3 dgdsl >> $LOG 2>> $ERR
echo "done."

rm -rf $SRC_DIR

LOG=$CUR_DIR"/depdency.log"
ERR=$CUR_DIR"/dep_err.log"

echo "DEP START" > $LOG

echo "Getting and installing pip dependencies..."
. $CUR_DIR/dgdsl/bin/activate >> $LOG 2>> $ERR
cd ..
pip install -r requirements.txt >> $LOG 2>> $ERR
echo "done."

echo "All done. Enjoy!"

