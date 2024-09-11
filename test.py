"""Publisher Subscriber model"""

class Publisher:
    
    def __init__(self, id, name, topic):
        self.id = id
        self.name = name
        self.topic = topic
    
    def publish(self, message):
        self.topic.publish(message)
    
class Subscriber:

    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def listen(self, message):
        print(f'Subscriber : {self.name}, Message : {message}')
        
class Topic:

    def __init__(self, id, topic_channel):
        self.id = id
        self.topic_channel = topic_channel
        self.subscribers = []
    
    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)
    
    def publish(self, message):
        for i in self.subscribers:
            i.listen(message)

class Pubsub:

    def __init__(self):
        self.publisher = {}
        self.subscriber = {}
        self.topic = {}
    
    def create_topic(self,topic_channel):
        topic_id = len(self.topic) + 1
        t = Topic(topic_id, topic_channel)
        self.topic[topic_id] = t
        return t
    
    def create_publisher(self,name, topic):
        pub_id = len(self.publisher) + 1
        pub = Publisher(pub_id, name, topic)
        self.publisher[pub_id] = pub
        return pub_id

    def create_subscriber(self, name):
        sub_id = len(self.subscriber) + 1
        sub = Subscriber(sub_id, name)
        self.subscriber[sub_id] = sub 
        return sub_id
    
    def subscribe_to_topic(self, subscriber_id, topic):
        topic.add_subscriber(self.subscriber[subscriber_id])

    def publish(self, message, publisher_id):
        publisher = self.publisher[publisher_id]
        publisher.publish(message)


pubsub = Pubsub()
topic = pubsub.create_topic('hall/kitchen/light')
pub = pubsub.create_publisher('device1', topic)
sub = pubsub.create_subscriber('IOT1')
sub2 = pubsub.create_subscriber('IOT2')
pubsub.subscribe_to_topic(sub, topic)
pubsub.subscribe_to_topic(sub2, topic)
pubsub.publish('Hello', publisher_id = pub)
