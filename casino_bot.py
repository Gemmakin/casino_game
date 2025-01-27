import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os
import json
from datetime import datetime
import threading
import time

# Importer les jeux
from games.roulette import RouletteGame
from games.blackjack import BlackjackGame
from games.crash import CrashGame
from games.dice import DiceGame
from wallet import Wallet, Transaction
from web_server import run_server

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Initialisation du portefeuille
wallet = Wallet(DATA_DIR)

# Instances des jeux
roulette_game = RouletteGame()
blackjack_game = BlackjackGame()
crash_game = CrashGame()
dice_game = DiceGame()

def get_webapp_url():
    # Attendre que l'URL ngrok soit disponible
    for _ in range(30):  # Attendre jusqu'à 30 secondes
        if os.path.exists("webapp_url.txt"):
            with open("webapp_url.txt", "r") as f:
                return f.read().strip()
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balance = wallet.get_user_balance(user.id)
    stats = wallet.get_user_stats(user.id)
    
    webapp_url = get_webapp_url()
    if not webapp_url:
        await update.message.reply_text(
            "⚠️ Erreur: Le serveur de jeu n'est pas encore prêt. Veuillez réessayer dans quelques secondes."
        )
        return
    
    keyboard = [
        [InlineKeyboardButton(
            "🎮 Jouer au Casino",
            web_app=WebAppInfo(url=webapp_url)
        )],
        [
            InlineKeyboardButton("💰 Portefeuille", callback_data='wallet'),
            InlineKeyboardButton("🎁 Bonus quotidien", callback_data='daily')
        ],
        [
            InlineKeyboardButton("📊 Statistiques", callback_data='stats'),
            InlineKeyboardButton("👥 Top 10", callback_data='top')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎰 Bienvenue au Casino Royal, {user.first_name}! 🎰\n\n"
        f"💰 Votre solde: {balance:,}€\n"
        f"🎲 Paris totaux: {stats['total_bets']}\n"
        f"🏆 Gains totaux: {stats['total_wins']:,}€\n\n"
        "Cliquez sur 'Jouer au Casino' pour lancer la mini-application !",
        reply_markup=reply_markup
    )

async def play_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🎲 Roulette", callback_data='game_roulette'),
            InlineKeyboardButton("🃏 Blackjack", callback_data='game_blackjack')
        ],
        [
            InlineKeyboardButton("🎲 Dés", callback_data='game_dice'),
            InlineKeyboardButton("🎯 Crash", callback_data='game_crash')
        ],
        [InlineKeyboardButton("🔙 Retour", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎮 Choisissez votre jeu :",
        reply_markup=reply_markup
    )

async def wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balance = wallet.get_user_balance(user.id)
    
    keyboard = [
        [
            InlineKeyboardButton("💳 Recharger", callback_data='deposit'),
            InlineKeyboardButton("💸 Retirer", callback_data='withdraw')
        ],
        [
            InlineKeyboardButton("📊 Historique", callback_data='history'),
            InlineKeyboardButton("🔙 Retour", callback_data='back_to_main')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"💰 Portefeuille de {user.first_name}\n\n"
        f"Solde actuel: {balance:,}€\n\n"
        "Que souhaitez-vous faire ?",
        reply_markup=reply_markup
    )

async def transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    transactions = wallet.get_user_transactions(user.id)
    history_text = wallet.format_transaction_history(transactions)
    
    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data='wallet')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        history_text,
        reply_markup=reply_markup
    )

async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Vérifier si le bonus a déjà été réclamé aujourd'hui
    user_transactions = wallet.get_user_transactions(user.id)
    for transaction in user_transactions:
        if (transaction.transaction_type == 'bonus' and 
            transaction.timestamp.startswith(today)):
            await update.callback_query.answer(
                "Vous avez déjà réclamé votre bonus aujourd'hui! Revenez demain! ⏰"
            )
            return
    
    # Donner le bonus
    bonus = 1000
    transaction = Transaction(
        user_id=user.id,
        amount=bonus,
        transaction_type='bonus'
    )
    wallet.add_transaction(transaction)
    
    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"🎁 Félicitations! Vous avez reçu {bonus}€ de bonus quotidien!\n"
        f"Nouveau solde: {wallet.get_user_balance(user.id):,}€\n\n"
        "Revenez demain pour un nouveau bonus!",
        reply_markup=reply_markup
    )

async def stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats = wallet.get_user_stats(user.id)
    
    stats_text = (
        f"📊 Statistiques de {user.first_name}\n\n"
        f"💰 Solde actuel: {wallet.get_user_balance(user.id):,}€\n"
        f"🎲 Paris totaux: {stats['total_bets']}\n"
        f"🏆 Gains totaux: {stats['total_wins']}\n"
        f"📈 Taux de réussite: {stats['win_rate']:.1f}%\n"
        f"💎 Plus gros gain: {stats['biggest_win']:,}€\n\n"
        "🎮 Jeux joués:\n"
    )
    
    for game, count in stats['games_played'].items():
        stats_text += f"- {game}: {count} fois\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        stats_text,
        reply_markup=reply_markup
    )

async def top_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Obtenir tous les soldes des utilisateurs
    all_users = {}
    for transaction in wallet.transactions:
        user_id = transaction.user_id
        if user_id not in all_users:
            all_users[user_id] = wallet.get_user_balance(user_id)
    
    # Trier par solde
    sorted_users = sorted(all_users.items(), key=lambda x: x[1], reverse=True)[:10]
    
    message = "🏆 Top 10 des joueurs\n\n"
    for i, (user_id, balance) in enumerate(sorted_users, 1):
        message += f"{i}. {'👑 ' if i == 1 else ''}{user_id}: {balance:,}€\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ Aide du Casino Royal\n\n"
        "🎮 Jeux disponibles:\n"
        "- 🎲 Roulette: Pariez sur un numéro ou une couleur\n"
        "- 🃏 Blackjack: Battez le croupier avec un 21\n"
        "- 🎲 Dés: Pariez sur le résultat des dés\n"
        "- 🎯 Crash: Retirez vos gains avant le crash\n\n"
        "💰 Commandes:\n"
        "/start - Démarrer le casino\n"
        "/daily - Bonus quotidien\n"
        "/balance - Voir votre solde\n\n"
        "💎 Bonus:\n"
        "- Bonus quotidien: 1000€\n"
        "- Bonus de parrainage: 500€"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        help_text,
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'play_menu':
        await play_menu(update, context)
    elif query.data == 'wallet':
        await wallet_menu(update, context)
    elif query.data == 'daily':
        await daily_bonus(update, context)
    elif query.data == 'stats':
        await stats_menu(update, context)
    elif query.data == 'help':
        await help_menu(update, context)
    elif query.data == 'top':
        await top_players(update, context)
    elif query.data == 'history':
        await transaction_history(update, context)
    elif query.data == 'back_to_main':
        await start(update, context)
    elif query.data.startswith('game_'):
        game = query.data.split('_')[1]
        if game == 'roulette':
            context.user_data['game'] = 'roulette'
            keyboard = [
                [
                    InlineKeyboardButton("🔴 Rouge", callback_data='bet_red'),
                    InlineKeyboardButton("⚫ Noir", callback_data='bet_black')
                ],
                [InlineKeyboardButton("🎯 Numéro", callback_data='bet_number')],
                [InlineKeyboardButton("🔙 Retour", callback_data='play_menu')]
            ]
            await query.edit_message_text(
                "🎰 Roulette\n\nChoisissez votre type de pari:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif game == 'blackjack':
            context.user_data['game'] = 'blackjack'
            keyboard = [
                [InlineKeyboardButton("🎮 Nouvelle partie", callback_data='blackjack_start')],
                [InlineKeyboardButton("🔙 Retour", callback_data='play_menu')]
            ]
            await query.edit_message_text(
                "🃏 Blackjack\n\nPrêt à jouer?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif game == 'dice':
            context.user_data['game'] = 'dice'
            keyboard = [
                [
                    InlineKeyboardButton("🎲 Somme", callback_data='dice_sum'),
                    InlineKeyboardButton("⬆️ Haut/Bas", callback_data='dice_highlow')
                ],
                [
                    InlineKeyboardButton("🔢 Pair/Impair", callback_data='dice_evenodd'),
                    InlineKeyboardButton("👥 Double", callback_data='dice_double')
                ],
                [InlineKeyboardButton("🔙 Retour", callback_data='play_menu')]
            ]
            await query.edit_message_text(
                "🎲 Dés\n\nChoisissez votre type de pari:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif game == 'crash':
            context.user_data['game'] = 'crash'
            keyboard = [
                [InlineKeyboardButton("🎮 Nouvelle partie", callback_data='crash_start')],
                [InlineKeyboardButton("📊 Historique", callback_data='crash_history')],
                [InlineKeyboardButton("🔙 Retour", callback_data='play_menu')]
            ]
            await query.edit_message_text(
                "🎯 Crash\n\nPrêt à jouer?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    
    game = data.get('game')
    action = data.get('action')
    amount = data.get('amount')
    result = data.get('result')
    
    if game == 'roulette':
        if result == 0:
            await update.message.reply_text(f"🎲 Roulette : Le 0 est sorti ! Vous avez perdu {amount}€")
        else:
            await update.message.reply_text(f"🎲 Roulette : Le {result} est sorti !")
            
    elif game == 'blackjack':
        await update.message.reply_text(f"🃏 Blackjack : Mise de {amount}€ placée")
        
    elif game == 'dice':
        await update.message.reply_text(f"🎲 Dés : Vous avez obtenu un {result}")
        
    elif game == 'crash':
        if result == 'crash':
            await update.message.reply_text(f"📉 Crash : Perdu ! Le multiplicateur était de {data['multiplier']}x")
        else:
            await update.message.reply_text(f"📈 Crash : Gagné ! Vous avez retiré à {data['multiplier']}x")

def main():
    # Démarrer le serveur web dans un thread séparé
    web_thread = threading.Thread(target=run_server)
    web_thread.daemon = True
    web_thread.start()
    
    # Démarrer le bot
    application = Application.builder().token("7606399757:AAGYOWOo9UtCisjjgVGQjFKXGm8ZOHEP-CA").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
