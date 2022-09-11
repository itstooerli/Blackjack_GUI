import tkinter as tk

def define_settings(num_decks, num_players, user_seat_no, starting_money):
  ## Start Settings GUI
  settings_window = tk.Tk()
  settings_window.title("Blackjack")
  # settings_window.geometry("500x300")
  label_settings_title = tk.Label(text="Initialize Settings...")
  label_settings_title.grid(row=0,column=0,columnspan=3)

  ## Set GUI Sizing Variables
  entry_width = 10
  
  num_decks_var = tk.StringVar()
  num_decks_var.set(num_decks)
  
  num_players_var = tk.StringVar()
  num_players_var.set(num_players)
  
  seat_no_var = tk.StringVar()
  seat_no_var.set(user_seat_no)
  
  starting_money_var = tk.StringVar()
  starting_money_var.set(starting_money)
  
  def set_num_decks():
    global num_decks
    try:
      input_num_decks = int(float(num_decks_var.get()))
      if 0 < input_num_decks < 101:
        num_decks = input_num_decks
      
      num_decks_var.set(num_decks)
    except:
      num_decks_var.set(num_decks)
  
  def set_num_players():
    global num_players
    try:
      input_num_players = int(float(num_players_var.get()))
      if 0 < input_num_players < 11:
        num_players = input_num_players
  
      num_players_var.set(num_players)
    except:
      num_players_var.set(num_players)
  
  def set_user_seat_no():
    global user_seat_no
    try:
      input_seat_no = int(float(seat_no_var.get()))
      if 0 < input_seat_no < num_players + 1:
        user_seat_no = input_seat_no
  
      seat_no_var.set(user_seat_no)
    except:
      seat_no_var.set(user_seat_no)
  
  def set_starting_money():
    global starting_money
    try:
      input_starting_money = int(float(starting_money_var.get()))
      if 0 < input_starting_money < 1000000001:
        starting_money = input_starting_money
  
      starting_money_var.set(starting_money)
    except:
      starting_money_var.set(starting_money)
  
  def start_game():
    settings_window.destroy()
  
  label_num_decks = tk.Label(text="Number of decks [1, 100]: ")
  entry_num_decks = tk.Entry(width=entry_width, textvariable=num_decks_var)
  button_num_decks = tk.Button(text="Submit",command=set_num_decks)
  label_num_decks.grid(row=1,column=0)
  entry_num_decks.grid(row=1,column=1)
  button_num_decks.grid(row=1,column=2)
  
  label_num_players = tk.Label(text="Number of players (player + computer) [1,10]: ")
  entry_num_players = tk.Entry(width=entry_width, textvariable=num_players_var)
  button_num_players = tk.Button(text="Submit",command=set_num_players)
  label_num_players.grid(row=2,column=0)
  entry_num_players.grid(row=2,column=1)
  button_num_players.grid(row=2,column=2)
  
  label_seat_no = tk.Label(text="Player's seat number [1, number of players]: ")
  entry_seat_no = tk.Entry(width=entry_width, textvariable=seat_no_var)
  button_seat_no = tk.Button(text="Submit",command=set_user_seat_no)
  label_seat_no.grid(row=3,column=0)
  entry_seat_no.grid(row=3,column=1)
  button_seat_no.grid(row=3,column=2)
  
  label_starting_money = tk.Label(text="Player's starting money [1,1000000000]: ")
  entry_starting_money = tk.Entry(width=entry_width, textvariable=starting_money_var)
  button_starting_money = tk.Button(text="Submit",command=set_starting_money)
  label_starting_money.grid(row=4,column=0)
  entry_starting_money.grid(row=4,column=1)
  button_starting_money.grid(row=4,column=2)
  
  button_start_game = tk.Button(text="Start Game",height=2,command=start_game)
  button_start_game.grid(row=5, columnspan=3)

  settings_window.mainloop()