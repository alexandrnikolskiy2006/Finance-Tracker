import tkinter as tk
from PIL import Image, ImageTk 
import os
from tkinter import messagebox
from datetime import datetime
import locale
import numpy as np
import pandas as pd

# --- Устанавливаем локаль для русского языка ---
# locale.setlocale(locale.LC_TIME, 'Russian')

# --- Путь к файлу ---
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Путь к файлам базы данных ---
category = pd.read_csv('category.csv')
history = pd.read_csv('history.csv', dtype={'Цена':int}, na_values=['np.nan'])

def calculate_balance():
    global history

    income = history[history['Операция'] == 'Доход']['Цена'].sum()
    expense = history[history['Операция'] == 'Расход']['Цена'].sum()
    balance = income - expense
    return balance

# --- Parametrs ---
transaction_category = ''
transaction_sum = ''
transaction_date = ''
profit = ''

balance = calculate_balance()

back = 0
indexCat = 0


BUTTON_X = 115
WIN_BG_COLOR = '#000000'
BUTTON_BG_COLOR = '#101616'
ACTIVE_BACKGROUND_BUTTON = '#2C3D3D'
FONT_COLOR = '#D8D8D8'
options = ['-Добавить категорию-', '-Изменить название категории-', '-Удалить категорию-', '-Закрыть-']
categories = category['Название категории'].tolist()
history_labels = []

# --- Start ---
win = tk.Tk()
win.geometry("1400x780+10+5")
win.resizable(False, False)
win.config(bg=WIN_BG_COLOR)
win.title("Finance Tracker")
# win.iconbitmap("images/icon.ico")

# --- Functions ---         
def quit_win():
    win.destroy()


# --- Нажатие на кнопку "Вернуться"
def goback():
    global back
    global profit
    if (back == 1):
        back = 0
        ProfitButton.place_forget()
        WasteButton.place_forget()
        MainButton.place(x=BUTTON_X, y=300)
        BackButton.place_forget()
        StatisticButton.place(x=BUTTON_X, y=420)
        ExitButton.place(x=BUTTON_X, y=550)
    elif (back == 2):
        back = 1
        EntryField.place_forget()
        InfoText.place_forget()
        CategoryButton.place_forget()
        ProfitButton.place(x=115, y=300)
        WasteButton.place(x=380, y=300)
    elif(back == 3) or (back == 4) or (back == 5):
        back = 2
        EntryField.place_forget()
        InfoText.place_forget()
        CategoryButton.place(x=115, y=300)
        CategoryButton.config(text='Выбрать категорию')  # забыли в базе данных выбранную категорию
    elif (back == 6):
        if profit == "Доход":
            back = 4
        else: back = 2
        InfoText.config(text='Введите дату операции (ДД.ММ.ГГГГ)')
    elif (back == 7):
        back = 0
        ProfitButton.place_forget()
        EntryField.place_forget()
        InfoText.place_forget()
        WasteButton.place_forget()
        MainButton.place(x=BUTTON_X, y=300)
        BackButton.place_forget()
        StatisticButton.place(x=BUTTON_X, y=420)


# --- Нажатие на кнопку "Добавить расход/доход" ---
def choice1():
    global back
    global balance
    back = 1
    MainButton.place_forget()
    if (balance == 0):
        ProfitButton.place(x=252, y=300)
        
    else:
        ProfitButton.place(x=115, y=300)
        WasteButton.place(x=390, y=300)
    StatisticButton.place_forget()
    BackButton.place(x=BUTTON_X, y=420)
    ExitButton.place_forget()


# --- Нажатие на кнопку "Расход" или "Доход"
def choice2_profit():
    global profit
    global back
    back = 7
    ProfitButton.place_forget()
    WasteButton.place_forget()
    choice4()
    profit = 'Доход'

def choice2_waste():
    global back
    global profit
    back = 2
    ProfitButton.place_forget()
    WasteButton.place_forget()
    CategoryButton.place(x=115, y=300)
    profit = 'Расход'


# --- Нажатие на кнопку "Выбрать категорию"
def choice3():
    global back
    global categories
    back = 3
    dropdown_window = tk.Toplevel(win)
    dropdown_window.geometry("530x270+134+415")
    dropdown_window.title("Выбор опции")
    if len(categories) == 0:
        if '-Изменить название категории-' in options:
            options.remove('-Изменить название категории-')
        if '-Удалить категорию-' in options:
            options.remove('-Удалить категорию-')

    dropdown_window.overrideredirect(True)

    lb = tk.Listbox(dropdown_window, width=510, height=50, font=('Arial', 26))
    for option in options+categories:
        lb.insert(tk.END, option)

    scrollbar = tk.Scrollbar(dropdown_window) #как кастомайзить? -никак
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lb.pack(side=tk.LEFT)
    scrollbar.config(command=lb.yview)
    lb.config(yscrollcommand=scrollbar.set)


    lb.bind('<<ListboxSelect>>', lambda e: select_option(lb.get(lb.curselection()), dropdown_window))
    dropdown_window.grab_set()


# --- категория введена ---
def choice4():
    global back
    if (back != 7):
        back = 4
    CategoryButton.place_forget()
    EntryField.place(x=115, y=300)
    InfoText.config(text='Введите дату операции (ДД.ММ.ГГГГ)')
    InfoText.place(x=115, y=250)


def choice6():
    global back
    back = 6
    MainButton.place_forget()
    StatisticButton.place_forget()
    InfoText.config(text='Введите сумму')
    InfoText.place(x=115, y=250)
    EntryField.place(x=115, y=300)


# -- ДОБАВЛЕНИЕ ТРАНЗАКЦИИ (ДОХОД И РАСХОД) + ДОБАВЛЕНИЕ В ФАЙЛ history.csv --
def add_transaction_interface():
    global history
    global category
    global transaction_sum
    global transaction_category
    global transaction_date
    global profit
    global balance

    if profit == 'Расход':
        # Проверяем, существует выбранная/введенная категория
        if transaction_category not in category['Название категории'].values:
            messagebox.showerror("Ошибка", f"Категория '{transaction_category}' не существует!")
            return

        # Получение индекса категории
        category_index = category.loc[category['Название категории'] == transaction_category, 'Индекс категории'].values[0]

    # Создаем новую запись для дальнейшей записи в history.csv
    new_transaction = pd.DataFrame({
        'Цена': [transaction_sum],
        'Операция': [profit],
        'Дата': [transaction_date],
        'Индекс категории': [category_index if profit == 'Расход' else np.nan]
    })

    # Добавляем запись в DataFrame
    history = pd.concat([history, new_transaction], ignore_index=True)

    # Сохраняем в файл
    history.to_csv('history.csv', index=False)

    messagebox.showinfo("Успех", f"Транзакция {profit.lower()} {transaction_sum} руб. добавлена!")
    balance = calculate_balance()
    text_balance.config(text = str(balance) + " руб.")
    get_history()
    choice1()



# --- СОЗДАНИЕ НОВОЙ КАТЕГОРИИ + ДОБАВЛЕНИЕ В ФАЙЛ category.csv ---
def add_category(transaction_category):
    global category

    transaction_category = transaction_category[0].upper() + transaction_category[1:].lower()

    if transaction_category in ["-добавить категорию-", "-изменить название категории-", "-удалить категорию-", "-закрыть-"]:
        messagebox.showerror("(╬◣ _ ◢)", "Вы думали мы вас не переиграем")
        return

     # Проверяем, существует ли такая категория
    if transaction_category in category['Название категории'].values:
        messagebox.showerror("Неверный формат данных", f"Категория {transaction_category} уже существует!")
        return


    # Определяем максимальный текущий индекс и генерируем новый
    if category['Индекс категории'].astype(str).str.isdigit().any():
        max_index = category['Индекс категории'].astype(int).max()
    else:
        max_index = -1  # Если нет числовых индексов, начнем с 0
    
    new_index = max_index + 1  # Формируем индекс с ведущими нулями

    # Добавляем новую категорию в DataFrame
    new_category = pd.DataFrame({'Название категории': [transaction_category], 'Индекс категории': [new_index]})
    category = pd.concat([category, new_category], ignore_index=True)
    
    # Сохраняем изменения в файл
    category.to_csv('category.csv', index=False)
    messagebox.showerror("", f"Категория {transaction_category.lower()} добавлена!")
    return transaction_category


# -- ИЗМЕНЕИЕ НАЗВАНИЯ КАТЕГОРИИ + СОХРАНЕНИЕ В ФАЙЛ category.csv
def rename_category(old_transaction_category, dropdown_cat):
    global back
    global transaction_category
    transaction_category = old_transaction_category
    back = 5

    dropdown_cat.destroy()

    CategoryButton.place_forget()
    EntryField.place(x=115, y=300)
    InfoText.config(text='Введите новое имя категории')
    InfoText.place(x=115, y=250)


def delete_category(old_transaction_category, dropdown_cat):
    """Удаляет запись категории из перем transaction_categoryенной category и обновляет файл."""
    global category  # Используем глобальную переменную
    global history
    global balance
    global categories
    global profit
    global transaction_category

    transaction_category = old_transaction_category

    dropdown_cat.destroy()

    if (profit == 'Доход'):
        choice2_profit()
    else:
        choice2_waste()

    try:
        # Подтверждение удаления категории
        confirm = messagebox.askyesno("Удаление категории", f"Вы уверены, что хотите удалить категорию '{transaction_category}'?")
        if not confirm:
            return

        category_index = category.loc[category['Название категории'] == transaction_category, 'Индекс категории'].values[0]
        # Проверяем, есть ли категория в данных
        category = category[category['Название категории'] != transaction_category]
        history = history[history['Индекс категории'] != category_index]
        
        # Сохраняем изменения в файл
        category.to_csv("category.csv", index=False, encoding="utf-8")
        history.to_csv("history.csv", index=False)
        messagebox.showinfo("Удаление категории", f"Категория '{transaction_category}' успешно удалена.")
        categories = category['Название категории'].tolist()
        

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    finally:
        balance = calculate_balance()
        text_balance.config(text=str(balance) + " руб.")
        get_history()
        dropdown_cat.destroy()


# --- Выбор категории в всплывающем окне --- 
def select_option(option, dropdown_window):
    global transaction_category

    if option == '-Добавить категорию-':
        dropdown_window.destroy()
        CategoryButton.place_forget()
        EntryField.place(x=115, y=300)
        InfoText.config(text='Введите имя категории')
        InfoText.place(x=115, y=250)

    elif option == '-Удалить категорию-':
        dropdown_window.destroy()
        dropdown_cat = tk.Toplevel(win)
        dropdown_cat.geometry("530x270+134+415")
        dropdown_cat.title("Выбор категории для удаления")

        dropdown_cat.overrideredirect(True)

        lb = tk.Listbox(dropdown_cat, width=510, height=50, font=('Arial', 26))
        for category in categories:
            lb.insert(tk.END, category)

        scrollbar = tk.Scrollbar(dropdown_cat)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(side=tk.LEFT)
        scrollbar.config(command=lb.yview)
        lb.config(yscrollcommand=scrollbar.set)

        lb.bind('<<ListboxSelect>>', lambda e: delete_category(lb.get(lb.curselection()), dropdown_cat))
        dropdown_cat.grab_set()

    elif option == '-Закрыть-':
        global back
        back = 2
        dropdown_window.destroy()
        
    elif option == '-Изменить название категории-':
        
        dropdown_window.destroy()
        dropdown_cat = tk.Toplevel(win)
        dropdown_cat.geometry("530x270+134+415")
        dropdown_cat.title("Выбор категории для изменения")

        dropdown_cat.overrideredirect(True)

        lb = tk.Listbox(dropdown_cat, width=510, height=50, font=('Arial', 26))
        for temp_category_name in categories:
            lb.insert(tk.END, temp_category_name)

        scrollbar = tk.Scrollbar(dropdown_cat)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(side=tk.LEFT)
        scrollbar.config(command=lb.yview)
        lb.config(yscrollcommand=scrollbar.set)

        lb.bind('<<ListboxSelect>>', lambda e: rename_category(lb.get(lb.curselection()), dropdown_cat))
        dropdown_cat.grab_set()
        
    else:
        # Извлечение выбранного значения
        transaction_category = option  # Сохраняем выбранную категорию
        dropdown_window.destroy()
        choice4()


# -- # ОБРАБОТКА ВЫБРАННЫХ ОПЕРАЦИЙ (ДОБАВЛЕНИЕ КАТЕГОРИИ ИЛИ ТРАНЗАКЦИИ)
def get_info(event=None):
    global categories               # Список названий всех категорий
    global back                     # Состояние выбора функции
    global transaction_sum                      # Сумма производимой операции
    global transaction_date           # Дата производимой операции
    global transaction_category            # Категория производимой операции (если Расход)
    global balance                   # Баланс пользователя

    userinput = EntryField.get()  # Вводимое значение в поле (тип str)

    EntryField.place_forget()
    EntryField.delete(0, tk.END)
    InfoText.place_forget()

    # Если выбран этап добавления категории
    if back == 3:
        input_category = add_category(userinput)
        transaction_category = input_category
        if len(categories) == 0:
            options.insert(1, '-Изменить название категории-')
            options.insert(2, '-Удалить категорию-')
        categories = category['Название категории'].tolist()

        back = 2
        CategoryButton.place(x=115, y=300)
        
    # Если выбран ввод даты
    elif back == 4 or back == 7:
        try:
            date_obj = datetime.strptime(userinput, '%d.%m.%Y')
            transaction_date = date_obj.strftime("%d-%m-%Y")
            choice6()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате ДД.ММ.ГГГГ")
            choice4()    

    elif back == 5:
        new_name = userinput
        print(new_name, transaction_category)
        try:
            new_name = new_name[0].upper() + new_name[1:].lower()
            # Проверяем, есть ли категория в данных
            if not category['Название категории'].str.contains(new_name).any():
                # Изменяем название категории
                
                category.loc[category['Название категории'] == transaction_category, 'Название категории'] = new_name
                
                # Сохраняем изменения в файл
                category.to_csv("category.csv", index=False, encoding="utf-8")
                messagebox.showinfo("Изменение категории", f"Категория '{transaction_category}' успешно переименована в '{new_name}'.")
                categories = category['Название категории'].tolist()
                get_history()
            else:
                messagebox.showerror("Ошибка", f"Категория '{new_name}' уже существует.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        finally:
            choice1()

    # Если выбран ввод суммы
    elif back == 6:
        transaction_sum = userinput
        try:
            transaction_sum = int(userinput)
            if (balance - transaction_sum >= 0 and profit == "Расход"):
                add_transaction_interface()
            elif (profit == "Доход"):
                add_transaction_interface()
            else:
                messagebox.showerror("Ошибка", "Расход слишком велик")
                choice6()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числовое значение")
            choice6()

def get_history():
    global history
    global category
    global floor1
    global floor2
    global floor3
    global floor4
    global floor5
    global floor6
    global floor7

    res = -1
    i = 0
    for index, row in history[::-1].head(7).iterrows():  # Берем первые 7 строк
        name = category[category["Индекс категории"] == row["Индекс категории"]]['Название категории'].values    
        if len(name)> 0:
            name = name[0]
        if row['Операция'] == 'Расход':
            t = f"{row['Цена']} руб. | {row['Дата']} | {name}"
        else:
            t = f"{row['Цена']} руб. | {row['Дата']} "
        if (i == 0):
            res = 0
            if(row['Операция'] == 'Расход'):
                floor1.config(fg='red')
            else:
                floor1.config(fg='#61892E')
            floor1.config(text=t)
        elif (i == 1):
            res = 1
            if(row['Операция'] == 'Расход'):
                floor2.config(fg='red')
            else:
                floor2.config(fg='#61892E')
            floor2.config(text=t)
        elif (i == 2):
            res = 2
            if(row['Операция'] == 'Расход'):
                floor3.config(fg='red')
            else:
                floor3.config(fg='#61892E')
            floor3.config(text=t)
        elif (i == 3):
            res = 3
            if(row['Операция'] == 'Расход'):
                floor4.config(fg='red')
            else:
                floor4.config(fg='#61892E')
            floor4.config(text=t)
        elif (i == 4):
            res = 4
            if(row['Операция'] == 'Расход'):
                floor5.config(fg='red')
            else:
                floor5.config(fg='#61892E')
            floor5.config(text=t)
        elif (i == 5):
            res = 5
            if(row['Операция'] == 'Расход'):
                floor6.config(fg='red')
            else:
                floor6.config(fg='#61892E')
            floor6.config(text=t)
        elif (i == 6):
            res = 6
            if(row['Операция'] == 'Расход'):
                floor7.config(fg='red')
            else:
                floor7.config(fg='#61892E')
            floor7.config(text=t)
        
        i += 1
    if (res == -1):
        floor1.config(text='')
        floor2.config(text='')
        floor3.config(text='')
        floor4.config(text='')
        floor5.config(text='')
        floor6.config(text='')
        floor7.config(text='')
    elif(res == 0):
        floor2.config(text='')
        floor3.config(text='')
        floor4.config(text='')
        floor5.config(text='')
        floor6.config(text='')
        floor7.config(text='')
    elif(res == 1):
        floor3.config(text='')
        floor4.config(text='')
        floor5.config(text='')
        floor6.config(text='')
        floor7.config(text='')
    elif(res == 2):
        floor4.config(text='')
        floor5.config(text='')
        floor6.config(text='')
        floor7.config(text='')
    elif(res == 3):
        floor5.config(text='')
        floor6.config(text='')
        floor7.config(text='')
    elif(res == 4):
        floor6.config(text='')
        floor7.config(text='')
    elif(res == 5):
        floor7.config(text='')
def sorry():
    messagebox.showinfo("٩(◕‿◕｡)۶","Ждите обновления! :)")
# --- logo ---
image1 = Image.open(script_dir + "/images/logo.png")
iconFT = ImageTk.PhotoImage(image1)
iconFTlabel = tk.Label(win, image=iconFT, bg=WIN_BG_COLOR, width=600, height=90)
iconFTlabel.place(x=70, y=120)

# --- Main Button ---
MainButton = tk.Button(win, text="Добавить доход/расход", font=('Arial', 31, "bold"), bg=BUTTON_BG_COLOR, fg='white', width=21, height=1, relief="flat", activebackground=ACTIVE_BACKGROUND_BUTTON, activeforeground='white', bd=0, command=choice1)
MainButton.place(x=BUTTON_X, y=300)

# --- Profit/Waste Button ---
ProfitButton = tk.Button(win, command=choice2_profit, text="Доход", font=('Arial', 31, 'bold'),  bg=BUTTON_BG_COLOR, fg='white', width=10, height=1, relief="flat", activebackground=ACTIVE_BACKGROUND_BUTTON, activeforeground='white', bd=0)
WasteButton = tk.Button(win, command=choice2_waste, text="Расход", font=('Arial', 31, 'bold'),  bg=BUTTON_BG_COLOR, fg='white', width=10, height=1, relief="flat", activebackground=ACTIVE_BACKGROUND_BUTTON, activeforeground='white', bd=0)

# --- Category Button ---
CategoryButton = tk.Button(win, command=choice3, text="Выбрать категорию", font=('Arial', 31, "bold"), bg=BUTTON_BG_COLOR, fg='white', width=21, height=1, relief="flat", activebackground=ACTIVE_BACKGROUND_BUTTON, activeforeground='white', bd=0)

# --- Back Button ---
BackButton = tk.Button(win, text="Вернуться", command=goback, font=('Arial', 31, 'bold'), bg=BUTTON_BG_COLOR, fg='white', width=21, height=1, relief="flat", activebackground=ACTIVE_BACKGROUND_BUTTON, activeforeground='white', bd=0)

# --- Statistic Button ---
StatisticButton = tk.Button(win, text="Статистика", font=('Arial', 31, "bold"), bg=BUTTON_BG_COLOR, fg='white', width=21, height=1, relief="flat", activebackground=ACTIVE_BACKGROUND_BUTTON, activeforeground='white', bd=0, command=sorry)
StatisticButton.place(x=BUTTON_X, y=420)

# --- Exit Button ---
ExitButton = tk.Button(win, text="Выход", font=('Arial', 31, "bold"), bg=BUTTON_BG_COLOR, fg='white', width=21, height=1, relief="flat", activebackground=ACTIVE_BACKGROUND_BUTTON, activeforeground='white', bd=0, command=quit_win)
ExitButton.place(x=BUTTON_X, y=550)

# --- White Line ---
Line = tk.Label(win, bg=FONT_COLOR, padx=0, pady=317,)
Line.place(x=750, y=70)

# --- Update Date ---
version = tk.Label(win, text='FT 13.12.24', font=('Arial', 20, 'bold'), fg=FONT_COLOR, bg=WIN_BG_COLOR) 
version.place(x=1230, y=730)

# --- Balance ---
image5 = Image.open(script_dir + "/images/balance.png")
balanceimg = ImageTk.PhotoImage(image5)
Balance = tk.Label(win, image=balanceimg, bg=WIN_BG_COLOR)
Balance.place(x=820, y=100)

text_balance = tk.Label(win, text=str(balance) + " руб.", font=('Arial', 31, 'bold'), anchor='w', height=1, width=19, background=BUTTON_BG_COLOR, relief="flat", fg='#61892E')
text_balance.place(x=850, y=165)


# --- History ---
image6 = Image.open(script_dir + "/images/history.png")
historyimg = ImageTk.PhotoImage(image6)
History = tk.Label(win, image=historyimg, bg=WIN_BG_COLOR)
History.place(x=820, y=255)
image7 = Image.open(script_dir + "/images/down.png")
downimg = ImageTk.PhotoImage(image7)



# --- History array --- 
floor1 = tk.Label(win, text='',anchor="center", font=('Arial', 18, 'bold'), height=1, width=33, background=BUTTON_BG_COLOR, fg='#61892E', bd=2, relief="solid")
floor1.place(x=827, y=310)
floor2 = tk.Label(win, text='', font=('Arial', 18, 'bold'), anchor='center', height=1, width=33, background=BUTTON_BG_COLOR, fg='#61892E', bd=2, relief="solid")
floor2.place(x=827, y=360)
floor3 = tk.Label(win, text='', font=('Arial', 18, 'bold'), anchor='center', height=1, width=33, background=BUTTON_BG_COLOR, fg='#61892E', bd=2, relief="solid")
floor3.place(x=827, y=410)
floor4 = tk.Label(win, text='', font=('Arial', 18, 'bold'), anchor='center', height=1, width=33, background=BUTTON_BG_COLOR, fg='#61892E', bd=2, relief="solid")
floor4.place(x=827, y=460)
floor5 = tk.Label(win, text='', font=('Arial', 18, 'bold'), anchor='center', height=1, width=33, background=BUTTON_BG_COLOR, fg='#61892E', bd=2, relief="solid")
floor5.place(x=827, y=510)
floor6 = tk.Label(win, text='', font=('Arial', 18, 'bold'), anchor='center', height=1, width=33, background=BUTTON_BG_COLOR, fg='#61892E', bd=2, relief="solid")
floor6.place(x=827, y=560)
floor7 = tk.Label(win, text='', font=('Arial', 18, 'bold'), anchor='center', height=1, width=33, background=BUTTON_BG_COLOR, fg='#61892E', bd=2, relief="solid")
floor7.place(x=827, y=610)
get_history()


#for i in range(1, 11):
#    label = tk.Label(win, text=profit+transaction_category+transaction_date+transaction_sum, font=('Arial', 20))
#    history_labels.append(label)
#    label.place(x=620, y=225+i*15)


# --- Entry Field ---
EntryField = tk.Entry(win, width=23, bg=BUTTON_BG_COLOR, fg='white', font=('Arial', 31, 'bold'), bd=0)
EntryField.bind('<Return>', get_info)

# --- Info ---
InfoText = tk.Label(win, text='stock', font=('Arial', 20, 'bold'), bg=WIN_BG_COLOR, fg='white', bd=0,)


win.mainloop()