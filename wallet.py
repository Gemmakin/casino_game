import json
import os
from datetime import datetime

class Transaction:
    def __init__(self, user_id, amount, transaction_type, game=None, bet_type=None, result=None, timestamp=None):
        self.user_id = user_id
        self.amount = amount
        self.transaction_type = transaction_type  # 'deposit', 'withdraw', 'bet', 'win', 'bonus'
        self.timestamp = timestamp or datetime.now().isoformat()
        self.game = game
        self.bet_type = bet_type
        self.result = result

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'timestamp': self.timestamp,
            'game': self.game,
            'bet_type': self.bet_type,
            'result': self.result
        }

class Wallet:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.transactions_file = os.path.join(data_dir, 'transactions.json')
        self.load_transactions()

    def load_transactions(self):
        if os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'r') as f:
                self.transactions = [Transaction(**t) for t in json.load(f)]
        else:
            self.transactions = []

    def save_transactions(self):
        with open(self.transactions_file, 'w') as f:
            json.dump([t.to_dict() for t in self.transactions], f, indent=4)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.save_transactions()

    def get_user_transactions(self, user_id, limit=10):
        user_transactions = [t for t in self.transactions if t.user_id == user_id]
        return sorted(user_transactions, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_user_balance(self, user_id):
        balance = 0
        for transaction in self.transactions:
            if transaction.user_id == user_id:
                if transaction.transaction_type in ['deposit', 'win', 'bonus']:
                    balance += transaction.amount
                elif transaction.transaction_type in ['withdraw', 'bet']:
                    balance -= transaction.amount
        return balance

    def get_user_stats(self, user_id):
        total_bets = 0
        total_wins = 0
        total_losses = 0
        biggest_win = 0
        games_played = {}
        
        for transaction in self.transactions:
            if transaction.user_id == user_id:
                if transaction.transaction_type == 'bet':
                    total_bets += 1
                    if transaction.game:
                        games_played[transaction.game] = games_played.get(transaction.game, 0) + 1
                elif transaction.transaction_type == 'win':
                    total_wins += 1
                    biggest_win = max(biggest_win, transaction.amount)
                elif transaction.transaction_type == 'bet' and transaction.result == 'loss':
                    total_losses += 1
        
        return {
            'total_bets': total_bets,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'win_rate': (total_wins / total_bets * 100) if total_bets > 0 else 0,
            'biggest_win': biggest_win,
            'games_played': games_played
        }

    def format_transaction_history(self, transactions):
        history = "📜 Historique des transactions\n\n"
        for t in transactions:
            if t.transaction_type == 'deposit':
                emoji = "💳"
            elif t.transaction_type == 'withdraw':
                emoji = "💸"
            elif t.transaction_type == 'bet':
                emoji = "🎲"
            elif t.transaction_type == 'win':
                emoji = "🏆"
            else:  # bonus
                emoji = "🎁"
            
            date = datetime.fromisoformat(t.timestamp).strftime("%d/%m %H:%M")
            amount = f"+{t.amount}€" if t.transaction_type in ['deposit', 'win', 'bonus'] else f"-{t.amount}€"
            
            game_info = f" ({t.game})" if t.game else ""
            history += f"{emoji} {date} : {amount}{game_info}\n"
        
        return history
