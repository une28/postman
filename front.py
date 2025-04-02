import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import os




# Файлы с данными
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "database.json")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# Функция загрузки данных
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Функция аутентификации пользователя
def authenticate_user(email, password):
    users = load_data(USERS_FILE)
    for user in users:
        if user['user'] == email and user['password'] == password:
            return True
    return False

def display_mails():
        global mails, mail_labels, toggle_buttons
        mail_labels.clear()
        toggle_buttons.clear()
        
        for index, mail in enumerate(mails):
            sender = mail.get('sender', 'Неизвестный отправитель')
            receiver = mail.get('receiver', 'Неизвестный получатель')
            subject = mail.get('subject', 'Без темы')
            text = mail.get('text', '')
            mail_id = mail.get('id', -1)
            
            mail_item = tk.Frame(mail_list_container)
            mail_item.pack(fill=tk.X, padx=5, pady=2)
            
            toggle_button = tk.Button(mail_item, text='▶', width=2, command=lambda i=index: toggle_mail(i))
            toggle_button.pack(side=tk.LEFT)
            toggle_buttons.append(toggle_button)
            
            mail_label = tk.Label(mail_item, text=f"Отправитель: {sender}\nПолучатель: {receiver}\nТема: {subject}", anchor='w', wraplength=600, justify='left')
            mail_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            mail_labels.append(mail_label)
            
            if current_folder == "Корзина":
                restore_button = tk.Button(mail_item, text="Восстановить", command=lambda mid=mail_id: restore_mail(mid))
                restore_button.pack(side=tk.RIGHT)
            
            delete_button_text = "В корзину" if current_folder != "Корзина" else "Удалить"
            delete_button = tk.Button(mail_item, text=delete_button_text, command=lambda mid=mail_id: delete_mail(mid))
            delete_button.pack(side=tk.RIGHT)

# Функция получения писем для пользователя
def get_user_mails(email, folder):
    mails = load_data(DATABASE_FILE)
    if folder == "Входящие":
        return [mail for mail in mails if mail['receiver'] == email and mail['inBin'] == 0]
    elif folder == "Отправленные":
        return [mail for mail in mails if mail['sender'] == email and mail['inBin'] == 0]
    elif folder == "Корзина":
        return [mail for mail in mails if (mail['sender'] == email or mail['receiver'] == email) and mail['inBin'] == 1]
    return []

# Функция генерации нового ID
def generate_new_id():
    mails = load_data(DATABASE_FILE)
    if not mails:
        return 1
    ids = [mail['id'] for mail in mails]
    return max(ids) + 1

# Функция обновления списка писем
def refresh_mail_list():
    global mails
    mails = get_user_mails(current_user, current_folder)
    mail_list_container.pack(fill=tk.BOTH, expand=True)  # Восстанавливаем отображение списка
    for widget in mail_list_container.winfo_children():
        widget.destroy()
    display_mails()

# Функция удаления письма (перемещение в корзину)
def delete_mail(mail_id):
    mails = load_data(DATABASE_FILE)
    for mail in mails:
        if mail['id'] == mail_id:
            if current_folder == "Корзина":
                # Полное удаление из корзины
                mails.remove(mail)
            else:
                # Перемещение в корзину
                mail['inBin'] = 1
            break
    save_data(DATABASE_FILE, mails)
    refresh_mail_list()

# Функция восстановления письма из корзины
def restore_mail(mail_id):
    mails = load_data(DATABASE_FILE)
    for mail in mails:
        if mail['id'] == mail_id:
            mail['inBin'] = 0
            break
    save_data(DATABASE_FILE, mails)
    refresh_mail_list()

# Функция переключения отображения письма
def toggle_mail(index):
    current_text = mail_labels[index].cget("text")
    if mails[index]['text'] not in current_text:
        mail_labels[index].config(text=f"Отправитель: {mails[index]['sender']}\nПолучатель: {mails[index]['receiver']}\nТема: {mails[index]['subject']}\nСодержание: {mails[index]['text']}")
        toggle_buttons[index].config(text='▼')
    else:
        mail_labels[index].config(text=f"Отправитель: {mails[index]['sender']}\nПолучатель: {mails[index]['receiver']}\nТема: {mails[index]['subject']}")
        toggle_buttons[index].config(text='▶')

# Функция для переключения между папками
def switch_folder(folder):
    global current_folder, compose_frame_visible
    current_folder = folder
    
    # Скрываем форму написания письма при переключении папок
    if compose_frame_visible:
        compose_frame.pack_forget()
        compose_frame_visible = False
    
    refresh_mail_list()

# Функция, вызываемая при нажатии на кнопку "Написать"
def compose_mail():
    global compose_frame_visible
    
    # Если форма уже отображается, ничего не делаем
    if compose_frame_visible:
        return
    
    # Очищаем поля формы
    receiver_entry.delete(0, tk.END)
    subject_entry.delete(0, tk.END)
    text_entry.delete("1.0", tk.END)
    
    # Скрываем список писем и показываем форму
    mail_list_container.pack_forget()
    compose_frame.pack(fill=tk.BOTH, expand=True)
    compose_frame_visible = True

# Функция, вызываемая при нажатии на кнопку "Отправить"
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
        'id': generate_new_id(),
        'sender': sender,
        'receiver': receiver,
        'subject': subject,
        'text': text,
        'inBin': 0
    }
    
    mails.append(new_mail)
    save_data(DATABASE_FILE, mails)

    # Очищаем форму и скрываем её
    receiver_entry.delete(0, tk.END)
    subject_entry.delete(0, tk.END)
    text_entry.delete("1.0", tk.END)
    
    compose_frame.pack_forget()
    compose_frame_visible = False
    
    # Показываем список писем и переключаемся на отправленные
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

def create_main_window():
    global main_frame, sidebar, mail_list_container, compose_frame
    global mail_labels, toggle_buttons, mails, current_folder
    global receiver_entry, subject_entry, text_entry, compose_frame_visible
    global current_user
    
    # Главное окно
    root = tk.Tk()
    root.title(f"Почтовый клиент - {current_user}")
    root.state('zoomed')

    # Основной фрейм
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Левое меню
    sidebar = tk.Frame(main_frame, bg='#f0f0f0', width=200)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)

    # Кнопка "Написать"
    compose_button = ttk.Button(sidebar, text="Написать", bg='#d0e1f9', relief=tk.FLAT, padx=10, pady=5, command=compose_mail)
    compose_button.pack(pady=10, padx=10, fill=tk.X)

    # Список папок
    folders_label = tk.Label(sidebar, text="Папки", bg='#f0f0f0', anchor='w')
    folders_label.pack(pady=5, padx=10, fill=tk.X)

    folders = ["Входящие", "Корзина", "Отправленные"]
    for folder in folders:
        folder_button = ttk.Button(sidebar, text=folder, bg='#f0f0f0', anchor='w', command=lambda f=folder: switch_folder(f))
        folder_button.pack(fill=tk.X, padx=10, pady=2)

    # Основная область для писем
    mail_frame = tk.Frame(main_frame)
    mail_frame.pack(fill=tk.BOTH, expand=True)

    # Список писем
    mail_list_container = tk.Frame(mail_frame)
    mail_list_container.pack(fill=tk.BOTH, expand=True)

    mail_labels = []
    toggle_buttons = []

    

    # Форма для написания письма
    compose_frame = tk.Frame(main_frame)
    compose_frame_visible = False

    receiver_label = tk.Label(compose_frame, text="Получатель:")
    receiver_label.pack(fill=tk.X, padx=10, pady=5)
    receiver_entry = tk.Entry(compose_frame)
    receiver_entry.pack(fill=tk.X, padx=10)

    subject_label = tk.Label(compose_frame, text="Тема:")
    subject_label.pack(fill=tk.X, padx=10, pady=5)
    subject_entry = tk.Entry(compose_frame)
    subject_entry.pack(fill=tk.X, padx=10)

    text_label = tk.Label(compose_frame, text="Текст:")
    text_label.pack(fill=tk.X, padx=10, pady=5)
    text_entry = tk.Text(compose_frame, height=10, wrap=tk.WORD)
    text_entry.pack(fill=tk.X, padx=10)

    buttons_frame = tk.Frame(compose_frame)
    buttons_frame.pack(fill=tk.X, padx=10, pady=10)

    send_button = tk.Button(buttons_frame, text="Отправить", command=send_mail)
    send_button.pack(side=tk.LEFT)

    cancel_button = tk.Button(buttons_frame, text="Отмена", command=lambda: switch_folder("Входящие"))
    cancel_button.pack(side=tk.RIGHT)

    # Отображение писем по умолчанию (входящие)
    current_folder = "Входящие"
    mails = get_user_mails(current_user, current_folder)
    display_mails()

    root.mainloop()

# Окно входа
login_window = tk.Tk()
login_window.title("Вход в почтовый клиент")


# Создание объекта стиля
style = ttk.Style()

# Установка темы (можно выбрать 'clam', 'alt', 'default' и др.)
style.theme_use('clam')

# Настройка стиля для всех кнопок
style.configure('TButton', font=('Arial', 20), background='lightgray', foreground='black', padding=5)

# Настройка стиля для всех текстовых полей
style.configure('TEntry', font=('Arial', 12), padding=5)

tk.Label(login_window, text="Email:").grid(row=0, column=0, padx=10, pady=5)
email_entry = tk.Entry(login_window)
email_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(login_window, text="Пароль:").grid(row=1, column=0, padx=10, pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

login_button = ttk.Button(login_window, text="Войти", command=login)
login_button.grid(row=2, column=0, columnspan=2, pady=10)

login_window.mainloop()