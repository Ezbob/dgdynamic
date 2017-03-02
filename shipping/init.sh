#!/bin/sh
echo "Wellcome to the Deviation Graph Dynamic Simulation Liberary, or:"
cat ./banner
echo
echo "By Anders Busch, 2017. Check the LICENSE file for licensing information."

CUR_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

echo "Setting up virtual environment..."

. $CUR_DIR/setup_virtual.sh
. $CUR_DIR/get_dependencies.sh

echo "Done. Enjoy!"

