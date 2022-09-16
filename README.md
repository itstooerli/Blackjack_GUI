# Blackjack w/ GUI
Vegas-style blackjack game using Python Tkinter

Functionality includes bets, splits, double downs, and up to 6 other computer seats that play blackjack basic strategy.

## Instructions
### Running the program
* This program requires the use of Python module Pillow.
  * > `py -m pip install Pillow`
  * Alternative is to run on Replit: [Blackjack GUI Replit](https://replit.com/@itstooerli/BlackjackGUI?v=1)
* Run the blackjack_GUI.py script
  * Command Line: > `py blackjackGUI.py`
### Configuring settings
* You should then see a settings window that allows you set specific parameters for your game.
![blackjack_Settings](/images/blackjack_settings.png)
  * Number of decks (default 6): Specify number of 52-card decks to shuffle for this game, minimum=1, maximum=10
  * Number of players (default 3): Specify number of players to play at table, one player will be you the user, the rest will be computers, minimum=1, maximum=6
  * Player's seat number (default 1): Specify where at the table you'd like to sit, 1 being the earliest, the number specified in Number of players being the latest
  * Player's starting money (default 1000): Specifiy number to begin with for player's funds
  * NOTE: You must click __Submit__ to actually change the setting. Otherwise, it will not save your change (and also verify that you submitted an integer)
* When ready (or if you're fine with defaults), click __Start Game__.
* You will then see a new game window. 
### Playing the Game
* At the bottom of the game window, you will see how much money you have left and an input to specify how much you'd like to bet for the next hand. You will use this button whenever you want to start a new hand.
![command_frames](/images/command_frames.png)
* When ready, click __Play (Submit Bet)__.
* You'll now see the table generate and cards dealt to each of the players.
![blackjack_game](/images/blackjack_game.png)
* Your hand(s) will be under the label "You", which also provides the total amount of funds you have left.
* The computers will automatically play their hands using basic strategy when it is their turn.
* When it is your turn, your hand's status (seen below you cards) will highlight in yellow.
* The status label under the hand will indicate
  1. hand's current status
  2. the total amount that your hand adds up to
  3. the amount invested/bet into this hand
* The possible statuses during play are
  * BLACKJACK: The hand is a blackjack (21 from first two cards without any action), no additional play is given to player in this scenario
  * ACTIVE: The hand is the current one being controlled
  * WAITING: The hand is waiting to be acted upon
  * STAND: The hand has completed action and is waiting for dealer to play
  * BUST: The hand has went over a total score of 21
* You can then act on your hand, whether that be Hit, Double Down, Split, Stand.
  * Hit: Ask for another card
  * Double Down: The player chooses to double their original bet for one and only one extra card. The player can do no other action after doublign down.
  * Split: If the player's first two cards are the same denomination/rank (e.g. Queen and Queen, but not Queen and Jack), then they can choose to treat them as two separate hands. The original bet is placed on the first hand and an equal amount is placed on the second hand. Each hand is dealt and extra card and then play begins as normal for each hand. Normally, with a pair of aces, the player is given one card for each ace and no additional action can begin, but this is ignored for this iteration of the game.
  * Stand: Do not ask for another card and stay with current total
  * For more detailed rules, suggested to see [Bicycle Cards Blackjack Rules](https://bicyclecards.com/how-to-play/blackjack/).
* After play is complete, the status label will update with the result of the hand and the net change in funds for the player.
![blackjack_result](/images/blackjack_result.png)
Possible results are
  * Blackjack Winner: Player won with blackjack! (Payout is 1.5 * Bet.)
  * Winner: Player had a greater total than dealer or dealer busted
  * Push: Player tied dealer
  * Loser: Player had lower total than dealer or player busted
* Play continues as from beginning of this subsection Playing the Game

## Next Steps
* Provide a recommendation system if desired to help users learn basic strategy

## Authors
Contributors names
* Eric Li

## Related Games
* For command line version : [Blackjack Replit](https://replit.com/@itstooerli/Blackjack?v=1) [Blackjack GitHub](https://github.com/itstooerli/Blackjack)
