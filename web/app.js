// Initialisation de Telegram WebApp
const tg = window.Telegram.WebApp;

// Initialisation
tg.ready();
tg.expand();

// Variables globales
let currentGame = null;
let balance = 1000;
let crashInterval = null;
let crashMultiplier = 1.00;
let isCrashing = false;

// Mise à jour du solde
function updateBalance(newBalance) {
    balance = newBalance;
    document.getElementById('balance-amount').textContent = balance.toLocaleString();
}

// Navigation
function openGame(game) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById(game).classList.add('active');
    currentGame = game;
    
    // Initialisation spécifique au jeu
    switch(game) {
        case 'roulette':
            initRoulette();
            break;
        case 'blackjack':
            initBlackjack();
            break;
        case 'dice':
            initDice();
            break;
        case 'crash':
            initCrash();
            break;
    }
    
    tg.MainButton.hide();
}

function backToMenu() {
    if (crashInterval) {
        clearInterval(crashInterval);
        crashInterval = null;
    }
    
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById('games').classList.add('active');
    currentGame = null;
}

// Placement des paris
function placeBet(game) {
    const betInput = document.getElementById(`${game}-bet`);
    const amount = parseInt(betInput.value);
    
    if (isNaN(amount) || amount < 1) {
        tg.showAlert('Veuillez entrer une mise valide');
        return;
    }
    
    if (amount > balance) {
        tg.showAlert('Solde insuffisant');
        return;
    }
    
    switch(game) {
        case 'roulette':
            spinRoulette(amount);
            break;
        case 'blackjack':
            startBlackjack(amount);
            break;
        case 'dice':
            rollDice(amount);
            break;
        case 'crash':
            startCrash(amount);
            break;
    }
}

// Roulette
function initRoulette() {
    const wheel = document.querySelector('.roulette-wheel');
    // Initialisation de la roue
}

function spinRoulette(amount) {
    const wheel = document.querySelector('.roulette-wheel');
    wheel.style.animation = 'spin 3s ease-out';
    
    setTimeout(() => {
        const result = Math.floor(Math.random() * 37);
        wheel.style.animation = '';
        
        tg.sendData(JSON.stringify({
            game: 'roulette',
            action: 'bet',
            amount: amount,
            result: result
        }));
    }, 3000);
}

// Blackjack
function initBlackjack() {
    document.getElementById('dealer-cards').innerHTML = '';
    document.getElementById('player-cards').innerHTML = '';
}

function startBlackjack(amount) {
    tg.sendData(JSON.stringify({
        game: 'blackjack',
        action: 'bet',
        amount: amount
    }));
}

// Dés
function initDice() {
    document.querySelector('.dice-container').innerHTML = '';
}

function rollDice(amount) {
    const container = document.querySelector('.dice-container');
    container.style.animation = 'shake 0.5s';
    
    setTimeout(() => {
        const result = Math.floor(Math.random() * 6) + 1;
        container.style.animation = '';
        container.textContent = result;
        
        tg.sendData(JSON.stringify({
            game: 'dice',
            action: 'bet',
            amount: amount,
            result: result
        }));
    }, 500);
}

// Crash
function initCrash() {
    document.getElementById('multiplier').textContent = '1.00x';
    document.getElementById('crash-btn').textContent = 'Démarrer';
}

function toggleCrash() {
    if (isCrashing) {
        cashOut();
    } else {
        const amount = parseInt(document.getElementById('crash-bet').value);
        if (isNaN(amount) || amount < 1) {
            tg.showAlert('Veuillez entrer une mise valide');
            return;
        }
        if (amount > balance) {
            tg.showAlert('Solde insuffisant');
            return;
        }
        startCrash(amount);
    }
}

function startCrash(amount) {
    isCrashing = true;
    crashMultiplier = 1.00;
    document.getElementById('crash-btn').textContent = 'Retirer';
    
    crashInterval = setInterval(() => {
        if (Math.random() < 0.03) {
            clearInterval(crashInterval);
            crashInterval = null;
            isCrashing = false;
            document.getElementById('multiplier').style.color = 'red';
            document.getElementById('crash-btn').textContent = 'Démarrer';
            
            tg.sendData(JSON.stringify({
                game: 'crash',
                action: 'bet',
                amount: amount,
                result: 'crash',
                multiplier: crashMultiplier
            }));
            return;
        }
        
        crashMultiplier += 0.01;
        document.getElementById('multiplier').textContent = crashMultiplier.toFixed(2) + 'x';
    }, 100);
}

function cashOut() {
    if (!isCrashing || !crashInterval) return;
    
    clearInterval(crashInterval);
    crashInterval = null;
    isCrashing = false;
    document.getElementById('multiplier').style.color = '#2ea6ff';
    document.getElementById('crash-btn').textContent = 'Démarrer';
    
    const amount = parseInt(document.getElementById('crash-bet').value);
    
    tg.sendData(JSON.stringify({
        game: 'crash',
        action: 'bet',
        amount: amount,
        result: 'cashout',
        multiplier: crashMultiplier
    }));
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    // Récupérer le solde initial depuis les paramètres de lancement
    const params = new URLSearchParams(window.location.search);
    const initialBalance = parseInt(params.get('balance')) || 1000;
    updateBalance(initialBalance);
    
    // Configurer le bouton principal Telegram
    tg.MainButton.text = "JOUER";
    tg.MainButton.show();
});
