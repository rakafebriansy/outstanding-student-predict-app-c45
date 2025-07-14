import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import joblib
from modules import c45, visualization
from utils import helper

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pemilihan Mahasiswa Berprestasi")
        self.root.geometry("600x400")
        
        self.label = tk.Label(root, text="", font=("Arial", 12))
        self.label.pack(pady=10)

        self.btn_upload = tk.Button(root, text="Upload Data", command=self.upload_data)
        self.btn_process = tk.Button(root, text="Proses C4.5", command=self.process)
        self.btn_chart = tk.Button(root, text="Tampilkan Chart", command=self.chart)

        self.data = None
        self.result = None

        if helper.is_model_available():
            self.result = helper.load_model()
            self.label.config(text="Model sudah tersedia. Anda bisa langsung melihat hasil.")
            self.btn_chart.pack(pady=10)
        else:
            self.label.config(text="Model belum tersedia. Silakan unggah data untuk pelatihan.")
            self.btn_upload.pack(pady=5)
            self.btn_process.pack(pady=5)
            self.btn_chart.config(state=tk.DISABLED)
            self.btn_chart.pack(pady=5)

    def upload_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                messagebox.showinfo("Sukses", "Data berhasil dimuat.")
                self.btn_process.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat data: {e}")

    def process(self):
        if self.data is not None:
            self.result, self.tree, clf = c45.c45_process(self.data)
            helper.save_model((self.result, self.tree))
            joblib.dump(clf, helper.MODEL_PATH)
            messagebox.showinfo("Sukses", "Data berhasil diproses dan model disimpan.")
            self.btn_chart.config(state=tk.NORMAL)

    def chart(self, filepath="data/dummy_500.csv"):
        # try:
            if self.result is None:
                data = pd.read_csv(filepath)
                self.result, _ = c45.c45_process(data)
            visualization.show_chart(self.result)
        # except FileNotFoundError:
        #     messagebox.showerror("File Error", f"File tidak ditemukan: {filepath}")
        # except Exception as e:
        #     messagebox.showerror("Error", f"Terjadi kesalahan saat membuat chart: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
