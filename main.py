import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image
import imagehash
from tqdm import tqdm
import threading


def are_duplicates(hash_matrix1, hash_matrix2, strength_threshold):
    difference = int(hash_matrix1 - hash_matrix2)
    return abs(difference) <= strength_threshold


def find_duplicates(folder_path, strength_threshold, status_text):
    hash_dict = {}
    duplicates = []

    for filename in tqdm(os.listdir(folder_path), desc="Searching"):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            try:
                file_path = os.path.join(folder_path, filename)
                img = Image.open(file_path)
                hash_matrix = imagehash.average_hash(img)
            except Exception as e:
                print(e)
                continue

            duplicate_found = False
            for existing_hash, existing_path in hash_dict.items():
                if are_duplicates(existing_hash, hash_matrix, strength_threshold):
                    duplicates.append((filename, existing_path))
                    duplicate_found = True
                    break

            if not duplicate_found:
                hash_dict[hash_matrix] = filename

    if not duplicates:
        status_text.set("No duplicates found.")
    else:
        status_text.set(f"{len(duplicates)} duplicates found.")
    return duplicates


def delete_duplicates(folder_path, duplicates, status_text):
    for duplicate in tqdm(duplicates, desc="Deletion"):
        file_path = os.path.join(folder_path, duplicate[0])
        os.remove(file_path)

    status_text.set(f"{len(duplicates)} duplicates deleted.")


def browse_folder(entry_var):
    folder_selected = filedialog.askdirectory()
    entry_var.set(folder_selected)


def browse_save_file(entry_var):
    file_selected = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    entry_var.set(file_selected)


def run_duplicate_checker_thread(folder_var, threshold_var, mode_var, save_file_var, status_text, run_button):
    run_button.config(state=tk.DISABLED)
    thread = threading.Thread(target=run_duplicate_checker, args=(folder_var, threshold_var, mode_var, save_file_var, status_text, run_button))
    thread.start()

def run_duplicate_checker(folder_var, threshold_var, mode_var, save_file_var, status_text, run_button):
    folder_path = folder_var.get()
    mode = mode_var.get()
    save_file_path = save_file_var.get()

    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "Selected folder does not exist.")
        run_button.config(state=tk.NORMAL)
        return
    try:
        strength_threshold = int(threshold_var.get())
    except Exception as e:
        messagebox.showerror("Error", "strength threshold should be integer")
        run_button.config(state=tk.NORMAL)
        return

    if mode == "search only":
        try:
            passed = False
            with open(save_file_path, 'w'):
                pass
            passed = True
        except:
            messagebox.showerror("Error", "save file cannot be created.")
        if passed:
            duplicates = find_duplicates(folder_path, strength_threshold, status_text)
            save_duplicates_to_file(duplicates, save_file_path)

    elif mode == "search and delete":
        duplicates = find_duplicates(folder_path, strength_threshold, status_text)
        delete_duplicates(folder_path, duplicates, status_text)
    else:
        messagebox.showerror("Error", "Invalid mode selected.")

    run_button.config(state=tk.NORMAL)


def save_duplicates_to_file(duplicates, save_file_path):
    with open(save_file_path, 'w') as f:
        for duplicate in duplicates:
            f.write(f"{duplicate[0]} is a duplicate of {duplicate[1]}\n")


def update_save_file_visibility(mode_var, label_save_file, entry_save_file, button_browse_save_file):
    mode = mode_var.get()
    if mode == "search only":
        entry_save_file.grid()
        button_browse_save_file.grid()
        label_save_file.grid()
    else:
        entry_save_file.grid_remove()
        button_browse_save_file.grid_remove()
        label_save_file.grid_remove()


def main():
    root = tk.Tk()
    root.title("Duplicate Images Remover")
    root.resizable(False, False)

    folder_var = tk.StringVar()
    threshold_var = tk.StringVar()
    mode_var = tk.StringVar()
    save_file_var = tk.StringVar()
    status_text = tk.StringVar()

    label_folder = tk.Label(root, text="Select Folder:")
    entry_folder = tk.Entry(root, textvariable=folder_var, width=50)
    button_browse_folder = tk.Button(root, text="Browse", command=lambda: browse_folder(folder_var))

    label_threshold = tk.Label(root, text="Select Strength Threshold (0-4):")
    entry_threshold = tk.Entry(root, textvariable=threshold_var)

    label_mode = tk.Label(root, text="Select Mode:")
    combo_mode = ttk.Combobox(root, textvariable=mode_var, values=["search only", "search and delete"], state="readonly")
    combo_mode.set("search only")
    combo_mode.bind("<<ComboboxSelected>>", lambda event: update_save_file_visibility(mode_var, label_save_file, entry_save_file, button_browse_save_file))

    label_save_file = tk.Label(root, text="Select Save File:")
    entry_save_file = tk.Entry(root, textvariable=save_file_var, width=50)
    button_browse_save_file = tk.Button(root, text="Browse", command=lambda: browse_save_file(save_file_var))

    status_label = tk.Label(root, textvariable=status_text)

    run_button = tk.Button(root, text="Run", width=7, height=1, command=lambda: run_duplicate_checker_thread(
        folder_var, threshold_var, mode_var, save_file_var, status_text, run_button))

    label_folder.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_folder.grid(row=0, column=1, padx=10, pady=10, columnspan=2, sticky="w")
    button_browse_folder.grid(row=0, column=3, padx=10, pady=10)

    label_threshold.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_threshold.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    label_mode.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    combo_mode.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    label_save_file.grid(row=3, column=0, padx=10, pady=10, sticky="w")
    entry_save_file.grid(row=3, column=1, padx=10, pady=10, columnspan=2, sticky="w")
    button_browse_save_file.grid(row=3, column=3, padx=10, pady=10)

    status_label.grid(row=4, column=0, padx=10, pady=10, columnspan=4)

    run_button.grid(row=5, column=0, padx=10, pady=10, columnspan=4)

    root.mainloop()


if __name__ == "__main__":
    main()
