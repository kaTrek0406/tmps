import tkinter as tk
from tkinter import ttk, messagebox

# ------------------------ Классы, реализующие паттерны ------------------------

# Класс Computer представляет конечный продукт.
class Computer:
    def __init__(self, name, cpu, gpu, ram, storage, os):
        self.name = name
        self.cpu = cpu
        self.gpu = gpu
        self.ram = ram
        self.storage = storage
        self.os = os

    def __str__(self):
        return (f"Имя: {self.name}\n"
                f"Процессор: {self.cpu}\n"
                f"Графика: {self.gpu}\n"
                f"ОЗУ: {self.ram}\n"
                f"Хранилище: {self.storage}\n"
                f"ОС: {self.os}")

# ------------------------ Builder (Строитель) ------------------------
class ComputerBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self.name = None
        self.cpu = None
        self.gpu = None
        self.ram = None
        self.storage = None
        self.os = None
        return self

    def set_name(self, name):
        self.name = name
        return self

    def set_cpu(self, cpu):
        self.cpu = cpu
        return self

    def set_gpu(self, gpu):
        self.gpu = gpu
        return self

    def set_ram(self, ram):
        self.ram = ram
        return self

    def set_storage(self, storage):
        self.storage = storage
        return self

    def set_os(self, os):
        self.os = os
        return self

    def build(self):
        computer = Computer(
            name=self.name,
            cpu=self.cpu,
            gpu=self.gpu,
            ram=self.ram,
            storage=self.storage,
            os=self.os
        )
        self.reset()  # сброс билдера для нового построения
        return computer

# ------------------------ Singleton (Одиночка) ------------------------
class ConfigurationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance.configs = {
                'gaming': {
                    'cpu': 'Intel i9',
                    'gpu': 'NVIDIA RTX 3080',
                    'ram': '32GB',
                    'storage': '1TB SSD',
                    'os': 'Windows 11'
                },
                'office': {
                    'cpu': 'Intel i5',
                    'gpu': 'Integrated Graphics',
                    'ram': '16GB',
                    'storage': '512GB SSD',
                    'os': 'Windows 10'
                },
                'server': {
                    'cpu': 'AMD EPYC',
                    'gpu': 'None',
                    'ram': '64GB',
                    'storage': '2TB NVMe',
                    'os': 'Linux'
                }
            }
        return cls._instance

    def get_config(self, type_):
        return self.configs.get(type_, None)

# ------------------------ Factory Method (Фабричный метод) ------------------------
class ComputerFactory:
    def __init__(self):
        self.builder = ComputerBuilder()
        self.config_manager = ConfigurationManager()

    def create_computer(self, type_):
        config = self.config_manager.get_config(type_)
        if config is None:
            raise ValueError(f"Нет конфигурации для типа компьютера '{type_}'")
        computer = (self.builder
                    .set_name(type_.capitalize() + " Computer")
                    .set_cpu(config['cpu'])
                    .set_gpu(config['gpu'])
                    .set_ram(config['ram'])
                    .set_storage(config['storage'])
                    .set_os(config['os'])
                    .build())
        return computer

# ------------------------ UI на tkinter ------------------------

# Функция-обработчик нажатия кнопки «Создать компьютер»
def create_computer_action():
    selected_type = computer_type_var.get()
    try:
        computer = factory.create_computer(selected_type)
        result_text.set(str(computer))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Создание главного окна приложения
root = tk.Tk()
root.title("Создание компьютера")

# Фабрика для создания компьютеров
factory = ComputerFactory()

# Фрейм для выбора типа компьютера
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

# Метка для выбора типа компьютера
ttk.Label(frame, text="Выберите тип компьютера:").grid(row=0, column=0, padx=5, pady=5)

# Переменная для хранения выбранного типа компьютера
computer_type_var = tk.StringVar(value='gaming')

# Выпадающий список (Combobox) с вариантами
type_combobox = ttk.Combobox(frame, textvariable=computer_type_var, state="readonly")
type_combobox['values'] = ('gaming', 'office', 'server')
type_combobox.grid(row=0, column=1, padx=5, pady=5)
type_combobox.current(0)  # выбор первого значения по умолчанию

# Кнопка для создания компьютера
create_button = ttk.Button(frame, text="Создать компьютер", command=create_computer_action)
create_button.grid(row=1, column=0, columnspan=2, pady=10)

# Метка для вывода результата
result_text = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_text, padding="10", relief="groove", justify=tk.LEFT)
result_label.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

# Запуск главного цикла обработки событий
root.mainloop()
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Приложение завершено пользователем.")
