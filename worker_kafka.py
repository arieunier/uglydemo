from libs import kafka_utils
import getopt, sys

def main (argv):
    topic = None
    try:
        opts, args = getopt.getopt(argv, "ht:", ["topic="])
    except getopt.GetoptError:
        print('worker_kafka.py -t <topic>')
        sys.exit(2)
    for opt, arg in opts:
        print("{}={}".format(opt, arg))
        if opt == '-h':
            print('workeyr_kafka.py -t <topic>')
        elif (opt in ('-t', '-topic')):
            topic =  arg 

    kafka_utils.receiveFromKafka('subscribe', topic)
    print("This is where Kafka intelligence and Postgres should be added")


if __name__ == "__main__":
    main(sys.argv[1:])
    

    