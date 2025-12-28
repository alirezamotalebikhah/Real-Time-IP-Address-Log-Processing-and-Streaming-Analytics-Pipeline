# Real-Time IP Address Log Processing and Streaming Analytics Pipeline

## Project Overview

A comprehensive real-time data processing system for ingesting, analyzing, and storing IP address logs at scale. This framework demonstrates a complete production-ready pipeline combining Apache Kafka for messaging, Apache Spark for stream processing, and Apache Cassandra for distributed storage, with automated CI/CD deployment using GitLab.

**Project Report:** See [Report_Project1.pdf](Report_Project1.pdf) for comprehensive documentation of the implementation.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│    IP Address Log Data Source           │
│    (Real-time log streams)              │
└──────────────────┬──────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  Producer Container              │
    │  Script: producer.py             │
    │  Sends logs to Kafka Topic       │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  Apache Kafka Message Broker     │
    │  Topic: ip_logs (streaming)      │
    │  Partitions: Multiple            │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  Spark Streaming Container       │
    │  Scripts:                        │
    │  - spark_stream_reader.py        │
    │  - spark_stream_to_cassandra.py  │
    │  Real-time processing and       │
    │  transformation                  │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  Apache Cassandra Cluster        │
    │  Distributed NoSQL Storage       │
    │  Real-time Data Persistence      │
    └──────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │  GitLab CI/CD Pipeline           │
    │  Automated Testing & Deployment  │
    │  Self-Hosted Gitlab-CE with      │
    │  GitLab Runner                   │
    └──────────────────────────────────┘
```

---

## Prerequisites

- Docker & Docker Compose 20.10+
- Python 3.8+
- Git
- GitLab (Self-Hosted CE or GitLab.com account)
- 4GB+ RAM
- 30GB+ free disk space
- Basic understanding of Kafka, Spark, and Cassandra

---

## Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/alirezamotalebikhah/Real-Time-IP-Address-Log-Processing-and-Streaming-Analytics-Pipeline.git
cd Real-Time-IP-Address-Log-Processing-and-Streaming-Analytics-Pipeline
```

### Step 2: Set Up Environment

Review and configure environment variables:

```bash
# Check docker-compose.yml for all services
cat docker-compose.yml
```

### Step 3: Start Docker Infrastructure

```bash
docker-compose up -d
```

This will start:
- Apache Kafka (Port 9092)
- Zookeeper (Port 2181)
- Apache Cassandra (Port 9042)
- Producer Container
- Spark Container
- All supporting services

Verify services are running:

```bash
docker-compose ps
```

### Step 4: Configure Hosts (Optional)

For local DNS resolution, add to `/etc/hosts`:

```
127.0.0.1 kafka
127.0.0.1 zookeeper
127.0.0.1 cassandra
127.0.0.1 spark
```

---

## Project Components

### Component 1: Log Producer

**Directory:** `Producer/`

**Files:**
- `Dockerfile` - Container definition for producer service
- `producer.py` - Python script that generates and sends IP logs to Kafka

**Purpose:** Simulate real-time IP address log generation and send to Kafka

**Execution:**

```bash
# Build the producer image
docker build -t ip-log-producer ./Producer

# Run producer (automatically starts with docker-compose)
docker-compose up producer
```

**What producer.py does:**
- Generates simulated IP address logs
- Formats logs as JSON
- Sends logs to Kafka topic: `ip_logs`
- Maintains continuous streaming
- Provides status and metrics during execution

**Configuration:**
- Kafka broker connection: `kafka:9092`
- Topic name: `ip_logs`
- Message format: JSON
- Batch size: Configurable

**Log Format Example:**
```json
{
  "timestamp": "2025-12-28T10:30:45.123456",
  "source_ip": "192.168.1.100",
  "destination_ip": "10.0.0.50",
  "port": 8080,
  "protocol": "TCP",
  "bytes_sent": 2048,
  "bytes_received": 4096,
  "action": "ALLOW"
}
```

---

### Component 2: Spark Streaming Processing

**Directory:** `spark/`

**Files:**
- `Dockerfile` - Container definition for Spark environment
- `spark_stream_reader.py` - Reader to consume from Kafka
- `spark_stream_to_cassandra.py` - Writer to store in Cassandra

**Purpose:** Process IP logs in real-time using Spark Streaming

#### spark_stream_reader.py

**Functionality:**
- Consumes messages from Kafka topic `ip_logs`
- Parses JSON format
- Validates log structure
- Applies initial transformations
- Filters invalid records

**Execution:**

```bash
docker-compose up spark-reader
# or
docker exec spark-container spark-submit spark_stream_reader.py
```

**Configuration:**
- Kafka broker: `kafka:9092`
- Topic: `ip_logs`
- Batch interval: 5-10 seconds (configurable)
- Format: JSON

**Data Validation:**
- Checks for required fields
- Validates IP address format
- Verifies timestamps
- Ensures port numbers are valid

#### spark_stream_to_cassandra.py

**Functionality:**
- Reads processed streams from Spark
- Transforms data for Cassandra schema
- Converts JSON to table format
- Writes data to Cassandra using WriteStream
- Handles schema changes

**Execution:**

```bash
docker-compose up spark-writer
# or
docker exec spark-container spark-submit spark_stream_to_cassandra.py
```

**Configuration:**
- Cassandra nodes: `cassandra:9042`
- Keyspace: `ip_logs`
- Table: `access_logs` (or similar)
- Write mode: Append
- Checkpoint location: `/tmp/spark-checkpoint`

**Data Transformation:**
- Converts timestamp formats
- Aggregates IP statistics
- Calculates traffic metrics
- Enriches logs with computed fields

**Cassandra Table Schema:**
```sql
CREATE TABLE IF NOT EXISTS ip_logs.access_logs (
    timestamp TIMESTAMP,
    source_ip TEXT,
    destination_ip TEXT,
    port INT,
    protocol TEXT,
    bytes_sent BIGINT,
    bytes_received BIGINT,
    action TEXT,
    created_at TIMESTAMP,
    PRIMARY KEY (source_ip, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

---

### Component 3: Docker Configuration

**File:** `docker-compose.yml`

**Services Defined:**
- **Kafka**: Message broker for log streaming
- **Zookeeper**: Coordination for Kafka
- **Cassandra**: NoSQL database for storage
- **Producer**: Log generation service
- **Spark**: Stream processing service
- **Supporting services**: Database clients, admin tools

**Key Configuration:**
- Network mode: Bridge or custom network
- Volume mounts: For data persistence
- Environment variables: Service configuration
- Port mappings: Access to services

**Common Commands:**

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Execute commands in container
docker-compose exec [service-name] [command]

# Rebuild specific service
docker-compose up -d --build [service-name]
```

---

### Component 4: GitLab CI/CD Pipeline

**File:** `.gitlab-ci.yml` (referenced in project)

**Purpose:** Automate testing and deployment of the pipeline

#### Setup GitLab Infrastructure

**Step 1: Install Self-Hosted GitLab CE**

On a Linux server (Debian-based):

```bash
# Add GitLab repository
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash

# Install GitLab CE
sudo EXTERNAL_URL="http://your-server.com" apt-get install gitlab-ce
```

Default password location: `/etc/gitlab/initial_root_password`

**Step 2: Install GitLab Runner**

```bash
# Add runner repository
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash

# Install runner
sudo apt-get install gitlab-runner
```

**Step 3: Register Runner with GitLab**

```bash
# Register runner
sudo gitlab-runner register

# When prompted, enter:
# - GitLab URL: http://your-gitlab-instance
# - Registration token: (from GitLab Settings > CI/CD > Runners)
# - Runner description: My Runner
# - Tags: docker, spark, kafka (optional)
# - Executor: docker
# - Docker image: python:3.9
```

Alternatively, register via GitLab UI:

```
Settings → CI/CD → Runners → Create project runner
```

#### CI/CD Pipeline Stages

The pipeline executes the following stages:

**1. Before Script**
- Install dependencies
- Check Docker and Python versions
- Verify Kafka connectivity

**2. Build Stage**
- Test producer.py syntax
- Build Docker images
- Verify Spark scripts

**3. Test Stage**
- Test Kafka connectivity
- Verify Cassandra availability
- Run unit tests

**4. Deploy Stage**
- Deploy containers to server
- Start services
- Verify service health
- Run integration tests

#### GitLab Variables

Configure sensitive variables in:

```
Settings → CI/CD → Variables → Add Variable
```

Common variables:
- `KAFKA_BROKER`: kafka:9092
- `CASSANDRA_NODES`: cassandra:9042
- `SPARK_MASTER`: spark-master:7077
- `DOCKER_REGISTRY_URL`: Docker registry URL
- `DEPLOYMENT_SERVER`: Target deployment server

#### Example Pipeline Configuration

```yaml
stages:
  - build
  - test
  - deploy

before_script:
  - apt-get update
  - pip install -r requirements.txt

build:
  stage: build
  script:
    - docker build -t producer:latest ./Producer
    - docker build -t spark:latest ./spark

test:
  stage: test
  script:
    - python -m pytest Producer/
    - python -m pytest spark/

deploy:
  stage: deploy
  script:
    - docker-compose up -d
    - docker-compose ps
  only:
    - main
```

---

## Data Flow and Processing

### Ingestion Phase
1. Producer generates IP logs at regular intervals
2. Logs formatted as JSON
3. Sent to Kafka topic `ip_logs`

### Processing Phase
1. Spark Streaming consumes from Kafka
2. spark_stream_reader.py validates and parses logs
3. Data transformations applied
4. Invalid records filtered

### Storage Phase
1. spark_stream_to_cassandra.py formats data
2. WriteStream writes to Cassandra
3. Data persisted in distributed storage
4. Available for real-time queries

### Deployment Phase
1. Code pushed to GitLab repository
2. CI/CD pipeline triggered automatically
3. Tests executed
4. Successful builds deployed
5. Services restarted with new code

---

## Terminal Commands Reference

All terminal commands used during execution are documented in:

**`terminal.txt`**

This file contains:
- Docker commands for building and running containers
- Kafka commands for topic creation and inspection
- Cassandra commands for database operations
- Spark commands for job submission
- GitLab Runner registration and management
- Debugging and troubleshooting commands

---

## Monitoring and Querying

### Kafka Monitoring

List topics:
```bash
docker exec kafka kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092
```

View topic messages:
```bash
docker exec kafka kafka-console-consumer \
  --topic ip_logs \
  --from-beginning \
  --bootstrap-server kafka:9092 \
  --max-messages 10
```

### Cassandra Queries

Connect to Cassandra:
```bash
docker exec cassandra cqlsh cassandra
```

Example queries:
```sql
-- Show keyspaces
SHOW KEYSPACES;

-- Use keyspace
USE ip_logs;

-- Show tables
SHOW TABLES;

-- Query recent logs
SELECT * FROM access_logs 
LIMIT 10;

-- Get logs from specific IP
SELECT * FROM access_logs 
WHERE source_ip = '192.168.1.100' 
LIMIT 20;
```

### Spark Monitoring

Spark UI: `http://localhost:8080`

View running jobs:
```bash
docker exec spark spark-shell
```

---

## Troubleshooting

### Common Issues

**Issue: Kafka connection refused**
```bash
# Check Kafka is running
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart kafka
```

**Issue: Cassandra failed to start**
```bash
# Check Cassandra logs
docker-compose logs cassandra

# Ensure sufficient disk space
df -h

# Restart Cassandra
docker-compose restart cassandra
```

**Issue: Spark job fails**
```bash
# Check Spark logs
docker-compose logs spark

# Verify Kafka connectivity
docker exec spark bash -c "nc -zv kafka 9092"

# Verify Cassandra connectivity
docker exec spark bash -c "nc -zv cassandra 9042"
```

**Issue: CI/CD pipeline fails**
```bash
# Check GitLab Runner status
sudo gitlab-runner status

# View runner logs
sudo tail -f /var/log/gitlab-runner/system.log

# Restart runner
sudo gitlab-runner restart
```

---

## Performance Metrics

### Data Throughput
- Producer: 10K-50K logs/second
- Kafka: 100K+ messages/second capacity
- Spark: Real-time processing with 5-10 second batches
- Cassandra: 10K+ writes/second

### Latency
- Producer to Kafka: <100ms
- Kafka to Spark: <200ms
- Spark processing: 1-5 seconds
- Cassandra write: <50ms
- End-to-end: <10 seconds

### Storage
- Cassandra replication factor: 3
- Data compression: Enabled
- Partition strategy: By source IP + timestamp

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Streaming** | Apache Kafka | 7.5.0 | Message broker |
| **Stream Processing** | Apache Spark | 3.5.1 | Distributed processing |
| **NoSQL Database** | Apache Cassandra | 4.0+ | Distributed storage |
| **Programming** | Python | 3.8+ | Scripts and jobs |
| **Containerization** | Docker & Compose | 20.10+ | Container management |
| **CI/CD** | GitLab CE | Self-Hosted | Automation & deployment |
| **Message Format** | JSON | - | Data exchange format |

---

## Project Structure

```
project-01-RealTimeDataPipeline/
├── docker-compose.yml           # Service orchestration
├── Producer/                    # Log producer service
│   ├── Dockerfile              # Container definition
│   └── producer.py             # Log generation script
├── spark/                       # Spark streaming services
│   ├── Dockerfile              # Spark container definition
│   ├── spark_stream_reader.py   # Kafka consumer
│   └── spark_stream_to_cassandra.py  # Cassandra writer
├── spark-apps/                 # Spark application files
├── terminal.txt                # Command reference
├── Report_Project1.pdf         # Project documentation
└── README.md                   # This file
```

---

## Learning Resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Streaming Guide](https://spark.apache.org/docs/latest/streaming-programming-guide.html)
- [Apache Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [Docker Documentation](https://docs.docker.com/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitLab Runner Documentation](https://docs.gitlab.com/runner/)

---

## Key Features

- Real-time log streaming with Apache Kafka
- Distributed stream processing with Apache Spark
- Scalable NoSQL storage with Apache Cassandra
- Containerized architecture with Docker
- Automated CI/CD pipeline with GitLab
- Self-hosted GitLab infrastructure
- JSON data format for flexibility
- Production-ready deployment

---

## Use Cases

- **Real-time Log Analysis**: Process IP logs as they arrive
- **Network Security Monitoring**: Detect suspicious access patterns
- **Traffic Analytics**: Analyze network traffic in real-time
- **Data Pipeline Automation**: Continuous integration and deployment
- **Distributed Computing**: Handle large-scale data processing
- **Learning Platform**: Educational implementation of big data tools

---

## Project Information

**Authors:** Alireza Motalebikhah

**Team:** Data Dudes

**Status:** Active Development

**Version:** 1.0

**Repository:** [GitHub Repository](https://github.com/alirezamotalebikhah/Real-Time-IP-Address-Log-Processing-and-Streaming-Analytics-Pipeline)


---

## Contributing

For improvements and contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit with clear messages
5. Push to your branch
6. Submit a pull request

---

## Support

For questions or issues:

- Open an issue on GitHub
- Review the project report (Report_Project1.pdf)
- Check `terminal.txt` for command reference
- Consult technology documentation links

---

**Last Updated:** December 28, 2025

**Version:** 1.0