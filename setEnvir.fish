#!/usr/bin/fish

set --export PYTHONPATH (mod --nopost | grep 'mod:' | awk '{print $2}')":"(cd ( dirname (status -f) ); and pwd)":"
echo "Exported "$PYTHONPATH" to Python Path"
