import tkinter as tk
import tkinter.messagebox as tkmb
import sqlite3
import webbrowser

DATABASE_FILE = "nyc.db"  # CHANGE TO MATCH YOUR .db FILE
conn = sqlite3.connect(DATABASE_FILE)
cur = conn.cursor()

class MainWin(tk.Tk):
    """Main Window."""
    def __init__(self):
        super().__init__()

        self.title("Restaurants")
        self.geometry("720x960+700+50")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.closefct)

        # Load background image
        self.bg_image = tk.PhotoImage(file="iykyk.png") 

        # Create a Label widget with the image and place it in the background
        background_label = tk.Label(self, image=self.bg_image)
        background_label.place(relwidth=1, relheight=1)  

        # Create all other widgets and place them on top of the background
        titleLabel = tk.Label(self, text="Local Michelin Guide Restaurants", font=("Arial", 25, "bold"), fg="blue", anchor='center', justify='center', bg="white")
        titleLabel.pack(pady=10)

        purposeLabel = tk.Label(self, text="Receive Data From Restaurants", font=("Arial", 17), bg="white")
        purposeLabel.pack(pady=10)

        searchByLabel = tk.Label(self, text="Search By:", font=("Arial", 15), bg="white")
        searchByLabel.pack(pady=10)

        buttonFrame = tk.Frame(self, bg="white")
        buttonFrame.pack(pady=10)

        cityButton = tk.Button(buttonFrame, text="City", font=("Arial", 15, "bold"), fg="blue", width=10, height=5, command=lambda: self.buttonFct("city"))
        cuisineButton = tk.Button(buttonFrame, text="Cuisine", font=("Arial", 15, "bold"), fg="blue", width=10, height=5, command=lambda: self.buttonFct("cuisine"))
        cityButton.pack(side=tk.LEFT)
        cuisineButton.pack(side=tk.LEFT)

    def buttonFct(self, choice):
        """When Any Of The Buttons Are Clicked From Main Window"""
        cityorcuisChoice = DialogWin(self, choice)
        self.wait_window(cityorcuisChoice)
        if not (cityorcuisChoice.getChoice())[0] == 0:
            restaurantChoice = DialogWin(self, *(cityorcuisChoice.getChoice()))
            self.wait_window(restaurantChoice)
            if (restaurantChoice.getChoice())[0] != 0:
                for r in (restaurantChoice.getChoice())[0]:
                    restaurantDisplay = DisplayWin(self, r)

    def closefct(self):
        """When User Tries To Exit Out Of Main Window"""
        val = tkmb.askokcancel("Confirm close", "Are you sure you want to close?", parent=self)
        if val:
            self.destroy()
            self.quit()

class DisplayWin(tk.Toplevel):
    """Window For Showing Restaurant Data"""
    def __init__(self, master, restaurant):
        super().__init__(master)
        self.geometry("500x500+1200+240")
        self.resizable(False, False)

        try:
            cur.execute("SELECT * FROM MainTable WHERE name = ?", (restaurant,))
            data = cur.fetchone()
            name, url, address = (data[0], data[1], data[5])
            cur.execute("SELECT * FROM CostTable WHERE id = ?", (data[3],))
            cost = cur.fetchone()[1]
            cur.execute("SELECT * FROM CuisineTable WHERE id = ?", (data[4],))
            cuisine = cur.fetchone()[1]
        except sqlite3.Error as e:
            tkmb.showinfo("no such table:", str(e), parent=self)
            conn.close()
            raise SystemExit()

        nameLabel = (tk.Label(self, text=name, font=("Arial", 25, "bold"), fg="orange", anchor='center', justify='center'))
        nameLabel.pack(pady=10)

        addressLabel = (tk.Label(self, text=address, font=("Arial", 15), anchor='center', justify='center'))
        addressLabel.pack(pady=10)

        costLabel = (tk.Label(self, text="Cost: " + cost, font=("Arial", 15), anchor='center', justify='center'))
        costLabel.pack(pady=10)

        cuisineLabel = (tk.Label(self, text="Cuisine: " + cuisine, font=("Arial", 15), fg="green", anchor='center', justify='center'))
        cuisineLabel.pack(pady=10)

        button = tk.Button(self, text="Visit Webpage", font=("Arial", 15, "bold"), width=10, height=5, command=lambda: webbrowser.open(url))
        button.pack(pady=10)

class DialogWin(tk.Toplevel):
    """Dialogue Window"""
    def __init__(self, master, choice, buttonChoice=""):
        super().__init__(master)
        self.grab_set()
        self.geometry("+1200+240")
        self.resizable(False, False)

        self.buttonChoice = choice
        self.choiceID = 0

        if not isinstance(choice, int):
            choiceLabel = (tk.Label(self, text="Click On A " + choice.title() + " To Select", font=("Arial", 12), anchor='center', justify='center'))
        else:
            choiceLabel = (tk.Label(self, text="Click On A Restaurant To Select", font=("Arial", 12), anchor='center', justify='center'))
        choiceLabel.pack(pady=10)

        try:
            if choice == "city":
                listbox = tk.Listbox(self, selectmode="single", height=6)
                cur.execute("SELECT * FROM CityTable")
                for city in cur.fetchall():
                    listbox.insert(tk.END, city[1])
            elif choice == "cuisine":
                listbox = tk.Listbox(self, selectmode="single", height=6)
                cur.execute("SELECT * FROM CuisineTable")
                for cuisine in cur.fetchall():
                    listbox.insert(tk.END, cuisine[1])
            else:
                listbox = tk.Listbox(self, selectmode="multiple", height=6)
                query = f"SELECT name FROM MainTable WHERE {buttonChoice} = {choice}"
                cur.execute(query)
                for r in cur.fetchall():
                    listbox.insert(tk.END, r[0])
        except sqlite3.Error as e:
            tkmb.showinfo("no such table:", str(e), parent=self)
            conn.close()
            raise SystemExit()

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        def selectFct():
            """Sets Selected Choice From List Box"""
            if buttonChoice == "":
                self.choiceID = listbox.curselection()[0] + 1
            else:
                self.choiceID = [listbox.get(index) for index in listbox.curselection()]
            self.destroy()

        button = tk.Button(self, text="Click To Select", command=selectFct)
        listbox.pack()
        button.pack(pady=10)

    def getChoice(self):
        """Returns Selected Choice From List Box"""
        return self.choiceID, self.buttonChoice

if __name__ == "__main__":
    conn.close()  # Close DB connection if frontend.py is directly run
