import json
import csv
import time
import sys
from abc import ABC, abstractmethod

#Chatbot has an interactive approach of responding
def typing_animation(texting, delay=0.05):
    for char in texting:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

#Singleton Pattern
QMU_DOWN = "our system is down! connecting you to a live agent..."
class JsonManager: 
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                with open("queries.json", "r") as f:
                    cls._instance.queries = json.load(f)
            except Exception as e:
                return False
        return cls._instance

    #Retrieval from queries.json
    def get_response(self, query):
        return self.queries.get(query.lower(), {}).get("response")
    
    def get_context(self, query):
        return self.queries.get(query.lower(), {}).get("context")
    
    def get_response_type(self, query):
        return self.queries.get(query.lower(), {}).get("response_type")
    
    def provide_product(self, query):
        return self.queries.get(query.lower(), {}).get("product")

#Facade Pattern
class DBManager:
    def __init__(self):
        self.orders = None
        self.stock = None
        
        #Open and read csv files for orders and stock (backend service)
        with open("orders.csv", "r") as f:
            self.orders = list(csv.DictReader(f))
        
        with open("stock.csv", "r") as f:
            self.stock = list(csv.DictReader(f))
    
    #Retrieve orders
    def get_orders(self):
        return self.orders
    
    #Retrieve stock
    def get_stock(self):
        return self.stock
    
    #Begin refund
    def initiate_refund(self, order_id):
        for order in self.orders:
            if order["order_id"] == order_id: 
                if order["order_status"] == "cancelled":
                    print("Order already has been cancelled")
                else:
                    print("Cancelling order and initiating refund...")
                    time.sleep(2)
                    print("Your order has been cancelled and the refund has been initiated.")
                    order["order_status"] = "cancelled"
        with open("orders.csv", "w") as f:
            writer = csv.DictWriter(f, fieldnames=("order_id","prod_id","order_price","customer_id","order_status"))         
            writer.writeheader()
            writer.writerows(self.get_orders())

    #Check stock
    def check_stock(self, prod_name):
        time.sleep(2)
        for product in self.stock:
            if product["prod_name"].lower() == prod_name.lower():
                typing_animation(f"There are ({product["prod_qty"]}) {prod_name} available.")
                return

        typing_animation(f"{prod_name} is out of stock.")
                

#Strategy Pattern
#Abstract Method 
class ContextHandler(ABC):
    @abstractmethod
    def handle(self, qmu=False):
        pass

#Handle orders
class OrderHandler(ContextHandler):
    def handle(self, order_id=None, qmu=True):
        if not qmu:
            return QMU_DOWN 
        db = DBManager()
        orders = db.get_orders()
        print([f"order status: {i['order_status']}" for i in orders if str(order_id)== i["order_id"]] or "not found")

#Handle refunds  
class RefundHandler(ContextHandler):
    def handle(self, order_id=None, qmu=True):
        if not qmu:
            return QMU_DOWN 
        db = DBManager()
        orders = db.get_orders()
        print([f"order status: {i['order_status']}" for i in orders if str(order_id)== i["order_id"]] or "not found")
        db.initiate_refund(str(order_id))

#Handle stock
class StockHandler(ContextHandler):
    def handle(self, product, qmu=True):
        if not qmu:
            return QMU_DOWN 
        db = DBManager()
        db.check_stock(product)


#Observer Pattern
class SentimentObserver:
    def __init__(self):
        self.sentiment = "content"

    #Detect angry words
    def check_sentiment(self, words):
        words = words.split(" ")
        with open("angry_words.txt", "r") as f:
            angry_words = f.read().split("\n")
            for word in words:
                if word.lower() in angry_words:
                    self.sentiment = "angry"
        return self.sentiment

#Direct to Live Agent when customer is angry
class LiveAgentNotifier:
    def notified(self):
        typing_animation("connecting to a live agent...")
        time.sleep(2)
        typing_animation("agent notified!")
        
#The main operation
class Chatbot:
    def __init__(self): #Handlers are called
        self.handlers = {
            "order": OrderHandler(),
            "refund": RefundHandler(),
            "stock": StockHandler()
        }
        
        #Call sessions, JsonManager, LiveAgent and SentimentObserver
        self.sessions = {}
        self.jsonmanager = JsonManager()
        self.liveagent = LiveAgentNotifier()
        self.observer = SentimentObserver()
    
    #Live Agent directed when customer's sentiment is angry
    def process_input(self, user_id, user_input):
        sentiment = self.observer.check_sentiment(user_input)
        if sentiment == "angry":
            return self.liveagent.notified()
        
        #Retrive Json Queries
        response = self.jsonmanager.get_response(user_input)
        context = self.jsonmanager.get_context(user_input)
        response_type = self.jsonmanager.get_response_type(user_input)

        #If customer's question does not make sense
        if not response:
            print("I am sorry. I did not understand that. Please rephrase.")
            return
        
        #Chatbot providing a non-asking response to customer's question
        if response_type == "non-asking":
            typing_animation(response)
            if context == "stock":
                prod = self.jsonmanager.provide_product(user_input)
                if context in self.handlers:
                    self.handlers[context].handle(prod)
            else:
                if context in self.handlers:
                    self.handlers[context].handle(prod)

        #Chatbot providing asking a question in response to customer's question
        if response_type == "asking":
            if context == "refund":
                typing_animation("why do you want to return your product?")
                input(">>>: ").strip().lower()
            user_input = input((f"{response}>>>: "))
            self.handlers[context].handle(user_input)
    
    #Chat procedure
    def start_chat(self, user_id):
        typing_animation("Welcome! How can I help you?")
        while True:
            user_input = input(">>>: ").strip().lower()
            self.process_input(user_id, user_input)
            further = input("Is there anything else I can help you with? (yes/no): ").strip().lower() #Follow up
            
            if further == "no": #Customer wants to end chat
                typing_animation("Sure. Have a good day! Bye!")
                break

if __name__ == "__main__":
    c1 = Chatbot()
    c1.start_chat("user1")
    