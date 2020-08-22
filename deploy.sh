set -exu
sudo chown $USER /dev/ttyUSB0
alias ampy="pipenv run ampy -p /dev/ttyUSB0"
for source in $(ls *.py libs/*.py)
do ampy put $source
done
