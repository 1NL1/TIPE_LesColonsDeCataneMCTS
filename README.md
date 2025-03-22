# TIPE de CPGE: IA pour Les Colons de Catane par MCTS

Un environnement simulant une version simplifiée des Colons de Catane munie de trois IAs.

# Règles
Nous n'expliquerons pas les règles des Colons de Catane, que vous pouvez trouver très facilement en ligne.

# Simplifications
Les simplifications effectuées sont les suivantes:
- 2 joueurs
- Pas d'échanges de ressource entre joueurs
- Pas de cartes développement

# IAs
Trois IAs sont présentes sur le projet:
- une IA aléatoire uniforme
- Une IA par Monte-Carlo simple
- Une IA par recherche arborescente de Monte-Carlo (MCTS)

# Lancement
Pour lancer une partie, il suffit d'executer le fichier "main.py"

/!\ Pour choisir quelle IA affronter, ce n'est pas ergonomique:
- Dans main.py, rendez-vous à la première ligne du __init__() de la classe "Jeu" (ligne 674)
- remplacez le deuxième objet du dictionnaire "self.dicoJoueurs" par une des trois lignes commentées au-dessus selon votre choix.

# Jeu
Au lancement, une telle interface devrait s'ouvrir:
<img width="603" alt="Plteau partie plus avancée" src="https://github.com/user-attachments/assets/aefca0e1-256c-4f75-aac6-e31c2571dcd3" />

L'imagerie utilisée suit cette logique:
- "x" pour les emplacements de colonie, blanc si aucune colonie n'y est construite, de la couleur du joueur propriétaire sinon
- "X" pour une ville, de la couleur du joueur propriétaire
- "-" pour un chemin, blanc si on peut y construire une route, de la couleur du joueur propriétaire si une route y est déjà construite
- "V" pour l'emplacement des voleurs

Les images représentent les cases de ressources, et les nombres dessus la valeur à faire aux dés pour que ces cases produisent.

![imgbétail](https://github.com/user-attachments/assets/55f2e1d4-13f7-43a2-9ce8-cfc74ecaa0af)
Bétail

![imgblé](https://github.com/user-attachments/assets/a1c08ce3-40a6-4e2b-b400-e1a8687e1ee4)
Blé

![imgbois](https://github.com/user-attachments/assets/ba440b7d-6822-4d0d-bc5d-a206e50c10cb)
Bois

![imgbrique](https://github.com/user-attachments/assets/a6178b2c-4e91-43e5-9136-8fb4a9437e66)
Brique

![imgpierre](https://github.com/user-attachments/assets/3b224002-de15-4df4-ab66-b240abaadf8f)
Pierre

![imgdesert](https://github.com/user-attachments/assets/a7ee1866-4035-407e-82da-96d1822fa5d1)
Désert (vide de ressource)

# Commandes
- Pour construire une route, une colonie ou améliorer une colonie en ville, il suffit de cliquer sur l'emplacement correspondant à votre tour en respectant les règles de placement et ayant suffisement de ressources (sauf durant le placement initial, où deux colonies et deux routes peuvent être placées gratuitement)
- Pour effectuer un échange avec la banque (4 ressources du même type données pour une reçue) il suffit de cliquer sur les icones de ressources sous le plateau de jeu: d'abord la ressource que vous donnez, puis celle que vous voulez recevoir.
- Vous serez prévenu qu'il faut déplacer les voleurs par un message dans la console (encore une fois pas très ergonomique). Il vous suffira alors de cliquer sur la tuile de ressource où vous souhaitez que les voleurs se rendent (on rappelle qu'elle doit être adjacente à la dernière position des voleurs)
  Pour finir votre tour, appuyez sur entrée 
