FROM openjdk:8-jre
ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.2.1
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH

ADD setup/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz /opt

COPY requirements.txt /opt

RUN apt-get update && apt-get -y install bash python3 python3-pip netcat

RUN pip3 --no-cache-dir install -r /opt/requirements.txt

# Create Sym Link 
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop3.2 ${SPARK_DIR} 

# Add Spark Manager
ADD spark-manager.sh $SPARK_DIR/bin/spark-manager

WORKDIR ${SPARK_DIR}
ENTRYPOINT [ "spark-manager" ]