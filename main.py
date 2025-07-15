import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from modules import c45, predict
from utils import helper
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pemilihan Mahasiswa Berprestasi")
        self.root.geometry("900x600")

        self.sidebar = tk.Frame(root, width=200, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(root, bg="white")
        self.content.pack(side="right", fill="both", expand=True)

        self.label = tk.Label(self.sidebar, text="Pemilihan\nMahasiswa Berprestasi", bg="#2c3e50", fg="white", font=("Arial", 14))
        self.label.pack(pady=20)

        prepare_text = "Replace Model" if helper.is_model_available() else "Add New Model"
        self.btn_prepare = tk.Button(self.sidebar, text=prepare_text, width=20, command=self.prepare_model)
        self.btn_prepare.pack(pady=5)


        self.btn_chart = tk.Button(self.sidebar, text="Tampilkan Basis Data", width=20, command=self.chart)
        self.btn_chart.pack(pady=5)

        self.btn_predict = tk.Button(self.sidebar, text="Prediksi Mahasiswa", width=20, command=self.show_prediction_form)
        self.btn_predict.pack(pady=5)


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

                self.status_label.config(text="Model sudah tersedia. Anda bisa langsung melihat hasil.")
                self.btn_chart.config(state=tk.NORMAL)

            except Exception as e:
                self.status_label.config(text="Gagal memuat model yang tersimpan.")
                self.btn_prepare.config(state=tk.DISABLED)
                self.btn_chart.config(state=tk.DISABLED)
                print(f"Error: {e}")

    def prepare_model(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        
        try:
            self.data = pd.read_csv(file_path)
            self.status_label.config(text="Data berhasil dimuat. Melatih model...")
            self.root.update_idletasks()

            self.result, self.tree, clf = c45.c45_process(self.data)
            helper.save_result((self.result, self.tree))
            helper.save_model(clf)

            self.status_label.config(text="Model berhasil dilatih dan disimpan.")
            self.btn_chart.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
            self.status_label.config(text="Gagal memproses data.")
            self.btn_chart.config(state=tk.DISABLED)

    def chart(self, filepath="data/dummy_500.csv"):
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
        self.chart_canvas.get_tk_widget().pack(pady=10)
    
    def show_prediction_form(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        tk.Label(self.content, text="Form Prediksi Mahasiswa", font=("Arial", 14), bg="white").pack(pady=10)

        # Ambil fitur dari model, bukan dari result
        fitur = list(self.clf.feature_names_in_) if self.clf is not None else []

        self.input_entries = {}
        for feature in fitur:
            frame = tk.Frame(self.content, bg="white")
            frame.pack(pady=5)
            tk.Label(frame, text=feature, width=20, anchor="w", bg="white").pack(side="left")
            entry = tk.Entry(frame, width=30)
            entry.pack(side="left")
            self.input_entries[feature] = entry

        tk.Button(self.content, text="Prediksi", command=self.predict_single).pack(pady=10)
        self.prediction_label = tk.Label(self.content, text="", font=("Arial", 12), bg="white")
        self.prediction_label.pack(pady=10)
        
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


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
