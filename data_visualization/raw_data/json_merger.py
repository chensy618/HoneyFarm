import json
import tkinter as tk
from tkinter import filedialog, messagebox

class JSONMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Log Merger")
        self.root.geometry("300x180")  # Set window size

        self.file1_path = ""
        self.file2_path = ""

        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(expand=True)

        # File selection buttons
        self.btn_file1 = tk.Button(frame, text="Select First JSON File", command=self.load_file1, width=25)
        self.btn_file1.pack(pady=5)

        self.btn_file2 = tk.Button(frame, text="Select Second JSON File", command=self.load_file2, width=25)
        self.btn_file2.pack(pady=5)

        # Merge button
        self.merge_button = tk.Button(frame, text="Merge Files", command=self.merge_files, width=25)
        self.merge_button.pack(pady=10)

    def load_file1(self):
        self.file1_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if self.file1_path:
            messagebox.showinfo("File 1 Loaded", f"Path: {self.file1_path}")

    def load_file2(self):
        self.file2_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if self.file2_path:
            messagebox.showinfo("File 2 Loaded", f"Path: {self.file2_path}")

    def merge_files(self):
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Warning", "Please select both files before merging.")
            return

        try:
            merged_data = []

            for path in [self.file1_path, self.file2_path]:
                with open(path, 'r') as f:
                    for line in f:
                        merged_data.append(json.loads(line))

            # Sort by timestamp field if present
            merged_data.sort(key=lambda x: x.get("timestamp", ""))

            # Save merged file
            save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if save_path:
                with open(save_path, 'w') as out:
                    for item in merged_data:
                        out.write(json.dumps(item) + '\n')
                messagebox.showinfo("Success", f"Merged file saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge files:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONMergerApp(root)
    root.mainloop()
