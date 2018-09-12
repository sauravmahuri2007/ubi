# Execute a python script after every 60 seconds

while true; do date; /home/ubuntu/ubi/venv/bin/python /home/ubuntu/ubi/scripts/update_points.py; echo ''; sleep 60; done >> /home/ubuntu/ubi/logs/free_points_job.log & echo $! > /home/ubuntu/ubi/scripts/UBIJOB.pid