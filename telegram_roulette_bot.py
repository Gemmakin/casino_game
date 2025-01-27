import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import math

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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

class RouletteWheel:
    def __init__(self):
        self.numbers = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ]
        self.colors = self.setup_colors()

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
        # Créer une nouvelle image
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

def create_roulette_gif(final_number, roulette):
    frames = []
    
    # Calculer l'angle final pour le numéro choisi
    final_index = roulette.numbers.index(final_number)
    final_angle = 2 * math.pi * final_index / len(roulette.numbers)
    # Ajouter quelques tours complets
    final_angle += 4 * 2 * math.pi
    
    # Générer les frames
    num_frames = 30
    for i in range(num_frames):
        progress = i / num_frames
        # Utiliser une fonction non linéaire pour la décélération
        current_angle = final_angle * (1 - (1 - progress) ** 2)
        
        frame = roulette.create_frame(0, current_angle)
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

# Dictionnaire pour stocker les soldes des utilisateurs
user_balances = {}
DEFAULT_BALANCE = 1000

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_balances:
        user_balances[user_id] = DEFAULT_BALANCE
    
    keyboard = [
        [
            InlineKeyboardButton("🔴 Rouge", callback_data='bet_red'),
            InlineKeyboardButton("⚫ Noir", callback_data='bet_black')
        ],
        [InlineKeyboardButton("🎯 Numéro spécifique", callback_data='bet_number')],
        [InlineKeyboardButton("💰 Voir mon solde", callback_data='balance')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Bienvenue à la Roulette! 🎰\n"
        f"Votre solde actuel est de {user_balances[user_id]}€\n"
        f"Choisissez votre type de mise :",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'bet_red':
        context.user_data['bet_type'] = 'red'
        await query.edit_message_text(
            "Vous pariez sur ROUGE 🔴\n"
            "Envoyez le montant de votre mise (exemple: 100)"
        )
    elif query.data == 'bet_black':
        context.user_data['bet_type'] = 'black'
        await query.edit_message_text(
            "Vous pariez sur NOIR ⚫\n"
            "Envoyez le montant de votre mise (exemple: 100)"
        )
    elif query.data == 'bet_number':
        context.user_data['bet_type'] = 'number'
        await query.edit_message_text(
            "Pariez sur un numéro spécifique 🎯\n"
            "Envoyez votre mise et le numéro au format: mise numero\n"
            "Exemple: 100 17"
        )
    elif query.data == 'balance':
        user_id = update.effective_user.id
        await query.edit_message_text(
            f"Votre solde actuel est de {user_balances[user_id]}€"
        )

async def handle_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_balances:
        user_balances[user_id] = DEFAULT_BALANCE
    
    if 'bet_type' not in context.user_data:
        await update.message.reply_text("Utilisez /start pour commencer une partie!")
        return

    bet_type = context.user_data['bet_type']
    roulette = RouletteWheel()
    
    try:
        if bet_type in ['red', 'black']:
            mise = int(update.message.text)
            if mise > user_balances[user_id]:
                await update.message.reply_text("Vous n'avez pas assez d'argent!")
                return
            
            # Message d'attente pendant la génération du GIF
            wait_message = await update.message.reply_text("🎰 Génération de la roulette en cours...")
            
            # Générer le numéro gagnant et créer le GIF
            winning_number = random.randint(0, 36)
            gif_buffer = create_roulette_gif(winning_number, roulette)
            
            # Envoyer le GIF
            await update.message.reply_animation(
                animation=gif_buffer,
                caption="La roulette tourne... 🎰"
            )
            
            # Supprimer le message d'attente
            await wait_message.delete()
            
            # Vérifier le résultat
            red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            is_red = winning_number in red_numbers
            won = (bet_type == 'red' and is_red) or (bet_type == 'black' and not is_red and winning_number != 0)
            
            if won:
                gain = mise
                user_balances[user_id] += gain
                await update.message.reply_text(
                    f"🎉 FÉLICITATIONS! Le numéro est {winning_number} "
                    f"({'ROUGE 🔴' if is_red else 'NOIR ⚫'})\n"
                    f"Vous gagnez {gain}€!\n"
                    f"Nouveau solde: {user_balances[user_id]}€"
                )
            else:
                user_balances[user_id] -= mise
                await update.message.reply_text(
                    f"😢 Perdu! Le numéro est {winning_number} "
                    f"({'ROUGE 🔴' if is_red else 'NOIR ⚫' if winning_number != 0 else 'VERT 🟢'})\n"
                    f"Vous perdez {mise}€\n"
                    f"Nouveau solde: {user_balances[user_id]}€"
                )
        
        elif bet_type == 'number':
            mise, numero = map(int, update.message.text.split())
            if mise > user_balances[user_id]:
                await update.message.reply_text("Vous n'avez pas assez d'argent!")
                return
            
            if numero < 0 or numero > 36:
                await update.message.reply_text("Le numéro doit être entre 0 et 36!")
                return
            
            # Message d'attente pendant la génération du GIF
            wait_message = await update.message.reply_text("🎰 Génération de la roulette en cours...")
            
            # Générer le numéro gagnant et créer le GIF
            winning_number = random.randint(0, 36)
            gif_buffer = create_roulette_gif(winning_number, roulette)
            
            # Envoyer le GIF
            await update.message.reply_animation(
                animation=gif_buffer,
                caption="La roulette tourne... 🎰"
            )
            
            # Supprimer le message d'attente
            await wait_message.delete()
            
            if winning_number == numero:
                gain = mise * 35
                user_balances[user_id] += gain
                await update.message.reply_text(
                    f"🎉 FÉLICITATIONS! Le numéro est {winning_number}\n"
                    f"Vous gagnez {gain}€!\n"
                    f"Nouveau solde: {user_balances[user_id]}€"
                )
            else:
                user_balances[user_id] -= mise
                await update.message.reply_text(
                    f"😢 Perdu! Le numéro est {winning_number}\n"
                    f"Vous perdez {mise}€\n"
                    f"Nouveau solde: {user_balances[user_id]}€"
                )
    
    except ValueError:
        await update.message.reply_text(
            "Format invalide!\n"
            "Pour un numéro: mise numero (exemple: 100 17)\n"
            "Pour une couleur: juste la mise (exemple: 100)"
        )

def main():
    application = Application.builder().token("7606399757:AAGYOWOo9UtCisjjgVGQjFKXGm8ZOHEP-CA").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bet))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
