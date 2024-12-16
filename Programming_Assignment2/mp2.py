import psycopg2
import uuid
from datetime import datetime

from config import read_config
from messages import *
from seller import Seller

"""
    Splits given command string by spaces and trims each token.
    Returns token list.
"""
def tokenize_command(command):
    tokens = command.split(" ")
    return [t.strip() for t in tokens]

class Mp2Client:
    def __init__(self, config_filename):
        self.db_conn_params = read_config(filename=config_filename, section="postgresql")
        self.conn = None

    """
        Connects to PostgreSQL database and returns connection object.
    """
    def connect(self):
        self.conn = psycopg2.connect(**self.db_conn_params)
        self.conn.autocommit = False

    """
        Disconnects from PostgreSQL database.
    """
    def disconnect(self):
        self.conn.close()

    """
        Prints list of available commands of the software.
    """
    def help(self):
        # prints the choices for commands and parameters
        print("\n*** Please enter one of the following commands ***")
        print("> help")
        print("> sign_up <seller_id> <password> <plan_id>")
        print("> sign_in <seller_id> <password>")
        print("> sign_out")
        print("> show_plans")
        print("> show_subscription")
        print("> change_stock <product_id> <add or remove> <amount>")
        print("> subscribe <plan_id>")
        print("> ship <order_id>")
        print("> show_cart <customer_id>")
        print("> change_cart <customer_id> <product_id> <seller_id> <add or remove> <amount>")
        print("> purchase_cart <customer_id>")
        print("> quit")
    
    """
        Saves seller with given details.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def sign_up(self, seller_id, password, plan_id):
        try:
            with self.conn.cursor() as cursor:
                # Insert the new seller into the database
                cursor.execute(
                    "INSERT INTO sellers (seller_id, password, session_count, plan_id) VALUES (%s, %s, 0, %s)",
                    (seller_id, password, plan_id)
                )
            self.conn.commit()
            return True, CMD_EXECUTION_SUCCESS
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED

    """
        Retrieves seller information if seller_id and password is correct and seller's session_count < max_parallel_sessions.
        - Return type is a tuple, 1st element is a Seller object and 2nd element is the response message from messages.py.
        - If seller_id or password is wrong, return tuple (None, USER_SIGNIN_FAILED).
        - If session_count < max_parallel_sessions, commit changes (increment session_count) and return tuple (seller, CMD_EXECUTION_SUCCESS).
        - If session_count >= max_parallel_sessions, return tuple (None, USER_ALL_SESSIONS_ARE_USED).
        - If any exception occurs; rollback, do nothing on the database and return tuple (None, USER_SIGNIN_FAILED).
    """
    def sign_in(self, seller_id, password):
        #First check if the seller_id and password is correct
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM sellers WHERE seller_id = %s AND password = %s",
                    (seller_id, password)
                )
                seller = cursor.fetchone()
                
                if seller is None:
                    return None, USER_SIGNIN_FAILED
                
                #Get the plan of the seller
                cursor.execute(
                    "SELECT * FROM plans WHERE plan_id = %s",
                    (seller[3],)
                )
                plan = cursor.fetchone()
                #Check if the session count is less than the max_parallel_sessions
                if seller[2] < plan[2]:
                    cursor.execute(
                        "UPDATE sellers SET session_count = session_count + 1 WHERE seller_id = %s",
                        (seller_id,)
                    )
                    self.conn.commit()
                    return Seller(seller[0], seller[2] + 1, seller[3]), CMD_EXECUTION_SUCCESS
                else:
                    return None, USER_ALL_SESSIONS_ARE_USED
        except Exception as e:
            self.conn.rollback()
            return None, USER_SIGNIN_FAILED

    """
        Signs out from given seller's account.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Decrement session_count of the seller in the database.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def sign_out(self, seller):
        try:
            with self.conn.cursor() as cursor:
                if(seller.session_count == 0):
                    return False, CMD_EXECUTION_FAILED
                cursor.execute(
                    "UPDATE sellers SET session_count = session_count - 1 WHERE seller_id = %s",
                    (seller.seller_id,)
                )
            self.conn.commit()
            return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED


    """
        Quits from program.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Remember to sign authenticated user out first.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def quit(self, seller):
        if not seller:
            return True, CMD_EXECUTION_SUCCESS
        #Sign out the seller first
        sign_out_success, sign_out_message = self.sign_out(seller)
        if not sign_out_success:
            return False, CMD_EXECUTION_FAILED

        try:
            self.conn.commit()
            return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED


    """
        Retrieves all available plans and prints them.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print available plans and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        #|Name|Max Sessions
        1|Basic|2
        2|Advanced|4
        3|Premium|6
    """
    def show_plans(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM plans"
                )
                plans = cursor.fetchall()
                print("#|Name|Max Sessions")
                for i, plan in enumerate(plans):
                    print(f"{plan[0]}|{plan[1]}|{plan[2]}")
            return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED
    
    """
        Retrieves plan of the authenticated seller.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print the seller's plan and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        #|Name|Max Sessions
        1|Basic|2
    """
    def show_subscription(self, seller):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM plans WHERE plan_id = %s",
                    (seller.plan_id,)
                )
                plan = cursor.fetchone()
                print("#|Name|Max Sessions")
                print(f"{plan[0]}|{plan[1]}|{plan[2]}")
            return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED
    
    """
        Change stock count of a product.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If new stock value is < 0, return tuple (False, CMD_EXECUTION_FAILED).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def change_stock(self, seller, product_id, change_amount):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM stocks WHERE product_id = %s AND seller_id = %s",
                    (product_id, seller.seller_id)
                )
                stock = cursor.fetchone()
                if stock is None:
                    return False, CMD_EXECUTION_FAILED
                new_stock = stock[2] + change_amount
                if new_stock < 0:
                    return False, CMD_EXECUTION_FAILED
                cursor.execute(
                    "UPDATE stocks SET stock_count = %s WHERE product_id = %s AND seller_id = %s",
                    (new_stock, product_id, seller.seller_id)
                )
            self.conn.commit()
            return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED

    """
        Subscribe authenticated seller to new plan.
        - Return type is a tuple, 1st element is a Seller object and 2nd element is the response message from messages.py.
        - If the new plan's max_parallel_sessions < current plan's max_parallel_sessions, return tuple (None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE).
        - If the operation is successful, commit changes and return tuple (seller, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (None, CMD_EXECUTION_FAILED).
    """
    def subscribe(self, seller, plan_id):
        try:
            with self.conn.cursor() as cursor:
                #Get the current plan of the seller
                cursor.execute(
                    "SELECT * FROM plans WHERE plan_id = %s",
                    (seller.plan_id,)
                )
                current_plan = cursor.fetchone()
                #Get the new plan
                cursor.execute(
                    "SELECT * FROM plans WHERE plan_id = %s",
                    (plan_id,)
                )
                new_plan = cursor.fetchone()
                #Check if the new plan's max_parallel_sessions is greater than or equal to the current plan's max_parallel_sessions
                if new_plan[2] < current_plan[2]:
                    return None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE
                cursor.execute(
                    "UPDATE sellers SET plan_id = %s WHERE seller_id = %s",
                    (plan_id, seller.seller_id)
                )
            self.conn.commit()
            return Seller(seller.seller_id, seller.session_count, plan_id), CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return None, CMD_EXECUTION_FAILED
    
    """
        Change stock amounts of sellers of products included in orders.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Check shopping cart of the orders, find products and sellers, then update stocks and order status & shipping time. 
        - If everything is OK and the operation is successful, return (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def ship(self, order_ids):
        try:
            with self.conn.cursor() as cursor:
                for order_id in order_ids:
                    # Check if the order exists
                    cursor.execute(
                        "SELECT COUNT(*) FROM orders WHERE order_id = %s",
                        (order_id,)
                    )
                    if cursor.fetchone()[0] == 0:
                        self.conn.rollback()
                        return False, CMD_EXECUTION_FAILED  

                    cursor.execute(
                        "SELECT product_id, seller_id, amount FROM shopping_carts WHERE order_id = %s",
                        (order_id,)
                    )
                    items = cursor.fetchall()
                    
                    # Check if all items have enough stock
                    for product_id, seller_id, amount in items:
                        cursor.execute(
                            "SELECT stock_count FROM stocks WHERE product_id = %s AND seller_id = %s",
                            (product_id, seller_id)
                        )
                        stock_count = cursor.fetchone()[0]
                        if stock_count < amount:
                            self.conn.rollback()
                            return False, CMD_EXECUTION_FAILED

                    # Decrease stock amounts and update order status
                    for product_id, seller_id, amount in items:
                        cursor.execute(
                            "UPDATE stocks SET stock_count = stock_count - %s WHERE product_id = %s AND seller_id = %s",
                            (amount, product_id, seller_id)
                        )
                    cursor.execute(
                        "UPDATE orders SET status = 'SHIPPED', shipping_time = NOW() WHERE order_id = %s",
                        (order_id,)
                    )

                self.conn.commit()
                return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED
    
    """
        Retrieves items on the customer's temporary shopping cart (order status = 'CREATED')
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print items on the cart and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        Order Id|Seller Id|Product Id|Amount
        orderX|sellerX|productX|3
        orderX|sellerX|productY|1
        orderX|sellerY|productZ|4
    """
    def show_cart(self, customer_id):
        try:
            with self.conn.cursor() as cursor:
                # Find the order_id for the customer's current shopping cart
                cursor.execute(
                    "SELECT order_id FROM orders WHERE customer_id = %s AND status = 'CREATED'",
                    (customer_id,)
                )
                result = cursor.fetchone()
                if not result:
                    return False, CMD_EXECUTION_FAILED
                order_id = result[0]
                
                # Retrieve items in the shopping cart
                cursor.execute(
                    "SELECT order_id, seller_id, product_id, amount FROM shopping_carts WHERE order_id = %s",
                    (order_id,)
                )
                cart_items = cursor.fetchall()
                
                # Display the cart items
                cart_output = "Order Id|Seller Id|Product Id|Amount\n"
                for item in cart_items:
                    cart_output += f"{item[0]}|{item[1]}|{item[2]}|{item[3]}\n"
                print(cart_output.strip())
                return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            return False, CMD_EXECUTION_FAILED

        
        
    """
        Change count of items in temporary shopping cart (order status = 'CREATED')
        - Return type is a tuple, 1st element is boolean and 2nd element is the response message from messages.py.
        - Consider stocks of sellers when you add items to the cart, in case stock is not enough, return (False, STOCK_UNAVAILABLE).
        - Consider weight limit per order, 15 kilograms. return (False, WEIGHT_LIMIT) if it is reached for the whole order.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """
    def change_cart(self, customer_id, product_id, seller_id, change_amount):
        try:
            with self.conn.cursor() as cursor:
                # Find the order_id for the customer's current shopping cart
                cursor.execute(
                    "SELECT order_id FROM orders WHERE customer_id = %s AND status = 'CREATED'",
                    (customer_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    # Create a new order if no active cart exists
                    cursor.execute(
                        "INSERT INTO orders (order_id, customer_id, status) VALUES (gen_random_uuid(), %s, 'CREATED') RETURNING order_id",
                        (customer_id,)
                    )
                    order_id = cursor.fetchone()[0]
                else:
                    order_id = result[0]

                # Check the current total weight in the cart
                cursor.execute(
                    "SELECT SUM(p.weight * sc.amount) FROM shopping_carts sc JOIN products p ON sc.product_id = p.product_id WHERE sc.order_id = %s",
                    (order_id,)
                )
                current_weight = cursor.fetchone()[0] or 0

                # Get the weight of the product being added/removed
                cursor.execute(
                    "SELECT weight FROM products WHERE product_id = %s",
                    (product_id,)
                )
                product_weight = cursor.fetchone()[0]

                if change_amount > 0:
                    # Check stock availability
                    cursor.execute(
                        "SELECT stock_count FROM stocks WHERE product_id = %s AND seller_id = %s",
                        (product_id, seller_id)
                    )
                    stock_count = cursor.fetchone()[0]
                    if stock_count < change_amount:
                        return False, STOCK_UNAVAILABLE

                    # Check weight limit
                    new_weight = current_weight + (product_weight * change_amount)
                    if new_weight > 15:
                        return False, WEIGHT_LIMIT

                    # Add item to cart
                    cursor.execute(
                        "INSERT INTO shopping_carts (order_id, product_id, seller_id, amount) VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT (order_id, product_id, seller_id) DO UPDATE SET amount = shopping_carts.amount + EXCLUDED.amount",
                        (order_id, product_id, seller_id, change_amount)
                    )

                elif change_amount < 0:
                    # Remove item from cart
                    cursor.execute(
                        "UPDATE shopping_carts SET amount = amount + %s WHERE order_id = %s AND product_id = %s AND seller_id = %s",
                        (change_amount, order_id, product_id, seller_id)
                    )
                    cursor.execute(
                        "DELETE FROM shopping_carts WHERE amount <= 0 AND order_id = %s AND product_id = %s AND seller_id = %s",
                        (order_id, product_id, seller_id)
                    )

                self.conn.commit()
                return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED
    
    """
        Purchases items on the cart
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - When there are no items to purchase, return (False, EMPTY_CART).
        - Consider stocks of sellers when you purchase the cart, in case stock is not enough, return (False, STOCK_UNAVAILABLE).
        - If the operation is successful; return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Actions:
        - Change stocks on stocks table
        - Update order with status='CREATED' -> status='RECEIVED' and put order_time with current datetime.
    """
    def purchase_cart(self, customer_id):
        try:
            with self.conn.cursor() as cursor:
                # Find the order_id for the customer's current shopping cart
                cursor.execute(
                    "SELECT order_id FROM orders WHERE customer_id = %s AND status = 'CREATED'",
                    (customer_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return False, EMPTY_CART
                order_id = result[0]

                # Retrieve items in the shopping cart
                cursor.execute(
                    "SELECT product_id, seller_id, amount FROM shopping_carts WHERE order_id = %s",
                    (order_id,)
                )
                cart_items = cursor.fetchall()

                # Check if all items have enough stock
                for product_id, seller_id, amount in cart_items:
                    cursor.execute(
                        "SELECT stock_count FROM stocks WHERE product_id = %s AND seller_id = %s",
                        (product_id, seller_id)
                    )
                    stock_count = cursor.fetchone()[0]
                    if stock_count < amount:
                        return False, STOCK_UNAVAILABLE

                # Decrease stock amounts
                for product_id, seller_id, amount in cart_items:
                    cursor.execute(
                        "UPDATE stocks SET stock_count = stock_count - %s WHERE product_id = %s AND seller_id = %s",
                        (amount, product_id, seller_id)
                    )

                # Update order status to 'RECEIVED' and set the order time
                cursor.execute(
                    "UPDATE orders SET status = 'RECEIVED', order_time = NOW() WHERE order_id = %s",
                    (order_id,)
                )

                self.conn.commit()
                return True, CMD_EXECUTION_SUCCESS
        except Exception as e:
            self.conn.rollback()
            return False, CMD_EXECUTION_FAILED