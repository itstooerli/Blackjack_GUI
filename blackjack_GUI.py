import tkinter as tk
from PIL import Image, ImageTk
# from functools import partial
import random
import math
import copy
from enum import Enum
# import blackjack_settings

class BlackjackGameModel:
  def __init__(self, main_frame, num_decks, num_players, user_seat_no, starting_money):
    self.main_frame = main_frame
    self.base_deck = self.create_deck(num_decks)
    self.user_seat_no = user_seat_no
    self.table = self.setup_table(self.main_frame, num_players, user_seat_no, starting_money)
    self.curr_deck = []
    self.reshuffle_cutoff = 1
    self.player_standing = tk.BooleanVar()

  class Card:
    def __init__(self, suit=None, card=None, value=None, image=None):
      self.suit = suit    # Stores the suit of the card, e.g. Clubs
      self.card = card    # Stores the number of the card, e.g. K or 3
      self.value = value  # Stores the value of the card for this game, e.g. K = 10, 3 = 3
      self.image = image  # Stores the image of the card for the GUI

    def copy(self):
      copyobj = BlackjackGameModel.Card()
      for key, value in self.__dict__.items():
        if key == "image":
          copyobj.__dict__[key] = value
        else:
          copyobj.__dict__[key] = copy.deepcopy(value)
      return copyobj
  
  class Hand:
    def __init__(self, cards, score, num_aces, bet):
      self.cards = cards        # Stores an array of Cards
      self.score = score        # Stores the cumulative score
      self.num_aces = num_aces  # Stores the number of aces, since in Blackjack, Ace = 11 or 1
      self.bet = bet            # If the type is a player/AI, what is current bet up to
      self.status = HandStatus.ACTIVE  # Status of the hand

  class Seat:
    def __init__(self, type, money=1000000, base_bet=100, frame=None):   
      self.type = type          # Stores the type of seat this is
      self.hand = []            # Stores the seat's hand as list of Hands
      self.money = money        # If the type is a player/AI, how much money does the player have
      self.base_bet = base_bet  # If the type is a player/AI, what was initial bet
      self.frame = frame        # Stores the frame for this Seat
  
  def create_deck(self, num_decks):
    ## These values may be unique to blackjack
    suit_values = {"Spades":"\u2664", "Hearts":"\u2661", "Clubs":"\u2667", "Diamonds":"\u2662"}
    card_values = {"A":11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}
    
    # Define basic components of a deck of cards
    deck = []
    suits = ["Spades", "Hearts", "Clubs", "Diamonds"]
    cards = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
  
    for suit in suits:
      for card in cards:
        card_image = self.resize_card(f'cards/{card}_of_{suit}.png')
        for i in range(num_decks):
          deck.append(self.Card(suit_values[suit], card, card_values[card], card_image))
    return deck

  def resize_card(self, card):
    card_img = Image.open(card)
    card_img_resized = card_img.resize((50, 73))
  
    global card_img_global
    card_img_global = ImageTk.PhotoImage(card_img_resized)
    return card_img_global
  
  def setup_table(self, main_frame, num_players, player_seat_no, player_money):
    ## Create frame for dealer above frame for rest of table
    dealer_frame = tk.LabelFrame(main_frame, text="Dealer", bd=0, bg="blue")
    dealer_frame.grid(row=0, column=0, padx=20, ipadx=20)
    table_frame = tk.LabelFrame(main_frame, text="Table", bd=0, bg="yellow")
    table_frame.grid(row=1, column=0, padx=20)
    
    # Create table as list of Seats
    table = []
    for player_no in range(num_players):
      if player_no == player_seat_no - 1:
        ## Initialize the player (Index 1)
        table.append(self.Seat(SeatType.PLAYER, player_money))
        table[player_no].base_bet = min(100, -(-player_money // 10)) ## 100 or Round-up Integer Divsion
      else:
        ## Create AI Seats
        table.append(self.Seat(SeatType.AI))
  
      ## Create a frame for this player
      frame = tk.LabelFrame(table_frame, text=f'Player {player_no + 1}', bd=0, bg = 'magenta')
      frame.grid(row=0, column=player_no, padx=20)
      table[player_no].frame = frame
  
    ## The last seat is always the dealer
    table.append(self.Seat(SeatType.DEALER))
    table[-1].frame = dealer_frame
  
    return table

  def reset_table(self):
    play_button.config(state="disabled")
    for seat in self.table:
      for label in seat.frame.winfo_children():
        label.destroy()
    
    # print("number of labels:", len(self.table[0].frame.winfo_children()))
    # print("curr_deck length:", len(self.curr_deck))
    self.play_game()

  def shuffle_deck(self):
    # curr_deck = copy.deepcopy(self.base_deck)
    self.curr_deck = [card.copy() for card in self.base_deck]
    self.reshuffle_cutoff = random.randrange(math.floor(len(self.base_deck) * 0.25), math.floor(len(self.base_deck) * 0.5))

  def display_card(self, seat, hand_number, new_card):
    label = tk.Label(seat.frame, image=new_card.image)
    label.grid(row=hand_number, column=len(seat.hand[hand_number].cards))
  
  def deal_cards(self):
    # Initialize each seat's hand
    for seat in self.table:
      seat.hand = [self.Hand([], 0, 0, seat.base_bet)]
  
    self.table[-1].hand[0].status = HandStatus.DEALER
  
    # Deal each seat 2 cards
    num_cards = 0
    while num_cards < 2:
      for seat in self.table:
        new_card = random.choice(self.curr_deck)
        self.display_card(seat, 0, new_card)
        seat.hand[0].cards.append(new_card)
        seat.hand[0].score += new_card.value
  
        if new_card.card == "A":
          seat.hand[0].num_aces += 1
  
        self.curr_deck.remove(new_card)
  
        # If hand receives two aces, treat one of the aces as a 1
        if seat.hand[0].score == 22:
          seat.hand[0].cards[1].value = 1
          seat.hand[0].score = 12
          seat.hand[0].num_aces -= 1
  
      num_cards = num_cards + 1

    ## Hide the dealer's second card
    default_image = self.resize_card(f'cards/default.png') ## TODO: Optimize to avoid always resizing the same image
    label = tk.Label(self.table[-1].frame, image=default_image)
    label.grid(row=0,column=1)

  def deal_new_card(self, seat, hand):
    # Deal a new card from the provided deck to the provided cards and update the provided score
    new_card = random.choice(self.curr_deck)
    self.display_card(seat, 0, new_card) ## TODO: Fix hand_number to accommodate split
    hand.cards.append(new_card)
    hand.score += new_card.value
    self.curr_deck.remove(new_card)
  
    if new_card.card == "A":
      hand.num_aces += 1
  
    if hand.score > 21 and hand.num_aces > 0:
      hand.score -= 10
      hand.num_aces -= 1
  
      for card in hand.cards:
        if card.card == "A":
          card.value = 1
          break
  
  def play_game(self):
    ## TODO: Need to define bets
    bet_input.config(state="disabled")
    ## TODO: Need to check if seats have blackjack 
    print(len(self.curr_deck), self.reshuffle_cutoff)
    if len(self.curr_deck) < self.reshuffle_cutoff:
      self.shuffle_deck()
      print('shuffled', len(self.curr_deck))
  
    self.deal_cards()
    
    for seat in self.table:
      if seat.type == SeatType.AI:
        ## TODO: Implement more difficult AI logic
        while seat.hand[0].score < 17:
          self.deal_new_card(seat, seat.hand[0])
      elif seat.type == SeatType.PLAYER:
        hit_button.config(state="active")
        double_down_button.config(state="active")
        stand_button.config(state="active")
        
        if len(seat.hand[0].cards) == 2:
          if seat.hand[0].cards[0].card == seat.hand[0].cards[1].card or seat.hand[0].cards[0].value == seat.hand[0].cards[1].value:
            split_button.config(state="active")
            
        stand_button.wait_variable(self.player_standing)
        print("score", seat.hand[0].score)
  
        hit_button.config(state="disabled")
        double_down_button.config(state="disabled")
        split_button.config(state="disabled")
        stand_button.config(state="disabled")
        
      elif seat.type == SeatType.DEALER:
        ## Reveal card
        label = tk.Label(self.table[-1].frame, image=self.table[-1].hand[0].cards[-1].image)
        label.grid(row=0,column=1)
        ## Play out rest of card
  
        ## TODO: Do not play out if any active hands (see original code)
  
        while seat.hand[0].score < 17:
          self.deal_new_card(seat, seat.hand[0])
  
        print(seat.hand[0].score)

      print("player", seat, "has played")
    
    ## Calculate payouts

    ## Config Buttons
    play_button.config(state="active")

  def hit_command(self):
    ## Debug
    print(self.player_standing.get())

    seat = self.table[self.user_seat_no - 1]
    hand = seat.hand[0]
    self.deal_new_card(seat, hand)
  
    if hand.score > 21:
      print('hit command function: bust')
      self.stand_command()

  def stand_command(self):
    self.player_standing.set(not self.player_standing)
    print(self.player_standing.get())

class SeatType(Enum):
  PLAYER = 0
  AI = 1
  DEALER = 2

class HandStatus(Enum):
  ACTIVE = 0
  BLACKJACK = 1
  WINNER = 2
  TIE = 3
  LOSER = 4
  DEALER = 5
  WAITING = 6

def define_settings(num_decks, num_players, player_seat_no, starting_money):
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
  seat_no_var.set(player_seat_no)
  
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
  
  def set_player_seat_no():
    global player_seat_no
    try:
      input_seat_no = int(float(seat_no_var.get()))
      if 0 < input_seat_no < num_players + 1:
        player_seat_no = input_seat_no
  
      seat_no_var.set(player_seat_no)
    except:
      seat_no_var.set(player_seat_no)
  
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
  button_seat_no = tk.Button(text="Submit",command=set_player_seat_no)
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

if __name__ == "__main__":
  ## Set Default Values
  num_decks = 6
  num_players = 6
  user_seat_no = 1
  starting_money = 1000

  ## TODO: Figure out how to move this function to a different script
  # define_settings(num_decks, num_players, user_seat_no, starting_money)
  ## For Debugging
  # print(num_decks)
  # print(num_players)
  # print(user_seat_no)
  # print(starting_money)

  ## Initialize main window
  ## xx ---------------- xx
  ## xx -----DEALER----- xx
  ## xx -----TABLE------ xx
  ## xx ---------------- xx
  ## xx -PLAYER ACTIONS- xx
  ## xx ---BET ACTION--- xx
  ## xx ---------------- xx
  
  root = tk.Tk()
  root.title("Blackjack")
  root.geometry("900x400")
  root.configure(background="green")

  main_frame = tk.Frame(root, bg="orange")
  main_frame.pack(pady=10)

  gameModel = BlackjackGameModel(main_frame, num_decks, num_players, user_seat_no, starting_money)

  bet_frame = tk.Frame(root, bg="purple")
  bet_frame.pack(side=tk.BOTTOM, pady=10)

  bet_label = tk.Label(bet_frame, text="Bet: ", font=("Helvetica", 14))
  bet_label.grid(row=0,column=0)
  
  bet_value_var = tk.StringVar()
  bet_value_var.set(gameModel.table[user_seat_no - 1].base_bet)
  bet_input = tk.Entry(bet_frame, width=10, textvariable=bet_value_var, font=("Helvetica", 14), justify=tk.CENTER)
  bet_input.grid(row=0,column=1)
  
  play_button = tk.Button(bet_frame, text="Play (Submit Bet)", font=("Helvetica", 14), command=gameModel.reset_table)
  play_button.grid(row=0,column=2)
  
  command_frame = tk.Frame(root, bg="gray")
  command_frame.pack(side=tk.BOTTOM)
  
  hit_button = tk.Button(command_frame, text="Hit", font=("Helvetica", 14), state="disabled", command=gameModel.hit_command)
  hit_button.grid(row=0, column=0,padx=10)

  double_down_button = tk.Button(command_frame, text="Double Down", state="disabled", font=("Helvetica", 14))
  double_down_button.grid(row=0, column=1,padx=10)

  split_button = tk.Button(command_frame, text="Split", font=("Helvetica", 14), state="disabled")
  split_button.grid(row=0, column=2,padx=10)

  stand_button = tk.Button(command_frame, text="Stand", font=("Helvetica", 14), state="disabled", command=gameModel.stand_command)
  stand_button.grid(row=0, column=3,padx=10)
  
  root.mainloop()