from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import pickle
import re
from collections import UserDict


class UserInterface(ABC):
    @abstractmethod
    def display_message(self, message):
        """Wyświetla wiadomość dla użytkownika."""
        pass

    @abstractmethod
    def get_input(self, prompt):
        """Pobiera dane wejściowe od użytkownika."""
        pass

    @abstractmethod
    def display_contacts(self, contacts):
        """Wyświetla listę kontaktów."""
        pass

    @abstractmethod
    def display_notes(self, notes):
        """Wyświetla listę notatek."""
        pass


class ConsoleInterface(UserInterface):
    def display_message(self, message):
        print(message)

    def get_input(self, prompt):
        return input(prompt)

    def display_contacts(self, contacts):
        print("Kontakty:")
        for contact in contacts:
            print(contact)

    def display_notes(self, notes):
        if not notes:
            print("Brak notatek do wyświetlenia.")
            return
        for idx, note in enumerate(notes, start=1):
            print(f"""ID: {idx} Tytuł: {note.get('title', 'Brak tytułu')}
    Treść: {note.get('content', 'Brak treści')}
    Tagi: {', '.join(note.get('tags', []))}""")


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not PhoneValidator.validate(value):
            raise ValueError("Niepoprawny numer telefonu")
        self.value = value


class PhoneValidator:
    @staticmethod
    def validate(phone_number):
        pattern = re.compile(r"^\d{9}$")
        return pattern.match(phone_number) is not None


class Email(Field):
    def __init__(self, value):
        if not EmailValidator.validate(value):
            raise ValueError("Niepoprawny adres email")
        self.value = value


class EmailValidator:
    @staticmethod
    def validate(email):
        pattern = re.compile(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        return pattern.match(email) is not None


class Birthday(Field):
    def __init__(self, value):
        if not BirthdayValidator.validate(value):
            raise ValueError("Niepoprawna data urodzenia")
        self.value = value


class BirthdayValidator:
    @staticmethod
    def validate(birthday):
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class Address(Field):
    def __init__(self, street, city, postal_code, country):
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        super().__init__(value=f"{street}, {city}, {postal_code}, {country}")


class Record:
    def __init__(self, name: Name, birthday: Birthday = None):
        self.id = None  # The ID will be assigned by AddressBook
        self.name = name
        self.phones = []
        self.emails = []
        self.birthday = birthday
        self.address = None  # Add a new property to store the address

    def add_address(self, address: Address):
        self.address = address

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        self.phones.remove(phone)

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_email(self, email: Email):
        self.emails.append(email)

    def remove_email(self, email: Email):
        self.emails.remove(email)

    def edit_email(self, old_email: Email, new_email: Email):
        self.remove_email(old_email)
        self.add_email(new_email)

    def edit_name(self, new_name: Name):
        self.name = new_name

    def days_to_birthday(self):
        if not self.birthday or not self.birthday.value:
            return "Brak daty urodzenia"
        today = datetime.now()
        bday = datetime.strptime(self.birthday.value, "%Y-%m-%d")
        next_birthday = bday.replace(year=today.year)
        if today > next_birthday:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones = ', '.join(phone.value for phone in self.phones)
        emails = ', '.join(email.value for email in self.emails)
        birthday_str = f", Urodziny: {self.birthday.value}" if self.birthday else ""
        days_to_bday_str = f", Dni do urodzin: {self.days_to_birthday()}" if self.birthday else ""
        address_str = f"\nAdres: {self.address.value}" if self.address else ""
        return (f"ID: {self.id}, Imię i nazwisko: {self.name.value}, "
                f"Telefony: {phones}, Email: {emails}"
                f"{birthday_str}{days_to_bday_str}{address_str}")


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.next_id = 1
        self.free_ids = set()

    def add_record(self, record: Record):
        """Dodaje wpis do książki adresowej z zarządzaniem ID."""
        record.id = self._get_next_record_id()
        self.data[record.id] = record
        print(f"Dodano wpis z ID: {record.id}.")

    def _get_next_record_id(self):
        """Pomocnicza metoda do uzyskania kolejnego ID."""
        while self.next_id in self.data or self.next_id in self.free_ids:
            self.next_id += 1
        return self.free_ids.pop() if self.free_ids else self.next_id

    def delete_record_by_id(self):
        user_input = input("Podaj ID rekordu, który chcesz usunąć: ").strip()
        record_id_str = user_input.replace("ID: ", "").strip()

        try:
            record_id = int(record_id_str)
            if record_id in self.data:
                del self.data[record_id]
                self.free_ids.add(record_id)
                print(f"Usunięto rekord o ID: {record_id}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")

    def find_record(self, search_term):
        found_records = []
        for record in self.data.values():
            if search_term.lower() in record.name.value.lower():
                found_records.append(record)
                continue
            for phone in record.phones:
                if search_term in phone.value:
                    found_records.append(record)
                    break
            for email in record.emails:
                if search_term in email.value:
                    found_records.append(record)
                    break
        return found_records

    def find_records_by_name(self, name):
        matching_records = []
        for record_id, record in self.data.items():
            if name.lower() in record.name.value.lower():
                matching_records.append((record_id, record))
        return matching_records

    def delete_record(self):
        name_to_delete = input(
            "Podaj imię i nazwisko osoby, którą chcesz usunąć: ")
        matching_records = self.find_records_by_name(name_to_delete)

        if not matching_records:
            print("Nie znaleziono pasujących rekordów.")
            return

        print("Znaleziono następujące pasujące rekordy:")
        for record_id, record in matching_records:
            print(f"{record}")

        try:
            record_id_to_delete = int(
                input("Podaj ID rekordu, który chcesz usunąć: "))
            if record_id_to_delete in self.data:
                del self.data[record_id_to_delete]
                # Add the ID back to the free ID pool
                self.free_ids.add(record_id_to_delete)
                print(f"Usunięto rekord o ID: {record_id_to_delete}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")

    def __iter__(self):
        self.current = 0
        return self

    def __next__(self):
        if self.current < len(self.data):
            records = list(self.data.values())[self.current:self.current+5]
            self.current += 5
            return records
        else:
            raise StopIteration

    def edit_record(self):

        name_to_edit = input(
            "Podaj imię i nazwisko osoby, którą chcesz edytować: ")
        matching_records = self.find_records_by_name(name_to_edit)

        if not matching_records:
            print("Nie znaleziono pasujących rekordów.")
            return

        print("Znaleziono następujące pasujące rekordy:")
        for record_id, record in matching_records:
            print(f"{record}")

        record_id_to_edit_input = input(
            "Podaj ID rekordu, który chcesz edytować: ")
        if record_id_to_edit_input.strip() == '':
            print("Anulowano edycję rekordu.")
            return

        try:
            record_id_to_edit = int(record_id_to_edit_input)
            if record_id_to_edit not in self.data:
                print("Nie znaleziono rekordu o podanym ID.")
                return
            record = self.data[record_id_to_edit]
        except ValueError:
            print("Nieprawidłowa wartość. Proszę podać liczbę.")
            return

        # Edycja imienia i nazwiska
        new_name_input = input(
            'Podaj nowe imię i nazwisko (lub wciśnij Enter, aby pominąć): ')
        if new_name_input:
            record.name = Name(new_name_input)

        # Edycja numeru telefonu
        if record.phones:
            print("Obecne numery telefonów:")
            for idx, phone in enumerate(record.phones, 1):
                print(f"{idx}. {phone.value}")
            phone_choice = input(
                "Wybierz numer do edycji (lub wciśnij Enter, aby pominąć): ")
            if phone_choice.isdigit():
                phone_index = int(phone_choice) - 1
                if 0 <= phone_index < len(record.phones):
                    new_phone_value = input("Podaj nowy numer telefonu: ")
                    if PhoneValidator.validate(new_phone_value):
                        record.phones[phone_index] = Phone(new_phone_value)
                    else:
                        print("Niepoprawny format numeru telefonu.")
                else:
                    print("Nieprawidłowy wybór numeru telefonu.")
            else:
                print("Pominięto edycję numeru telefonu.")

        # Edycja adresu email
        if record.emails:
            # Wyświetlenie obecnych adresów email
            print("Obecne adresy email:")
            for idx, email in enumerate(record.emails, 1):
                print(f"{idx}. {email.value}")
            email_choice = input(
                "Wybierz adres email do edycji (lub wciśnij Enter, aby pominąć): ")
            if email_choice.isdigit():
                email_index = int(email_choice) - 1
                if 0 <= email_index < len(record.emails):
                    new_email_value = input("Podaj nowy adres email: ")
                    if EmailValidator.validate(new_email_value):
                        record.emails[email_index] = Email(new_email_value)
                    else:
                        print("Niepoprawny format adresu email.")
                else:
                    print("Nieprawidłowy wybór adresu email.")
            else:
                print("Pominięto edycję adresu email.")

        new_birthday_input = input(
            "Podaj nową datę urodzenia (YYYY-MM-DD) lub wciśnij Enter, aby pominąć: ")
        if new_birthday_input:
            if BirthdayValidator.validate(new_birthday_input):
                record.birthday = Birthday(new_birthday_input)
            else:
                print("Niepoprawny format daty urodzenia.")

        print("Wpis zaktualizowany.")


def save_address_book(book, filename='address_book.pkl'):
    try:
        with open(filename, 'wb') as file:
            pickle.dump(book.data, file)
        print("Zapisano książkę adresową.")
    except Exception as e:
        print(f"Błąd przy zapisie książki adresowej: {e}")


def load_address_book(filename='address_book.pkl'):
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            book = AddressBook()
            book.data = data
            print("Książka adresowa została wczytana.")
            return book
    except FileNotFoundError:
        print("Plik nie istnieje. Tworzenie nowej książki adresowej.")
        return AddressBook()
    except Exception as e:
        print(f"Nie udało się wczytać książki adresowej: {e}")
        return AddressBook()


def input_phone():

    while True:
        try:
            number = input(
                "Podaj numer telefonu w formacie '123456789' (naciśnij Enter, aby pominąć): ")
            if not number:
                return None
            return Phone(number)
        except ValueError as e:
            print(e)


def input_email():

    while True:
        try:
            address = input(
                "Podaj adres email (naciśnij Enter, aby pominąć): ")
            if not address:
                return None
            return Email(address)
        except ValueError as e:
            print(e)


def create_record():

    name_input = input("Podaj imię i nazwisko: ")
    name = Name(name_input)

    birthday = None
    while True:
        birthday_input = input(
            "Podaj datę urodzenia (YYYY-MM-DD) lub wciśnij Enter, aby pominąć: ")
        if not birthday_input:
            break
        try:
            birthday = Birthday(birthday_input)
            break
        except ValueError as e:
            print(e)

    record = Record(name, birthday)

    while True:
        try:
            phone_input = input(
                "Podaj numer telefonu (lub wciśnij Enter, aby zakończyć dodawanie numerów): ")
            if not phone_input:
                break
            phone = Phone(phone_input)
            record.add_phone(phone)
        except ValueError as e:
            print(e)

    while True:
        try:
            email_input = input(
                "Podaj adres email (lub wciśnij Enter, aby zakończyć dodawanie adresów email): ")
            if not email_input:
                break
            email = Email(email_input)
            record.add_email(email)
        except ValueError as e:
            print(e)

    add_address = input("Czy chcesz dodać adres? (t/n): ").lower().strip()
    if add_address in ['t']:
        street = input("Podaj ulicę: ")
        city = input("Podaj miasto: ")
        postal_code = input("Podaj kod pocztowy: ")
        country = input("Podaj nazwę państwa: ")
        address = Address(street, city, postal_code, country)
        record.add_address(address)

    return record


class Note:
    def __init__(self, title, content, tags=None):
        self.title = title
        self.content = content
        self.tags = tags if tags else []
        self.created_at = datetime.now()

    def __str__(self):
        return f"{self.created_at}: {self.title} - {self.content} - Tagi: {', '.join(self.tags)}"


class Notebook:
    def __init__(self):
        self.notes = []
        self.tag_manager = TagManager(self.notes)  # Adding TagManager

    def add_note(self, title, content, tags=None):
        tags = tags or []  # Ustaw pustą listę, jeśli tags jest None
        note = {"title": title, "content": content, "tags": tags}
        self.notes.append(note)
        self.update_tags()

    def update_tags(self):
        self.tag_manager.set_notes(self.notes)

    def show_notes(self):
        if not self.notes:
            print("Brak notatek do wyświetlenia.")
            return
        for idx, note in enumerate(self.notes, start=1):
            print(f"""ID: {idx} Tytuł: {note.get('title', 'Brak tytułu')}
    Treść: {note.get('content', 'Brak treści')}
    Tagi: {', '.join(note.get('tags', []))}""")

    def delete_note(self, note_id):
        try:
            note_id = int(note_id)
            if 0 < note_id <= len(self.notes):
                deleted_note = self.notes.pop(note_id - 1)
                print(
                    f"Usunięto notatkę: {deleted_note.get('title', 'Brak tytułu')}")
            else:
                print("Notatka o podanym ID nie istnieje.")
        except ValueError:
            print("Podane ID nie jest liczbą całkowitą.")
        except IndexError:
            print("Podane ID jest poza zakresem listy notatek.")

    def edit_note(self):
        if not self.notes:
            print("Brak notatek do wyświetlenia.")
            return

        self.show_notes()
        note_id_input = input("Podaj ID notatki do edycji: ")

        try:
            note_id = int(note_id_input) - 1
            if note_id < 0 or note_id >= len(self.notes):
                print("Niepoprawne ID notatki.")
                return
        except ValueError:
            print("Nieprawidłowa wartość ID. Proszę podać liczbę.")
            return

        note = self.notes[note_id]
        title = input(
            "Podaj nowy tytuł notatki (naciśnij Enter, aby pominąć): ")
        content = input(
            "Podaj nową treść notatki (naciśnij Enter, aby pominąć): ")
        tags_input = input(
            "Podaj nowe tagi oddzielone przecinkami (lub wciśnij Enter, aby pominąć): ")
        tags = [tag.strip() for tag in tags_input.split(",")
                ] if tags_input else note['tags']

        # Aktualizacja notatki
        note['title'] = title if title else note['title']
        note['content'] = content if content else note['content']
        note['tags'] = tags

        print("Notatka została zaktualizowana.")

    def update_note(self, note_id, title=None, content=None, tags=None):
        """Aktualizuje notatkę o podanym ID."""
        note = self.notes[note_id]
        if title:
            note['title'] = title
        if content:
            note['content'] = content
        if tags is not None:
            note['tags'] = tags

        print("Notatka została zaktualizowana.")

        print("Notatka została zaktualizowana.")

    def search_notes_by_tag(self, tag):
        found_notes = [note for note in self.notes if tag in note['tags']]
        if not found_notes:
            print("Nie znaleziono notatek z podanym tagiem.")
        else:
            for note in found_notes:
                print(
                    f"Tytuł: {note['title']}\nTreść: {note['content']}\nTagi: {', '.join(note['tags'])}")

    def save_notes(self, filename='notes.pkl'):
        try:
            with open(filename, 'wb') as file:
                pickle.dump(self.notes, file)
            print("Notatki zostały zapisane.")
        except Exception as e:
            print(f"Błąd przy zapisie notatek: {e}")

    def load_notes(self, filename='notes.pkl'):
        try:
            with open(filename, 'rb') as file:
                self.notes = pickle.load(file)
            print("Notatki zostały wczytane.")
        except FileNotFoundError:
            print("Plik z notatkami nie istnieje. Tworzenie nowego pliku.")
            self.notes = []
        except Exception as e:
            print(f"Błąd przy wczytywaniu notatek: {e}")

    def sort_notes_by_tags(self, tag):
        """Sortuje notatki według daty utworzenia dla wybranego tagu."""
        notes_with_tag = [note for note in self.notes if tag in note['tags']]
        if not notes_with_tag:
            print("Brak notatek z podanym tagiem.")
            return False  # Wskazuje na to, że sortowanie nie zostało wykonane

        sorted_notes = sorted(notes_with_tag, key=lambda x: x.get(
            'created_at', datetime.min), reverse=True)
        self.notes = sorted_notes + \
            [note for note in self.notes if note not in notes_with_tag]
        return True

    def show_unique_tags(self):
        unique_tags = set()
        for note in self.notes:
            for tag in note['tags']:
                unique_tags.add(tag)
        print("Dostępne tagi:", ", ".join(unique_tags)
              if unique_tags else "Brak tagów")


class TagManager:
    def __init__(self, notes):
        self.set_notes(notes)

    def set_notes(self, notes):
        self.notes = notes

    def display_available_tags(self):
        """Wyświetla dostępne tagi."""
        tags = set()
        for note in self.notes:
            tags.update(note['tags'])
        if tags:
            print("Dostępne tagi:", ', '.join(tags))
        else:
            print("Brak dostępnych tagów.")

    def search_notes_by_tag(self, tag):
        self.display_available_tags()  # Shows available tags before searching
        found_notes = [
            note for note in self.notes if tag in note.get('tags', [])]
        if not found_notes:
            print("Nie znaleziono notatek z podanym tagiem.")
            return
        for note in found_notes:
            print(
                f"Tytuł: {note['title']}\nTreść: {note['content']}\nTagi: {', '.join(note['tags'])}")

    def sort_notes_by_tags(self, tag):
        self.display_available_tags()  # Shows available tags before sorting
        tag_exists = any(tag in note.get('tags', []) for note in self.notes)
        if not tag_exists:
            print("Nie ma takiego tagu.")
            return False
        self.notes.sort(key=lambda note: list(
            note['tags']).count(tag), reverse=True)
        print("Posortowano notatki według tagu:", tag)
        return True


def main():
    notebook = Notebook()
    notebook.load_notes()
    book = load_address_book()
    user_interface = ConsoleInterface()

    while True:
        action = input(
            "Wybierz akcję: \nZarządzaj Kontaktami (c), Zarządzaj notatkami (n), albo Wyjdź (q): ")
        if action == 'c':
            while True:
                contact_action = user_interface.get_input(
                    "Wybierz działanie: \nDodaj kontakt (add), Znajdź kontakt (find), "
                    "Usuń kontakt (delete), Edytuj kontakt (edit), Pokaż wszystkie (show), Wróć (q): ")
                if contact_action == 'add':
                    record = create_record()
                    book.add_record(record)
                    user_interface.display_message("Dodano kontakt.")
                elif contact_action == 'find':
                    search_term = input("Wpisz szukaną frazę: ")
                    found = book.find_record(search_term)
                    for record in found:
                        print(record)

                elif contact_action == 'delete':
                    book.delete_record_by_id()
                    user_interface.display_message("Usunięto kontakt.")
                elif contact_action == 'edit':
                    book.edit_record()
                    user_interface.display_message(
                        "Zaktualizowano kontakt.")
                elif contact_action == 'show':
                    user_interface.display_contacts(book.data.values())
                elif contact_action == 'q':
                    break

        elif action == 'n':
            while True:
                note_action = input("Wybierz działanie dla notatek: \nDodaj notatkę (add), Pokaż notatki (show), "
                                    "Usuń notatkę (delete), Edytuj notatkę (edit), Wyszukaj notatki według tagu (tag), "
                                    "Sortuj notatki według tagów (sort), Wróć (q): ")
                if note_action == 'add':
                    title = input("Podaj tytuł notatki: ")
                    content = input("Podaj treść notatki: ")
                    tags = [tag.strip() for tag in input("Podaj tagi oddzielone przecinkami "
                                                         "(naciśnij Enter, aby pominąć): ").split(',')]
                    notebook.add_note(title, content, tags)
                    user_interface.display_message("Dodano notatkę.")
                elif note_action == 'show':
                    user_interface.display_notes(notebook.notes)
                elif note_action == 'delete':
                    note_id = input("Podaj ID notatki do usunięcia: ")
                    notebook.delete_note(int(note_id))
                    user_interface.display_message("Usunięto notatkę.")
                elif note_action == 'edit':
                    notebook.edit_note()
                    user_interface.display_message(
                        "Zaktualizowano notatkę.")
                elif note_action == 'tag':
                    notebook.show_unique_tags()
                    tag = input("Podaj tag do wyszukiwania: ")
                    notebook.search_notes_by_tag(tag)
                elif note_action == 'sort':
                    notebook.show_unique_tags()
                    tag = input(
                        "Podaj tag po którym chcesz sortować notatki: ")
                    if notebook.sort_notes_by_tags(tag):
                        notebook.show_notes()
                    else:
                        user_interface.display_message(
                            "Sortowanie nie zostało wykonane.")
                    if notebook.sort_notes_by_tags(tag):
                        notebook.show_notes()
                elif note_action == 'q':
                    break
                else:
                    user_interface.display_message(
                        "Nieznana akcja, spróbuj ponownie.")
        elif action == 'q':
            user_interface.display_message("Wyjście z programu.")
            break
        else:
            user_interface.display_message(
                "Nieznana akcja, spróbuj ponownie.")

    save_address_book(book)
    notebook.save_notes()


if __name__ == '__main__':
    main()
