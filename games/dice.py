import random
from PIL import Image, ImageDraw
import io

class DiceGame:
    def __init__(self):
        self.dice_patterns = {
            1: [(50, 50)],
            2: [(25, 25), (75, 75)],
            3: [(25, 25), (50, 50), (75, 75)],
            4: [(25, 25), (25, 75), (75, 25), (75, 75)],
            5: [(25, 25), (25, 75), (50, 50), (75, 25), (75, 75)],
            6: [(25, 25), (25, 50), (25, 75), (75, 25), (75, 50), (75, 75)]
        }

    def roll_dice(self, num_dice=2):
        return [random.randint(1, 6) for _ in range(num_dice)]

    def create_dice_image(self, dice_values):
        # Créer une nouvelle image
        width = len(dice_values) * 120
        height = 100
        image = Image.new('RGB', (width, height), 'darkgreen')
        draw = ImageDraw.Draw(image)

        for i, value in enumerate(dice_values):
            # Dessiner le carré blanc du dé
            x_offset = i * 120 + 10
            draw.rectangle([x_offset, 10, x_offset + 80, 90], fill='white', outline='black')

            # Dessiner les points
            for x, y in self.dice_patterns[value]:
                dot_x = x_offset + (x * 80 // 100)
                dot_y = y * 80 // 100
                draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill='black')

        # Convertir l'image en bytes pour Telegram
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    def check_win(self, bet_type, bet_value, dice_values):
        total = sum(dice_values)
        
        if bet_type == 'sum':
            return total == bet_value, 5  # Gain x5 pour la somme exacte
        elif bet_type == 'high_low':
            if bet_value == 'high':
                return total > 7, 2  # Gain x2 pour high/low
            else:  # low
                return total < 7, 2
        elif bet_type == 'even_odd':
            if bet_value == 'even':
                return total % 2 == 0, 2  # Gain x2 pour pair/impair
            else:  # odd
                return total % 2 == 1, 2
        elif bet_type == 'double':
            return dice_values[0] == dice_values[1], 12  # Gain x12 pour un double
        
        return False, 0

    def get_possible_bets(self):
        return {
            'sum': list(range(2, 13)),  # Somme des dés (2-12)
            'high_low': ['high', 'low'],  # Plus grand ou plus petit que 7
            'even_odd': ['even', 'odd'],  # Pair ou impair
            'double': True  # Paris sur un double
        }
