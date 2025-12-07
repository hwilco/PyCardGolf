# How to Play PyCardGolf

## Objective

Golf is a card game where the goal is to achieve the **lowest score** possible. The player with the lowest total score after all rounds wins!

## Setup

- Each player is dealt **6 cards** face down, arranged in a 2×3 grid:
  ```
  [1] [2] [3]
  [4] [5] [6]
  ```
- At the start of the round, each player **flips 2 cards** of their choice face up
- The remaining deck is placed face down (draw pile)
- One card is flipped face up to start the discard pile

## Turn Structure

On your turn, you must:

1. **Draw a card** from either:
   - The **deck** (face down pile)
   - The **discard pile** (top card, face up)

2. **Make a decision**:
   - **If you drew from the deck:**
     - **Keep** the card: Replace one of your 6 cards with it (the replaced card goes to the discard pile)
     - **Discard** the card: Put it on the discard pile, then optionally flip one of your face-down cards
   - **If you drew from the discard pile:**
     - You **must keep** it and replace one of your 6 cards (no discard option)

## Scoring

Scoring is based on **columns** (vertical pairs). Each column is scored independently:

| Card | Value |
|------|-------|
| **Ace** | 1 point |
| **2** | -2 points (negative) |
| **3-10** | Face value (3 = 3 points, 7 = 7 points, etc.) |
| **Jack, Queen** | 10 points each |
| **King** | 0 points |
| **Matching pair in a column** | 0 points (pairs cancel out - including 2s) |

**Example scoring:**
```
A♠ K♥ 3♦  (top row)
2♣ 5♠ 3♥  (bottom row)

Column 1: A♠ + 2♣ = 1 + (-2) = -1
Column 2: K♥ + 5♠ = 0 + 5 = 5
Column 3: 3♦ + 3♥ = 0 (pair cancels!)
Total: -1 + 5 + 0 = 4 points
```

**Example with pairs:**
```
7♠ K♥ 5♦  (top row)
7♣ 2♠ 5♥  (bottom row)

Column 1: 7♠ + 7♣ = 0 (pair cancels!)
Column 2: K♥ + 2♠ = 0 + (-2) = -2
Column 3: 5♦ + 5♥ = 0 (pair cancels!)
Total: 0 + (-2) + 0 = -2 points
```

## How a Round Ends

- The round ends when **one player has all 6 cards face up**
- When this happens, **every other player gets one final turn**
- After all final turns, all cards are revealed and scored
- The round score is added to each player's total score

## Winning

After all rounds are complete, the player with the **lowest total score** wins!


## Controls & Options

### In-Game Controls
- **Quit**: Type `q` or `quit` at any prompt to exit the game immediately.

### Animation Speed
You can adjust the speed of the game (useful for watching bot turns) using the `--delay` flag:
```bash
# Run with 1 second delay between actions
python -m pycardgolf --delay 1.0

When using the `--delay` flag, any keyboard input will skip the delay for that action.
```

---

For more information, visit: https://github.com/hwilco/PyCardGolf
