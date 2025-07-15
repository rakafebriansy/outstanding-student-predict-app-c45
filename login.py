import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
import os

load_dotenv() 

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x200")
        self.root.configure(bg="white")

        self.on_success = on_success

        tk.Label(root, text="Username", bg="white").pack(pady=(20, 5))
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password", bg="white").pack(pady=(10, 5))
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", command=self.check_login).pack(pady=20)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == USER and password == PASSWORD:
            self.root.destroy()
            self.on_success()
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.")
