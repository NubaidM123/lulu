#Importing required dependencies
from config import db
from google.cloud.firestore_v1.base_query import FieldFilter

#Defining class User
class User:
    def __init__(self,name:str,email:str,password,isEmployee:bool):
        self.name = name
        self.email = email
        self.password=password
        self.isEmployee=isEmployee

#function to add user        
def addUser(name,email,password,isEmployee):
    data={
            'name':name,
            'email':email,
            'isEmployee':isEmployee,
            'password':password
    }
    doc_ref=db.collection('Users').document()
    doc_ref.set(data)
    print('User Succesfully Added')

#Defining class Item
class Item:
    def __init__(self,name:str,price:float,quantity:int):
        if name != '':
            self.name = name
        else:
            print("Name cannot be empty.")
        if price > 0:
            self.price = price
        else:
            print("Price can only be positive.")
        if quantity >= 0:
            self.qty = quantity
        else:
            print("Quantity cannot be non-negative.")
    
    # Tells Python how to check if two items are equal (by name)
    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name
        return False

    # Tells Python how to generate a dictionary key hash based on the name
    def __hash__(self):
        return hash(self.name)
    
    #Method to change name of item
    def change_name(self, new_name:str):
        if new_name != '':
            item_ref=db.collection('Items')
            query=item_ref.where(filter=FieldFilter('name','==',self.name)).stream()
            #found checks if an item with that name exists in the database
            found=False
            for item in query:
                found=True
                doc_ref=item_ref.document(item.id)
                doc_ref.update({
                    'name':new_name
                })
            if not found:
                print('Item not found')
            else:
                print('The item name has been updated')
                self.name = new_name
        else:
            print("Name cannot be empty.")
    
    #Method to change price of item
    def change_price(self, new_price):
        if new_price > 0:
            item_ref=db.collection('Items')
            query=item_ref.where(filter=FieldFilter('name','==',self.name)).stream()
            #found checks if an item with that name exists in the database
            found=False
            for item in query:
                found=True
                doc_ref=item_ref.document(item.id)
                doc_ref.update({
                    'price':new_price
                })
            if found:
                print('The item price has been updated')
                self.price = new_price
            if not found:
                print('Item not found')
        else:
            print("Price can only be positive.")
    
    #Method to change quantity of item
    def change_qty(self, new_qty):
        if new_qty >= 0:
            item_ref=db.collection('Items')
            query=item_ref.where(filter=FieldFilter('name','==',self.name)).stream()
            #found checks if an item with that name exists in the database
            found=False
            for item in query:
                found=True
                doc_ref=item_ref.document(item.id)
                doc_ref.update({
                    'qty':new_qty
                })
            if found:
                print('The item quantity has been updated.')
                self.qty = new_qty
            
        else:
            print("Quantity cannot be non-negative.")


#Function to add a new item to firebase and to return it, or return an existing item
def add_item(name,price,quantity):
    item_ref=db.collection('Items')
    query=item_ref.where(filter=FieldFilter('name','==',name)).stream()
    #found checks if an item with that name exists in the database
    found=False
    idi = None
    for doc in query:
        found=True
        idi=doc.id
    #If item exists, doesn't make a new item; it returns an Item object with the details from the database
    if found:
        print("Item already exists")
        doc_ref=item_ref.document(idi) #type: ignore
        data=doc_ref.get().to_dict() #type: ignore
        return Item(
                name=data.get('name'),  #type: ignore
                price=data.get('price'), #type: ignore
                quantity=data.get('qty') #type: ignore
            )
    #If item doesn't exist, add to database
    else:
        item = Item(name,price,quantity)
        data={
            'name':name,
            'price':price,
            'qty':quantity,
        }
        doc_ref=db.collection('Items').document()
        doc_ref.set(data)
        print('Item Successfully Added')
        return item

#Function to remove an item from firebase
def remove_item(name):
    item_ref=db.collection('Items')
    query=item_ref.where(filter=FieldFilter('name','==',name)).stream()
    #found checks if an item with that name exists in the database
    found=False
    for i in query:
        found=True
        item_ref.document(i.id).delete()
    if not found:
        print("Item does not exist.")
    else:
        print('Item has been deleted')

#Defining class Cart   
class Cart:
    #Initializing cart and adding it to database, linked with user
    def __init__(self,user:User,cart:dict = {},iteminf:dict = {}):
        self.user = user
        self.cart = cart
        self.iteminf = iteminf
        
    #Method to add item to cart
    def addtocart(self, item: Item, quant):
        cart_ref = db.collection('Carts')
        query = cart_ref.where(filter=FieldFilter('user', '==', self.user.email)).stream()
        
        cart_doc_id = None
        #found checks if a user with that email exists in the database
        found = False
        cart_found=False
        for i in query:
            cart_found=True
            cart_doc_id = i.id
            cart_data = i.to_dict().get('cart', {}) #type: ignore   
            if item.name in cart_data:
                found = True
                break
        if not cart_found:
            print("Error: Could not find a cart document associated with this user.")
            return
        if found:
            print('Item is already added.')
            return
        
        if quant > item.qty:
            print("Not enough quantity in stock.")
            return
        if quant==0:
            print('"Why do you want to add 0 items?"-N')
        elif quant<0:
            print('Cant add negative items')
        else:
            self.cart[item] = quant
            self.iteminf[item.name] = quant   
            if cart_doc_id:
                doc_ref = cart_ref.document(cart_doc_id)
                doc_ref.update({
                    'cart': self.iteminf
                })
                print(f"Successfully added {quant}x '{item.name}' to your cart.")
        
    
    #Method to delete a specific amount of items from cart
    def removefromCart(self,quantity,item:Item):
        cart_ref = db.collection('Carts')
        query = cart_ref.where(filter=FieldFilter('user','==',self.user.email)).stream()
        self.cart[item]-=quantity
        self.iteminf[item.name]-=quantity
        for i in query:
                doc_ref=cart_ref.document(i.id)
                doc_ref.update({
                    'cart':self.iteminf
                })
    
    #Method to delete all items from card
    def clearCart(self):
        cart_ref = db.collection('Carts')
        query = cart_ref.where(filter=FieldFilter('user','==',self.user.email)).stream()
        self.cart={}
        self.iteminf={}
        for i in query:
                doc_ref=cart_ref.document(i.id)
                doc_ref.update({
                    'cart':{}
                })
    
    #Method to calculate the total amount
    def getTotal(self):
        a=list(map(lambda x:x.price, self.cart.keys()))
        b=list(self.cart.values())
        s=0
        for i in range(len(a)):
            s+=a[i]*b[i]
        print(f"The total comes to {s}")

#Function to add a cart linked to a user to the database
def addCart(user):
    data={
            'user':user.email,
            'cart':{}
        }
    cart_ref = db.collection('Carts')
    query = cart_ref.where(filter=FieldFilter('user','==',user.email)).stream()
    found=False
    for i in query:
            found=True
    if not found:
        doc_ref = db.collection('Carts').document()
        doc_ref.set(data)
        print('User Successfully Added')
    else:
        print('Cart Found!')

#Menu Driven Program
print("LULU    - an NMMR company")

#Dealing with login and registration
c=input('Do you already have an account? Y/N: ')
if c.lower()=='n' or c.lower()=='no':
    #Signup
    print("No Worries! Let's create an account now")
    name=input('Enter your name: ')
    email=input('Enter your email: ')
    #Password verification
    while True:
        hasUpper = False
        hasLower = False
        hasNumber = False
        password=input('Create a password: ')
        if len(password) < 8:
            print('Password should atleast be 8 characters.')
            continue
        for ch in password:
            if ch.isupper():
                hasUpper = True
            if ch.islower():
                hasLower= True
            if ch.isdigit():
                hasNumber = True
        if not hasUpper or not hasLower or not hasNumber:
            print("Password must have atleast one uppercase character, one lowercase character, and a number.")
            continue
        recheck=input('Re-type your password: ')
        if password==recheck:
            break
        print('Seems to be incorrect, try again')
    #Checking if employee
    while True:
        q = input("Enter the company motto if you are an employee: ")
        if q.lower() == 'where the world comes to shop':
            emp=True
            print("Comfirmed employee status")
            break
        else:
            c=input('Try Again? (Y/N) If not Signup as customer ')
            if c.lower()=='y':
                continue
            else:
                emp=False
                break
    #Creating User object
    user=User(name,email,password,emp)
    #Adding user to database, since new user
    addUser(name,email,password,emp)
#Login for all users
print('Login')
user=None
while True:
    email=input('Enter Email (or Q to quit): ')
    if email.lower() in ('q', 'quit'):
        print('Login aborted')
        break
    passw=input('Enter password: ')
    #Getting the correct user from database
    user_ref = db.collection('Users')
    query = user_ref.where(filter=FieldFilter('email','==',email)).stream()
    #found checks if a user with that email exists in the database
    found=False
    for i in query:
        found=True
        idi=i.id
        break
    if found:
        doc_ref=user_ref.document(idi)
        data=doc_ref.get().to_dict()  # type: ignore
        #Checking if given password matches stored password
        if passw==data.get('password'): #type: ignore
            print('Login Successful')
            user=User(data.get('name'),data.get('email'),data.get('password'),data.get('isEmployee')) #type: ignore
            break
        print("Incorrect details entered")
    else:
        print('Account not found, Try again')
        retry=input('Try again? (Y/N): ')
        if retry.lower() != 'y':
            print('Login aborted')
            break

if user is None:
    raise SystemExit

#Different actions based on employee status

#Employee actions
if user.isEmployee == True:
    while True:
        print('''\nOptions:
    1) Add an item
    2) Delete an item
    3) Change an item
    4) Ban a user
    5) View all users
    6) View all items
    0) Exit
''')
        try:
            choice = int(input("Enter your choice: "))
        except:
            print('Invalid Input!')
        if choice == 1: #Adding an item to the shop
            try:
                name = input("Enter the name of the item: ")
                price = float(input("Enter the price of the item: "))
                quantity = int(input("Enter the quantity of the item: "))
                if price<=0 or quantity<=0:
                    raise ValueError('Negative or zero Value is invalid')
                add_item(name,price,quantity)
            except Exception as e:
                print("Something went wrong.... Try again", e)

        elif choice == 2: #Deleting an item
            try:
                name = input("Enter the name of the item: ")
                remove_item(name)
            except Exception as e:
                print("Error:",e)
            
        elif choice == 3: #Changing the details of an item
            try:
                name = input("Enter the name of the item: ")
                price = float(input("Enter the new price of the item: "))
                quantity = int(input("Enter the new quantity of the item: "))
                if price<=0 or quantity<=0:
                    raise ValueError('Negative or zero Value is invalid')
                item_ref=db.collection('Items')
                query=item_ref.where(filter=FieldFilter('name','==',name)).stream()
                found=False
                for i in query:
                    found = True
                    data = i.to_dict()
                    item = Item(name,data.get('price'),data.get('qty')) #type: ignore
                if not found:
                    print("Item not found")
                else:
                    item.change_price(price)
                    item.change_qty(quantity)
            except Exception as e:
                print("Error occurred:",e)
                
        elif choice == 4: #Banning a particular user
            try:    
                name = input("Enter the name of the user: ")
                email = input("Enter the email of the user: ")
                user_ref=db.collection('Users')
                query=user_ref.where(filter=FieldFilter('email','==',email)).stream()
                found=False
                for user in query:
                    found=True
                    user_ref.document(user.id).delete()
                    print('User has been banned')
                if not found:
                    print("User does not exist.")
            except Exception as e:
                print("Error occurred:",e)
            
                
        elif choice == 5: #Viewing all users
            try:
                user_ref=db.collection('Users')
                query=user_ref.stream()
                print(f"{'Name':<20} | {'Email':<30} | {'Employee Status':<10}")
                print("-" * 66)
                for user in query:
                    data=user.to_dict()
                    print(f"{data.get('name'):<20} | {data.get('email'):<30} | {data.get('isEmployee'):<10}") #type: ignore
            except Exception as e:
                print("Error occurred:",e)

        elif choice==6: #Viewing all items
            try:
                items_ref = db.collection('Items')
                docs = items_ref.stream()
                print(f"{'Name':<20} | {'Price':<10} | {'Quantity':<10}")
                print("-" * 46)
                has_items = False
                for doc in docs:
                    has_items = True
                    data = doc.to_dict()
                    name = data.get('name', 'N/A') #type: ignore
                    price = data.get('price', 0.0)#type: ignore
                    quantity = data.get('qty', 0)  #type: ignore
                    print(f"{name:<20} | ${price:<9.2f} | {quantity:<10}")
                if not has_items:
                    print("No items found in the collection.")
            except Exception as e:
                print("Error fetching items:", e)
        elif choice == 0:
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
else: #Customer actions
    #Checks if customer has a saved cart
    user_ref=db.collection('Carts')
    query=user_ref.where(filter=FieldFilter('user','==',email)).stream()
    found=False
    for cart in query:
        found=True
        data = cart.to_dict()
        print("Welcome back! Cart has been retrieved")
    
    #If not, creates a new cart and adds it to the database
    if not found:
        cart_user=Cart(user)
        addCart(user)
    #If saved cart if found, retrieves its data and creates a Cart object with specified data
    else:
        a={}
        for i in data.get('cart'): #type: ignore
            item_ref=db.collection('Items')
            query=item_ref.where(filter=FieldFilter('name','==',i)).stream()
            found=False
            for j in query:
                found = True
                data1 = j.to_dict()
                item = Item(i,data1.get('price'),data.get('cart').get(i)) #type: ignore
                a[item]=data.get('cart').get(i) #type: ignore
        cart_user=Cart(user,a,data.get('cart')) #type: ignore
    
    while True:
        print('''\nOptions:
1) View items in cart
2) View all items in shop
3) Add to cart
4) Remove from cart
5) Clear cart
6) Get total
7) Checkout
0) Exit
''')
        # Customer Operations
        try:
            choice = int(input("Enter your choice: "))
        except:
            print('Invalid Input!')
        if choice == 1: # Views the cart
            print("Items in cart:")
            for item, quantity in cart_user.cart.items():
                print(f"{item.name} : {quantity}")
        elif choice == 2: #Views all items in shop
            try:
                #Retrieves items from database
                items_ref = db.collection('Items')
                docs = items_ref.stream()
                print(f"{'Name':<30} | {'Price':<20} | {'Quantity':<10}")
                print("-" * 46)
                has_items = False
                for doc in docs:
                    has_items = True
                    data = doc.to_dict()
                    name = data.get('name', 'N/A') #type: ignore
                    price = data.get('price', 0.0)#type: ignore
                    quantity = data.get('qty', 0)  #type: ignore
                    #Displays all items
                    print(f"{name:<30} | ${price:<20.2f} | {quantity:<10}")
            
                if not has_items:
                    print("Sold out.... Come back later!")
            
            except Exception as e:
                print("Error fetching items:", e)
        
        elif choice == 3: #Adds item to cart
            try:
                name = input("Enter the name of the item: ")
                quantity = int(input("Enter the quantity of the item: "))
                if quantity<0:
                    raise ValueError('Quantity cannot be negative')
                item_ref=db.collection('Items')
                query=item_ref.where(filter=FieldFilter('name','==',name)).stream()
                found=False
                #Checks if item exists
                for i in query: 
                    found = True
                    data = i.to_dict()
                    item = Item(name,data.get('price'),data.get('qty')) #type: ignore
                if not found:
                    print("Item not found")
                else:
                    cart_user.addtocart(item,quantity)
                    
            except Exception as e:
                print("Error occurred:",e)

        elif choice == 4: #Removes item from cart
            try:
                name = input("Enter the name of the item: ")
                quantity = int(input("Enter the number of items to remove: "))
                if quantity<0:
                    raise ValueError('Quantity cannot be negative')
                item_ref=db.collection('Items')
                query=item_ref.where(filter=FieldFilter('name','==',name)).stream()
                #Checking if item exists
                found=False
                for i in query:
                    found = True
                    data = i.to_dict()
                    item = Item(name,data.get('price'),data.get('qty')) #type: ignore
                if not found: #Checks if item in cart
                    print("Item not found")
                if name in cart_user.iteminf: 
                    cart_user.removefromCart(quantity,item)
                    print('Item removed succesfully')
                else:
                    print("Item not in cart.")
            except Exception as e:
                print("Error occurred:",e)
                
        elif choice == 5: # Clears the cart
            print("Clearing carts...")
            cart_user.clearCart()

        elif choice == 6: # Gives the total
            cart_user.getTotal()
        
        elif choice == 7: # Checkout
            try:
                print("Checking out...")
                total = 0
                print("Your receipt:")
                print()
                for item, quantity in cart_user.cart.items(): # Computes total and prints price of each item
                    total += item.price * quantity
                    print(f"{item.name} : {quantity} x ${item.price:.2f} = ${item.price * quantity:.2f}")
                    item.change_qty(item,item.qty - quantity)

                cart_user.clearCart() 
                print(f"Your total is ${total:.2f}. Thank you for shopping with us!")
            except Exception as e:
                print("Error occurred:",e)
        elif choice == 0:
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")
#Copyright
print("© Vobjt Bobt Productions est. 2026")