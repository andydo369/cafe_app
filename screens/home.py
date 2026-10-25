import tkinter as tk
import state


class HomeScreen(tk.Frame):
    def __init__(self, master, navigate): # takes root and navigate from main.py
        super().__init__(master)

        tk.Label(self, 
                 text="Boba Tea POS", 
                 font=("Segoe UI", 18, "bold")).pack(pady=30)
        tk.Label(self, text=f"Logged in as: {state.role}").pack()

        if state.role == "manager":
            # tk.Button(  self, 
            #             text="Item Management", 
            #             width=25,
            #             command=navigate # this is the conventional way of using callback function, but if we do this we cannot pass in the parameters such as "items" -> needs lambda to pass in parameters
            #         ).pack(pady=8) # when clicked navigates like in main.py

            tk.Button(
                        self, 
                        text="Item Management", 
                        width=25,
                        command=lambda: navigate("items") # quick way to create a function in one line
                    ).pack(pady=8) # when clicked navigates like in main.py
            
            tk.Button(
                        self, 
                        text="Subcategory Management", 
                        width=25,
                        command=lambda: navigate("subcategories") # quick way to create a function in one line
                    ).pack(pady=8) # when clicked navigates like in main.py

            tk.Button(self, text="Inventory", width=25,
                      command=lambda: navigate("inventory")).pack(pady=8)
            tk.Button(self, text="Business Reports", width=25,
                      command=lambda: navigate("reports")).pack(pady=8)
        else:
            tk.Button(self, text="Order Processing", width=25,
                      command=lambda: navigate("order")).pack(pady=8)
            tk.Button(self, text="Inventory", width=25,
                      command=lambda: navigate("inventory")).pack(pady=8)

        tk.Button(self, text="Logout", width=25,
                  command=lambda: navigate("logout")).pack(pady=20)
