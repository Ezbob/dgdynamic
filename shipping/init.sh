#!/bin/sh
echo "Wellcome to the Deviation Graph Dynamic Simulation Liberary, or:"
cat ./banner
echo
echo "By Anders Busch, 2017. Check the LICENSE file for licensing information."

echo "Setting up virtual environment..."
exec ./setup_virtual.sh
exec ./get_dependencies.sh

echo "Done. Enjoy!"

