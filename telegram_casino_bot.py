import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Dictionnaire pour stocker les soldes des utilisateurs
user_balances = {}
DEFAULT_BALANCE = 1000

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_balances:
        user_balances[user_id] = DEFAULT_BALANCE
    
    keyboard = [
        [InlineKeyboardButton("🎰 Roulette", callback_data='roulette')],
        [InlineKeyboardButton("🎲 Blackjack", callback_data='blackjack')],
        [InlineKeyboardButton("💰 Voir mon solde", callback_data='balance')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Bienvenue au Casino Telegram! 🎰\n"
        f"Votre solde actuel est de {user_balances[user_id]}€\n"
        f"Choisissez un jeu :",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'roulette':
        await start_roulette(query, context)
    elif query.data == 'blackjack':
        await start_blackjack(query, context)
    elif query.data == 'balance':
        user_id = update.effective_user.id
        await query.edit_message_text(f"Votre solde actuel est de {user_balances[user_id]}€")

async def start_roulette(query: Update.callback_query, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['game'] = 'roulette'
    await query.edit_message_text(
        "🎰 Roulette\n"
        "Pour jouer, envoyez votre mise et le numéro choisi au format:\n"
        "mise numero\n"
        "Exemple: 100 17"
    )

async def start_blackjack(query: Update.callback_query, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['game'] = 'blackjack'
    await query.edit_message_text(
        "🎲 Blackjack\n"
        "Pour commencer, envoyez votre mise.\n"
        "Exemple: 100"
    )

async def handle_game_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_balances:
        user_balances[user_id] = DEFAULT_BALANCE
    
    if 'game' not in context.user_data:
        await update.message.reply_text("Utilisez /start pour commencer une partie!")
        return
    
    game = context.user_data['game']
    
    if game == 'roulette':
        await handle_roulette(update, context)
    elif game == 'blackjack':
        await handle_blackjack(update, context)

async def handle_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mise, numero = map(int, update.message.text.split())
        user_id = update.effective_user.id
        
        if mise > user_balances[user_id]:
            await update.message.reply_text("Vous n'avez pas assez d'argent!")
            return
            
        if numero < 0 or numero > 36:
            await update.message.reply_text("Le numéro doit être entre 0 et 36!")
            return
            
        resultat = random.randint(0, 36)
        if resultat == numero:
            gain = mise * 35
            user_balances[user_id] += gain
            await update.message.reply_text(
                f"🎉 FÉLICITATIONS! La bille s'arrête sur le {resultat}\n"
                f"Vous gagnez {gain}€!\n"
                f"Nouveau solde: {user_balances[user_id]}€"
            )
        else:
            user_balances[user_id] -= mise
            await update.message.reply_text(
                f"😢 Perdu! La bille s'arrête sur le {resultat}\n"
                f"Vous perdez {mise}€\n"
                f"Nouveau solde: {user_balances[user_id]}€"
            )
    except ValueError:
        await update.message.reply_text("Format invalide! Utilisez: mise numero (exemple: 100 17)")

async def handle_blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mise = int(update.message.text)
        user_id = update.effective_user.id
        
        if mise > user_balances[user_id]:
            await update.message.reply_text("Vous n'avez pas assez d'argent!")
            return
            
        context.user_data['blackjack_mise'] = mise
        context.user_data['blackjack_cards'] = [random.randint(1, 11), random.randint(1, 11)]
        context.user_data['dealer_cards'] = [random.randint(1, 11)]
        
        keyboard = [
            [
                InlineKeyboardButton("🎯 Tirer", callback_data='hit'),
                InlineKeyboardButton("⏹ Rester", callback_data='stand')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Vos cartes: {context.user_data['blackjack_cards']} (Total: {sum(context.user_data['blackjack_cards'])})\n"
            f"Carte du croupier: {context.user_data['dealer_cards']}\n"
            "Que voulez-vous faire?",
            reply_markup=reply_markup
        )
    except ValueError:
        await update.message.reply_text("Format invalide! Envoyez juste le montant de votre mise (exemple: 100)")

async def blackjack_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'hit':
        context.user_data['blackjack_cards'].append(random.randint(1, 11))
        total = sum(context.user_data['blackjack_cards'])
        
        if total > 21:
            user_id = update.effective_user.id
            mise = context.user_data['blackjack_mise']
            user_balances[user_id] -= mise
            await query.edit_message_text(
                f"Vos cartes: {context.user_data['blackjack_cards']} (Total: {total})\n"
                f"💥 Perdu! Vous avez dépassé 21.\n"
                f"Vous perdez {mise}€\n"
                f"Nouveau solde: {user_balances[user_id]}€"
            )
        else:
            keyboard = [
                [
                    InlineKeyboardButton("🎯 Tirer", callback_data='hit'),
                    InlineKeyboardButton("⏹ Rester", callback_data='stand')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"Vos cartes: {context.user_data['blackjack_cards']} (Total: {total})\n"
                f"Carte du croupier: {context.user_data['dealer_cards']}\n"
                "Que voulez-vous faire?",
                reply_markup=reply_markup
            )
    
    elif query.data == 'stand':
        while sum(context.user_data['dealer_cards']) < 17:
            context.user_data['dealer_cards'].append(random.randint(1, 11))
        
        player_total = sum(context.user_data['blackjack_cards'])
        dealer_total = sum(context.user_data['dealer_cards'])
        user_id = update.effective_user.id
        mise = context.user_data['blackjack_mise']
        
        result_text = (
            f"Vos cartes: {context.user_data['blackjack_cards']} (Total: {player_total})\n"
            f"Cartes du croupier: {context.user_data['dealer_cards']} (Total: {dealer_total})\n"
        )
        
        if dealer_total > 21 or player_total > dealer_total:
            user_balances[user_id] += mise
            result_text += (
                f"🎉 FÉLICITATIONS! Vous gagnez {mise}€!\n"
                f"Nouveau solde: {user_balances[user_id]}€"
            )
        elif player_total < dealer_total:
            user_balances[user_id] -= mise
            result_text += (
                f"😢 Perdu! Vous perdez {mise}€\n"
                f"Nouveau solde: {user_balances[user_id]}€"
            )
        else:
            result_text += (
                "🤝 Égalité! Vous récupérez votre mise.\n"
                f"Solde: {user_balances[user_id]}€"
            )
        
        await query.edit_message_text(result_text)

def main():
    # Création de l'application avec votre token
    application = Application.builder().token("7995554685:AAGAARe4ab1oD-M1bhAZOgWTNYCeEsUl87U").build()

    # Ajout des handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^(roulette|blackjack|balance)$'))
    application.add_handler(CallbackQueryHandler(blackjack_button_handler, pattern='^(hit|stand)$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_game_input))

    # Démarrage du bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
