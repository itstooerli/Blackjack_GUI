import tkinter as tk
from PIL import Image, ImageTk
import random
import math
import copy
import os
from enum import Enum
# import blackjack_settings

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

class Card:
  def __init__(self, suit=None, card=None, value=None, image=None):
    # Stores the suit of the card, e.g. Clubs
    self.suit = suit

    # Stores the number of the card, e.g. K or 3
    self.card = card

    # Stores the value of the card for this game, e.g. K = 10, 3 = 3
    self.value = value

    # Stores the image of the card for the GUI
    self.image = image

  # def copy(self):
  #   copyobj = Card()
  #   for name, attr in self.__dict__.items():
  #       if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
  #         copyobj.__dict__[name] = attr.copy()
  #       else:
  #         print(name, attr)
  #         copyobj.__dict__[name] = copy.deepcopy(attr)
  #   return copyobj

  # def copy(self):
  #   clone = copy.copy(self) # to copy __dict__ only
  #   for key, value in clone.__dict__.items():
  #     print(key,value)
  #     if isinstance(value, Card):
  #         clone.__dict__[key] = value.copy() # recursively
  #     elif isinstance(value, Image):
  #         clone.__dict__[key] = value.copy()
  #     else:
  #         clone.__dict__[key] = copy.deepcopy(value)
  #   return clone

  def copy(self):
    copyobj = Card()
    for key, value in self.__dict__.items():
      if key == "image":
        # copyobj.__dict__[key] = value.copy()
        copyobj.__dict__[key] = value
      else:
        copyobj.__dict__[key] = copy.deepcopy(value)
    return copyobj

class Hand:
  def __init__(self, cards, score, num_aces, bet):
    # Stores an array of Cards
    self.cards = cards
    
    # Stores the cumulative score
    self.score = score

    # Stores the number of aces, since in Blackjack, Ace = 11 or 1
    self.num_aces = num_aces

    # If the type is a player/AI, what is current bet up to
    self.bet = bet

    # Status of the hand
    self.status = HandStatus.ACTIVE

class Seat:
  def __init__(self, type, money=0, base_bet=100, frame=None):   
    # Stores the type of seat this is
    self.type = type

    # Stores the seat's hand as list of Hands
    self.hand = []
    
    # If the type is a player/AI, how much money does the player have
    self.money = money

    # If the type is a player/AI, what was initial bet
    self.base_bet = base_bet

    # Stores the frame for this Seat
    self.frame = frame

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

def create_deck(num_decks, suit_values, card_values):
  # Define basic components of a deck
  deck = []
  suits = ["Spades", "Hearts", "Clubs", "Diamonds"]
  cards = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

  # Create deck with cards based on provided values and total number of decks
  # for i in range(num_decks):
  #   for suit in suits:
  #     for card in cards:
  #       card_image = resize_card(f'cards/{card}_of_{suit}.png')
  #       deck.append(Card(suit_values[suit], card, card_values[card], card_image))

  for suit in suits:
    for card in cards:
      card_image = resize_card(f'cards/{card}_of_{suit}.png')
      for i in range(num_decks):
        deck.append(Card(suit_values[suit], card, card_values[card], card_image))
  return deck

def resize_card(card):
  card_img = Image.open(card)
  card_img_resized = card_img.resize((50, 73))

  global card_img_global
  card_img_global = ImageTk.PhotoImage(card_img_resized)
  return card_img_global

def setup_table(main_frame, num_players, player_seat_no, player_money, ai_money):
  ## Dealer Frame
  dealer_frame = tk.LabelFrame(main_frame, text="Dealer", bd=0, bg="blue")
  dealer_frame.grid(row=0, column=0, padx=20, ipadx=20)

  ## Table Frame
  table_frame = tk.LabelFrame(main_frame, text="Table", bd=0, bg="yellow")
  table_frame.grid(row=1, column=0, padx=20)
  
  # Initialize the table as list of Seats
  table = []
  
  # Create specified number of players
  for player_no in range(num_players):
    # Initialize the player
    if player_no == player_seat_no - 1:
      table.append(Seat(SeatType.PLAYER, player_money))
      table[player_no].base_bet = min(100, -(-player_money // 10)) ## 100 or Round-up Integer Divsion
    # Create AI seats
    else:
      table.append(Seat(SeatType.AI, ai_money))

    ## Create a frame for this player
    frame = tk.LabelFrame(table_frame, text=f'Player {player_no}', bd=0, bg = 'magenta')
    frame.grid(row=0, column=player_no, padx=20)
    table[player_no].frame = frame

  # The last seat is always the dealer
  table.append(Seat(SeatType.DEALER))
  table[-1].frame = dealer_frame

  return table

def display_card(seat, hand_number, new_card):
  label = tk.Label(seat.frame, image=new_card.image)
  label.grid(row=hand_number, column=len(seat.hand[hand_number].cards))
  
def deal_cards(deck, table):
  # Initialize each seat's hand
  for seat in table:
    seat.hand = [Hand([], 0, 0, seat.base_bet)]

  table[-1].hand[0].status = HandStatus.DEALER

  # Deal each seat 2 cards
  num_cards = 0
  while num_cards < 2:
    for seat in table:
      new_card = random.choice(deck)
      display_card(seat, 0, new_card)
      seat.hand[0].cards.append(new_card)
      seat.hand[0].score += new_card.value

      if new_card.card == "A":
        seat.hand[0].num_aces += 1

      deck.remove(new_card)

      # If hand receives two aces, treat one of the aces as a 1
      if seat.hand[0].score == 22:
        seat.hand[0].cards[1].value = 1
        seat.hand[0].score = 12
        seat.hand[0].num_aces -= 1

    num_cards = num_cards + 1

  ## Hide the dealer's second card
  default_image = resize_card(f'cards/default.png')
  label = tk.Label(table[-1].frame, image=default_image)
  label.grid(row=0,column=1)

def shuffle_deck(new_deck):
  # curr_deck = copy.deepcopy(new_deck)
  curr_deck = [card.copy() for card in new_deck]
  cutoff = random.randrange(math.floor(len(new_deck) * 0.25), math.floor(len(new_deck) * 0.5))
  return curr_deck, cutoff

def deal_new_card(deck, seat, hand):
  # Deal a new card from the provided deck to the provided cards and update the provided score
  new_card = random.choice(deck)
  display_card(seat, 0, new_card) ## TODO: Fix hand_number to accommodate split
  hand.cards.append(new_card)
  hand.score += new_card.value
  deck.remove(new_card)

  if new_card.card == "A":
    hand.num_aces += 1

  if hand.score > 21 and hand.num_aces > 0:
    hand.score -= 10
    hand.num_aces -= 1

    for card in hand.cards:
      if card.card == "A":
        card.value = 1
        break

def hit_command():
  global seat, curr_deck
  print(seat.type)

  ## Debug
  global player_standing
  print(player_standing.get())

  deal_new_card(curr_deck, seat, seat.hand[0])
  

if __name__ == "__main__":
  ## Set Default Values
  num_decks = 6
  num_players = 6
  player_seat_no = 1
  starting_money = 1000

  ## TODO: Figure out how to move this function to a different script
  # define_settings(num_decks, num_players, player_seat_no, starting_money)

  ## For Debugging
  print(num_decks)
  print(num_players)
  print(player_seat_no)
  print(starting_money)

  ## Initialize window
  root = tk.Tk()
  root.title("Blackjack")
  root.geometry("900x400")
  root.configure(background="green")

  main_frame = tk.Frame(root, bg="orange")
  main_frame.pack(pady=10)

  # Define AI variables
  ai_money = 1000000
  ai_bet = 100
  
  ## Setup table
  table = setup_table(main_frame, num_players, player_seat_no, starting_money, ai_money)

  # Define suit values for blackjack
  suit_values = {"Spades":"\u2664", "Hearts":"\u2661", "Clubs":"\u2667", "Diamonds":"\u2662"}

  # Define card values for blackjack
  card_values = {"A":11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}

  # Create a new deck for blackjack
  new_deck = create_deck(num_decks, suit_values, card_values)
  curr_deck, cutoff = shuffle_deck(new_deck)

  ## TODO: Need to shuffle deck here to avoid modifying original deck
  ## TODO: Need to define bets
  
  deal_cards(curr_deck, table)

  ## TODO: Need to check if seats have blackjack 
  
  # default_image = resize_card(f'cards/default.png')
  # for labels in table[-1].frame.winfo_children():
  #   labels.destroy()
    
  # label = tk.Label(table[-1].frame, image=default_image)
  # label.grid(row=0,column=0)
  # label = tk.Label(table[-1].frame, image=default_image)
  # label.grid(row=0,column=1)

  ## Playing the Seat's Hand
  command_frame = tk.Frame(root, bg="gray")
  command_frame.pack(side=tk.BOTTOM, pady=20)
  
  hit_button = tk.Button(command_frame, text="Hit", font=("Helvetica", 14),command=hit_command)
  hit_button.grid(row=0, column=0,padx=10)

  double_down_button = tk.Button(command_frame, text="Double Down", font=("Helvetica", 14))
  double_down_button.grid(row=0, column=1,padx=10)

  split_button = tk.Button(command_frame, text="Split", font=("Helvetica", 14))
  split_button.grid(row=0, column=2,padx=10)

  # player_standing = tk.StringVar()
  player_standing = tk.IntVar()
  stand_button = tk.Button(command_frame, text="Stand", font=("Helvetica", 14), command=lambda: player_standing.set(player_standing.get() + 1))
  stand_button.grid(row=0, column=3,padx=10)
  
  for seat in table:
    if seat.type == SeatType.AI:
      pass
    elif seat.type == SeatType.PLAYER:
      stand_button.wait_variable(player_standing)
    elif seat.type == SeatType.DEALER:
      pass
  
  root.mainloop()
  # blackjack_game(num_decks, num_players, player_seat_no, starting_money)