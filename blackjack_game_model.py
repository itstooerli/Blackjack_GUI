import tkinter as tk
from PIL import Image, ImageTk
import random
import math
import copy
from enum import Enum

## TODO: Clean up code, e.g. restructure and add comments
## TODO: Change all colors to green
## TODO: Rewrite README
## TODO: Merge changes back to main
## TODO: Figure out what to do if no more money
## TODO: Implement recommended action for basic strategy practice

class BlackjackGameModel:
  def __init__(self, 
               main_frame,
               bet_value_var,
               bet_input,
               play_button,
               hit_button,
               double_down_button,
               split_button,
               stand_button,
               num_decks,
               num_players,
               user_seat_no,
               starting_money):
    self.main_frame = main_frame
    self.bet_value_var = bet_value_var
    self.bet_input = bet_input
    self.play_button = play_button
    self.hit_button = hit_button
    self.double_down_button = double_down_button
    self.split_button = split_button
    self.stand_button = stand_button
    self.base_deck = self.create_deck(num_decks)
    self.user_seat_no = user_seat_no
    self.table = self.setup_table(self.main_frame, num_players, user_seat_no, starting_money)
    self.curr_deck = []
    self.reshuffle_cutoff = 1
    self.player_standing = tk.BooleanVar()
    self.default_image = self.resize_card(f'cards/default.png')
    self.blackjack_payout_factor = 1.5
    self.starting_money = starting_money
    self.bet_value_var.set(self.table[self.user_seat_no - 1].base_bet)
    self.active_user_hand = None ## State variable for which hand the user is currently acting on

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
    def __init__(self, cards, score, num_aces, bet, frame=None, status_label=None):
      self.cards = cards        # Stores an array of Cards
      self.score = score        # Stores the cumulative score
      self.num_aces = num_aces  # Stores the number of aces, since in Blackjack, Ace = 11 or 1
      self.bet = bet            # If the type is a player/AI, what is current bet up to
      self.status = HandStatus.ACTIVE  # Status of the hand
      self.frame = frame        # Stores the frame for this Hand
      self.status_label = status_label  # Stores the status widget to be updated for this hand

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
    dealer_frame.grid(row=0, column=0)
    table_frame = tk.LabelFrame(main_frame, bd=0, bg="yellow")
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
      frame = tk.LabelFrame(table_frame, text=f'Player {player_no + 1}: ${table[player_no].money}', bd=0, bg='magenta')
      frame.grid(row=0, column=player_no, padx=20)
      table[player_no].frame = frame
  
    ## The last seat is always the dealer
    table.append(self.Seat(SeatType.DEALER))
    table[-1].frame = dealer_frame
  
    return table

  def reset_table(self):
    self.play_button.config(state="disabled")
    for seat in self.table:
      for widget in seat.frame.winfo_children():
        widget.destroy()
    
    self.play_game()

  def shuffle_deck(self):
    # curr_deck = copy.deepcopy(self.base_deck)
    self.curr_deck = [card.copy() for card in self.base_deck]
    self.reshuffle_cutoff = random.randrange(math.floor(len(self.base_deck) * 0.25), math.floor(len(self.base_deck) * 0.5))

  def display_card(self, hand, new_card):
    ## Assumed display after cards array increased
    label = tk.Label(hand.frame, image=new_card.image)
    label.grid(row=0, column=(len(hand.cards) - 1))
  
  def deal_cards(self):
    # Initialize each seat's first hand
    for seat in self.table:
      hand_frame = tk.LabelFrame(seat.frame, bd=0, bg='black')
      hand_frame.grid(row=0,column=0)
      status_label = tk.Label(hand_frame)
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
    # Deal a new card to the provided hand
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

  def play_AI_hand_naive_strategy(self, hand):
    while hand.score < 17:
      self.deal_new_card(hand)

    if hand.score > 21:
      hand.status = HandStatus.LOSER
      hand.status_label.config(text=f'BUST {hand.score}, BET: {hand.bet}')
    else:
      hand.status = HandStatus.WAITING
      hand.status_label.config(text=f'STAND {hand.score}, BET: {hand.bet}')

  def play_AI_hand_basic_strategy(self, seat, hand):
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
  
        # Assess Double
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


  def play_game(self):
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
    
    for index, seat in enumerate(self.table):
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

          if current_hand.status == HandStatus.ACTIVE:
            current_hand.status_label.config(text=f'ACTIVE {current_hand.score}, BET: {current_hand.bet}')
            ## Activate relevant buttons
            self.hit_button.config(state="active")
            self.stand_button.config(state="active")
            if seat.base_bet * 2 <= seat.money:
              self.double_down_button.config(state="active")

            if len(current_hand.cards) == 2:
              if (current_hand.cards[0].card == current_hand.cards[1].card) or (current_hand.cards[0].value == current_hand.cards[1].value):
                self.split_button.config(state="active")
            
            self.active_user_hand = current_hand
            self.stand_button.wait_variable(self.player_standing)
        
            if current_hand.score > 21:
              current_hand.status = HandStatus.LOSER
              current_hand.status_label.config(text=f'BUST {current_hand.score}, BET: {current_hand.bet}')
            else:
              current_hand.status = HandStatus.WAITING
              current_hand.status_label.config(text=f'STAND {current_hand.score}, BET: {current_hand.bet}')
          
          self.hit_button.config(state="disabled")
          self.double_down_button.config(state="disabled")
          self.split_button.config(state="disabled")
          self.stand_button.config(state="disabled")
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

      if index < len(self.table) - 1:
        seat.frame.config(text=f'Player {index + 1}: ${seat.money}')
      
      if seat.type == SeatType.PLAYER and seat.money <= 0:
        ## TODO: Figure out what to do if out of money
        seat.money = self.starting_money
        seat.frame.config(text=f'Player {index + 1}: ${seat.money}')

    ## Config Buttons
    self.play_button.config(state="normal")
    self.bet_input.config(state="normal")

  def hit_command(self):
    self.deal_new_card(self.active_user_hand)
  
    if self.active_user_hand.score > 21:
      self.stand_command()

  def double_down_command(self):
    self.double_down(self.active_user_hand)
    self.stand_command()

  def double_down(self, hand):
    self.deal_new_card(hand)
    hand.bet *= 2

  def split_command(self):
    self.split_button.config(state="disabled")
    seat = self.table[self.user_seat_no - 1]
    self.split_hand(seat, self.active_user_hand)

    if (self.active_user_hand.cards[0].card == self.active_user_hand.cards[1].card) or (self.active_user_hand.cards[0].value == self.active_user_hand.cards[1].value):
      self.split_button.config(state="active")

  def split_hand(self, seat, hand):
    split_card = hand.cards[1]
    
    # Remove the split card from the current hand
    hand.score -= split_card.value
    hand.cards.pop()
    hand.frame.winfo_children()[-1].destroy()

    # Create new hand
    if split_card.card == "A":
      split_card.value = 11
      hand.num_aces -= 1

    hand_frame = tk.LabelFrame(seat.frame, bd=0, bg='black')
    hand_frame.grid(row=len(seat.hand),column=0)
    status_label = tk.Label(hand_frame, text=f'Bet ${seat.base_bet}')
    status_label.grid(row=1,column=0,columnspan=2)
    seat.hand.append(self.Hand([split_card], split_card.value, hand.num_aces, seat.base_bet, hand_frame, status_label))
    self.display_card(seat.hand[-1], split_card)

    # Deal both hands a new card
    self.deal_new_card(hand)
    self.deal_new_card(seat.hand[-1])
    seat.hand[-1].status_label.config(text=f'WAITING {seat.hand[-1].score}, BET: {seat.hand[-1].bet}')

  def stand_command(self):
    self.player_standing.set(not self.player_standing)

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