from libs import kafka_utils

if __name__ == "__main__":
    #kafka_utils.sendToKafka_HardCoded('subscribe')
    kafka_utils.receiveFromKafka('subscribe')
    print("This is where Kafka intelligence and Postgres should be added")




