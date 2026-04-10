# Player Logic Flow - HAMOOPIG (Ver. 1.0 CPU 6.2 [Nemezes Edition])

This version of HAMOOPIG, known as the "Nemezes Edition," expands the core engine with a full single-player campaign and a sophisticated AI system.

## 1. Single-Player Campaign (Tournament)

The engine implements a standard fighting game progression:
*   **Stage-Based Opponents**: Defined in `P2fase[9]`. For example, P1 might face Gillius in Stage 1 and Haohmaru in Stage 2.
*   **Dynamic Environments**: Each stage automatically maps to a specific background (`BGfase[9]`).
*   **Difficulty Scaling**: As the player progresses through `faseMAX`, the AI becomes more aggressive and has better defensive reaction times.

## 2. AI Logic (Nemezes System)

The Player 2 AI operates through a set of independent timers and state variables:

### Decision Matrix
*   **Proximity Check**: The AI calculates `abs(P[1].x - P[2].x)`.
    *   **Close Range (< 150px)**: Triggers `tempoIAataque`. The AI enters an "Attack Window" based on `tempoMinIAataque[fase]`.
    *   **Long Range (> 200px)**: Triggers `tempoIAmagia`. The AI attempts to zone the player with projectiles.
*   **Attack Selection**: Uses `acaoIA` to choose between Weak, Medium, or Fierce strikes.
*   **Defensive Logic**: Uses `defesaIA[fase]`. A lower value means the AI is more likely to enter a blocking state when the player is close and attacking.

### AI State Flow

```ascii
       [ IDLE / SCANNING ] <------------------------+
               |                                    |
       +-------+-------+                            |
       |               |                            |
    [ CLOSE ]       [ FAR ]                         |
       |               |                            |
    [ ATK / DEF ]   [ ZONE / DASH ]                 |
       |               |                            |
       +-------+-------+                            |
               |                                    |
       [ COOLDOWN (tempoIA) ] ----------------------+
```

## 3. Gameplay Enhancements

*   **P1 vs CPU Menu**: A new entry screen allows players to toggle `IAP2 = TRUE`.
*   **Pause System**: Players can now pause the game, freezing state updates while maintaining VRAM contents.
*   **Nemezes Branding**: Credits the AI developer and features unique "Nemezes Edition" UI text.
