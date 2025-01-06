import tkinter as tk

root = tk.Tk()

# Membuat Text
analysis_box = tk.Text(root, height=10, width=30)
analysis_box.pack()

# Menambahkan teks ke Text widget
analysis_result = "Hasil analisis baru"
analysis_box.insert(tk.END, analysis_result)

root.mainloop()
