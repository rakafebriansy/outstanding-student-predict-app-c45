import matplotlib.pyplot as plt

def show_chart(result):
    summary = result['Hasil'].value_counts()
    summary.plot(kind='bar', color='skyblue')
    plt.title("Hasil Pemilihan Mahasiswa Berprestasi")
    plt.xlabel("Kategori")
    plt.ylabel("Jumlah Mahasiswa")
    plt.tight_layout()
    plt.show()
