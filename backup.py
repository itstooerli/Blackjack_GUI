import tkinter as tk
import random
import math
import copy
import os
from enum import Enum

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
  def __init__(self, suit, card, value):
    # Stores the suit of the card, e.g. Clubs
    self.suit = suit

    # Stores the number of the card, e.g. K or 3
    self.card = card

    # Stores the value of the card for this game, e.g. K = 10, 3 = 3
    self.value = value

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
  def __init__(self, type):
    # Stores the type of seat this is
    self.type = type

    # Stores the seat's hand as list of Hands
    self.hand = []
    
    # If the type is a player/AI, how much money does the player have
    self.money = 0

    # If the type is a player/AI, what was initial bet
    self.base_bet = 100

def define_settings(num_decks, num_players, player_seat_no, starting_money):
  ## Start Settings GUI
  settings_window = tk.Tk()
  settings_window.title("Blackjack")
  settings_window.geometry("900x500")
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

# Clear the terminal
def clear():
    os.system("clear")

def create_deck(num_decks, suit_values, card_values):
  # Define basic components of a deck
  deck = []
  suits = ["Spades", "Hearts", "Clubs", "Diamonds"]
  cards = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

  # Create deck with cards based on provided values and total number of decks
  for i in range(num_decks):
    for suit in suits:
      for card in cards:
        deck.append(Card(suit_values[suit], card, card_values[card]))

  return deck

def setup_table(num_players, player_seat_no, player_money, ai_money):
  # Initialize the table as list of Seats
  table = []
  
  # Create specified number of players
  for player_no in range(num_players):
    # Initialize the player
    if player_no == player_seat_no - 1:
      table.append(Seat(SeatType.PLAYER))
      table[player_no].money = player_money
      table[player_no].base_bet = min(100, -(-player_money // 10)) ## 100 or Round-up Integer Divsion
    # Create AI seats
    else:
      table.append(Seat(SeatType.AI))
      table[player_no].money = ai_money

  # The last seat is always the dealer
  table.append(Seat(SeatType.DEALER))

  return table

def define_bets(table, ai_money, ai_bet):
  # Determine bets for every seat
  for seat in table:  
    # Player specifies bet
    if seat.type == SeatType.PLAYER:
      while (True):
        print("Current cash pool: " + str(seat.money))
        player_bet = input("Press enter to keep old bet. Enter new bet: ")

        # If player wants to keep old bet and bet was not 0, then skip
        if not player_bet and seat.base_bet > 0:
          break
        
        try:
          player_bet = float(player_bet)
          if player_bet < 0 or player_bet > seat.money:
            print("Not enough money. Please try again.")
            continue
        except ValueError:
          print("Not a valid input. Please try again.")
          continue
  
        if player_bet % 0.5 != 0:
          player_bet = round(player_bet * 2) / 2

        seat.base_bet = player_bet
        break
    
    # Define AI bet
    elif seat.type == 1:
      # If the ai doesn't have enough money to bet/double down/split, reload bank
      if ai_bet * 4 > seat.money:
        seat.money = ai_money
      seat.base_bet = ai_bet
    
    # Skip dealer
    else:
      continue

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

def deal_new_card(deck, hand):
  # Deal a new card from the provided deck to the provided cards and update the provided score
  new_card = random.choice(deck)
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

def display_table(table, hidden):
  clear()
  
  # Display dealer's cards first, if hidden then only first card is shown
  dealer_hand = table[-1].hand[0]
  
  print("\nDealer's cards:", end="\n\t")
  if hidden:
    print(str(dealer_hand.cards[0].card) + str(dealer_hand.cards[0].suit) + " XX", end=" ")
    print("Value: " + str(dealer_hand.cards[0].value))
  else:
    for card in dealer_hand.cards:
      print(str(card.card) + str(card.suit), end=" ")
    print("Value: " + str(dealer_hand.score))

  # Display every other seat's cards
  for seat in table:
    if seat.type == SeatType.PLAYER:
      print("\nPlayer's cards " + "(money: " + str(seat.money) + "):", end="")
    elif seat.type == SeatType.AI:
      print("\nAI's cards " + "(money: " + str(seat.money) + "):", end="")
    else:
      continue

    for hand in seat.hand:
      print("\n\t", end="")
      for card in hand.cards:
        print(str(card.card) + str(card.suit), end=" ")
      print("Value: " + str(hand.score) + "\t(bet: " + str(hand.bet) + ")" + "\t" + str(hand.status.name))
    
  print()

def shuffle_deck(new_deck):
  curr_deck = copy.deepcopy(new_deck)
  cutoff = random.randrange(math.floor(len(new_deck) * 0.25), math.floor(len(new_deck) * 0.5))
  return curr_deck, cutoff

def double_down(curr_deck, hand):
  hand.bet *= 2
  deal_new_card(curr_deck, hand)
  hand.status = HandStatus.WAITING

def split_hand(curr_deck, seat, hand, split_card):
  # Remove the split card from the current hand
  hand.score -= split_card.value
  hand.cards.pop()

  # Create new hand
  if split_card.card == "A":
    split_card.value = 11
    hand.num_aces -= 1
    seat.hand.append(Hand([split_card], split_card.value, 1, seat.base_bet))
  else:
    seat.hand.append(Hand([split_card], split_card.value, 0, seat.base_bet))
  
  # Deal both hands a new card
  deal_new_card(curr_deck, hand)
  deal_new_card(curr_deck, seat.hand[-1])
  
# AI hits if score is less than 17; otherwise stand
def play_AI_hand_naive_strategy(curr_deck, table, seat, hand):
  while hand.score < 17:  
    deal_new_card(curr_deck, hand)
  
  if hand.score > 21:
    hand.status = HandStatus.LOSER
  else:
    hand.status = HandStatus.WAITING


def play_AI_hand_basic_strategy(curr_deck, table, seat, hand):
  """
  # Defining Basic Strategy
  # - Always split As and 8s
  # - Never split 5s and 10s
  # - Split 2s and 3s against Dealer 2-7
  # - Split 4s against Dealer 5-6
  # - Split 6s against Dealer 2-6
  # - Split 7s against Dealer 2-7
  # - Split 9s against Dealer 2-6 or 8-9
  # - Double hard 9 against Dealer 3-6
  # - Double hard 10 against Dealer 2-9
  # - Double hard 11 against Dealer 2-K 
  # - Double soft 13 or 14 against Dealer 5-6
  # - Double soft 15 or 16 against Dealer 4-6
  # - Double soft 17 or 18 against Dealer 3-6
  # - Always hit hard 11 or less
  # - Stand on hard 12 against dealer 4-6, otherwise hit
  # - Stand on hard 13-16 against dealer 2-6, otherwise hit
  # - Always stand on hard 17 or more
  # - Always hit soft 17 or less
  # - Stand on soft 18 except hit against Dealer 9-A 
  # - Always stand on soft 19 or more
  """
  
  dealer_shown_card = table[-1].hand[0].cards[0]

  while hand.score < 21:
    if len(hand.cards) == 2:
      # Assess Split
      if hand.cards[0].card == hand.cards[1].card:
        # Only need to look at card and not value because we never split 10s anyways
        split_card = hand.cards[1]
  
        if split_card.card == "A":
          split_hand(curr_deck, seat, hand, split_card)
          seat.hand[-1].status = HandStatus.WAITING
          hand.status = HandStatus.WAITING
          break
        elif split_card.card in ("2", "3"):
          if dealer_shown_card.value in (2,3,4,5,6,7):
            split_hand(curr_deck, seat, hand, split_card)
            continue
        elif split_card.card == "4":
          if dealer_shown_card.value in (5,6):
            split_hand(curr_deck, seat, hand, split_card)
            continue
        elif split_card.card == "5":
          pass
        elif split_card.card == "6":
          if dealer_shown_card.value in (2,3,4,5,6):
            split_hand(curr_deck, seat, hand, split_card)
            continue
        elif split_card.card == "7":
          if dealer_shown_card.value in (2,3,4,5,6,7):
            split_hand(curr_deck, seat, hand, split_card)
            continue
        elif split_card.card == "8":
          split_hand(curr_deck, seat, hand, split_card)
          continue
        elif split_card.card == "9":
          if dealer_shown_card.value in (2,3,4,5,6,8,9):
            split_hand(curr_deck, seat, hand, split_card)
            continue
        else:  # 10, J, Q, K
          pass

      # Assess Double
      if hand.num_aces == 0:
        if hand.score == 9:
          if dealer_shown_card.value in (3,4,5,6):  
            double_down(curr_deck, hand)
            break
        elif hand.score == 10:
          if dealer_shown_card.value in (2,3,4,5,6,7,8,9):
            double_down(curr_deck, hand)
            break
        elif hand.score == 11:
          if dealer_shown_card.value in (2,3,4,5,6,7,8,9,10):
            double_down(curr_deck, hand)
            break
      else:
        if hand.score in (13,14):
          if dealer_shown_card.value in (5,6):
            double_down(curr_deck, hand)
            break
        elif hand.score in (15,16):
          if dealer_shown_card.value in (4,5,6):
            double_down(curr_deck, hand)
            break
        elif hand.score in (17,18):
          if dealer_shown_card.value in (3,4,5,6):
            double_down(curr_deck, hand)
            break
  
    if hand.num_aces == 0:
      if hand.score <= 11:
        deal_new_card(curr_deck, hand)
      elif hand.score == 12:
        if dealer_shown_card.value in (4,5,6):
          hand.status = HandStatus.WAITING
          break
        else:
          deal_new_card(curr_deck, hand)
      elif hand.score in (13,14,15,16):
        if dealer_shown_card.value in (2,3,4,5,6):
          hand.status = HandStatus.WAITING
          break
        else:
          deal_new_card(curr_deck, hand)
      else:
        hand.status = HandStatus.WAITING
        break
    else:
      if hand.score <= 17:
        deal_new_card(curr_deck, hand)
      elif hand.score == 18:
        if dealer_shown_card.value in (9,10,11):
          deal_new_card(curr_deck, hand)
        else:
          hand.status = HandStatus.WAITING
          break
      else:
        hand.status = HandStatus.WAITING
        break
  if hand.score > 21:
    hand.status = HandStatus.LOSER

def ask_continue_game():
  player_choice = input("Enter Q to quit or any other key to continue: ")
  print()
  return player_choice.upper() != "Q"
  
def blackjack_game(num_decks, num_players, player_seat_no, player_money):

  # Define suit values for blackjack
  suit_values = {"Spades":"\u2664", "Hearts":"\u2661", "Clubs":"\u2667", "Diamonds":"\u2662"}

  # Define card values for blackjack
  card_values = {"A":11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}

  # Create a new deck for blackjack
  new_deck = create_deck(num_decks, suit_values, card_values)
  curr_deck, cutoff = shuffle_deck(new_deck)  

  # Define AI variables
  ai_money = 1000000
  ai_bet = 100
  
  # Setup table
  table = setup_table(num_players, player_seat_no, player_money, ai_money)
  
  # Play Game
  while(True):
    # print("Number of cards left: " + str(len(curr_deck)))
    
    # Reshuffle deck if we're at the cutoff point
    if len(curr_deck) < cutoff:
      curr_deck, cutoff = shuffle_deck(new_deck)  

    # Define bets for each seat for this round
    define_bets(table, ai_money, ai_bet)

    # Deal the new hand
    deal_cards(curr_deck, table)
    display_table(table, True)

    # Check if seats have blackjack
    dealer_hand = table[-1].hand[0]
    if dealer_hand.score == 21:
      for seat in table:
        if seat.type == SeatType.DEALER:
          continue
        elif seat.hand[0].score == 21:
          seat.hand[0].status = HandStatus.TIE
        else:
          seat.hand[0].status = HandStatus.LOSER
      print("Dealer has blackjack!")
    else:
      for seat in table:
        if seat.hand[0].score == 21:
          seat.hand[0].status = HandStatus.BLACKJACK

    display_table(table, True)

    # Play the Seat's Hand
    for seat in table:
      if seat.type == SeatType.AI:
        completed_hands = 0
        while completed_hands != len(seat.hand):
          current_hand = seat.hand[completed_hands]
          
          if current_hand.status != HandStatus.ACTIVE:
            completed_hands += 1
            continue
          
          #play_AI_hand_naive_strategy(curr_deck, table, seat, current_hand)
          play_AI_hand_basic_strategy(curr_deck, table, seat, current_hand)
          
          completed_hands += 1
          display_table(table, True)
          
      elif seat.type == SeatType.PLAYER:
        completed_hands = 0
        while completed_hands != len(seat.hand):
          current_hand = seat.hand[completed_hands]
          
          if current_hand.status != HandStatus.ACTIVE:
            completed_hands += 1
            continue
            
          while current_hand.score < 22:
            display_table(table, True)
            
            # Player Input
            if len(current_hand.cards) == 2:
              if current_hand.cards[0].card == current_hand.cards[1].card or current_hand.cards[0].value == current_hand.cards[1].value:
                player_choice = input("Enter H to hit, D to double down, L to split, S to stand: ")
                if (len(player_choice) != 1 or player_choice.upper() not in ("H", "D", "L", "S")):
                  print("Invalid Choice.")
                  continue
              else:
                player_choice = input("Enter H to hit, D to double down, S to stand: ")
                if (len(player_choice) != 1 or player_choice.upper() not in ("H", "D", "S")):
                  print("Invalid Choice.")
                  continue
            else:
              player_choice = input("Enter H to hit, S to stand: ")
              if (len(player_choice) != 1 or player_choice.upper() not in ("H", "S")):
                print("Invalid Choice.")
                continue

            if player_choice.upper() == "H":
              # Player Hits
              deal_new_card(curr_deck, current_hand)
              display_table(table, True)
            elif player_choice.upper() == "D":
              # Player Doubles Down
              double_down(curr_deck, current_hand)
              break
            elif player_choice.upper() == "L":
              split_card = current_hand.cards[1]
              
              # Create the new hand
              if split_card.card == "A":
                split_hand(curr_deck, seat, current_hand, split_card)
                seat.hand[-1].status = HandStatus.WAITING
                current_hand.status = HandStatus.WAITING
                break
              else:
                split_hand(curr_deck, seat, current_hand, split_card)
                continue
              
            elif player_choice.upper() == "S":
              # Player Stands
              current_hand.status = HandStatus.WAITING
              break

          if current_hand.score > 21:
            current_hand.status = HandStatus.LOSER
            
          display_table(table, True)
          
          completed_hands += 1
              
      elif seat.type == SeatType.DEALER:
        any_active_hands = False
        
        for seat in table:
          if not any_active_hands:
            for hand in seat.hand:
              if hand.status == HandStatus.WAITING:
                any_active_hands = True
                break
          else:
            break

        if any_active_hands:
          while dealer_hand.score < 17:
            deal_new_card(curr_deck, dealer_hand)
            display_table(table, False)
    
    # Determine Winners/Losers
    if dealer_hand.score > 21:
      for seat in table:
        for hand in seat.hand:
          if hand.status == HandStatus.WAITING:
            hand.status = HandStatus.WINNER
    else:
      for seat in table:
        for hand in seat.hand:
          if hand.status == HandStatus.WAITING:
            if hand.score == dealer_hand.score:
              hand.status = HandStatus.TIE
            elif hand.score > dealer_hand.score:
              hand.status = HandStatus.WINNER
            else:
              hand.status = HandStatus.LOSER

    display_table(table, False)
    
    # Determine Payouts
    out_of_money = False
    for seat in table:
      for hand in seat.hand:
        if hand.status == HandStatus.BLACKJACK:
          seat.money += hand.bet * 1.5
        elif hand.status == HandStatus.WINNER:
          seat.money += hand.bet
        elif hand.status == HandStatus.LOSER:
          seat.money -= hand.bet

          if seat.type == SeatType.PLAYER and seat.money <= 0:
            out_of_money = True
            
    display_table(table, False)

    if out_of_money:
      print("Player is out of money!")
      break
    
    if ask_continue_game():
      continue
    else:
      break

if __name__ == "__main__":
  ## Set Default Values
  num_decks = 6
  num_players = 6
  player_seat_no = 1
  starting_money = 1000

  define_settings(num_decks, num_players, player_seat_no, starting_money)
  
  print(num_decks)
  print(num_players)
  print(player_seat_no)
  print(starting_money)
  # main_window = tk.Tk()
  # main_window.title("Blackjack")
  # main_window.mainloop()
  blackjack_game(num_decks, num_players, player_seat_no, starting_money)