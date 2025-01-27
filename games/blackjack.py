import random
from PIL import Image, ImageDraw, ImageFont
import io
import os

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.display_value = {
            1: 'A', 11: 'J', 12: 'Q', 13: 'K'
        }.get(value, str(value))
        self.suit_symbol = {
            'hearts': '♥',
            'diamonds': '♦',
            'clubs': '♣',
            'spades': '♠'
        }[suit]
        self.is_red = suit in ['hearts', 'diamonds']

    def get_value(self):
        if self.value == 1:
            return 11  # As vaut 11 par défaut
        return min(self.value, 10)  # Les figures valent 10

class BlackjackGame:
    def __init__(self):
        self.suits = ['hearts', 'diamonds', 'clubs', 'spades']
        self.reset_deck()

    def reset_deck(self):
        self.deck = []
        for suit in self.suits:
            for value in range(1, 14):
                self.deck.append(Card(suit, value))
        random.shuffle(self.deck)

    def draw_card(self):
        if not self.deck:
            self.reset_deck()
        return self.deck.pop()

    def calculate_score(self, cards):
        score = 0
        aces = 0
        
        for card in cards:
            if card.value == 1:
                aces += 1
            else:
                score += card.get_value()
        
        # Ajouter les as
        for _ in range(aces):
            if score + 11 <= 21:
                score += 11
            else:
                score += 1
        
        return score

    def create_card_image(self, card, x, y, draw, font):
        # Dessiner le fond de la carte
        card_width = 60
        card_height = 80
        draw.rectangle([x, y, x + card_width, y + card_height], fill='white', outline='black')
        
        # Couleur du texte
        text_color = 'red' if card.is_red else 'black'
        
        # Dessiner la valeur et le symbole
        text = f"{card.display_value}{card.suit_symbol}"
        draw.text((x + 5, y + 5), text, fill=text_color, font=font)
        draw.text((x + card_width - 20, y + card_height - 25), text, fill=text_color, font=font)

    def create_game_image(self, player_cards, dealer_cards, show_dealer=False):
        # Créer une nouvelle image
        image = Image.new('RGB', (400, 300), 'darkgreen')
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # Dessiner les cartes du croupier
        draw.text((10, 10), "Croupier:", fill='white', font=font)
        for i, card in enumerate(dealer_cards):
            if i == 0 or show_dealer:
                self.create_card_image(card, 10 + i * 70, 30, draw, font)
            else:
                # Carte face cachée
                draw.rectangle([10 + i * 70, 30, 70 + i * 70, 110], fill='blue', outline='white')

        # Dessiner les cartes du joueur
        draw.text((10, 150), "Joueur:", fill='white', font=font)
        for i, card in enumerate(player_cards):
            self.create_card_image(card, 10 + i * 70, 170, draw, font)

        # Afficher les scores
        player_score = self.calculate_score(player_cards)
        draw.text((10, 270), f"Score: {player_score}", fill='white', font=font)
        
        if show_dealer:
            dealer_score = self.calculate_score(dealer_cards)
            draw.text((10, 130), f"Score: {dealer_score}", fill='white', font=font)

        # Convertir l'image en bytes pour Telegram
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    def is_blackjack(self, cards):
        return len(cards) == 2 and self.calculate_score(cards) == 21

    def is_bust(self, cards):
        return self.calculate_score(cards) > 21

    def dealer_should_hit(self, cards):
        return self.calculate_score(cards) < 17
