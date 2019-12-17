echo "If you have any missing dependencies, check setup.sh for what a clean linux install uses"
docker build --tag mat-python-v1 .
docker-compose up -d
python MAT-python-standalone.py
