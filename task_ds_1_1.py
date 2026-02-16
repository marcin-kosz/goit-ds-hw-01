from collections import UserDict
from datetime import datetime, date, timedelta
import pickle 

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}"
        except KeyError:
            return "Error: contact not found"
        except IndexError:
            return "Error: missing arguments"
    return wrapper

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower() if parts else ""
    args = parts[1:]
    return command, args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = Phone(new_phone).value
                return
        raise ValueError("Phone not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return self.birthday.value if self.birthday else None

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.show_birthday() or "No birthday"
        return f"{self.name.value}: {phones}, birthday: {birthday}"

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name not in self.data:
            raise KeyError
        return self.data[name]

    def delete(self, name):
        if name not in self.data:
            raise KeyError
        del self.data[name]

    @staticmethod
    def find_next_weekday(start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7):
        result = []
        today = date.today()

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday_date = datetime.strptime(
                record.birthday.value, "%d.%m.%Y"
            ).date()

            birthday_this_year = birthday_date.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date = self.adjust_for_weekend(birthday_this_year)
                result.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })

        return result

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

@input_error
def add_contact(args, book):
    name, phone = args
    try:
        record = book.find(name)
        record.add_phone(phone)
        return "Contact updated."
    except KeyError:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    phones = "; ".join(p.value for p in record.phones)
    return phones or "No phones"


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    return record.show_birthday() or "No birthday"


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays"
    return "\n".join(f"{item['name']}: {item['congratulation_date']}" for item in upcoming)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter command: ")
        command, args = parse_input(user_input)

        if command in ("exit", "close"):
            save_data(book)
            print("Good bye!")
            break
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Unknown command")


if __name__ == "__main__":
    main()