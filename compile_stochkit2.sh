#!/usr/bin/env bash

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

cd $CUR_DIR/dgdynamic/plugins/stochastic/stochkit2/

echo "Extracting StochKit2"
tar --extract --verbose --file stochkit.tar.gz
echo "done."
echo "Running install script..."
cd StochKit/
. ./install.sh
echo "done."
echo "all done."

cd $CUR_DIR
