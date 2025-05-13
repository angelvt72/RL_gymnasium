# src/utils.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random

# Global game state tracking
player_cards_history = []  # Stores historical sequence of player's drawn cards
dealer_visible_card = None  # Tracks dealer's visible card across game states

# Variable global para mantener consistencia en símbolos 10/J/Q/K
TEN_VALUE_SYMBOL = None  # Se establecerá al generar la primera carta 10+


def card_value_to_str(value):
    """Convierte valor numérico a símbolo, manteniendo consistencia en 10/J/Q/K."""
    global TEN_VALUE_SYMBOL

    if value == 1:
        return "A"
    elif value == 10:
        if TEN_VALUE_SYMBOL is None:
            TEN_VALUE_SYMBOL = random.choice(["10", "J", "Q", "K"])
        return TEN_VALUE_SYMBOL
    return str(value)


def reset_globals():
    """Reinicia estado global para nuevas partidas."""
    global player_cards_history, dealer_visible_card, TEN_VALUE_SYMBOL
    player_cards_history = []
    dealer_visible_card = None
    TEN_VALUE_SYMBOL = None  # ¡Importante! Resetea el símbolo para nuevas partidas


def generate_initial_player_cards(player_sum, usable_ace):
    """Generate valid initial two-card hand matching specified Blackjack conditions.

    Args:
        player_sum (int): Target sum for initial two-card hand (12-21)
        usable_ace (bool): Whether the hand should contain a usable ace

    Returns:
        list[str]: Two-card combination meeting criteria, formatted as symbols

    Raises:
        ValueError: If no valid combination exists for given parameters

    Example:
        >>> generate_initial_player_cards(16, True)
        ['A', '5']  # 11 + 5 = 16
        >>> generate_initial_player_cards(19, False)
        ['9', '10']  # 9 + 10 = 19
    """
    if usable_ace:
        other_card_value = player_sum - 11
        return ["A", card_value_to_str(other_card_value)]

    # Generate valid non-ace pairs that sum to target
    valid_pairs = [
        (a, player_sum - a) for a in range(2, 11) if 2 <= (player_sum - a) <= 10
    ]

    if not valid_pairs:
        raise ValueError(f"No valid initial hands for sum {player_sum} without ace")

    a, b = random.choice(valid_pairs)
    return [card_value_to_str(a), card_value_to_str(b)]


def determine_new_card(
    old_sum: int,
    new_sum: int,
    old_usable: bool,
    new_usable: bool,
    player_cards_history: list[str],
) -> str:
    """Determine the drawn card symbol between game states while maintaining visual consistency.

    Handles special cases for aces and 10-value cards (10/J/Q/K), prioritizing existing symbols
    in the player's hand for consistent visualization.

    Args:
        old_sum (int): Player's total sum before drawing the new card
        new_sum (int): Player's total sum after drawing the new card
        old_usable (bool): Whether the player had a usable ace before drawing
        new_usable (bool): Whether the player has a usable ace after drawing
        player_cards_history (list[str]): Sequence of card symbols in player's hand

    Returns:
        str: Symbol representing the drawn card (A, 2-10, J, Q, K)

    Examples:
        >>> # Case 1: Drawing an Ace that becomes usable
        >>> determine_new_card(15, 16, False, True, ['10', '5'])
        'A'

        >>> # Case 2: Ace becomes non-usable due to bust
        >>> determine_new_card(16, 7, True, False, ['A', '5'])
        'A'

        >>> # Case 3: Drawing a 10-value card with existing J
        >>> determine_new_card(10, 20, False, False, ['J'])
        'J'  # Maintains consistency with existing Jack

        >>> # Case 4: Normal card draw
        >>> determine_new_card(12, 15, False, False, ['7', '5'])
        '3'
    """
    # Case 1: New Ace added (wasn't usable before, now is)
    if not old_usable and new_usable:
        return "A"

    # Case 2: Existing Ace became non-usable (11 → 1 value change)
    if old_usable and not new_usable:
        return "A"

    # Calculate numerical difference between states
    value_diff = new_sum - old_sum

    # Case 3: Handle 10-value cards using existing symbols for consistency
    if value_diff == 10:
        # Find all 10-value symbols already in player's hand
        existing_10s = [
            card for card in player_cards_history if card in {"10", "J", "Q", "K"}
        ]

        # Prioritize existing symbols to maintain visual consistency
        if existing_10s:
            return random.choice(existing_10s)

    # General case: Convert numerical difference to card symbol
    # Cap at 10 for face cards (J/Q/K are all value 10)
    return card_value_to_str(min(value_diff, 10))


def draw_card(ax, x, y, card_value, hidden=False, highlight=False):
    """Draw a single playing card on matplotlib axes.

    Args:
        ax (matplotlib.axes.Axes): Target axes object for drawing
        x (float): X-coordinate for card center (0-1 normalized)
        y (float): Y-coordinate for card center (0-1 normalized)
        card_value (str): Card symbol to display (ignored if hidden=True)
        hidden (bool): Draw face-down card if True
        highlight (bool): Highlight card border if True

    Returns:
        None: Modifies axes object directly

    Example:
        >>> fig, ax = plt.subplots()
        >>> draw_card(ax, 0.5, 0.5, 'A', highlight=True)
        # Draws centered ace card with gold border
    """
    # Card dimensions and styling parameters
    CARD_WIDTH, CARD_HEIGHT = 0.15, 0.19
    EDGE_COLOR = "gold" if highlight else "black"
    LINE_WIDTH = 2 if highlight else 1

    # Create card background rectangle
    card = Rectangle(
        (x - CARD_WIDTH / 2, y - CARD_HEIGHT / 2),
        CARD_WIDTH,
        CARD_HEIGHT,
        facecolor="white" if not hidden else "#222222",  # Dark gray for hidden
        edgecolor=EDGE_COLOR,
        linewidth=LINE_WIDTH,
    )
    ax.add_patch(card)

    # Draw hidden card pattern
    if hidden:
        for i in range(5):  # Create grid pattern
            for j in range(10):
                pattern_tile = Rectangle(
                    (
                        x - CARD_WIDTH / 2 + i * CARD_WIDTH / 5,
                        y - CARD_HEIGHT / 2 + j * CARD_HEIGHT / 10,
                    ),
                    CARD_WIDTH / 10,
                    CARD_HEIGHT / 20,
                    facecolor="#8B0000",  # Dark red
                    alpha=0.5,
                )
                ax.add_patch(pattern_tile)
        return

    # Determine card text color
    color = "red" if card_value in ["A", "J", "Q", "K", "10"] else "black"

    # Top-left value display
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

    # Central large value
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
    player_sum: int,
    dealer_card: int,
    usable_ace: bool,
    new_card: str = None,
    dealer_cards: list[int] = None,
) -> plt.Figure:
    """
    Genera una visualización completa del estado del juego de Blackjack.

    Args:
        player_sum (int): Suma total de las cartas del jugador
        dealer_card (int): Valor numérico de la carta visible del dealer (1-13)
        usable_ace (bool): Indica si el jugador tiene un As usable
        new_card (str, opcional): Símbolo de la última carta robada
        dealer_cards (list[int], opcional): Lista completa de cartas del dealer cuando se revelan

    Returns:
        matplotlib.figure.Figure: Figura con la visualización del juego

    Ejemplo:
        >>> # Muestra estado inicial: jugador 18, dealer muestra 10
        >>> fig = create_card_visualization(18, 10, False)
    """
    global player_cards_history, dealer_visible_card

    # Reiniciar SIEMPRE que cambie la carta del dealer
    if dealer_visible_card != dealer_card:
        dealer_visible_card = dealer_card
        player_cards_history = generate_initial_player_cards(player_sum, usable_ace)
    elif new_card:
        player_cards_history.append(new_card)

    # ------ Configuración inicial de la figura ------
    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_facecolor("#076324")  # Color de mesa de blackjack
    ax.axis("off")
    ax.set_title("BLACKJACK", fontsize=20, color="white", fontweight="bold")
    fig.patch.set_facecolor("#076324")  # Restaura el fondo
    ax.set_facecolor("#076324")  # Fondo del área de juego

    # ------ Sección Dealer ------
    ax.text(0.5, 0.93, "Dealer", fontsize=14, color="white", ha="center")

    # Lógica clave para mostrar cartas del dealer
    if dealer_cards is None:
        # Caso 1: Solo muestra carta visible + oculta
        dealer_total = 11 if dealer_card == 1 else min(dealer_card, 10)
        draw_card(ax, 0.35, 0.80, card_value_to_str(dealer_card))  # Carta visible
        draw_card(ax, 0.65, 0.80, None, hidden=True)  # Carta oculta (boca abajo)
    else:
        # Caso 2: Muestra todas las cartas del dealer (juego terminado)
        dealer_total = sum([11 if c == 1 else min(c, 10) for c in dealer_cards])
        num_aces = dealer_cards.count(1)

        # Ajuste de Ases para evitar pasarse de 21
        while dealer_total > 21 and num_aces > 0:
            dealer_total -= 10
            num_aces -= 1

        # Dibuja todas las cartas del dealer
        dealer_x_positions = np.linspace(0.2, 0.8, len(dealer_cards))
        for idx, card_val in enumerate(dealer_cards):
            draw_card(ax, dealer_x_positions[idx], 0.80, card_value_to_str(card_val))

    # Muestra siempre el total del dealer
    ax.text(
        0.5,
        0.85,
        f"Dealer Total: {dealer_total}",
        fontsize=12,
        color="white",
        ha="center",
    )

    # ------ Sección Jugador ------
    ax.text(0.5, 0.55, "Player", fontsize=14, color="white", ha="center")
    sum_display = f"Total: {player_sum}"
    sum_display += " (As usable)" if usable_ace else ""
    ax.text(0.5, 0.50, sum_display, fontsize=12, color="white", ha="center")

    # ------ Posicionamiento de cartas del jugador ------
    num_cards = len(player_cards_history)
    if num_cards <= 3:
        x_positions = np.linspace(0.2, 0.8, num_cards)
        y_positions = [0.30] * num_cards
    else:  # Dos filas para más de 3 cartas
        top_row = num_cards // 2 + num_cards % 2
        x_positions = np.concatenate(
            [np.linspace(0.2, 0.8, top_row), np.linspace(0.2, 0.8, num_cards - top_row)]
        )
        y_positions = [0.35] * top_row + [0.15] * (num_cards - top_row)

    # Dibuja todas las cartas del jugador
    for idx, card in enumerate(player_cards_history):
        highlight = (idx == len(player_cards_history) - 1) and (new_card is not None)
        draw_card(ax, x_positions[idx], y_positions[idx], card, highlight=highlight)

    plt.tight_layout()
    return fig


def visualize_blackjack_step(old_obs, new_obs=None, action=None, dealer_cards=None):
    """Visualize game state transitions for Blackjack environment.

    Handles different visualization states:
    - Initial state (when new_obs/action=None)
    - Hit action (action=1) showing new card
    - Stick action (action=0) revealing dealer cards
    - Terminal states (player sum >=21) with dealer reveal

    Args:
        old_obs (tuple): Previous observation (player_sum, dealer_card, usable_ace)
        new_obs (tuple, optional): Updated observation after action
        action (int, optional): 0=stick, 1=hit
        dealer_cards (list[int], optional): Dealer's full hand when known

    Returns:
        matplotlib.figure.Figure: Updated visualization figure

    Example:
        >>> # Initial state
        >>> fig = visualize_blackjack_step((15, 10, True))
        >>> # After hit action
        >>> fig = visualize_blackjack_step((15,10,True), (20,10,False), 1)
    """
    global player_cards_history

    # Handle initial state
    if new_obs is None or action is None:
        player_cards_history = []
        return create_card_visualization(*old_obs)

    # Determine if dealer cards should be fully revealed
    show_full_dealer = dealer_cards is not None or action == 0 or new_obs[0] >= 21

    # Handle hit action visualization
    if action == 1:
        new_card = determine_new_card(
            old_obs[0],
            new_obs[0],
            old_obs[2],
            new_obs[2],
            player_cards_history,  # ← Pasar el historial
        )
    # Handle stick action or terminal state
    else:
        return create_card_visualization(
            new_obs[0],
            new_obs[1],
            new_obs[2],
            dealer_cards=dealer_cards if show_full_dealer else None,
        )
