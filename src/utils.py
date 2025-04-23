# src/utils.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random

# Global game state tracking
player_cards_history = []  # Stores player's card sequence during gameplay
dealer_visible_card = None  # Tracks dealer's face-up card across states


def card_value_to_str(value):
    """Convert numeric card value to standard Blackjack representation.

    Args:
        value (int): Numeric card value (1-13)

    Returns:
        str: Card symbol (A, 2-10, J, Q, K)
    """
    if value == 1:
        return "A"
    elif value == 10:
        return random.choice(["10", "J", "Q", "K"])  # Randomize 10-value cards
    return str(value)


def generate_initial_player_cards(player_sum, usable_ace):
    """Generate valid initial two-card hand matching specified conditions.

    Args:
        player_sum (int): Desired total sum of initial cards
        usable_ace (bool): Whether hand contains usable ace

    Returns:
        list[str]: Two-card combination meeting criteria

    Raises:
        ValueError: If no valid combination exists
    """
    if usable_ace:
        other_card_value = player_sum - 11
        return ["A", card_value_to_str(other_card_value)]

    # Find all valid non-ace pairs that sum to target
    valid_pairs = [
        (a, player_sum - a) for a in range(2, 11) if 2 <= (player_sum - a) <= 10
    ]

    if not valid_pairs:
        raise ValueError(f"No valid initial hands for sum {player_sum} without ace")

    a, b = random.choice(valid_pairs)
    return [card_value_to_str(a), card_value_to_str(b)]


def determine_new_card(old_sum, new_sum, old_usable, new_usable):
    """Calculate which card caused transition between game states.

    Args:
        old_sum (int): Previous hand total
        new_sum (int): Updated hand total
        old_usable (bool): Previous usable ace status
        new_usable (bool): Current usable ace status

    Returns:
        str: Card symbol representing the drawn card
    """
    if old_usable and not new_usable:
        # Ace value changed from 11 to 1
        raw_value = (new_sum + 10) - old_sum
    else:
        raw_value = new_sum - old_sum

    return card_value_to_str(min(raw_value, 10))  # Cap at 10 for face cards


def draw_card(ax, x, y, card_value, hidden=False, highlight=False):
    """Render a single playing card on matplotlib axes.

    Args:
        ax (matplotlib.axes): Target axes object
        x (float): X-coordinate for card center
        y (float): Y-coordinate for card center
        card_value (str): Card symbol to display
        hidden (bool): Whether to draw as face-down card
        highlight (bool): Whether to emphasize card border
    """
    # Card dimensions and styling
    CARD_WIDTH, CARD_HEIGHT = 0.15, 0.19
    EDGE_COLOR = "gold" if highlight else "black"
    LINE_WIDTH = 2 if highlight else 1

    # Create card background
    card = Rectangle(
        (x - CARD_WIDTH / 2, y - CARD_HEIGHT / 2),
        CARD_WIDTH,
        CARD_HEIGHT,
        facecolor="white" if not hidden else "#222222",
        edgecolor=EDGE_COLOR,
        linewidth=LINE_WIDTH,
    )
    ax.add_patch(card)

    # Hidden card pattern
    if hidden:
        for i in range(5):  # X-axis pattern
            for j in range(10):  # Y-axis pattern
                pattern_tile = Rectangle(
                    (
                        x - CARD_WIDTH / 2 + i * CARD_WIDTH / 5,
                        y - CARD_HEIGHT / 2 + j * CARD_HEIGHT / 10,
                    ),
                    CARD_WIDTH / 10,
                    CARD_HEIGHT / 20,
                    facecolor="#8B0000",
                    alpha=0.5,
                )
                ax.add_patch(pattern_tile)
        return

    # Card value styling
    color = "red" if card_value in ["A", "J", "Q", "K", "10"] else "black"

    # Top-left value
    ax.text(
        x - CARD_WIDTH / 2 + CARD_WIDTH * 0.2,
        y + CARD_HEIGHT / 2 - CARD_HEIGHT * 0.15,
        card_value,
        fontsize=10,
        color=color,
        ha="center",
        va="center",
    )

    # Bottom-right value (upside down)
    ax.text(
        x + CARD_WIDTH / 2 - CARD_WIDTH * 0.2,
        y - CARD_HEIGHT / 2 + CARD_HEIGHT * 0.15,
        card_value,
        fontsize=10,
        color=color,
        ha="center",
        va="center",
        rotation=180,
    )

    # Central value
    ax.text(
        x,
        y,
        card_value,
        fontsize=18,
        color=color,
        ha="center",
        va="center",
        fontweight="bold",
    )


def create_card_visualization(
    player_sum, dealer_card, usable_ace, new_card=None, dealer_cards=None
):
    """Generate complete Blackjack game visualization.

    Args:
        player_sum (int): Current player hand total
        dealer_card (int): Dealer's face-up card value
        usable_ace (bool): Player's usable ace status
        new_card (str, optional): Most recently drawn card
        dealer_cards (list[int], optional): Full dealer hand when revealed

    Returns:
        matplotlib.figure: Complete game visualization
    """
    global player_cards_history, dealer_visible_card

    # Reset state for new game
    if not player_cards_history or dealer_visible_card != dealer_card:
        dealer_visible_card = dealer_card
        player_cards_history = generate_initial_player_cards(player_sum, usable_ace)
    elif new_card:
        player_cards_history.append(new_card)

    # Initialize figure
    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_facecolor("#076324")  # Casino table green
    fig.patch.set_facecolor("#076324")
    ax.axis("off")
    ax.set_title("BLACKJACK", fontsize=20, color="white", fontweight="bold")

    # — Dealer section —
    ax.text(0.5, 0.93, "Dealer", fontsize=14, color="white", ha="center")

    # Calculate dealer total (NUEVO: siempre calculamos la suma)
    if dealer_cards is None:
        # Solo tenemos la carta visible
        dealer_total = 11 if dealer_card == 1 else min(dealer_card, 10)
        draw_card(ax, 0.35, 0.80, card_value_to_str(dealer_card))
        draw_card(ax, 0.65, 0.80, None, hidden=True)
    else:
        # Tenemos todas las cartas del dealer
        dealer_total = sum([11 if c == 1 else min(c, 10) for c in dealer_cards])
        num_aces = dealer_cards.count(1)

        # Ajustar suma si hay Ases y se pasa de 21
        while dealer_total > 21 and num_aces > 0:
            dealer_total -= 10
            num_aces -= 1

        # Mostrar todas las cartas del dealer
        dealer_x_positions = np.linspace(0.2, 0.8, len(dealer_cards))
        for idx, card_val in enumerate(dealer_cards):
            draw_card(ax, dealer_x_positions[idx], 0.80, card_value_to_str(card_val))

    # Mostrar suma del dealer (SIEMPRE) (NUEVO)
    ax.text(
        0.5,
        0.85,  # Posición debajo del título "Dealer"
        (
            f"Dealer Total: {dealer_total}"
            if dealer_cards is None
            else f"Dealer Total: {dealer_total}"
        ),
        fontsize=12,
        color="white",
        ha="center",
    )

    # - Player section
    ax.text(0.5, 0.55, "Player", fontsize=14, color="white", ha="center")
    sum_display = f"Total: {player_sum}"
    sum_display += " (Usable Ace)" if usable_ace else ""
    ax.text(0.5, 0.50, sum_display, fontsize=12, color="white", ha="center")

    # Calculate card positions
    num_cards = len(player_cards_history)
    if num_cards <= 3:
        x_positions = np.linspace(0.2, 0.8, num_cards)
        y_positions = [0.30] * num_cards
    else:  # Split cards into two rows
        top_row = num_cards // 2 + num_cards % 2
        x_positions = np.concatenate(
            [np.linspace(0.2, 0.8, top_row), np.linspace(0.2, 0.8, num_cards - top_row)]
        )
        y_positions = [0.35] * top_row + [0.15] * (num_cards - top_row)

    # Draw player cards
    for idx, card in enumerate(player_cards_history):
        highlight = (idx == len(player_cards_history) - 1) and (new_card is not None)
        draw_card(ax, x_positions[idx], y_positions[idx], card, highlight=highlight)

    plt.tight_layout()
    return fig


def visualize_blackjack_step(old_obs, new_obs=None, action=None, dealer_cards=None):
    """
    Dibuja un paso:
    - new_obs/action=None → solo estado inicial.
    - action==1 → hit (añade new_card).
    - action==0 → stick: muestra dealer_cards si están disponibles.
    - En estados finales (incluyendo empates), muestra dealer_cards si están disponibles.
    
    """
    global player_cards_history

    if new_obs is None or action is None:
        player_cards_history = []
        return create_card_visualization(*old_obs)

    # Show full dealer cards if available
    show_full_dealer = dealer_cards is not None or action == 0 or new_obs[0] >= 21

    if action == 1:
        new_card = determine_new_card(old_obs[0], new_obs[0], old_obs[2], new_obs[2])
        return create_card_visualization(
            new_obs[0],
            new_obs[1],
            new_obs[2],
            new_card=new_card,
            dealer_cards=dealer_cards if show_full_dealer else None,
        )
    else:
        return create_card_visualization(
            new_obs[0],
            new_obs[1],
            new_obs[2],
            dealer_cards=dealer_cards if show_full_dealer else None,
        )
