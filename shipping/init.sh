#!/bin/sh

#CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

echo "Wellcome to the Deviation Graph Dynamic Simulation Library, or:"
echo "       __          __     __"
echo "  ____/ /___ _____/ /____/ /"
echo " / __  / __ \`/ __  / ___/ / "
echo "/ /_/ / /_/ / /_/ (__  ) /  "
echo "\__,_/\__, /\__,_/____/_/   "
echo "     /____/                 "

echo "By Anders Busch, 2017. Check the LICENSE file for licensing information."

echo "Setting up virtual environment in "$(pwd)"..."

N_THREADS=4
LOG="dump.log"
ERR="err.log"

PY_DIR=$(pwd)/python353

mkdir -p $PY_DIR

echo "Extracting Python 3.5.3..."
tar --extract --file Python-3.5.3.tgz
echo "done."

echo "Compiling Python 3.5.3 from source..."
cd Python-3.5.3/
./configure --prefix=$PY_DIR
make -j$N_THREADS >> $LOG 2>> $ERR
make install >> $LOG 2>> $ERR
echo "done."
cd ..
rm -rf Python-3.5.3/

echo "Setting up virtual environment in "$(pwd)"/dgdsl..."
virtualenv --python=$PY_DIR/bin/python3 dgdsl
echo "done."


echo "Getting and installing pip dependencies..."
. ./dgdsl/bin/activate
cd ..
pip install -r requirements.txt
echo "done."

echo "All done. Enjoy!"

