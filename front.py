import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import os
import sv_ttk
import re

# Файлы с данными
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "database.json")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


# Функция загрузки данных
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Функция аутентификации пользователя
def authenticate_user(email, password):
    users = load_data(USERS_FILE)
    for user in users:
        if user["user"] == email and user["password"] == password:
            return True
    return False


# Функция получения писем для пользователя
def get_user_mails(email, folder):
    mails = load_data(DATABASE_FILE)
    if folder == "Входящие":
        return [
            mail for mail in mails if mail["receiver"] == email and mail["inBin"] == 0
        ]
    elif folder == "Отправленные":
        return [
            mail for mail in mails if mail["sender"] == email and mail["inBin"] == 0
        ]
    elif folder == "Корзина":
        return [
            mail
            for mail in mails
            if (mail["sender"] == email or mail["receiver"] == email)
            and mail["inBin"] == 1
        ]
    return []


# Функция генерации нового ID
def generate_new_id():
    mails = load_data(DATABASE_FILE)
    if not mails:
        return 1
    ids = [mail["id"] for mail in mails]
    return max(ids) + 1


# Функция обновления списка писем
def refresh_mail_list():
    global mails
    mails = get_user_mails(current_user, current_folder)
    mail_list_container.pack(fill=tk.BOTH, expand=True)
    for widget in mail_list_container.winfo_children():
        widget.destroy()
    display_mails()


# Функция удаления письма (перемещение в корзину)
def delete_mail(mail_id):
    mails = load_data(DATABASE_FILE)
    for mail in mails:
        if mail["id"] == mail_id:
            if current_folder == "Корзина":
                mails.remove(mail)
            else:
                mail["inBin"] = 1
            break
    save_data(DATABASE_FILE, mails)
    refresh_mail_list()


# Функция восстановления письма из корзины
def restore_mail(mail_id):
    mails = load_data(DATABASE_FILE)
    for mail in mails:
        if mail["id"] == mail_id:
            mail["inBin"] = 0
            break
    save_data(DATABASE_FILE, mails)
    refresh_mail_list()


# Функция переключения отображения письма
def toggle_mail(index):
    current_text = mail_labels[index].cget("text")
    if mails[index]["text"] not in current_text:
        mail_labels[index].config(
            text=f"Отправитель: {mails[index]['sender']}\nПолучатель: {mails[index]['receiver']}\nТема: {mails[index]['subject']}\n{mails[index]['text']}"
        )
        toggle_buttons[index].config(text="▼")
    else:
        mail_labels[index].config(
            text=f"Отправитель: {mails[index]['sender']}\nПолучатель: {mails[index]['receiver']}\nТема: {mails[index]['subject']}"
        )
        toggle_buttons[index].config(text="▶")


# Функция для переключения между папками
def switch_folder(folder):
    global current_folder, compose_frame_visible
    current_folder = folder

    if compose_frame_visible:
        compose_frame.place_forget()
        compose_frame_visible = False

    refresh_mail_list()


# Функция написания письма
def compose_mail():
    global compose_frame_visible

    if compose_frame_visible:
        return
    

    receiver_entry.delete(0, tk.END)
    subject_entry.delete(0, tk.END)
    text_entry.delete("1.0", tk.END)

    mail_list_container.pack_forget()
    #compose_frame.pack(fill=tk.BOTH, expand=True)
    compose_frame.place(x=160, y=10)
    compose_frame_visible = True


# Функция отправки письма
def send_mail():
    global compose_frame_visible

    sender = current_user
    receiver = receiver_entry.get()
    subject = subject_entry.get()
    text = text_entry.get("1.0", tk.END).strip()

    if not receiver or not subject or not text:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
        return

    mails = load_data(DATABASE_FILE)

    new_mail = {
        "id": generate_new_id(),
        "sender": sender,
        "receiver": receiver,
        "subject": subject,
        "text": text,
        "inBin": 0,
    }

    mails.append(new_mail)
    save_data(DATABASE_FILE, mails)

    receiver_entry.delete(0, tk.END)
    subject_entry.delete(0, tk.END)
    text_entry.delete("1.0", tk.END)

    compose_frame.place_forget()
    compose_frame_visible = False

    refresh_mail_list()
    switch_folder("Отправленные")


# Функция входа в систему
def login():
    global current_user
    email = email_entry.get()
    password = password_entry.get()

    if authenticate_user(email, password):
        current_user = email
        login_window.destroy()
        create_main_window()
    else:
        messagebox.showerror("Ошибка", "Неверный email или пароль")


def display_mails():
    global mails, mail_labels, toggle_buttons
    mail_labels.clear()
    toggle_buttons.clear()

    for index, mail in enumerate(mails):
        mail_item = ttk.Frame(mail_list_container)
        mail_item.pack(fill=tk.X, padx=5, pady=2)

        # Кнопка "▶/▼" в левом верхнем углу
        toggle_button = ttk.Button(
            mail_item, text="▶", width=2, command=lambda i=index: toggle_mail(i)
        )
        toggle_button.pack(side=tk.LEFT, anchor="nw", padx=15, pady=18)
        toggle_buttons.append(toggle_button)

        # Текст письма с переносом строк
        mail_label = ttk.Label(
            mail_item,
            text=f"Отправитель: {mail['sender']}\nПолучатель: {mail['receiver']}\nТема: {mail['subject']}",
            wraplength=1000,  # Ограничивает ширину, после которой текст переносится
            justify="left"
        )
        mail_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        mail_labels.append(mail_label)

        # Кнопки удаления и восстановления
        if current_folder == "Корзина":
            restore_button = ttk.Button(
                mail_item, text="Восстановить", command=lambda mid=mail["id"]: restore_mail(mid)
            )
            restore_button.pack(side=tk.RIGHT, padx=2)

        delete_button_text = "В корзину" if current_folder != "Корзина" else "Удалить"
        delete_button = ttk.Button(
            mail_item, text=delete_button_text, command=lambda mid=mail["id"]: delete_mail(mid)
        )
        delete_button.pack(side=tk.RIGHT, padx=2)


def create_main_window():
    global main_frame, sidebar, mail_list_container, compose_frame
    global mail_labels, toggle_buttons, mails, current_folder
    global receiver_entry, subject_entry, text_entry, compose_frame_visible
    global current_user

    root = tk.Tk()
    root.title(f"Почтовый клиент - {current_user}")
    root.state("zoomed")

    sv_ttk.set_theme("dark")
    style = ttk.Style()
    style.configure('TButton', font=('Cascadia Code', 11), padding=5,  sticky='N')
    style.configure('Sidebar.TButton', font=('Cascadia Code', 11), padding=5,  sticky='E', background = 'red')
    style.map('Sidebar.TButton',
             background=[('active', '#a0c0e0'), ('pressed', '#8090c0')])
    
    style.configure('TLabel', font=('Cascadia Code', 11), padding=10)


    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    sidebar = ttk.Frame(main_frame, width=200)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)


    compose_button = ttk.Button(sidebar, text="Написать", style = 'Sidebar.TButton', command=compose_mail)
    compose_button.pack(pady=20, padx=10, fill=tk.X)

    folders_label = ttk.Label(sidebar, text="Папки")
    folders_label.pack(pady=5, padx=10, fill=tk.X)

    folders = ["Входящие", "Корзина", "Отправленные"]
    for folder in folders:
        folder_button = ttk.Button(
            sidebar, text=folder, command=lambda f=folder: switch_folder(f)
        )
        folder_button.pack(fill=tk.X, padx=10, pady=2)

    mail_frame = ttk.Frame(main_frame)
    mail_frame.pack(fill=tk.BOTH, expand=True)

    mail_list_container = ttk.Frame(mail_frame)
    mail_list_container.pack(fill=tk.BOTH, expand=True)

    mail_labels = []
    toggle_buttons = []

    compose_frame = tk.Frame(main_frame)
    
    #compose_frame.lift(aboveThis=None)
    
    compose_frame_visible = False

    receiver_label = ttk.Label(compose_frame, text="Получатель:")
    receiver_label.pack(fill=tk.X, padx=10, pady=5)
    receiver_entry = ttk.Entry(compose_frame)
    receiver_entry.pack(fill=tk.X, padx=10)

    subject_label = ttk.Label(compose_frame, text="Тема:")
    subject_label.pack(fill=tk.X, padx=10, pady=5)
    subject_entry = ttk.Entry(compose_frame)
    subject_entry.pack(fill=tk.X, padx=10)

    text_label = ttk.Label(compose_frame, text="Текст:")
    text_label.pack(fill=tk.X, padx=10, pady=5)
    text_entry = tk.Text(compose_frame, height=10, wrap=tk.WORD)
    text_entry.pack(fill=tk.X, padx=10)

    buttons_frame = ttk.Frame(compose_frame)
    buttons_frame.pack(fill=tk.X, padx=10, pady=10)

    send_button = ttk.Button(buttons_frame, text="Отправить", command=send_mail)
    send_button.pack(side=tk.LEFT)

    cancel_button = ttk.Button(
        buttons_frame, text="Отмена", command=lambda: switch_folder("Входящие")
    )
    cancel_button.pack(side=tk.RIGHT)

    current_folder = "Входящие"
    mails = get_user_mails(current_user, current_folder)
    display_mails()

    root.mainloop()

def register():
    global current_user
    email = email_entry.get()
    password = password_entry.get()
    
    if not email or not password:
        messagebox.showerror("Ошибка", "Логин и пароль не могут быть пустыми")
        return
    
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
        messagebox.showerror("Ошибка", "Логин должен быть действительным почтовым адресом")
        return
    
    users = load_data(USERS_FILE)
    
    # Проверяем, есть ли уже такой пользователь
    for user in users:
        if user["user"] == email:
            messagebox.showerror("Ошибка", "Этот логин уже используется")
            return
    
    # Добавляем нового пользователя
    users.append({"user": email, "password": password})
    save_data(USERS_FILE, users)
    
    current_user = email
    login_window.destroy()
    create_main_window()


# Окно входа
login_window = tk.Tk()
login_window.title("Вход в почтовый клиент")


sv_ttk.set_theme("dark")

style = ttk.Style()
style.configure('TButton', font=('Cascadia Code', 11), padding=5,  sticky='E')
style.configure('TEntry', font=('Cascadia Code', 11), padding=5,  sticky='E')
style.configure('TLabel', font=('Cascadia Code', 11), padding=5,  sticky='E')

ttk.Label(login_window, text="Логин:").grid(row=0, column=0, padx=10, pady=5,  sticky='E')
email_entry = ttk.Entry(login_window)
email_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(login_window, text="Пароль:").grid(row=1, column=0, padx=10, pady=5,  sticky='E')
password_entry = ttk.Entry(login_window, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

login_button = ttk.Button(login_window, text="Войти", command=login)
login_button.grid(row=2, column=0, columnspan=2, pady=10, padx = 10, sticky='E')

# Добавляем кнопку "Создать аккаунт"
register_button = ttk.Button(login_window, text="Создать аккаунт", command=register)
register_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky='W')


login_window.mainloop()
