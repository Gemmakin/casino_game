import random
from colorama import init, Fore, Style

init()  # Initialiser colorama

class Casino:
    def __init__(self):
        self.solde = 1000  # Solde initial de 1000€

    def afficher_menu(self):
        print(f"\n{Fore.GREEN}=== CASINO PYTHON ==={Style.RESET_ALL}")
        print(f"Votre solde: {self.solde}€")
        print("\n1. Jouer à la roulette")
        print("2. Jouer au blackjack")
        print("3. Quitter")

    def roulette(self):
        print(f"\n{Fore.YELLOW}=== ROULETTE ==={Style.RESET_ALL}")
        mise = int(input("Combien voulez-vous miser? "))
        
        if mise > self.solde:
            print(f"{Fore.RED}Vous n'avez pas assez d'argent!{Style.RESET_ALL}")
            return
        
        numero = int(input("Choisissez un numéro (0-36): "))
        if numero < 0 or numero > 36:
            print(f"{Fore.RED}Numéro invalide!{Style.RESET_ALL}")
            return
        
        resultat = random.randint(0, 36)
        print(f"\nLa bille s'arrête sur le {Fore.CYAN}{resultat}{Style.RESET_ALL}")
        
        if resultat == numero:
            gain = mise * 35
            print(f"{Fore.GREEN}FÉLICITATIONS! Vous gagnez {gain}€!{Style.RESET_ALL}")
            self.solde += gain
        else:
            print(f"{Fore.RED}Perdu! Vous perdez {mise}€{Style.RESET_ALL}")
            self.solde -= mise

    def blackjack(self):
        print(f"\n{Fore.YELLOW}=== BLACKJACK ==={Style.RESET_ALL}")
        mise = int(input("Combien voulez-vous miser? "))
        
        if mise > self.solde:
            print(f"{Fore.RED}Vous n'avez pas assez d'argent!{Style.RESET_ALL}")
            return
            
        cartes_joueur = [random.randint(1, 11), random.randint(1, 11)]
        cartes_croupier = [random.randint(1, 11)]
        
        print(f"\nVos cartes: {cartes_joueur} (Total: {sum(cartes_joueur)})")
        print(f"Carte du croupier: {cartes_croupier}")
        
        while sum(cartes_joueur) < 21:
            choix = input("\nVoulez-vous tirer une carte? (o/n) ")
            if choix.lower() == 'o':
                nouvelle_carte = random.randint(1, 11)
                cartes_joueur.append(nouvelle_carte)
                print(f"Nouvelle carte: {nouvelle_carte}")
                print(f"Vos cartes: {cartes_joueur} (Total: {sum(cartes_joueur)})")
            else:
                break
        
        total_joueur = sum(cartes_joueur)
        if total_joueur > 21:
            print(f"{Fore.RED}Perdu! Vous avez dépassé 21.{Style.RESET_ALL}")
            self.solde -= mise
            return
            
        while sum(cartes_croupier) < 17:
            cartes_croupier.append(random.randint(1, 11))
            
        total_croupier = sum(cartes_croupier)
        print(f"\nCartes du croupier: {cartes_croupier} (Total: {total_croupier})")
        
        if total_croupier > 21 or total_joueur > total_croupier:
            print(f"{Fore.GREEN}FÉLICITATIONS! Vous gagnez {mise}€!{Style.RESET_ALL}")
            self.solde += mise
        elif total_joueur < total_croupier:
            print(f"{Fore.RED}Perdu! Vous perdez {mise}€{Style.RESET_ALL}")
            self.solde -= mise
        else:
            print(f"{Fore.YELLOW}Égalité! Vous récupérez votre mise.{Style.RESET_ALL}")

def main():
    casino = Casino()
    while True:
        casino.afficher_menu()
        choix = input("\nQue voulez-vous faire? ")
        
        if choix == "1":
            casino.roulette()
        elif choix == "2":
            casino.blackjack()
        elif choix == "3":
            print("Merci d'avoir joué! Au revoir!")
            break
        else:
            print("Choix invalide!")
            
        if casino.solde <= 0:
            print(f"{Fore.RED}Vous n'avez plus d'argent! Fin du jeu.{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    main()
