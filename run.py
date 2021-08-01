import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime
from time import sleep

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('coders_bistro')


class Customer:
    "Create a customer"
    def __init__(self, f_name, l_name, email):
        # Instance attibutes
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
        self.balance = []

    def info(self):
        """
        Return the clients full info
        """
        return f'Client: {self.f_name} {self.l_name}.Email: {self.email}.Balance: {self.balance}'

    def full_name(self):
        """
        Return customer name
        """
        return f'{self.f_name} {self.l_name}'


class Admin:
    """
    Create a admin
    """
    def __init__(self, email, password):
        # Instance attributes
        self.email = email
        self.password = password

    def info(self):
        """
        Return admin info
        """
        return f'Email: {self.email} Password: {self.password}'

    def check_sales(self, date):
        """
        Check the sum of the sales from the chosen day
        """
        worksheet = select_worksheet("sales")
        day_col = worksheet.col_values(1)
        sales = worksheet.get_all_values()
        total = 0

        if date not in day_col:
            print(f"We don't have any sale register for {date}")

            return [total, True]
        else:
            for sale in sales:
                if sale[0] == date:
                    num_sheet = sale[1]
                    num = num_sheet.replace(",", ".")
                    total += float(num)

            return [total, True]

    def new_expanse(self):
        """
        Register a new expanse on the worksheet
        """
        today = date.today().strftime("%d-%m-%Y")
        print("How much is the expnase?")
        print("Example: 15.50")
        value = float(input("Enter your answear here:\n"))
        print("Give a small description for your expanse")
        description = input("Enter your answear here:\n")

        data = [today, value, description]
        update_worksheet(data, "expenses")

    def check_expenses(self, date):
        """
        Check the sum of the expenses from the chosen day
        """
        worksheet = select_worksheet("expenses")
        day_col = worksheet.col_values(1)
        expenses = worksheet.get_all_values()
        total = 0

        if date not in day_col:
            print(f"We don't have ane expense register for {date}")

            return [total, True]
        else:
            for expense in expenses:
                if expense[0] == date:
                    num_sheet = expense[1]
                    num = num_sheet.replace(",", ".")
                    total += float(num)

            return [total, True]


def is_registred():
    """
    Ask if the user is already registered and return the answear
    """
    while True:
        print("Are you registered (Y / N)?")
        answear = input("Enter your answear here:\n").strip().upper()
        print(" ")
        print("# "*15)
        print(" ")
        if validate_yes_no(answear):
            break

    return answear


def validate_yes_no(answear):
    """
    Validate yes or no questions
    """
    try:
        if answear not in ("Y", "N"):
            raise ValueError('Choose between Y or N')

    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


def collect_data(value):
    """
    Check if the user is really registered.
    If not, register a new client.
    """
    data = []

    # Code to run if the user is already registered
    if value == "Y":
        print("Good to have you back!")
        print("I just need to check your email.")
        client_sheet = select_worksheet("clients")
        email = check_email(client_sheet, 3)
        row = find_row(email, client_sheet)
        data = customer_data(row)

    # Code to run if the user is not registered
    elif value == "N":
        print("First time here!")
        print("Let's make a register for you")
        print("I just need a few information")
        data = new_customer_data()
        update_worksheet(data, "clients")

    return data


def check_email(sheet, col):
    """
    Check if the email is already registered
    """
    worksheet = sheet
    email_collum = worksheet.col_values(col)

    while True:
        print("Can you write it for me?")
        email = input("Enter your answear here:\n").strip()
        print(" ")
        print("# "*15)
        print(" ")

        if validate_email(email):
            if email in email_collum:
                break
            else:
                print("Sorry, I can't find your email.")
                print("Let's try again.\n")

    return email


def validate_email(email):
    """
    Validate if email has a @ sign
    """
    try:
        if "@" not in email:
            raise ValueError("Please enter a valid email")
    except ValueError as e:
        print(f"Invalid data: {e}")
        print("Example: code@codersbistro.com\n")
        return False

    return True


def find_row(item, sheet):
    """
    Find the item's row in the specified worksheet
    """
    worksheet = sheet
    cell = worksheet.find(item)

    return cell.row


def customer_data(row):
    """
    Collect the customer data from the worksheet
    """
    client_sheet = select_worksheet("clients")
    customer_data = client_sheet.row_values(row)

    return [customer_data[0], customer_data[1], customer_data[2]]


def new_customer_data():
    """
    Colect customer data and check if its not already registered
    """
    client_sheet = select_worksheet('clients')
    email_collum = client_sheet.col_values(3)

    f_name = input("What's your first name?\n").capitalize().strip()
    l_name = input("What's your last name?\n").capitalize().strip()

    while True:
        email = input("What's your email?\n").strip()

        if email not in email_collum:
            if validate_email(email):
                break
        else:
            print("Sorry, this email is already in use")
            print("Can we try again?\n")

    print(" ")
    print("# "*15)
    print(" ")

    return [f_name, l_name, email]


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    worksheet_to_update = select_worksheet(worksheet)
    worksheet_to_update.append_row(data)


def create_customer(data):
    """
    Create the customer
    """
    return Customer(data[0], data[1], data[2])


def menu_options():
    """
    Present the menus and return user otpion
    """
    print("Wich menu do you want to check?")
    print("A - Foods menu")
    print("B - Drinks menu")
    print("C - Deserts menu")
    menu_option = input("Enter your answear here:\n").upper().strip()
    print(" ")
    print("# "*15)
    print(" ")

    while menu_option not in ("A", "B", "C"):
        print("Please choose between one of the options")
        menu_option = input("Enter your answear here:\n").upper().strip()

    return menu_option


def display_menu(sheet):
    """
    Print the chosen menu on the screen
    """
    menu_sheet = sheet.get_all_values()

    for item in menu_sheet:
        print(f'{item[0]:<5}{item[1]:_<20}{item[2]:_>20}')


def customer_order(worksheet):
    """
    Collect the customer order
    """
    while True:
        print("What's the ID from the item that you want?")
        id = input("Enter your answear here:\n").strip()
        print(" ")
        print("# "*15)
        print(" ")

        if validate_order(id, worksheet):
            print("Noted!")
            break

    return id


def validate_order(id, worksheet):
    """
    Validate the ID passed from the user
    """
    ids = worksheet.col_values(1)
    try:
        if id not in ids:
            raise ValueError("Choose between one of the printed Ids")
    except ValueError as e:
        print(f"Invalid option: {e}, please try again.\n")
        return False

    return True


def select_worksheet(option):
    """
    From the option, select the needed worksheet
    """
    worksheet = ""

    if option.upper() == "A":
        worksheet = SHEET.worksheet("food_menu")
    elif option.upper() == "B":
        worksheet = SHEET.worksheet("drink_menu")
    elif option.upper() == "C":
        worksheet = SHEET.worksheet("deserts_menu")
    elif option.upper() == "ADMIN":
        worksheet = SHEET.worksheet("admin")
    elif option.upper() == "SALES":
        worksheet = SHEET.worksheet("sales")
    elif option.upper() == "EXPENSES":
        worksheet = SHEET.worksheet("expenses")
    elif option.upper() == "CLIENTS":
        worksheet = SHEET.worksheet("clients")
    else:
        print("Worksheet name problem")

    return worksheet


def item_value(id, sheet):
    """
    Return the value from the chosen item
    """
    row = find_row(id, sheet)
    item_row = sheet.row_values(row)

    return item_row[2]


def add_balance(customer, value):
    """
    Add value on the customer balance
    """
    customer.balance.append(float(value))


def ordering():
    """
    Check if the user wants to keep ordering
    """
    while True:
        answear = input("Enter your answear here:\n").strip().upper()
        print(" ")
        print("# "*15)
        print(" ")

        if validate_yes_no(answear):
            break

    if answear == "Y":
        return True
    elif answear == "N":
        return False


def total(customer):
    """
    Calculate the total for the customer order
    """
    order = customer.balance
    total = 0
    today = date.today().strftime("%d-%m-%Y")

    for value in order:
        total += value
        total = round(total, 2)

    return [today, total]


def customer():
    """
    Code used when it is a customer
    """
    # Welcome message
    print("Welcome to the Coders Bistro\n")

    # Check if the customer need to be register or not
    # Create a customer from the collected data
    register = is_registred()
    customer_data = collect_data(register)
    customer = create_customer(customer_data)
    print("All done!")
    print(f'Welcome {customer.full_name()}')

    # While loop to print the menu on the screen and collect the customer order
    # Item' value added to the customer balance
    print("Would you like to check our menu? (Y / N)")
    while ordering():
        menu_option = menu_options()
        menu_sheet = select_worksheet(menu_option)
        display_menu(menu_sheet)
        id = customer_order(menu_sheet)
        value = item_value(id, menu_sheet)
        add_balance(customer, value)
        print("Anything else? (Y / N)")

    # Add the order on the sales worksheet
    total_order = total(customer)
    update_worksheet(total_order, "sales")

    # Farewell message
    print("Thanks for eating with us!")
    print(f"The total of your order is ${total_order[1]}.")
    print(f'A copy of your order was send for {customer.email}')


def adm_user():
    """
    Ask if the user wants to log in as customer or admin
    """
    print("Do you want to log in as:")
    print("1 - Admin")
    print("2 - Customer")
    answear = input("Enter your answear here:\n").strip()
    print(" ")
    print("# "*15)
    print(" ")
    while answear not in ("1", "2"):
        print("Please choose between one of the otpions.")
        answear = input("Enter your answear here:\n").strip()

    return answear


def run_system(option):
    """
    Run the code based on the given option
    """
    # Admin code
    if option == "1":
        adm()
    # Customer code
    elif option == "2":
        customer()


def adm():
    """
    Code to use when it is admin
    """
    email_password = adm_email_password()
    admin = Admin(email_password[0], email_password[1])

    print("Do you want to check your options?(Y / N)")
    while working():
        option = adm_options()
        adm_functions(admin, option)
        print("Do you want to check anything else?(Y / N)")

    print("System ended.")


def adm_email_password():
    """
    Collect validate admin's email and password
    """
    worksheet = select_worksheet("admin")
    print("First I need to check your email.")
    email = check_email(worksheet, 1)
    print("Now your password.")
    password = check_password(worksheet, 2)

    print("Validating data...")
    sleep(2)
    print("All good!")
    print(" ")
    print("# "*15)
    print(" ")

    return [email, password]


def check_password(sheet, col):
    """
    Check if the password is valid
    """
    worksheet = sheet
    password_collum = worksheet.col_values(col)

    while True:
        print("Can you write it for me?")
        password = input("Enter your answear here:\n").strip()
        print(" ")
        print("# "*15)
        print(" ")

        if password in password_collum:
            break
        else:
            print("Wrong password.")
            print("Let's try again?\n")

    return password


def adm_options():
    """
    Displays admin options
    """
    print("What do you want to do today?")
    print("A - Check your Sales")
    print("B - Update Expanses")
    print("C - Check Expanses")
    print("D - Check your Total")
    option = input("Enter your answear here:\n").strip().upper()

    while option not in ("A", "B", "C", "D"):
        print("Choose between one of the otpions.")
        option = input("Enter your answear here:\n").strip().upper()

    print(" ")
    print("# "*15)
    print(" ")

    return option


def adm_functions(adm, option):
    """
    From the admin option, execute the code
    """
    # Check the sales' total
    if option == 'A':
        while True:
            print("Wich day do you want to check?")
            print("Ex: 30-07-2021")
            date = input("Enter your answear here:\n").strip()
            total_sales = adm.check_sales(date)

            if total_sales[1]:
                break

        print(f"The sales' total in {date} is ${total_sales[0]}")

    # Create a new expanse
    elif option == "B":
        adm.new_expanse()

    # Check the expanses' total
    elif option == 'C':
        while True:
            print("Wich day do you want to check?")
            print("Ex: 30-07-2021")
            date = input("Enter your answear here:\n").strip()
            total_expenses = adm.check_expenses(date)

            if total_expenses[1]:
                break

        print_expenses(date)
        print(f"The expenses' total in {date} is ${total_expenses[0]}")

    # Display the day balance
    elif option == "D":
        print(day_balance(adm))


def print_expenses(date):
    """
    From the worksheet, display the expanses
    """
    worksheet = select_worksheet("expenses")
    expenses = worksheet.get_all_values()

    header = expenses[0]
    print(f'{header[0]:<15}{header[1]:<10}{header[2]:<20}')

    for expense in expenses:
        if expense[0] == date:
            print(f'{expense[0]:<15}${expense[1]:<9}{expense[2]:<20}')


def day_balance(adm):
    """
    Print the total balance from the chosen day
    """
    print("Wich day do you want to check?")
    print("Ex: 30-07-2021")
    date = input("Enter your answear here:\n").strip()

    sales = adm.check_sales(date)[0]
    expenses = adm.check_expenses(date)[0]

    total = sales - expenses

    return f'In {date} you sold ${sales} and spent ${expenses}. Your total is ${total}.'


def working():
    """
    Check if the admin want to keep working
    """
    while True:
        answear = input("Enter your answear here:\n").strip().upper()
        print(" ")
        print("# "*15)
        print(" ")

        if validate_yes_no(answear):
            break

    if answear == "Y":
        return True
    elif answear == "N":
        return False


def main():
    """
    Run the main code
    """
    option = adm_user()
    run_system(option)


print("LOADING SYSTEM...")
sleep(2)
print(" ")
print("# "*15)
print(" ")
main()
