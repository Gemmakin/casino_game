import pygame
import math
import random
import time

# Initialisation de Pygame
pygame.init()

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
GOLD = (255, 215, 0)

# Configuration de la fenêtre
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Roulette Casino")

# Police
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

class RouletteWheel:
    def __init__(self):
        self.center = (400, 250)
        self.radius = 150
        self.numbers = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ]
        self.colors = {}
        self.setup_colors()
        self.angle = 0
        self.ball_angle = 0
        self.ball_speed = 0
        self.is_spinning = False
        self.selected_number = None
        self.result = None

    def setup_colors(self):
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        for num in self.numbers:
            if num == 0:
                self.colors[num] = GREEN
            elif num in red_numbers:
                self.colors[num] = RED
            else:
                self.colors[num] = BLACK

    def draw(self, surface):
        # Dessiner le cercle extérieur
        pygame.draw.circle(surface, GOLD, self.center, self.radius + 5)
        pygame.draw.circle(surface, BLACK, self.center, self.radius)

        # Dessiner les sections de la roulette
        slice_angle = 2 * math.pi / len(self.numbers)
        for i, number in enumerate(self.numbers):
            start_angle = self.angle + i * slice_angle
            end_angle = start_angle + slice_angle
            
            # Dessiner le secteur coloré
            points = [self.center]
            for angle in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi)):
                rad = angle * math.pi / 180
                x = self.center[0] + self.radius * math.cos(rad)
                y = self.center[1] + self.radius * math.sin(rad)
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.polygon(surface, self.colors[number], points)

            # Ajouter le numéro
            mid_angle = (start_angle + end_angle) / 2
            text_x = self.center[0] + (self.radius * 0.85) * math.cos(mid_angle)
            text_y = self.center[1] + (self.radius * 0.85) * math.sin(mid_angle)
            text = small_font.render(str(number), True, WHITE)
            text_rect = text.get_rect(center=(text_x, text_y))
            surface.blit(text, text_rect)

        # Dessiner la bille
        if self.is_spinning:
            ball_x = self.center[0] + (self.radius * 0.9) * math.cos(self.ball_angle)
            ball_y = self.center[1] + (self.radius * 0.9) * math.sin(self.ball_angle)
            pygame.draw.circle(surface, WHITE, (int(ball_x), int(ball_y)), 8)

    def spin(self, bet_number=None):
        self.is_spinning = True
        self.ball_speed = random.uniform(0.2, 0.3)
        self.selected_number = bet_number
        self.result = None

    def update(self):
        if self.is_spinning:
            self.ball_angle += self.ball_speed
            self.ball_speed *= 0.995  # Ralentissement progressif

            if self.ball_speed < 0.001:
                self.is_spinning = False
                # Calculer le numéro gagnant
                angle_normalized = self.ball_angle % (2 * math.pi)
                index = int(len(self.numbers) * angle_normalized / (2 * math.pi))
                if index >= len(self.numbers):
                    index = 0
                self.result = self.numbers[index]

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, surface):
        color = (min(self.color[0] + 30, 255), min(self.color[1] + 30, 255), min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

def main():
    clock = pygame.time.Clock()
    roulette = RouletteWheel()
    
    # Création des boutons
    spin_button = Button(350, 450, 100, 40, "SPIN", RED)
    bet_input = ""
    number_input = ""
    message = ""
    
    # Boutons pour les couleurs
    red_button = Button(250, 500, 100, 40, "ROUGE", RED)
    black_button = Button(450, 500, 100, 40, "NOIR", BLACK)
    
    input_active = False
    betting_on_color = False
    selected_color = None

    running = True
    while running:
        screen.fill(GREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 300 <= event.pos[0] <= 500 and 400 <= event.pos[1] <= 430:
                    input_active = True
                else:
                    input_active = False
            
            if event.type == pygame.KEYDOWN and input_active and not roulette.is_spinning:
                if event.key == pygame.K_RETURN:
                    try:
                        bet = int(bet_input)
                        number = int(number_input)
                        if 0 <= number <= 36:
                            roulette.spin(number)
                            message = f"Mise de {bet}€ sur le numéro {number}"
                        else:
                            message = "Numéro invalide (0-36)"
                    except ValueError:
                        message = "Entrée invalide"
                elif event.key == pygame.K_BACKSPACE:
                    bet_input = bet_input[:-1]
                elif event.key == pygame.K_SPACE:
                    bet_input += " "
                elif event.unicode.isdigit():
                    if len(bet_input.split()) == 0:
                        bet_input += event.unicode
                    elif len(bet_input.split()) == 1:
                        number_input = event.unicode
            
            if spin_button.handle_event(event) and not roulette.is_spinning:
                if betting_on_color and selected_color:
                    try:
                        bet = int(bet_input)
                        roulette.spin()
                        message = f"Mise de {bet}€ sur {selected_color}"
                    except ValueError:
                        message = "Entrée invalide"
                elif bet_input and number_input:
                    try:
                        bet = int(bet_input)
                        number = int(number_input)
                        if 0 <= number <= 36:
                            roulette.spin(number)
                            message = f"Mise de {bet}€ sur le numéro {number}"
                        else:
                            message = "Numéro invalide (0-36)"
                    except ValueError:
                        message = "Entrée invalide"
            
            if red_button.handle_event(event):
                betting_on_color = True
                selected_color = "ROUGE"
                number_input = ""
            
            if black_button.handle_event(event):
                betting_on_color = True
                selected_color = "NOIR"
                number_input = ""

        roulette.update()
        roulette.draw(screen)
        
        # Afficher les boutons
        spin_button.draw(screen)
        red_button.draw(screen)
        black_button.draw(screen)
        
        # Afficher la zone de mise
        pygame.draw.rect(screen, WHITE if input_active else GOLD, (300, 400, 200, 30), 2)
        text_surface = font.render(f"{bet_input} {number_input}", True, WHITE)
        screen.blit(text_surface, (310, 405))
        
        # Afficher le message
        if message:
            text_surface = font.render(message, True, WHITE)
            screen.blit(text_surface, (250, 350))
        
        # Afficher le résultat
        if roulette.result is not None:
            result_color = "ROUGE" if roulette.colors[roulette.result] == RED else "NOIR" if roulette.colors[roulette.result] == BLACK else "VERT"
            if betting_on_color:
                won = (selected_color == "ROUGE" and result_color == "ROUGE") or (selected_color == "NOIR" and result_color == "NOIR")
                result_text = f"Numéro: {roulette.result} ({result_color}) - {'Gagné!' if won else 'Perdu!'}"
            else:
                won = roulette.result == roulette.selected_number
                result_text = f"Numéro: {roulette.result} ({result_color}) - {'Gagné!' if won else 'Perdu!'}"
            text_surface = font.render(result_text, True, GOLD)
            screen.blit(text_surface, (250, 300))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
