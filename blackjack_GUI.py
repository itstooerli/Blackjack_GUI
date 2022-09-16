import tkinter as tk
import blackjack_game_model as bj

class MainApplication(tk.Tk):
  def __init__(self):
    ## Define starting variables w/ user input
    self.num_decks = 6
    self.num_players = 3
    self.user_seat_no = 1
    self.starting_money = 1000
    self.define_settings()

    ## Initialize Main Window
    tk.Tk.__init__(self)
    self.title('Blackjack')
    self.geometry(f"{700 + (self.num_players-3)*200}x500")
    self.configure(background="green")
    self.state('zoomed')
    
    ## Initialize main frame
    ## xx ---------------- xx
    ## xx -----DEALER----- xx
    ## xx -----TABLE------ xx
    ## xx ---------------- xx
    ## xx -COMMAND_FRAME-- xx
    ## xx ---BET_FRAME---- xx
    ## xx ---------------- xx

    main_frame = tk.Frame(self, bg="orange")
    main_frame.pack(pady=10)
    
    bet_frame = tk.Frame(self, bg="purple")
    bet_frame.pack(side=tk.BOTTOM, pady=10)

    bet_label = tk.Label(bet_frame, text="Bet: ", font=("Helvetica", 14))
    bet_label.grid(row=0,column=0)
    bet_value_var = tk.IntVar()
    bet_input = tk.Entry(bet_frame, width=10, textvariable=bet_value_var, font=("Helvetica", 14), justify=tk.CENTER)
    bet_input.grid(row=0,column=1)
    play_button = tk.Button(bet_frame, text="Play (Submit Bet)", font=("Helvetica", 14))
    play_button.grid(row=0,column=2)

    command_frame = tk.Frame(self, bg="gray")
    command_frame.pack(side=tk.BOTTOM)

    hit_button = tk.Button(command_frame, text="Hit", font=("Helvetica", 14), state="disabled")
    hit_button.grid(row=0, column=0,padx=10)
    double_down_button = tk.Button(command_frame, text="Double Down", state="disabled", font=("Helvetica", 14))
    double_down_button.grid(row=0, column=1,padx=10)
    split_button = tk.Button(command_frame, text="Split", font=("Helvetica", 14), state="disabled")
    split_button.grid(row=0, column=2,padx=10)
    stand_button = tk.Button(command_frame, text="Stand", font=("Helvetica", 14), state="disabled")
    stand_button.grid(row=0, column=3,padx=10)

    self.gameModel = bj.BlackjackGameModel(main_frame,
                                          bet_value_var,
                                          bet_input,
                                          play_button,
                                          hit_button,
                                          double_down_button,
                                          split_button,
                                          stand_button,
                                          self.num_decks,
                                          self.num_players,
                                          self.user_seat_no,
                                          self.starting_money)

    play_button.config(command=self.gameModel.reset_table)
    hit_button.config(command=self.gameModel.hit_command)
    double_down_button.config(command=self.gameModel.double_down_command)
    split_button.config(command=self.gameModel.split_command)
    stand_button.config(command=self.gameModel.stand_command)

    self.protocol('WM_DELETE_WINDOW', self.on_exit)

  def define_settings(self):
    settings_window = tk.Tk()
    settings_window.title("Blackjack Settings")
    label_settings_title = tk.Label(text="Initialize Settings...\n Must click Submit to change setting.")
    label_settings_title.grid(row=0,column=0,columnspan=3)
    
    entry_width = 10 ## Width of each entry space in settings window

    ## Setting number of 52-card decks to use
    min_num_decks = 1
    max_num_decks = 10

    num_decks_var = tk.IntVar()
    num_decks_var.set(self.num_decks)
    
    def set_num_decks():
      try:
        input_num_decks = num_decks_var.get()
        if min_num_decks <= input_num_decks <= max_num_decks:
          self.num_decks = input_num_decks
        
        num_decks_var.set(self.num_decks)
      except:
        num_decks_var.set(self.num_decks)

    label_num_decks = tk.Label(text=f"Number of decks [{min_num_decks}, {max_num_decks}]: ")
    entry_num_decks = tk.Entry(width=entry_width, textvariable=num_decks_var)
    button_num_decks = tk.Button(text="Submit",command=set_num_decks)
    label_num_decks.grid(row=1,column=0)
    entry_num_decks.grid(row=1,column=1)
    button_num_decks.grid(row=1,column=2)

    ## Setting number of players at table
    min_num_players = 1
    max_num_players = 6

    num_players_var = tk.IntVar()
    num_players_var.set(self.num_players)

    def set_num_players():
      try:
        input_num_players = num_players_var.get()
        if min_num_players <= input_num_players <= max_num_players:
          self.num_players = input_num_players

        num_players_var.set(self.num_players)

        if self.num_players < self.user_seat_no:
          ## If the number of players was changed to a value less
          ## than the user's current position, reset position to 1
          self.user_seat_no = 1
          user_seat_no_var.set(self.user_seat_no)

      except:
        num_players_var.set(self.num_players)

    label_num_players = tk.Label(text=f"Number of players (player + computer) [{min_num_players}, {max_num_players}]: ")
    entry_num_players = tk.Entry(width=entry_width, textvariable=num_players_var)
    button_num_players = tk.Button(text="Submit",command=set_num_players)
    label_num_players.grid(row=2,column=0)
    entry_num_players.grid(row=2,column=1)
    button_num_players.grid(row=2,column=2)

    ## Setting position of player (1-indexed)
    min_user_seat_no = 1

    user_seat_no_var = tk.IntVar()
    user_seat_no_var.set(self.user_seat_no)

    def set_user_seat_no():
      try:
        input_seat_no = user_seat_no_var.get()
        if min_user_seat_no <= input_seat_no <= self.num_players:
          self.user_seat_no = input_seat_no
    
        user_seat_no_var.set(self.user_seat_no)
      except:
        user_seat_no_var.set(self.user_seat_no)

    label_seat_no = tk.Label(text=f"Player's seat number [{min_user_seat_no}, number of players]: ")
    entry_seat_no = tk.Entry(width=entry_width, textvariable=user_seat_no_var)
    button_seat_no = tk.Button(text="Submit",command=set_user_seat_no)
    label_seat_no.grid(row=3,column=0)
    entry_seat_no.grid(row=3,column=1)
    button_seat_no.grid(row=3,column=2)

    ## Setting starting money for user
    min_starting_money = 1
    max_starting_money = 1000000000

    starting_money_var = tk.IntVar()
    starting_money_var.set(self.starting_money)

    def set_starting_money():
      try:
        input_starting_money = starting_money_var.get()
        if min_starting_money <= input_starting_money <= max_starting_money:
          self.starting_money = input_starting_money
    
        starting_money_var.set(self.starting_money)
      except:
        starting_money_var.set(self.starting_money)

    label_starting_money = tk.Label(text="Player's starting money [1,1000000000]: ")
    entry_starting_money = tk.Entry(width=entry_width, textvariable=starting_money_var)
    button_starting_money = tk.Button(text="Submit",command=set_starting_money)
    label_starting_money.grid(row=4,column=0)
    entry_starting_money.grid(row=4,column=1)
    button_starting_money.grid(row=4,column=2)

    ## Create Start Game Button
    def start_game():
      settings_window.destroy()

    button_start_game = tk.Button(text="Start Game",height=2,command=start_game)
    button_start_game.grid(row=5, columnspan=3)

    settings_window.mainloop()

  def on_exit(self):
    ## This is necessary since we automatically start waiting for user command and
    ## tkinter will start a mini-loop and won't exit the program even if the user
    ## has closed it. This solution allows the mini-loop to break, system to quit,
    ## then the objects to be destroyed
    ## Proving SO: https://stackoverflow.com/questions/56175296/unable-to-exit-tkinter-app-when-using-wait-variable
    self.gameModel.stand_command()
    self.quit()

def main():
  app = MainApplication()
  app.mainloop()

if __name__ == "__main__":
  main()