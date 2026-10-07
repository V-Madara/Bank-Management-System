import uuid

from pathlib import Path
import json


class Bank:
    database = 'databse.json'
    users = []
    try:
        if Path.exists(database):
            with open(database) as jf:
                users = json.loads(jf.read())
        else:
            print("Path does not exist")
    except Exception as e:
        print("An Exception occured:-> ",e)
    


    def createAccount(self):
        print("1. Saving acccount")
        print("2. Current account")
        self.typ = int(input("Enter your choice:-> "))
        self.typeAC = "Saving Account" if self.typ == 1 else "Current Account"
        data = {
        "name" : input("Enter your name:-> "),
        "age" : int(input("Enter your age:-> ")),
        "phoneNo" : input("Enter your phone number:-> "),
        "email" : input("Enter your email:-> "),
        "typeAC" :self.typeAC,
        "accountNumber" : uuid.uuid4().int % 10 ** 4,
        "pin" : int(input("Enter your pin:-> ")),
        "balance" : 0
        }
        if (data['age']<18) or (len(str(data['pin']))<4 or not(data["email"].endswith("@gmail.com")) or len(str(data['phoneNo']))<10 ):
            print("Invalid Try Again")
        else:
            print("Acccout has been created")
            print("----X-------------X----------X----------")
            print()
            for i in data:
                print(f"{i} :-> {data[i]}")

            print("Please save your account number carefully")
            print()
            print("----X-------------X----------X----------")

            Bank.users.append(data)
            Bank.update()

    @staticmethod
    def update():
        with open(Bank.database,'w') as jf:
            jf.write(json.dumps(Bank.users))

    def deposite(self,accno,pinno):
        userdata = [user for user in Bank.users if user['accountNumber'] == accno and user['pin'] == pinno]
        print("----X---------------X------------------X-----------------X----")
        if len(userdata) == 0: print("Data Not Fount! ")
        else:
            print(f" Name :-> {userdata[0]['name']}")
            print(f" Current Balance :-> {userdata[0]['balance']}")
            amount = int(input("Enter your amount to be deposited:-> "))
            userdata[0]['balance'] += amount
            print(f" New Balance :-> {userdata[0]['balance']}")
            print("----X---------------X------------------X-----------------X----")


            Bank.update()


    def withdrawl(self,accno,pinno):
        userdata = [user for user in Bank.users if user['accountNumber'] == accno and user['pin'] == pinno]
        print("----X---------------X------------------X-----------------X----")
        if len(userdata) == 0: print("Data Not Fount! ")
        else:
            print(f" Name :-> {userdata[0]['name']}")
            print(f" Current Balance :-> {userdata[0]['balance']}")
            amount = int(input("Enter your amount to be withdrawl:-> "))
            if amount > userdata[0]['balance']:
                print("Insufficient Balance")
                return
            else:
                userdata[0]['balance'] -= amount
                print(f" New Balance :-> {userdata[0]['balance']}")
            print("----X---------------X------------------X-----------------X----")
            Bank.update()

    def checkBalance(self,accno,pinno):
        userdata = [user for user in Bank.users if user['accountNumber'] == accno and user['pin'] == pinno]
        print("----X---------------X------------------X-----------------X----")
        if len(userdata) == 0: print("Data Not Fount! ")
        else:
            print(f" Name :-> {userdata[0]['name']}")
            print(f" Current Balance :-> {userdata[0]['balance']}")
            print("----X---------------X------------------X-----------------X----")

    def printDetails(self,accno,pinno):
        userdata = [user for user in Bank.users if user['accountNumber'] == accno and user['pin'] == pinno]
        print("----X---------------X------------------X-----------------X----")
        if len(userdata) == 0: print("Data Not Fount! ")
        else:
            print(f" Name :-> {userdata[0]['name']}")
            print(f" Age :-> {userdata[0]['age']}")
            print(f" Type of Account :-> {userdata[0]['typeAC']}")
            print(f" Phone Number :-> {userdata[0]['phoneNo']}")
            print(f" Email :-> {userdata[0]['email']}")
            print(f" Account Number :-> {userdata[0]['accountNumber']}")
            print(f" Pin Number :-> **{userdata[0]['pin']%100}")
            print(f" Current Balance :-> {userdata[0]['balance']}")
        print("----X---------------X------------------X-----------------X----")

    def change(self,accno,pinno):
        userdata = [user for user in Bank.users if user['accountNumber'] == accno and user['pin'] == pinno]
        if len(userdata) == 0: print("Data Not Fount! ")
        else:
            Bank.printDetails(accno,pinno)
            chs = int(input("Enter what you want to Update:-> "))
            if chs == 1: userdata[0]['name'] = input("Enter new name:-> ")
            elif chs == 2: userdata[0]['age'] = input("Enter new age:-> ")
            elif chs == 3:
                if userdata[0]['typeAC'] == "Saving Account" :
                    userdata[0]['typeAC'] = "Current Account"
                else: userdata[0]['typeAC'] = "Saving Account"
            elif chs ==4: userdata[0]['phone'] = int(input("Enter new phone number:-> "))
            elif chs ==5: userdata[0]['email'] = input("Enter new email:-> ")
            elif chs ==6: userdata[0]['pin'] = int(input("Enter new pin number:-> "))
            else: print("Invalid Choice!")

        Bank.update()

    def delete(self,accno,pinno):
        userdata = [user for user in Bank.users if user['accountNumber'] == accno and user['pin'] == pinno]
        if len(userdata) == 0: print("Data Not Fount! ")
        else:
            idx = Bank.users.index(userdata[0])
            Bank.users.pop(idx)
            Bank.update()


print("1. Create account ")
print("2. Deposit  ")
print("3. Withdraw ")
print("4. Check balance ")
print("5. Check details ")
print("6. Update details ")
print("7. Delete account")
choice = int(input("Enter your choice: "))


obj = Bank()
accno = int(input("Enter your account number:-> "))
pinno = int(input("Enter your pin number:-> "))
if choice == 1:
    obj.createAccount()
elif choice == 2:
    obj.deposite(accno,pinno)
elif choice == 3:
    obj.withdrawl(accno,pinno)
elif choice == 4:
    obj.checkBalance(accno,pinno)
elif choice == 5:
    obj.printDetails(accno,pinno)
elif choice == 6:
    obj.change(accno,pinno)
elif choice ==7:
    obj.delete(accno,pinno)

