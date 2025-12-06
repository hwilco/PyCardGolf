# CLI User Experience Improvements

This document tracks potential improvements to the PyCardGolf CLI to enhance user experience and playability.

## Display & Visibility Issues

- [x] **1. No visual card position indicators**: The hand display shows cards in 2 rows (indices 1-3 on top, 4-6 on bottom), but doesn't label them with their index numbers. Players have to mentally map positions to indices, which is error-prone.
  - Files: `src/pycardgolf/interfaces/cli.py`
  - **COMPLETED**: Added 1-indexed position indicators (1-6) below each card

- [x] **2. No current score display during gameplay**: Players can't see their running score or visible score during the round. They only see final scores after the round ends.
  - Files: `src/pycardgolf/interfaces/cli.py`, `src/pycardgolf/core/game.py`
  - **COMPLETED**: Added visible score display for each player

- [x] **3. Improve hand display**: The hand display shows cards in 2 rows with indices beneath each row. This could be improved to show the cards in a more compact and intuitive way while still maintaining the 1-indexed position indicators. Perhaps indicators on top of the first row and below the second row, with a deliniation around the actual hand?
  - Files: `src/pycardgolf/interfaces/cli.py`
  - **COMPLETED**: Updated hand display to use a boxed layout with indices aligned above the first row and below the second row.

- [x] **4. No turn counter**: Players don't know how many turns have passed.
  - Files: `src/pycardgolf/interfaces/cli.py`, `src/pycardgolf/core/round.py`
  - **COMPLETED**: Added turn counter to CLI interface

- [x] **5. Unclear face down cards**: Face down cards show as "??" - should include color to indicate which deck they came from.
  - Files: `src/pycardgolf/utils/card.py`
  - **COMPLETED**: Added color to face down cards

## Information & Feedback Gaps

- [x] **6. No explanation of scoring rules**: New players don't know that pairs cancel, 2s are -2 points, Kings are 0, etc. There's no help command or rules summary.
  - Files: `src/pycardgolf/main.py`, `src/pycardgolf/interfaces/cli.py`
  - **COMPLETED**: Added "How to Play" section to README and `--rules` CLI flag

- [x] **7. Missing deck cards remaining**: Players can't see how many cards are left in the deck, which is strategic information.
  - Files: `src/pycardgolf/interfaces/cli.py`
  - **COMPLETED**: Added deck cards remaining display to CLI interface

- [x] **8. No notification when someone triggers end game**: When a player gets all cards face up (triggering the final round), other players aren't not ified that this is everyone's last turn.
  - Files: `src/pycardgolf/core/round.py` (lines 72-76)
  - **COMPLETED**: Added notification when end game condition is triggered

- [x] **10. Bot actions are invisible**: When the bot takes its turn, there's no indication of what action it took, making the game feel empty and less engaging.
  - Files: `src/pycardgolf/players/bots/random_bot.py`
  - **COMPLETED**: Added bot action logging to CLI interface

- [x] **11. No final hand display after each round**: Players don't know what their final hand looks like after each round.
  - Files: `src/pycardgolf/interfaces/cli.py`, `src/pycardgolf/core/round.py`
  - **COMPLETED**: Added final hand display after each round

## Input & Interaction Issues

- [ ] **13. No undo or confirmation**: If you accidentally hit the wrong key, there's no way to undo or confirm risky actions. The undo part is a bit tricky as any move that reveals information (flips a card or draws from the deck) cannot be undone.
  - Files: `src/pycardgolf/players/human.py`

- [ ] **14. No option to quit mid-game**: If a player wants to exit early, they have to Ctrl+C which is jarring. Should be an option to end after each round or see the current standings at any point.
  - Files: `src/pycardgolf/core/game.py`, `src/pycardgolf/players/human.py`

## Polish & Quality of Life

- [x] **15. No color coding**: Even though cards have suit symbols, there's no color differentiation for red/black suits which is traditional.
  - Files: `src/pycardgolf/utils/card.py`
  - **COMPLETED**: Added color coding for all card displays (face up and face down)

- [ ] **16. No animation or delays**: Everything happens instantly, making it hard to follow bot actions or state changes.
  - Files: `src/pycardgolf/interfaces/cli.py`, `src/pycardgolf/players/bots/random_bot.py`

- [x] **17. Winner announcement could be more informative**: Just says "Winner: X with score Y" - should show final standings for all players.
  - Files: `src/pycardgolf/core/game.py` (lines 54-60)
  - **COMPLETED**: Added final standings to winner announcement

- [ ] **18. No game statistics**: At the end, no summary of best round, worst round, average score per round, etc.
  - Files: `src/pycardgolf/core/game.py`

- [x] **19. Initial card flip is automatic**: Players don't get to choose which 2 cards to flip at the start (comment in code says "TODO: allow player to choose").
  - Files: `src/pycardgolf/core/round.py` (lines 47-51)
  - **COMPLETED**: Added option to choose initial cards to flip

## Critical Usability Issues

- [x] **21. No indication that taking from pile is mandatory keep**: When you draw from the discard pile, you MUST replace a card with it. This isn't explained and differs from deck draws.
  - Files: `src/pycardgolf/players/human.py` (lines 68-77)
  - **COMPLETED**: Updated message to explicitly state the card must be kept and player must replace one of their cards

## Notes
- Generated from code analysis on 2025-12-04
- Based on review of CLI implementation without actual gameplay testing
- Many of these improvements would benefit from user testing to validate priority
