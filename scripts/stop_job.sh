# This kills the job which was created by start_job script

kill $(cat /home/ubuntu/ubi/scripts/UBIJOB.pid) # kill what ever the process id in the file
rm /home/ubuntu/ubi/scripts/UBIJOB.pid  # remove the pid file