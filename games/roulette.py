from PIL import Image, ImageDraw, ImageFont
import math
import io
import random

# Configuration
SURFACE_SIZE = (500, 500)
CENTER = (250, 250)
RADIUS = 200

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
GOLD = (255, 215, 0)

class RouletteGame:
    def __init__(self):
        self.numbers = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ]
        self.colors = self.setup_colors()
        self.payouts = {
            'number': 35,  # Mise x35
            'color': 2,    # Mise x2
            'dozen': 3,    # Mise x3
            'half': 2,     # Mise x2
            'column': 3    # Mise x3
        }

    def setup_colors(self):
        colors = {}
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        for num in self.numbers:
            if num == 0:
                colors[num] = GREEN
            elif num in red_numbers:
                colors[num] = RED
            else:
                colors[num] = BLACK
        return colors

    def create_frame(self, angle, ball_angle):
        image = Image.new('RGB', SURFACE_SIZE, GREEN)
        draw = ImageDraw.Draw(image)

        # Dessiner le cercle extérieur
        draw.ellipse([50, 50, 450, 450], fill=BLACK, outline=GOLD, width=5)

        # Dessiner les sections de la roulette
        slice_angle = 2 * math.pi / len(self.numbers)
        for i, number in enumerate(self.numbers):
            start_angle = angle + i * slice_angle
            end_angle = start_angle + slice_angle
            
            # Convertir les angles en degrés pour PIL
            start_deg = math.degrees(start_angle)
            end_deg = math.degrees(end_angle)
            
            # Dessiner le secteur
            draw.pieslice([60, 60, 440, 440], start_deg, end_deg,
                         fill=self.colors[number])
            
            # Ajouter le numéro
            mid_angle = (start_angle + end_angle) / 2
            text_x = CENTER[0] + (RADIUS * 0.75) * math.cos(mid_angle)
            text_y = CENTER[1] + (RADIUS * 0.75) * math.sin(mid_angle)
            
            # Utiliser une police par défaut
            font = ImageFont.load_default()
            text = str(number)
            
            # Obtenir la taille du texte
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Positionner le texte
            text_x -= text_width / 2
            text_y -= text_height / 2
            
            draw.text((text_x, text_y), text, fill=WHITE, font=font)

        # Dessiner la bille
        ball_x = CENTER[0] + (RADIUS * 0.85) * math.cos(ball_angle)
        ball_y = CENTER[1] + (RADIUS * 0.85) * math.sin(ball_angle)
        draw.ellipse([ball_x-8, ball_y-8, ball_x+8, ball_y+8], fill=WHITE)

        return image

    def create_spin_animation(self, final_number):
        frames = []
        
        # Calculer l'angle final pour le numéro choisi
        final_index = self.numbers.index(final_number)
        final_angle = 2 * math.pi * final_index / len(self.numbers)
        # Ajouter quelques tours complets
        final_angle += 4 * 2 * math.pi
        
        # Générer les frames
        num_frames = 30
        for i in range(num_frames):
            progress = i / num_frames
            # Utiliser une fonction non linéaire pour la décélération
            current_angle = final_angle * (1 - (1 - progress) ** 2)
            
            frame = self.create_frame(0, current_angle)
            frames.append(frame)
        
        # Ajouter quelques frames de la position finale
        for _ in range(10):
            frames.append(frames[-1])
        
        # Créer le GIF
        output = io.BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=50,
            loop=0
        )
        output.seek(0)
        return output

    def check_win(self, bet_type, bet_value, winning_number):
        if bet_type == 'number':
            return bet_value == winning_number, self.payouts['number']
        elif bet_type == 'color':
            is_red = winning_number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            if bet_value == 'red':
                return is_red, self.payouts['color']
            else:  # black
                return not is_red and winning_number != 0, self.payouts['color']
        elif bet_type == 'dozen':
            if bet_value == 1:
                return 1 <= winning_number <= 12, self.payouts['dozen']
            elif bet_value == 2:
                return 13 <= winning_number <= 24, self.payouts['dozen']
            else:  # 3
                return 25 <= winning_number <= 36, self.payouts['dozen']
        elif bet_type == 'half':
            if bet_value == 'first':
                return 1 <= winning_number <= 18, self.payouts['half']
            else:  # second
                return 19 <= winning_number <= 36, self.payouts['half']
        elif bet_type == 'column':
            if bet_value == 1:
                return winning_number % 3 == 1, self.payouts['column']
            elif bet_value == 2:
                return winning_number % 3 == 2, self.payouts['column']
            else:  # 3
                return winning_number % 3 == 0 and winning_number != 0, self.payouts['column']
        return False, 0

    def get_color_name(self, number):
        if number == 0:
            return "VERT 🟢"
        elif number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
            return "ROUGE 🔴"
        else:
            return "NOIR ⚫"
