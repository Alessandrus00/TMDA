#!/bin/bash
[[ -z "${SPARK_ACTION}" ]] && { echo "SPARK_ACTION required"; exit 1; }

echo "Running action ${SPARK_ACTION}"
case ${SPARK_ACTION} in

"streaming")
./bin/spark-submit --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1,org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0" /opt/tap/streaming.py
;;
"training")
./bin/spark-submit --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1,org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0" /opt/tap/training.py
;;
"cleaning")
./bin/spark-submit --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1,org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0" /opt/tap/cleaning.py
;;

"bash")
while true
do
	echo "Keep Alive"
	sleep 10
done
;;
esac

