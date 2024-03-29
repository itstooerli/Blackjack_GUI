import tkinter as tk
from PIL import Image, ImageTk
import random
import math
import copy
from enum import Enum

## TODO: Implement recommended action for basic strategy practice

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

class BlackjackGameModel:
  def __init__(self, 
               main_frame,
               bet_label,
               bet_value_var,
               bet_input,
               play_button,
               hit_button,
               double_down_button,
               split_button,
               stand_button,
               recommend_toggle,
               recommend_label,
               num_decks,
               num_players,
               user_seat_no,
               starting_money):
    self.main_frame = main_frame                        # Frame that holds the dealer and player cards
    self.bet_label = bet_label                          # Label that holds the user's current money total
    self.bet_value_var = bet_value_var                  # User input variable holding user bet value
    self.bet_input = bet_input                          # Tk input for user to type user bet value
    self.play_button = play_button                      # Tk button to begin play
    self.hit_button = hit_button                        # Tk button to hit
    self.double_down_button = double_down_button        # Tk button to double down
    self.split_button = split_button                    # Tk button to split
    self.stand_button = stand_button                    # Tk button to stand
    self.recommend_toggle = recommend_toggle            # Tk button to turn on recommendations for basic strategy to user
    self.recommend_label = recommend_label              # Tk label to display recommendation if recommend_toggle on
    self.base_deck = self.create_deck(num_decks)        # Array that holds the Cards used for play
    self.user_seat_no = user_seat_no                    # Position of player at table
    self.table = self.setup_table(self.main_frame, num_players, user_seat_no, starting_money) # Array that holds Seats
    self.curr_deck = []                                 # Deck that game is currently using (copy of base_deck to allow removing cards)
    self.reshuffle_cutoff = 1                           # Maximum value for length of curr_deck when it should re-copy from base_deck
    self.player_standing = tk.BooleanVar()              # Tk boolean used to wait for player input
    self.default_image = self.resize_card(f'cards/default.png') # Image back-of-card to hide dealer card
    self.blackjack_payout_factor = 1.5                  # The multiplicative factor for how much players should receive upon blackjack
    self.starting_money = starting_money                # The starting money for the user
    self.bet_value_var.set(self.table[self.user_seat_no - 1].base_bet)
    self.active_user_hand = None                        # State variable for which hand the user is currently acting on
    self.program_exiting = False                        # State variable for whether the program is exiting to avoid mini-wait-variable-loop
    self.recommendation_on = False                      # State variable for whether recommendations should be turned on

  class Card:
    """ Class used to represent a playing card (suit, number, value in game, image)"""
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
    """ Class used to represent one set of cards given to a user"""

    def __init__(self, cards, score, num_aces, bet, frame=None, status_label=None):
      self.cards = cards        # Stores an array of Cards
      self.score = score        # Stores the cumulative score
      self.num_aces = num_aces  # Stores the number of aces, since in Blackjack, Ace = 11 or 1
      self.bet = bet            # If the type is a player/AI, what is current bet up to
      self.status = HandStatus.ACTIVE  # Status of the hand
      self.frame = frame        # Stores the frame for this Hand
      self.status_label = status_label  # Stores the status widget to be updated for this hand

  class Seat:
    """ Class used to represent one player at the table"""

    def __init__(self, type, money=1000000, base_bet=100, frame=None):   
      self.type = type          # Stores the type of seat this is
      self.hand = []            # Stores the seat's hand as list of Hands
      self.money = money        # If the type is a player/AI, how much money does the player have
      self.base_bet = base_bet  # If the type is a player/AI, what was initial bet
      self.frame = frame        # Stores the frame for this Seat
  
  def create_deck(self, num_decks):
    """ Creates an array of Card variables given the number of decks to play with
    Input: Integer value for number of decks to play with
    Output: Array of Cards
    """
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
        for _ in range(num_decks):
          deck.append(self.Card(suit_values[suit], card, card_values[card], card_image))
    return deck

  def resize_card(self, card):
    """ Resize the card to be smaller
    Input: Card class variable for card
    Output: ImageTk.PhotoImage variable for card 
    """
    card_img = Image.open(card)
    # card_img_resized = card_img.resize((50, 73))
    # card_img_resized = card_img.resize((67, 97))
    # card_img_resized = card_img.resize((71, 104))
    card_img_resized = card_img.resize((84, 121))
    card_img_global = ImageTk.PhotoImage(card_img_resized)
    return card_img_global
  
  def setup_table(self, main_frame, num_players, user_seat_no, player_money):
    """ Creates an array of Seats that will represent the state of each player
    
    Input: main_frame:      tk.Frame to represent table
           num_players:     Number of Seats to create at table
           user_seat_no:  Position whwere use is at table (Index-1)
           player_money:    Integer for starting money given to user
    Output: Array of Seats
    """
    ## Create frame for dealer above frame for rest of table
    dealer_frame = tk.LabelFrame(main_frame, text="Dealer", bd=0, labelanchor="n", font=("Helvetica", 14), bg="#FFC06E")
    dealer_frame.grid(row=0, column=0, pady=(0,10))
    table_frame = tk.LabelFrame(main_frame, bd=0, bg="#BDD99E")
    table_frame.grid(row=1, column=0)
    
    # Create table as list of Seats
    table = []
    for player_no in range(num_players):
      if player_no == user_seat_no - 1:
        ## Initialize the player (Index 1)
        table.append(self.Seat(SeatType.PLAYER, player_money))
        table[player_no].base_bet = min(100, -(-player_money // 10)) ## 100 or Round-up Integer Divsion
        frame_text = f'You: ${table[player_no].money}'
      else:
        ## Create AI Seats
        table.append(self.Seat(SeatType.AI))
        frame_text = f'Player {player_no + 1}: ${table[player_no].money}'
  
      ## Create a frame for this player
      frame = tk.LabelFrame(table_frame, text=frame_text, bd=0, font=("Helvetica", 10), bg='#FFC06E')
      frame.grid(row=0, column=player_no, padx=10)
      table[player_no].frame = frame
  
    ## The last seat is always the dealer
    table.append(self.Seat(SeatType.DEALER))
    table[-1].frame = dealer_frame
  
    return table

  def reset_table(self):
    """ Resets the table by destroying all relevant widgets from previous round"""
    self.play_button.config(state="disabled")
    for seat in self.table:
      for widget in seat.frame.winfo_children():
        widget.destroy()
    
    self.play_game()

  def shuffle_deck(self):
    """ Create a new copy of the base_deck and assign to curr_deck with a cutoff for when to copy again"""
    # curr_deck = copy.deepcopy(self.base_deck) # NOTE: ImageTk cannot be copied using deepcopy
    self.curr_deck = [card.copy() for card in self.base_deck]
    self.reshuffle_cutoff = random.randrange(math.floor(len(self.base_deck) * 0.25), math.floor(len(self.base_deck) * 0.5))

  def display_card(self, hand, new_card):
    """ Creates a new label for the given hand's frame to represent card
    
    Input: hand:      Hand class variable that provides the frame for the given hand
           new_card:  Card class variable that requires an image for the frame
    NOTE: Assumed display after cards array has already been increased by new card
    """
    label = tk.Label(hand.frame, image=new_card.image)
    label.grid(row=0, column=(len(hand.cards) - 1))
  
  def create_status_label(self, hand_frame):
    """Create a tk.Label for given hand_frame
    
    Input:    hand_frame:   tk.Frame to which tk.Label will be added
    Output    status_label: tk.Label added to the tk.Frame providing information about hand
    """
    status_label = tk.Label(hand_frame, font=("Helvetica", 10))
    return status_label

  def deal_cards(self):
    """ Deal each player 2 cards at the beginning of play and updates labels accordingly"""
    # Initialize each seat's first hand
    for seat in self.table:
      hand_frame = tk.LabelFrame(seat.frame, bd=0)
      hand_frame.grid(row=0,column=0)
      status_label = self.create_status_label(hand_frame)
      status_label.grid(row=1,column=0,columnspan=2)
      seat.hand = [self.Hand([], 0, 0, seat.base_bet, hand_frame, status_label)]
    self.table[-1].hand[0].status = HandStatus.DEALER
  
    # Deal each seat 2 cards
    num_cards = 0
    while num_cards < 2:
      for seat in self.table:
        new_card = random.choice(self.curr_deck)

        seat.hand[0].cards.append(new_card)
        seat.hand[0].score += new_card.value
        if new_card.card == "A":
          seat.hand[0].num_aces += 1
          
        self.display_card(seat.hand[0], new_card)
        
        self.curr_deck.remove(new_card)
  
        # If hand receives two aces, treat one of the aces as a 1
        if seat.hand[0].score == 22:
          seat.hand[0].cards[1].value = 1
          seat.hand[0].score = 12
          seat.hand[0].num_aces -= 1

        if num_cards + 1 == 2:
          ## If this is the second card, update the status label
          seat.hand[0].status_label.config(text=f'WAITING {seat.hand[0].score}, BET: {seat.hand[0].bet}')
  
      num_cards = num_cards + 1

    ## Hide the dealer's second card
    label = tk.Label(self.table[-1].hand[0].frame, image=self.default_image)
    label.grid(row=0,column=1)
    self.table[-1].hand[0].status_label.config(text=f'Total: {self.table[-1].hand[0].cards[0].value}')

  def deal_new_card(self, hand):
    """ Deal a new card to the provided hand and update the label accordingly
    
    Input: hand:  Hand class variable that will be given a new card
    """
    new_card = random.choice(self.curr_deck)
    hand.cards.append(new_card)
    hand.score += new_card.value
    self.display_card(hand, new_card)
    
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

    hand.status_label.config(text=f'ACTIVE {hand.score}, BET: {hand.bet}')
    hand.status_label.grid(columnspan=len(hand.cards))

  def play_AI_hand_naive_strategy(self, hand):
    """ Play given hand with naive strategy
    
    Naive strategy is hitting until the total score is 17 or greater

    Input:  hand:   Hand variable that will be updated with new card
    """
    while hand.score < 17:
      self.deal_new_card(hand)

    if hand.score > 21:
      hand.status = HandStatus.LOSER
      hand.status_label.config(text=f'BUST {hand.score}, BET: {hand.bet}')
    else:
      hand.status = HandStatus.WAITING
      hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')

  def play_AI_hand_basic_strategy(self, seat, hand):
    """ Play given hand with basic strategy

    Defining Basic Strategy
    - Always split As and 8s
    - Never split 5s and 10s
    - Split 2s and 3s against Dealer 2-7
    - Split 4s against Dealer 5-6
    - Split 6s against Dealer 2-6
    - Split 7s against Dealer 2-7
    - Split 9s against Dealer 2-6 or 8-9
    - Double hard 9 against Dealer 3-6
    - Double hard 10 against Dealer 2-9
    - Double hard 11 against Dealer 2-K 
    - Double soft 13 or 14 against Dealer 5-6
    - Double soft 15 or 16 against Dealer 4-6
    - Double soft 17 or 18 against Dealer 3-6
    - Always hit hard 11 or less
    - Stand on hard 12 against dealer 4-6, otherwise hit
    - Stand on hard 13-16 against dealer 2-6, otherwise hit
    - Always stand on hard 17 or more
    - Always hit soft 17 or less
    - Stand on soft 18 except hit against Dealer 9-A 
    - Always stand on soft 19 or more
    
    Input:    seat:   Seat class variable that will be updated in the event of a split
              hand:   Hand class variable that will be updated when new cards are given
    """
    
    dealer_shown_card = self.table[-1].hand[0].cards[0]
  
    while hand.score < 21:
      if len(hand.cards) == 2:
        # Assess Split
        if hand.cards[0].card == hand.cards[1].card:
          # Only need to look at card and not value because we never split 10s anyways
          split_card = hand.cards[1]
    
          if split_card.card == "A":
            self.split_hand(seat, hand)
            seat.hand[-1].status = HandStatus.WAITING
            hand.status = HandStatus.WAITING
            break
          elif split_card.card in ("2", "3"):
            if dealer_shown_card.value in (2,3,4,5,6,7):
              self.split_hand(seat, hand)
              continue
          elif split_card.card == "4":
            if dealer_shown_card.value in (5,6):
              self.split_hand(seat, hand)
              continue
          elif split_card.card == "5":
            pass
          elif split_card.card == "6":
            if dealer_shown_card.value in (2,3,4,5,6):
              self.split_hand(seat, hand)
              continue
          elif split_card.card == "7":
            if dealer_shown_card.value in (2,3,4,5,6,7):
              self.split_hand(seat, hand)
              continue
          elif split_card.card == "8":
            self.split_hand(seat, hand)
            continue
          elif split_card.card == "9":
            if dealer_shown_card.value in (2,3,4,5,6,8,9):
              self.split_hand(seat, hand)
              continue
          else:  # 10, J, Q, K
            pass
  
        # Assess Double Down
        if hand.num_aces == 0:
          if hand.score == 9:
            if dealer_shown_card.value in (3,4,5,6):  
              self.double_down(hand)
              hand.status = HandStatus.WAITING
              hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
              break
          elif hand.score == 10:
            if dealer_shown_card.value in (2,3,4,5,6,7,8,9):
              self.double_down(hand)
              hand.status = HandStatus.WAITING
              hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
              break
          elif hand.score == 11:
            if dealer_shown_card.value in (2,3,4,5,6,7,8,9,10):
              self.double_down(hand)
              hand.status = HandStatus.WAITING
              hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
              break
        else:
          if hand.score in (13,14):
            if dealer_shown_card.value in (5,6):
              self.double_down(hand)
              hand.status = HandStatus.WAITING
              hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
              break
          elif hand.score in (15,16):
            if dealer_shown_card.value in (4,5,6):
              self.double_down(hand)
              hand.status = HandStatus.WAITING
              hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
              break
          elif hand.score in (17,18):
            if dealer_shown_card.value in (3,4,5,6):
              self.double_down(hand)
              hand.status = HandStatus.WAITING
              hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
              break
      
      ## Assess all other hit/stand scenarios
      if hand.num_aces == 0:
        if hand.score <= 11:
          self.deal_new_card(hand)
        elif hand.score == 12:
          if dealer_shown_card.value in (4,5,6):
            hand.status = HandStatus.WAITING
            hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
            break
          else:
            self.deal_new_card(hand)
        elif hand.score in (13,14,15,16):
          if dealer_shown_card.value in (2,3,4,5,6):
            hand.status = HandStatus.WAITING
            hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
            break
          else:
            self.deal_new_card(hand)
        else:
          hand.status = HandStatus.WAITING
          hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
          break
      else:
        if hand.score <= 17:
          self.deal_new_card(hand)
        elif hand.score == 18:
          if dealer_shown_card.value in (9,10,11):
            self.deal_new_card(hand)
          else:
            hand.status = HandStatus.WAITING
            hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
            break
        else:
          hand.status = HandStatus.WAITING
          hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')
          break
    if hand.score > 21:
      hand.status = HandStatus.LOSER
      hand.status_label.config(text=f'BUST {hand.score}, BET: {hand.bet}')

  def recommend_basic_strategy(self, hand):
    """ Recommend to player what basic strategy would suggest given current state

    Defining Basic Strategy
    - Always split As and 8s
    - Never split 5s and 10s
    - Split 2s and 3s against Dealer 2-7
    - Split 4s against Dealer 5-6
    - Split 6s against Dealer 2-6
    - Split 7s against Dealer 2-7
    - Split 9s against Dealer 2-6 or 8-9
    - Double hard 9 against Dealer 3-6
    - Double hard 10 against Dealer 2-9
    - Double hard 11 against Dealer 2-K 
    - Double soft 13 or 14 against Dealer 5-6
    - Double soft 15 or 16 against Dealer 4-6
    - Double soft 17 or 18 against Dealer 3-6
    - Always hit hard 11 or less
    - Stand on hard 12 against dealer 4-6, otherwise hit
    - Stand on hard 13-16 against dealer 2-6, otherwise hit
    - Always stand on hard 17 or more
    - Always hit soft 17 or less
    - Stand on soft 18 except hit against Dealer 9-A 
    - Always stand on soft 19 or more
    
    Input:    seat:   Seat class variable that will be updated in the event of a split
              hand:   Hand class variable that will be updated when new cards are given
    """
    
    dealer_shown_card = self.table[-1].hand[0].cards[0]
  
    if len(hand.cards) == 2:
      # Assess Split
      if hand.cards[0].card == hand.cards[1].card:
        # Only need to look at card and not value because we never split 10s anyways
        split_card = hand.cards[1]
  
        if split_card.card == "A":
          self.recommend_label.config(text='Split')
          return
        elif split_card.card in ("2", "3"):
          if dealer_shown_card.value in (2,3,4,5,6,7):
            self.recommend_label.config(text='Split')
            return
        elif split_card.card == "4":
          if dealer_shown_card.value in (5,6):
            self.recommend_label.config(text='Split')
            return
        elif split_card.card == "5":
          pass
        elif split_card.card == "6":
          if dealer_shown_card.value in (2,3,4,5,6):
            self.recommend_label.config(text='Split')
            return
        elif split_card.card == "7":
          if dealer_shown_card.value in (2,3,4,5,6,7):
            self.recommend_label.config(text='Split')
            return
        elif split_card.card == "8":
          self.recommend_label.config(text='Split')
          return
        elif split_card.card == "9":
          if dealer_shown_card.value in (2,3,4,5,6,8,9):
            self.recommend_label.config(text='Split')
            return
        else:  # 10, J, Q, K
          pass

      # Assess Double Down
      if hand.num_aces == 0:
        if hand.score == 9:
          if dealer_shown_card.value in (3,4,5,6):  
            self.recommend_label.config(text='Double Down')
            return
        elif hand.score == 10:
          if dealer_shown_card.value in (2,3,4,5,6,7,8,9):
            self.recommend_label.config(text='Double Down')
            return
        elif hand.score == 11:
          if dealer_shown_card.value in (2,3,4,5,6,7,8,9,10):
            self.recommend_label.config(text='Double Down')
            return
      else:
        if hand.score in (13,14):
          if dealer_shown_card.value in (5,6):
            self.recommend_label.config(text='Double Down')
            return
        elif hand.score in (15,16):
          if dealer_shown_card.value in (4,5,6):
            self.recommend_label.config(text='Double Down')
            return
        elif hand.score in (17,18):
          if dealer_shown_card.value in (3,4,5,6):
            self.recommend_label.config(text='Double Down')
            return
    
    ## Assess all other hit/stand scenarios
    if hand.num_aces == 0:
      if hand.score <= 11:
        self.recommend_label.config(text='Hit')
        return
      elif hand.score == 12:
        if dealer_shown_card.value in (4,5,6):
          self.recommend_label.config(text='Stand')
          return
        else:
          self.recommend_label.config(text='Hit')
          return
      elif hand.score in (13,14,15,16):
        if dealer_shown_card.value in (2,3,4,5,6):
          self.recommend_label.config(text='Stand')
          return
        else:
          self.recommend_label.config(text='Hit')
          return
      else:
        self.recommend_label.config(text='Stand')
        return
    else:
      if hand.score <= 17:
        self.recommend_label.config(text='Hit')
        return
      elif hand.score == 18:
        if dealer_shown_card.value in (9,10,11):
          self.recommend_label.config(text='Hit')
          return
        else:
          self.recommend_label.config(text='Stand')
          return
      else:
        self.recommend_label.config(text='Stand')
        return

  def hit_command(self):
    """ Command for hit button: Deal new card to user"""
    self.deal_new_card(self.active_user_hand)
    self.double_down_button.config(state="disabled")
    self.recommend_basic_strategy(self.active_user_hand)

    if self.active_user_hand.score > 21:
      self.stand_command()

  def double_down_command(self):
    """ Command for double down button: Deal new card to user, double bet, and stand"""
    self.double_down(self.active_user_hand)
    self.double_down_button.config(state="disabled")
    self.stand_command()

  def double_down(self, hand):
    """ Double down to given Hand class variable: Deal new card and double bet"""
    self.deal_new_card(hand)
    hand.bet *= 2

  def split_command(self):
    """ Command for split button: Split the current active hand"""

    self.split_button.config(state="disabled")
    seat = self.table[self.user_seat_no - 1]
    self.split_hand(seat, self.active_user_hand)
    self.recommend_basic_strategy(self.active_user_hand)

    if (self.active_user_hand.cards[0].card == self.active_user_hand.cards[1].card):
      self.split_button.config(state="active")

  def split_hand(self, seat, hand):
    """ Split the given Hand class variable and add new Hand class variable to given Seat class variable
    
    Input:  seat:   Seat class variable for which to extend with new Hand class variable
            hand:   Hand class variable for which to modify
    """
    # The split card is the second card in the given hand
    split_card = hand.cards[1]
    
    # Remove the split card from the current hand
    hand.score -= split_card.value
    hand.cards.pop()
    hand.frame.winfo_children()[-1].destroy()

    # Create new hand
    if split_card.card == "A":
      split_card.value = 11
      hand.num_aces -= 1

    hand_frame = tk.LabelFrame(seat.frame, bd=0)
    hand_frame.grid(row=len(seat.hand),column=0)
    status_label = self.create_status_label(hand_frame)
    status_label.config(text=f'Bet ${seat.base_bet}')
    status_label.grid(row=1,column=0,columnspan=2)
    seat.hand.append(self.Hand([split_card], split_card.value, hand.num_aces, seat.base_bet, hand_frame, status_label))
    self.display_card(seat.hand[-1], split_card)

    # Deal both hands a new card
    self.deal_new_card(hand)
    self.deal_new_card(seat.hand[-1])
    seat.hand[-1].status_label.config(text=f'WAITING {seat.hand[-1].score}, BET: {seat.hand[-1].bet}')

  def stand_command(self):
    """ Command for stand_button or if player has double down or busted
    
    This sets the active variable that the main_loop is waiting on to continue actions: self.player_standing
    """
    self.player_standing.set(not self.player_standing)

  def recommend_command(self):
    """ Command for recommend_toggle to turn off or on recommendations for basic strategy to user"""
    if self.recommendation_on:
      self.recommend_toggle.config(text="Recommend Basic Strategy: OFF")
      self.recommend_label.config(fg="#BDD99E")
      self.recommendation_on = False
    else:
      self.recommend_toggle.config(text="Recommend Basic Strategy: ON")
      self.recommend_label.config(fg="Black")
      self.recommendation_on = True

  def play_game(self):
    """ This is the primary game loop for blackjack 
    
    Order of Play:
    - Submit the bet from the user
    - Check if current deck needs to be reshuffled
    - Deal cards to all players at table
    - Check if seats have blackjack
    - Play table hands
    - Play dealer hand if applicable
    - Determine payouts
    - Reactivate Bet/Play button for next round
    """
    
    # Update the user's bet
    self.bet_input.config(state="disabled")
    try:
      user_bet_val = self.bet_value_var.get()

      if user_bet_val <= self.table[self.user_seat_no - 1].money:
        self.table[self.user_seat_no - 1].base_bet = user_bet_val
      else:
        self.table[self.user_seat_no - 1].base_bet = min(100, -(-self.table[self.user_seat_no - 1].money // 10))
    except:
      self.table[self.user_seat_no - 1].base_bet = min(100, -(-self.table[self.user_seat_no - 1].money // 10))

    self.bet_value_var.set(self.table[self.user_seat_no - 1].base_bet)
    
    # Shuffle deck if necessary and deal cards
    if len(self.curr_deck) < self.reshuffle_cutoff:
      self.shuffle_deck()
  
    self.deal_cards()
    
    # Check if seats have blackjack
    dealer_hand = self.table[-1].hand[0]
    if dealer_hand.score == 21:
      ## Reveal card
      label = tk.Label(self.table[-1].hand[0].frame, image=self.table[-1].hand[0].cards[-1].image)
      label.grid(row=0,column=1)

      ## Check outcomes
      for seat in self.table:
        if seat.type == SeatType.DEALER:
          continue
        elif seat.hand[0].score == 21:
          seat.hand[0].status = HandStatus.TIE
        else:
          seat.hand[0].status = HandStatus.LOSER
    else:
      for seat in self.table:
        if seat.hand[0].score == 21:
          seat.hand[0].status = HandStatus.BLACKJACK
          seat.hand[0].status_label.config(text=f'BLACKJACK {seat.hand[0].score}, BET: {seat.hand[0].bet}')
    
    for seat in self.table:
      completed_hands = 0
      if seat.type == SeatType.AI:
        while completed_hands < len(seat.hand):
          current_hand = seat.hand[completed_hands]

          if current_hand.status == HandStatus.ACTIVE:
            # self.play_AI_hand_naive_strategy(current_hand)
            self.play_AI_hand_basic_strategy(seat, current_hand)
          
          completed_hands += 1
        
      elif seat.type == SeatType.PLAYER:
        while completed_hands < len(seat.hand):
          current_hand = seat.hand[completed_hands]
          status_label_orig_color = current_hand.status_label.cget('background')
          current_hand.status_label.config(bg='yellow')

          if current_hand.status == HandStatus.ACTIVE:
            current_hand.status_label.config(text=f'ACTIVE {current_hand.score}, BET: {current_hand.bet}')
            self.recommend_basic_strategy(current_hand) ## Update recommend label for recommendation to player
            
            ## Activate relevant buttons
            self.hit_button.config(state="active")
            self.stand_button.config(state="active")
            if seat.base_bet * 2 <= seat.money:
              self.double_down_button.config(state="active")

            if len(current_hand.cards) == 2:
              if (current_hand.cards[0].card == current_hand.cards[1].card):
                self.split_button.config(state="active")
            
            self.active_user_hand = current_hand
            if not self.program_exiting:
              self.stand_button.wait_variable(self.player_standing)
        
            if current_hand.score > 21:
              current_hand.status = HandStatus.LOSER
              current_hand.status_label.config(text=f'BUST {current_hand.score}, BET: {current_hand.bet}')
            else:
              current_hand.status = HandStatus.WAITING
              current_hand.status_label.config(text=f'STAND {current_hand.score}, BET: {current_hand.bet}')
          
          current_hand.status_label.config(bg=status_label_orig_color)
          self.hit_button.config(state="disabled")
          self.double_down_button.config(state="disabled")
          self.split_button.config(state="disabled")
          self.stand_button.config(state="disabled")
          self.recommend_label.config(text='')
          completed_hands += 1
        
      elif seat.type == SeatType.DEALER:
        ## Reveal card
        label = tk.Label(self.table[-1].hand[0].frame, image=self.table[-1].hand[0].cards[-1].image)
        label.grid(row=0,column=1)
        
        ## Play out rest of card
        any_active_hands = False
        
        for seat in self.table:
          if not any_active_hands:
            for hand in seat.hand:
              if hand.status == HandStatus.WAITING:
                any_active_hands = True
                break
          else:
            break

        if any_active_hands:
          while dealer_hand.score < 17:
            self.deal_new_card(dealer_hand)
    
    ## Calculate payouts
    # Determine Winners/Losers
    for seat in self.table:
      for hand in seat.hand:
        if hand.status == HandStatus.WAITING:
          if dealer_hand.score > 21:
            hand.status = HandStatus.WINNER
          elif hand.score == dealer_hand.score:
            hand.status = HandStatus.TIE
          elif hand.score > dealer_hand.score:
            hand.status = HandStatus.WINNER
          else:
            hand.status = HandStatus.LOSER
    
    # Determine Payouts
    for index, seat in enumerate(self.table):
      for hand in seat.hand:
        payout = 0
        
        if hand.status == HandStatus.BLACKJACK:
          payout = hand.bet * self.blackjack_payout_factor
        elif hand.status == HandStatus.WINNER:
          payout = hand.bet
        elif hand.status == HandStatus.LOSER:
          payout = -1 * hand.bet
        
        seat.money += payout

        if hand.status == HandStatus.DEALER:
          if hand.score > 21:
            payout_text = f'BUST {hand.score}'
          else:
            payout_text = f'Total {hand.score}'
        elif hand.status == HandStatus.BLACKJACK:
          payout_text = f'Blackjack Winner {hand.score} +${payout}'
        elif payout > 0:
          payout_text = f'Winner {hand.score} +${payout}'
        elif payout < 0:
          payout_text = f'Loser {hand.score} -${-1 * payout}'
        else:
          payout_text = f'Push {hand.score} +${payout}'

        hand.status_label.config(text=payout_text)
        hand.status_label.grid(columnspan=len(hand.cards))

      frame_text = f'Player {index + 1}: ${seat.money}'

      if index == self.user_seat_no - 1:
        frame_text = f'You: ${seat.money}'
        self.bet_label.config(text=f"Funds: ${seat.money} | Bet Amount:")

      if index < len(self.table) - 1:
        seat.frame.config(text=f'{frame_text}')
      
      if seat.type == SeatType.PLAYER and seat.money <= 0:
        ## If player runs out of money, reload their money.
        ## NOTE: We could change this functionality but this seems to be most convenient.
        seat.money = self.starting_money
        seat.frame.config(text=f'Player {index + 1}: ${seat.money}')

    ## Config Buttons and Labels
    self.play_button.config(state="normal")
    self.bet_input.config(state="normal") 

  def on_exit(self):
    """ Called when user decides to close the window; all active and pending wait_variables are completed or avoided"""
    self.stand_command()
    self.program_exiting = True