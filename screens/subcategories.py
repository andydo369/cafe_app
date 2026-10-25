import tkinter as tk
from tkinter import messagebox
import db


class SubcategoryManagementScreen(tk.Frame):
    def __init__(self, master, navigate):
        super().__init__(master)
        self.navigate = navigate
        self.selected_id = None

        self.build_ui()
        self.load_subcategories()

    def build_ui(self):
        tk.Button(self, 
                  text="<- Back",    
                  command=lambda: self.navigate("home")
                  ).pack(anchor="w", padx=10, pady=6)
        tk.Label(self, 
                  text="Subcategory Management", 
                  font=("Segoe UI", 14, "bold")
                  ).pack()

        list_frame = tk.Frame(self)
        list_frame.pack(padx=10, pady=6, fill="both", expand=True)

        self.subcategory_listbox = tk.Listbox(list_frame, width=50, height=12)
        self.subcategory_listbox.pack(side="left", fill="both", expand=True)
        self.subcategory_listbox.bind("<<ListboxSelect>>", self.on_select)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=6)
        tk.Button(button_frame, 
                  text="Add Subcategory", 
                  width=14, 
                  command=self.open_add
                ).pack(side="left", padx=4)
        tk.Button(button_frame, 
                  text="Edit Subcategory", 
                  width=14, 
                  command=self.open_edit
                ).pack(side="left", padx=4)
        tk.Button(button_frame, 
                  text="Delete Subcategory", 
                  width=14, 
                  command=self.delete_subcategory
                ).pack(side="left", padx=4)

    def load_subcategories(self):
        self.subcategory_listbox.delete(0, tk.END)
        self.subcategories_data = db.get_all_subcategories()
        for subcategory in self.subcategories_data:
            self.subcategory_listbox.insert(tk.END, f"{subcategory[1]}  —  {subcategory[2]} VND")

    def on_select(self, event):
        selection = self.subcategory_listbox.curselection()
        if selection:
            self.selected_id = self.subcategories_data[selection[0]][0]

    def delete_subcategory(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a subcategory first.")
            return
        if messagebox.askyesno("Confirm", "Delete this subcategory?"):
            db.delete_subcategory(self.selected_id)
            self.selected_id = None
            self.load_subcategories()

    def open_add(self):
        SubcategoryFormPopup(self, item_id=None, on_save=self.load_subcategories)

    def open_edit(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select an subcategory first.")
            return
        SubcategoryFormPopup(self, item_id=self.selected_id, on_save=self.load_subcategories)


class SubcategoryFormPopup(tk.Toplevel):

    def __init__(self, master, item_id, on_save):
        super().__init__(master)
        self.subcategory_id = item_id
        self.on_save = on_save
        if item_id:
            self.title("Edit Subcategory")
        else:
            self.title("Add Subcategory")
        self.geometry("500x600")
        self.grab_set()

        self.build_ui()
        if item_id:
            self.populate()

    def build_ui(self):
        tk.Label(self, 
                 text="Subcategory Name:" 
                 ).pack(anchor="w", padx=16, pady=(12, 0))
        self.name_entry = tk.Entry(self, width=40)
        self.name_entry.pack(anchor="w", padx=16)

        tk.Label(self, 
                 text="Price (VND):" 
                 ).pack(anchor="w", padx=16, pady=(8, 0))
        self.price_entry = tk.Entry(self, width=20)
        self.price_entry.pack(anchor="w", padx=16)

        tk.Button(self, 
                 text="Save Name & Price", 
                 command=self.save_item 
                 ).pack(anchor="w", padx=16, pady=8)


    def populate(self):
        item = db.get_subcategory_by_id(self.subcategory_id)
        if item:
            self.name_entry.insert(0, item[1])
            self.price_entry.insert(0, item[2])


    def save_item(self):
        name = self.name_entry.get().strip()
        try:
            price = float(self.price_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")
            return
        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        if self.subcategory_id:
            db.update_subcategory(self.subcategory_id, name, price)
        else:
            self.subcategory_id = db.add_subcategory(name, price)

        self.on_save()
        messagebox.showinfo("Saved", "Subcategory saved.")