##REBAG challange

## REQUIREMENT:
    We want to award gift cards to customers. 
    Once a customer is awarded a gift card, 
    he can use it to pay with any order placed on our website.

    We need a django admin Page where we can see all our current customers, 
    and for individual customer pages, 
    we need to be able to see the customer name, email and all the giftcards awarded to that customer 
    plus we need the ability to award gift cards and the ability to record when they are used in an order. 
    Add two buttons to the individual customer page: Create Gift card and Record Order Usage
    
    For each individual Gift card we want to see: name, current amount, initial amount, Orders where it was used,

    REST API calls should be built to create/update and retrieve gift card records. 
    For the extra parts that are not covered by django admin you can use either plain js or jquery.

## DATABASE STRUCTURE:

    - A CUSTOMER IS A USER (Customer is a Group, and a USER can be added to the group)
    - USERS -- OneToMany -- ORDERS
    - USERS -- OneToMany -- GIFTCARDS
    - GIFTCARDS -- ManyToMany -- ORDERS

##   STARTUP
    - docker compose up --build
    - python manage.py createsuperuser
    - login

##   SET UP
    - Create new Group Called 'Customer'
    - Create new users and assign them to the 'Customer' group
    - Insert Orders into DB. (Assumed Order is an already implemented app)
    INSERT INTO orders (id, total_amount, created_at, user_id) VALUES (1, '1500', NOW(), 2),

