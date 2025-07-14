import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from modules import c45
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

        self.label = tk.Label(self.sidebar, text="Load Model", bg="#2c3e50", fg="white", font=("Arial", 14))
        self.label.pack(pady=20)

        self.btn_prepare = tk.Button(self.sidebar, text="Load Model", width=20, command=self.prepare_model)
        self.btn_prepare.pack(pady=5)

        self.btn_chart = tk.Button(self.sidebar, text="Tampilkan Chart", width=20, command=self.chart)
        self.btn_chart.pack(pady=5)

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
                self.btn_prepare.config(state=tk.DISABLED)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
