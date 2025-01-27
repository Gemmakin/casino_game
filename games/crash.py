import random
import math
from PIL import Image, ImageDraw, ImageFont
import io

class CrashGame:
    def __init__(self):
        self.multiplier = 1.0
        self.is_crashed = False
        self.crash_point = self.generate_crash_point()
        self.history = []

    def generate_crash_point(self):
        # Algorithme pour générer un point de crash
        # La probabilité diminue de manière exponentielle
        random_value = random.random()
        crash_value = 0.99 / (1 - random_value)
        return round(max(1.0, min(crash_value, 10.0)), 2)

    def get_current_multiplier(self, elapsed_time):
        if self.is_crashed:
            return self.crash_point
        
        # Calculer le multiplicateur en fonction du temps écoulé
        current = 1.0 + (elapsed_time * 0.5)
        if current >= self.crash_point:
            self.is_crashed = True
            return self.crash_point
        return round(current, 2)

    def create_graph_image(self, elapsed_time):
        # Créer une nouvelle image
        width = 400
        height = 300
        image = Image.new('RGB', (width, height), 'black')
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # Dessiner la grille
        for i in range(0, width, 50):
            draw.line([(i, 0), (i, height)], fill='gray', width=1)
        for i in range(0, height, 50):
            draw.line([(0, i), (width, i)], fill='gray', width=1)

        # Dessiner la courbe
        points = []
        current_multiplier = self.get_current_multiplier(elapsed_time)
        
        for t in range(int(elapsed_time * 100)):
            x = t * width / (elapsed_time * 100)
            y = height - (math.log(1 + (t/100) * 0.5) * 50)
            points.append((x, y))

        if len(points) > 1:
            draw.line(points, fill='green' if not self.is_crashed else 'red', width=2)

        # Afficher le multiplicateur actuel
        multiplier_text = f"{current_multiplier}x"
        draw.text((10, 10), multiplier_text, fill='white', font=font)

        if self.is_crashed:
            draw.text((width//2 - 30, height//2), "CRASH!", fill='red', font=font)

        # Convertir l'image en bytes pour Telegram
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    def calculate_win(self, bet_amount, cash_out_multiplier):
        if cash_out_multiplier <= self.crash_point:
            return int(bet_amount * cash_out_multiplier)
        return 0
