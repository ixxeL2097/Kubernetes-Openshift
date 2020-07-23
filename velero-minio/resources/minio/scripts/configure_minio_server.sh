#!/bin/bash
# auto provisioning script used after minio client start-up to add minio servers and provision bucket

########## VARIABLES ##########
buckets=( vault bpm awx )
###############################

########## CODE ##########
echo "CHECK > waiting for minio port opening..."
while [ $(nc -z minio1 9000; echo $?) != "0" ]
do
  echo "IDLE > waiting a bit more..."
  sleep 5
done

echo "SUCCESS > minio1 port opened"
sleep 10

echo "PROCESS > addind minio instances to minio client"
mc config host add minio http://${MINIO_IP}:9001 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
echo "SUCCESS > minio instances added"

echo "DISPLAY > minio servers status"
mc admin info minio

echo "PROCESS > creating buckets..."
for bucket in "${buckets[@]}"
do
  mc mb minio/${bucket}
  sleep 1
done
echo "SUCCESS > buckets created."

echo "DISPLAY > minio buckets tree"
mc tree minio

echo "FINISH > keeping container up & running by laucnhing shell"
sh