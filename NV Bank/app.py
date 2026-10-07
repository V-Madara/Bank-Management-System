import streamlit as st
import json
import uuid
import hashlib
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = Path("database.json")


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def hash_pin(pin: str) -> str:
    """
    Convert PIN into a SHA-256 hash.
    We don't store the actual PIN in the database.
    """
    return hashlib.sha256(pin.encode()).hexdigest()


def generate_account_number():
    """
    Generate a unique 10-digit account number.
    """
    while True:
        account_number = str(uuid.uuid4().int % 10**10).zfill(10)

        if not any(
            user["accountNumber"] == account_number
            for user in Bank.users
        ):
            return account_number


def load_database():
    """
    Load users from JSON database.
    """
    if not DATABASE.exists():
        return []

    try:
        with open(DATABASE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_database():
    """
    Save users to JSON database.
    """
    try:
        with open(DATABASE, "w") as file:
            json.dump(Bank.users, file, indent=4)

    except OSError as e:
        st.error(f"Unable to save database: {e}")


# ============================================================
# BANK CLASS
# ============================================================

class Bank:

    users = load_database()

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    @staticmethod
    def find_user(account_number, pin):
        """
        Find user using account number and PIN.
        """

        hashed_pin = hash_pin(pin)

        for user in Bank.users:

            if (
                user["accountNumber"] == account_number
                and user["pin"] == hashed_pin
            ):
                return user

        return None

    # --------------------------------------------------------
    # FIND ACCOUNT
    # --------------------------------------------------------

    @staticmethod
    def find_account(account_number):

        for user in Bank.users:

            if user["accountNumber"] == account_number:
                return user

        return None

    # --------------------------------------------------------
    # CREATE ACCOUNT
    # --------------------------------------------------------

    @staticmethod
    def create_account(
        name,
        age,
        phone,
        email,
        account_type,
        pin
    ):

        # -------------------------
        # Validation
        # -------------------------

        name = name.strip()
        phone = phone.strip()
        email = email.strip().lower()

        if not name:
            return False, "Name cannot be empty."

        if age < 18:
            return False, "You must be at least 18 years old."

        if not phone.isdigit() or len(phone) != 10:
            return False, "Phone number must contain exactly 10 digits."

        if not email.endswith("@gmail.com"):
            return False, "Please enter a valid Gmail address."

        if not pin.isdigit() or len(pin) != 4:
            return False, "PIN must contain exactly 4 digits."

        # Check duplicate email

        if any(user["email"] == email for user in Bank.users):
            return False, "An account with this email already exists."

        # Check duplicate phone

        if any(user["phoneNo"] == phone for user in Bank.users):
            return False, "An account with this phone number already exists."

        # -------------------------
        # Create account
        # -------------------------

        account = {
            "name": name,
            "age": age,
            "phoneNo": phone,
            "email": email,
            "typeAC": account_type,
            "accountNumber": generate_account_number(),
            "pin": hash_pin(pin),
            "balance": 0,
            "transactions": []
        }

        Bank.users.append(account)

        save_database()

        return True, account

    # --------------------------------------------------------
    # DEPOSIT
    # --------------------------------------------------------

    @staticmethod
    def deposit(user, amount):

        if amount <= 0:
            return False, "Deposit amount must be greater than zero."

        user["balance"] += amount

        user["transactions"].append({
            "type": "Deposit",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        save_database()

        return True, user["balance"]

    # --------------------------------------------------------
    # WITHDRAW
    # --------------------------------------------------------

    @staticmethod
    def withdraw(user, amount):

        if amount <= 0:
            return False, "Withdrawal amount must be greater than zero."

        if amount > user["balance"]:
            return False, "Insufficient balance."

        user["balance"] -= amount

        user["transactions"].append({
            "type": "Withdrawal",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        save_database()

        return True, user["balance"]

    # --------------------------------------------------------
    # UPDATE USER
    # --------------------------------------------------------

    @staticmethod
    def update_user(user, name, age, phone, email, account_type):

        if not name.strip():
            return False, "Name cannot be empty."

        if age < 18:
            return False, "Age must be at least 18."

        if not phone.isdigit() or len(phone) != 10:
            return False, "Phone number must contain 10 digits."

        if not email.endswith("@gmail.com"):
            return False, "Please enter a valid Gmail address."

        user["name"] = name.strip()
        user["age"] = age
        user["phoneNo"] = phone
        user["email"] = email.lower()
        user["typeAC"] = account_type

        save_database()

        return True, "Details updated successfully."

    # --------------------------------------------------------
    # CHANGE PIN
    # --------------------------------------------------------

    @staticmethod
    def change_pin(user, new_pin):

        if not new_pin.isdigit() or len(new_pin) != 4:
            return False, "PIN must contain exactly 4 digits."

        user["pin"] = hash_pin(new_pin)

        save_database()

        return True, "PIN changed successfully."

    # --------------------------------------------------------
    # DELETE ACCOUNT
    # --------------------------------------------------------

    @staticmethod
    def delete_account(user):

        Bank.users.remove(user)

        save_database()

        return True


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏦 Bank Management System")

if st.session_state.logged_in:

    st.sidebar.success(
        f"Welcome, {st.session_state.user['name']}"
    )

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Deposit",
            "Withdraw",
            "Account Details",
            "Update Details",
            "Transactions",
            "Delete Account"
        ]
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user = None

        st.rerun()

else:

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Login",
            "Create Account"
        ]
    )


# ============================================================
# TITLE
# ============================================================

st.title("🏦 Bank Management System")

st.caption(
    "A simple banking application built using Python + Streamlit"
)


# ============================================================
# CREATE ACCOUNT
# ============================================================

if menu == "Create Account":

    st.header("📝 Create New Account")

    with st.form("create_account_form"):

        name = st.text_input("Full Name")

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=18
        )

        phone = st.text_input(
            "Phone Number",
            max_chars=10
        )

        email = st.text_input("Email")

        account_type = st.selectbox(
            "Account Type",
            [
                "Saving Account",
                "Current Account"
            ]
        )

        pin = st.text_input(
            "4 Digit PIN",
            type="password",
            max_chars=4
        )

        submitted = st.form_submit_button(
            "Create Account"
        )

    if submitted:

        success, result = Bank.create_account(
            name,
            age,
            phone,
            email,
            account_type,
            pin
        )

        if success:

            st.success(
                "🎉 Account created successfully!"
            )

            st.info(
                f"Your Account Number is: **{result['accountNumber']}**"
            )

            st.warning(
                "Please save your account number safely."
            )

        else:

            st.error(result)


# ============================================================
# LOGIN
# ============================================================

elif menu == "Login":

    st.header("🔐 Login")

    with st.form("login_form"):

        account_number = st.text_input(
            "Account Number"
        )

        pin = st.text_input(
            "PIN",
            type="password"
        )

        login = st.form_submit_button(
            "Login"
        )

    if login:

        user = Bank.find_user(
            account_number.strip(),
            pin
        )

        if user:

            st.session_state.logged_in = True
            st.session_state.user = user

            st.success("Login successful!")

            st.rerun()

        else:

            st.error(
                "Invalid account number or PIN."
            )


# ============================================================
# LOGGED-IN FEATURES
# ============================================================

elif st.session_state.logged_in:

    user = st.session_state.user

    # ========================================================
    # DASHBOARD
    # ========================================================

    if menu == "Dashboard":

        st.header("📊 Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Account Holder",
                user["name"]
            )

        with col2:

            st.metric(
                "Account Type",
                user["typeAC"]
            )

        with col3:

            st.metric(
                "Balance",
                f"₹ {user['balance']:,.2f}"
            )

        st.divider()

        st.subheader("Account Number")

        st.code(
            user["accountNumber"]
        )

        st.info(
            "Use the sidebar to deposit, withdraw, "
            "update details or view transactions."
        )

    # ========================================================
    # DEPOSIT
    # ========================================================

    elif menu == "Deposit":

        st.header("💰 Deposit Money")

        with st.form("deposit_form"):

            amount = st.number_input(
                "Enter amount",
                min_value=1.0,
                step=100.0
            )

            submit = st.form_submit_button(
                "Deposit"
            )

        if submit:

            success, result = Bank.deposit(
                user,
                amount
            )

            if success:

                st.success(
                    f"₹{amount:,.2f} deposited successfully."
                )

                st.metric(
                    "New Balance",
                    f"₹ {result:,.2f}"
                )

            else:

                st.error(result)

    # ========================================================
    # WITHDRAW
    # ========================================================

    elif menu == "Withdraw":

        st.header("💸 Withdraw Money")

        st.metric(
            "Available Balance",
            f"₹ {user['balance']:,.2f}"
        )

        with st.form("withdraw_form"):

            amount = st.number_input(
                "Enter amount",
                min_value=1.0,
                step=100.0
            )

            submit = st.form_submit_button(
                "Withdraw"
            )

        if submit:

            success, result = Bank.withdraw(
                user,
                amount
            )

            if success:

                st.success(
                    f"₹{amount:,.2f} withdrawn successfully."
                )

                st.metric(
                    "New Balance",
                    f"₹ {result:,.2f}"
                )

            else:

                st.error(result)

    # ========================================================
    # ACCOUNT DETAILS
    # ========================================================

    elif menu == "Account Details":

        st.header("👤 Account Details")

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Name:** {user['name']}"
            )

            st.write(
                f"**Age:** {user['age']}"
            )

            st.write(
                f"**Phone:** {user['phoneNo']}"
            )

            st.write(
                f"**Email:** {user['email']}"
            )

        with col2:

            st.write(
                f"**Account Type:** {user['typeAC']}"
            )

            st.write(
                f"**Account Number:** "
                f"{user['accountNumber']}"
            )

            st.write(
                f"**Balance:** ₹ "
                f"{user['balance']:,.2f}"
            )

    # ========================================================
    # UPDATE DETAILS
    # ========================================================

    elif menu == "Update Details":

        st.header("✏️ Update Account")

        tab1, tab2 = st.tabs(
            [
                "Personal Details",
                "Change PIN"
            ]
        )

        # ----------------------------------------------------
        # PERSONAL DETAILS
        # ----------------------------------------------------

        with tab1:

            with st.form("update_form"):

                name = st.text_input(
                    "Name",
                    value=user["name"]
                )

                age = st.number_input(
                    "Age",
                    min_value=18,
                    max_value=120,
                    value=user["age"]
                )

                phone = st.text_input(
                    "Phone",
                    value=user["phoneNo"],
                    max_chars=10
                )

                email = st.text_input(
                    "Email",
                    value=user["email"]
                )

                account_type = st.selectbox(
                    "Account Type",
                    [
                        "Saving Account",
                        "Current Account"
                    ],
                    index=0
                    if user["typeAC"] == "Saving Account"
                    else 1
                )

                submit = st.form_submit_button(
                    "Update"
                )

            if submit:

                success, message = Bank.update_user(
                    user,
                    name,
                    age,
                    phone,
                    email,
                    account_type
                )

                if success:

                    st.success(message)

                else:

                    st.error(message)

        # ----------------------------------------------------
        # CHANGE PIN
        # ----------------------------------------------------

        with tab2:

            with st.form("pin_form"):

                new_pin = st.text_input(
                    "New 4 Digit PIN",
                    type="password",
                    max_chars=4
                )

                confirm_pin = st.text_input(
                    "Confirm PIN",
                    type="password",
                    max_chars=4
                )

                submit_pin = st.form_submit_button(
                    "Change PIN"
                )

            if submit_pin:

                if new_pin != confirm_pin:

                    st.error(
                        "PINs do not match."
                    )

                else:

                    success, message = Bank.change_pin(
                        user,
                        new_pin
                    )

                    if success:

                        st.success(message)

                    else:

                        st.error(message)

    # ========================================================
    # TRANSACTIONS
    # ========================================================

    elif menu == "Transactions":

        st.header("📜 Transaction History")

        transactions = user.get(
            "transactions",
            []
        )

        if not transactions:

            st.info(
                "No transactions found."
            )

        else:

            for transaction in reversed(transactions):

                if transaction["type"] == "Deposit":

                    st.success(
                        f"⬆️ **Deposit** — "
                        f"₹{transaction['amount']:,.2f}"
                    )

                else:

                    st.error(
                        f"⬇️ **Withdrawal** — "
                        f"₹{transaction['amount']:,.2f}"
                    )

                st.caption(
                    transaction["date"]
                )

    # ========================================================
    # DELETE ACCOUNT
    # ========================================================

    elif menu == "Delete Account":

        st.header("⚠️ Delete Account")

        st.warning(
            "This action cannot be undone."
        )

        confirmation = st.checkbox(
            "I understand that my account will be permanently deleted."
        )

        if confirmation:

            if st.button(
                "Delete My Account",
                type="primary"
            ):

                Bank.delete_account(user)

                st.session_state.logged_in = False
                st.session_state.user = None

                st.success(
                    "Account deleted successfully."
                )

                st.rerun()