import tkinter as tk
from tkinter import messagebox
import db


class SubcategoryManagementScreen(tk.Frame):
    def __init__(self, master, navigate):
        super().__init__(master)
        self.navigate = navigate
        self.selected_subcategory_id = None

        self.build_ui()
        self.load_subcategories()

    def build_ui(self):
        tk.Button(self, text="<- Back", command=lambda: self.navigate("home")).pack(anchor="w", padx=10, pady=6)
        tk.Label(self, text="Subcategory Management", font=("Segoe UI", 14, "bold")).pack()

        list_frame = tk.Frame(self)
        list_frame.pack(padx=10, pady=6, fill="both", expand=True)

        self.subcategory_listbox = tk.Listbox(list_frame, width=50, height=12)
        self.subcategory_listbox.pack(side="left", fill="both", expand=True)
        self.subcategory_listbox.bind("<<ListboxSelect>>", self.on_select)
        self.item_listbox = self.subcategory_listbox

        button_frame = tk.Frame(self)
        button_frame.pack(pady=6)
        tk.Button(button_frame, 
                  text="Add Subcategory", 
                  width=16, 
                  command=self.open_add
                ).pack(side="left", padx=4)
        tk.Button(button_frame, text="Edit Subcategory", width=16, command=self.open_edit).pack(side="left", padx=4)
        tk.Button(button_frame, text="Delete Subcategory", width=16, command=self.delete_subcategory).pack(side="left", padx=4)

    def load_subcategories(self):
        self.subcategory_listbox.delete(0, tk.END)
        if hasattr(db, "get_all_subcategories"):
            self.subcategories_data = db.get_all_subcategories()
        else:
            self.subcategories_data = db.fetchall("SELECT subcategory_id, name, price FROM Subcategories ORDER BY name")
        self.items_data = self.subcategories_data
        for subcategory in self.subcategories_data:
            self.subcategory_listbox.insert(tk.END, f"{subcategory[1]}  —  {subcategory[2]} VND")

    def on_select(self, event):
        selection = self.subcategory_listbox.curselection()
        if selection:
            self.selected_subcategory_id = self.subcategories_data[selection[0]][0]

    def delete_subcategory(self):
        if not self.selected_subcategory_id:
            messagebox.showwarning("No Selection", "Please select a subcategory first.")
            return
        if messagebox.askyesno("Confirm", "Delete this subcategory?"):
            db.delete_subcategory(self.selected_subcategory_id)
            self.selected_subcategory_id = None
            self.load_subcategories()

    def open_add(self):
        SubcategoryFormPopup(self, subcategory_id=None, on_save=self.load_subcategories)

    def open_edit(self):
        if not self.selected_subcategory_id:
            messagebox.showwarning("No Selection", "Please select a subcategory first.")
            return
        SubcategoryFormPopup(self, subcategory_id=self.selected_subcategory_id, on_save=self.load_subcategories)

    # Aliases for backwards compatibility with old method names
    load_items = load_subcategories
    delete_item = delete_subcategory


class SubcategoryFormPopup(tk.Toplevel):

    def __init__(self, master, subcategory_id, on_save):
        super().__init__(master)
        self.subcategory_id = subcategory_id
        self.on_save = on_save
        if subcategory_id:
            self.title("Edit Subcategory")
        else:
            self.title("Add Subcategory")
        self.geometry("500x600")
        self.grab_set()

        self.build_ui()
        if subcategory_id:
            self.populate()

    def build_ui(self):
        tk.Label(self, text="Subcategory Name:").pack(anchor="w", padx=16, pady=(12, 0))
        self.name_entry = tk.Entry(self, width=40)
        self.name_entry.pack(anchor="w", padx=16)

        tk.Label(self, text="Price (VND):").pack(anchor="w", padx=16, pady=(8, 0))
        self.price_entry = tk.Entry(self, width=20)
        self.price_entry.pack(anchor="w", padx=16)

        tk.Button(self, text="Save Name & Price", command=self.save_subcategory).pack(anchor="w", padx=16, pady=8)

        tk.Label(self, text="Ingredient Costs:").pack(anchor="w", padx=16, pady=(6, 0))

        self.ingredient_listbox = tk.Listbox(self, width=50, height=5)
        self.ingredient_listbox.pack(anchor="w", padx=16, pady=4)

        ingredient_input_frame = tk.Frame(self)
        ingredient_input_frame.pack(anchor="w", padx=16)

        self.ingredient_data = db.get_all_ingredients()
        ingredient_names = []
        for ingredient in self.ingredient_data:
            ingredient_names.append(ingredient[1])

        tk.Label(ingredient_input_frame, text="Ingredient:").pack(side="left")
        if ingredient_names:
            self.ingredient_var = tk.StringVar(value=ingredient_names[0])
            self.ingredient_dropdown = tk.OptionMenu(ingredient_input_frame, self.ingredient_var, *ingredient_names)
        else:
            self.ingredient_var = tk.StringVar(value="")
            self.ingredient_dropdown = tk.OptionMenu(ingredient_input_frame, self.ingredient_var, "None")
        self.ingredient_dropdown.pack(side="left", padx=4)

        tk.Label(ingredient_input_frame, text="Quantity used:").pack(side="left")
        self.ingredient_qty_entry = tk.Entry(ingredient_input_frame, width=8)
        self.ingredient_qty_entry.pack(side="left", padx=4)
        tk.Button(ingredient_input_frame, text="Set", command=self.set_ingredient).pack(side="left", padx=4)

        tk.Button(self, text="Remove Selected Ingredient", command=self.remove_ingredient).pack(anchor="w", padx=16, pady=2)

    def populate(self):
        subcategory = db.fetchone("SELECT name, price FROM Subcategories WHERE subcategory_id = ?", (self.subcategory_id,))
        if subcategory:
            self.name_entry.insert(0, subcategory[0])
            self.price_entry.insert(0, subcategory[1])
        self.reload_ingredients()

    def save_subcategory(self):
        name = self.name_entry.get().strip()
        try:
            price = float(self.price_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")
            return
        if not name:
            messagebox.showerror("Error", "Subcategory name cannot be empty.")
            return

        if self.subcategory_id:
            if hasattr(db, "update_subcategory"):
                db.update_subcategory(self.subcategory_id, name, price)
            else:
                db.execute("UPDATE Subcategories SET name = ?, price = ? WHERE subcategory_id = ?", (name, price, self.subcategory_id))
        else:
            if hasattr(db, "add_subcategory_direct"):
                self.subcategory_id = db.add_subcategory_direct(name, price)
            else:
                first_item = db.fetchone("SELECT item_id FROM Items LIMIT 1")
                item_id = first_item[0] if first_item else 1
                cursor = db.execute("INSERT INTO Subcategories (item_id, name, price) VALUES (?, ?, ?)", (item_id, name, price))
                self.subcategory_id = cursor.lastrowid

        self.on_save()
        messagebox.showinfo("Saved", "Subcategory saved.")

    def reload_ingredients(self):
        self.ingredient_listbox.delete(0, tk.END)
        if not self.subcategory_id:
            return
        if hasattr(db, "get_subcategory_ingredients"):
            self.subcategory_ingredient_data = db.get_subcategory_ingredients(self.subcategory_id)
        else:
            self.subcategory_ingredient_data = db.fetchall(
                """SELECT i.ingredient_id, i.name, si.quantity_used
                   FROM Subcategories_Ingredients si
                   JOIN Ingredients i ON i.ingredient_id = si.ingredient_id
                   WHERE si.subcategory_id = ?""",
                (self.subcategory_id,)
            )
        for row in self.subcategory_ingredient_data:
            self.ingredient_listbox.insert(tk.END, f"{row[1]}  —  {row[2]} units")

    def set_ingredient(self):
        if not self.subcategory_id:
            messagebox.showwarning("Save Subcategory First", "Save the subcategory name and price first.")
            return
        ingredient_name = self.ingredient_var.get()
        match = None
        for ingredient in self.ingredient_data:
            if ingredient[1] == ingredient_name:
                match = ingredient
                break
        if not match:
            messagebox.showerror("Error", "No ingredients exist yet. Add them in Inventory first.")
            return
        try:
            quantity = float(self.ingredient_qty_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number.")
            return
        if hasattr(db, "set_subcategory_ingredient"):
            db.set_subcategory_ingredient(self.subcategory_id, match[0], quantity)
        else:
            db.execute(
                "DELETE FROM Subcategories_Ingredients WHERE subcategory_id = ? AND ingredient_id = ?",
                (self.subcategory_id, match[0])
            )
            db.execute(
                "INSERT INTO Subcategories_Ingredients (subcategory_id, ingredient_id, quantity_used) VALUES (?, ?, ?)",
                (self.subcategory_id, match[0], quantity)
            )
        self.ingredient_qty_entry.delete(0, tk.END)
        self.reload_ingredients()

    def remove_ingredient(self):
        selection = self.ingredient_listbox.curselection()
        if not selection:
            return
        ingredient_id = self.subcategory_ingredient_data[selection[0]][0]
        if hasattr(db, "delete_subcategory_ingredient"):
            db.delete_subcategory_ingredient(self.subcategory_id, ingredient_id)
        else:
            db.execute(
                "DELETE FROM Subcategories_Ingredients WHERE subcategory_id = ? AND ingredient_id = ?",
                (self.subcategory_id, ingredient_id)
            )
        self.reload_ingredients()

    # Aliases
    save_item = save_subcategory
    reload_subcategories = reload_ingredients


# Backward compatibility aliases
SubManagementScreen = SubcategoryManagementScreen
ItemFormPopup = SubcategoryFormPopup
