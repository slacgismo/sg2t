#!/bin/bash
echo "Installing all sg2t packages in editable mode. Run for dev work only."

for dir in ./sg2t/*/    # list directories in the form "/tmp/dirname/"
do
  dir=${dir%*/}
  pip install -e $dir/.
done