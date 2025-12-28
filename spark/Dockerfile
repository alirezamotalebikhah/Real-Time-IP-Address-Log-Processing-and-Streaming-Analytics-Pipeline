FROM apache/spark:latest

USER root

RUN apt-get update && \
    apt-get install -y openjdk-21-jdk


ENV JAVA_HOME /usr/lib/jvm/java-21-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH


RUN apt-get install -y python3 python3-pip

RUN pip3 install pyspark==3.5.1 confluent-kafka


CMD ["/opt/spark/sbin/start-master.sh"]
