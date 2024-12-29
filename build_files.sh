# build_files.sh
#!/bin/bash
python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip
pip3.9 install -r requirements.txt
python3.9 manage.py collectstatic --noinput
