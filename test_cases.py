import pytest 
from chatbot import DBManager, JsonManager, SentimentObserver, OrderHandler, RefundHandler, StockHandler, Chatbot, QMU_DOWN


class TestClass:
    #Test for DBManager class to retrieve orders
    def test_get_orders(self): 
        obj = DBManager()
        assert isinstance(obj.get_orders(), list)
    
    #Test for DBManager class to retrieve stock
    def test_get_stock(self): 
        obj = DBManager()
        assert isinstance(obj.get_stock(), list)

    #Test for the angry sentiment to be detected 
    def test_check_sentiment(self): 
        obj = SentimentObserver()
        assert isinstance(obj.check_sentiment("I am angry"), str)

    #Test for no sentiment detected
    def test_check_sentiment_empty(self): 
        obj = SentimentObserver()
        assert isinstance(obj.check_sentiment(""), str)
        
    #Test for the response of the customer's question regarding order status
    def test_get_response_order(self): 
        obj = JsonManager()
        response = obj.get_response("where is my order?")
        assert response == "please enter your order id"
    
    #Test for invalid input to be handled
    def test_get_response_invalid(self): 
        obj = JsonManager()
        response = obj.get_response("invalid input")
        assert response is None

    #Test for the context of the customer's question regarding products in stock
    def test_get_context(self): 
        obj = JsonManager()
        assert isinstance(obj.get_context("is the iphone 15 in stock?"), str)
    
    #Test for teardown method to reset the singleton instance of JsonManager
    def teardown(self): 
        JsonManager._instance = None
    
    #Test for the product in question to be provided 
    def test_provide_product(self): 
        obj = JsonManager()
        assert obj.provide_product("is the iphone 15 in stock?") == "iphone 15"
    
    #Test for the QMU_DOWN constant to be defined
    def test_QMU_DOWN(self): 
        obj = OrderHandler()
        assert obj.handle(order_id="123", qmu= False) == QMU_DOWN

