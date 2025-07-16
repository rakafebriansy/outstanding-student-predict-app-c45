import tkinter as tk
import login
import os
from tkinter import messagebox
import pandas as pd
from modules import c45, predict
from utils import helper
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
from pandas.api.types import is_numeric_dtype

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pemilihan Mahasiswa Berprestasi")
        self.root.geometry("900x600")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(root, width=200, bg="#2c3e50")
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content = tk.Frame(root, bg="white")
        self.content.grid(row=0, column=1, sticky="nsew")

        self.label = tk.Label(self.sidebar, text="Pemilihan\nMahasiswa Berprestasi", bg="#2c3e50", fg="white", font=("Arial", 14))
        self.label.pack(pady=20)

        prepare_text = "Replace Model" if helper.is_model_available() else "Add New Model"
        self.btn_prepare = tk.Button(self.sidebar, text=prepare_text, width=20, command=self.prepare_model)
        self.btn_prepare.pack(pady=5)

        self.btn_chart = tk.Button(self.sidebar, text="Tampilkan Basis Data", width=20, command=self.chart)
        self.btn_chart.pack(pady=5)

        self.btn_visualize_all = tk.Button(self.sidebar, text="Visualisasi Semua Fitur", width=20, command=self.visualize_all_features)
        self.btn_visualize_all.pack(pady=5)

        self.btn_predict = tk.Button(self.sidebar, text="Prediksi Mahasiswa", width=20, command=self.show_prediction_form)
        self.btn_predict.pack(pady=5)
        self.btn_predict.config(state=tk.DISABLED)

        self.status_label = tk.Label(self.content, text="", font=("Arial", 12), bg="white")
        self.status_label.pack(pady=20)

        self.chart_canvas = None
        self.data = None
        self.result = None
        self.tree = None
        self.clf = None

        if helper.is_model_available():
            try:
                self.result, self.tree = helper.load_result()
                self.clf = helper.load_model()

                self.status_label.config(text="Model sudah tersedia. Anda bisa langsung melakukan prediksi.")
                self.btn_chart.config(state=tk.NORMAL)
                self.btn_predict.config(state=tk.NORMAL)

            except Exception as e:
                self.status_label.config(text="Gagal memuat model yang tersimpan.")
                self.btn_prepare.config(state=tk.DISABLED)
                self.btn_chart.config(state=tk.DISABLED)
                print(f"Error: {e}")

    def refresh_model(self):
        try:
            self.result, self.tree = helper.load_result()
            self.clf = helper.load_model()

        except Exception as e:
            print(f"Error: {e}")

    def prepare_model(self):            
        file_path = helper.DATABASE_PATH
        if not file_path:
            return
        
        dir_path = os.path.dirname(helper.MODEL_PATH)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        for widget in self.content.winfo_children():
            widget.destroy()

        try:
            self.data = pd.read_csv(file_path)
            self.status_label = tk.Label(self.content, text="Data berhasil dimuat. Melatih model...", font=("Arial", 12), bg="white")
            self.status_label.pack(pady=20)
            self.root.update_idletasks()

            self.result, self.tree, clf = c45.c45_process(self.data)
            helper.save_result((self.result, self.tree))
            helper.save_model(clf)

            self.status_label.config(text="Model berhasil dilatih dan disimpan.")
            self.btn_chart.config(state=tk.NORMAL)
            self.btn_prepare.config(text="Replace Model")
            self.btn_predict.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
            self.status_label.config(text="Gagal memproses data.")
            self.btn_chart.config(state=tk.DISABLED)

    def chart(self, filepath=helper.DATABASE_PATH):
        for widget in self.content.winfo_children():
            widget.destroy()

        self.status_label = tk.Label(self.content, text="Visualisasi Data", font=("Arial", 14), bg="white")
        self.status_label.pack(pady=10)

        if self.result is None:
            data = pd.read_csv(filepath)
            self.result, _, _ = c45.c45_process(data)

        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        summary = self.result['Hasil'].value_counts()

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        summary.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title("Distribusi Mahasiswa Terpilih")
        ax.set_ylabel("Jumlah")
        ax.set_xlabel("Hasil")

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.content)
        self.chart_canvas.draw()
        canvas_widget = self.chart_canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill="both", padx=10, pady=10)

    def show_prediction_form(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        title_label = tk.Label(self.content, text="Form Prediksi Mahasiswa", font=("Arial", 16, "bold"), bg="white")
        title_label.pack(pady=(20, 10))

        form_frame = tk.Frame(self.content, bg="white")
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)

        if not helper.is_model_available():
            return
        
        self.refresh_model()

        fitur = list(self.clf.feature_names_in_) if self.clf is not None else []

        self.input_entries = {}

        def validate_numeric(value):
            if value == "":
                return True
            try:
                float(value)
                return True
            except ValueError:
                return False

        vcmd = (self.root.register(validate_numeric), '%P')

        for feature in fitur:
            row = tk.Frame(form_frame, bg="white")
            row.pack(fill="x", pady=5)

            label = tk.Label(row, text=feature, width=20, anchor="w", bg="white", font=("Arial", 10))
            label.pack(side="left")

            entry = tk.Entry(row, width=30, validate="key", validatecommand=vcmd)
            entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

            self.input_entries[feature] = entry

        predict_btn = tk.Button(self.content, text="Prediksi", font=("Arial", 11, "bold"), command=self.predict_single)
        predict_btn.pack(pady=15)

        self.prediction_label = tk.Label(self.content, text="", font=("Arial", 12), bg="white", fg="green")
        self.prediction_label.pack(pady=(0, 20))


    def predict_single(self):
        if self.clf is None:
            messagebox.showerror("Model Error", "Model belum tersedia.")
            return

        try:
            input_data = {feature: float(entry.get()) for feature, entry in self.input_entries.items()}
            prediction = predict.predict_single_input(self.clf, input_data)
            self.prediction_label.config(
                text=f"Prediksi: Mahasiswa {'Terpilih' if prediction == 'Ya' else 'Tidak Terpilih'}"
            )
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
    
    def visualize_all_features(self):
        if self.data is None:
            try:
                self.data = pd.read_csv(helper.DATABASE_PATH)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat data: {e}")
                return

        for widget in self.content.winfo_children():
            widget.destroy()

        tk.Label(self.content, text="Visualisasi Semua Fitur", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        numeric_cols = [col for col in self.data.columns if is_numeric_dtype(self.data[col]) and col not in ['Hasil', 'Nama']]

        if not numeric_cols:
            tk.Label(self.content, text="Tidak ada fitur numerik untuk divisualisasikan.", bg="white").pack(pady=20)
            return
        
        for col in numeric_cols:
                self.data[col] = self.data[col].astype(int)

        canvas_frame = tk.Frame(self.content, bg="white")
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        fig = Figure(figsize=(6, len(numeric_cols) * 2), dpi=100)
        for i, col in enumerate(numeric_cols):
            ax = fig.add_subplot(len(numeric_cols), 1, i + 1)
            self.data[col].plot(kind='hist', bins=15, ax=ax, color='skyblue', edgecolor='black')
            ax.set_title(f'Distribusi {col}', fontsize=10)
            ax.set_ylabel("Frekuensi")

        fig.tight_layout()

        chart_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
        chart_widget = chart_canvas.get_tk_widget()
        chart_widget.pack()

        chart_canvas.draw()

        # Simpan refKerensi agar bisa destroy nanti
        self.chart_canvas = chart_canvas


def start_main_app():
    main_root = tk.Tk()
    app = App(main_root)
    main_root.mainloop()

if __name__ == "__main__":
    login_root = tk.Tk()
    login_app = login.LoginWindow(login_root, start_main_app)
    login_root.mainloop()