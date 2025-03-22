"""
Les fonctions principales du programme
"""
from math import exp
import random as rd
from interfaceGraphique import IG_draw, IG_init, IG_clic
import pygame
# Taille du plateau
dimensions = (11, 21)

nbJoueur = 2
pygame.init()

# Initialisation de la fenetre pour l'interface graphique
grid_pos = (0, 0, 800, 800)
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("TIPE")
background = pygame.Surface(screen.get_size())
background = background.convert()
font = pygame.font.Font(None, 36)
IG_init()
affichage = True

###########################
###         Jeu         ###
###########################

def estCoordonnesValide(pos):
    """
    Retourne un booleen indiquant si les coordonnées passées en argument sont valides (ie indiquent une case dans la grille)
    pos: position
    """
    i, j = pos
    return 0 <= i and 0 <= j and dimensions[0] > i and dimensions[1] > j


class Tuile:
    """
    Une tuile de ressource
    """
    ressource = ""
    num = 0
    pos = 0, 0
    type = "Tuile"
    voleur = False

    def __init__(self, i, j, num, ressource="desert"):
        """
        Initialisation d'un objet Tuile
        i,j : positions dans le plateau de la tuile
        num : numéro de la tuile
        ressource: ressource de la tuile
        """
        self.pos = i, j
        self.num = num
        self.ressource = ressource
        if self.ressource == "desert":
            self.voleur = True

    def copie(self):
        nouvelleTuile = Tuile(
            self.pos[0], self.pos[1], self.num, self.ressource)
        nouvelleTuile.voleur = self.voleur
        return nouvelleTuile

    def produit(self, plateau):
        """
        Fonction à appeler quand la tuile produit des ressources (ie quand son numero est tiré). 
        Revoie la ressource de la tuile et un dictionnaire associant à chaque joueur la quantité de la ressource gagnée
        plateau: plateau de jeu
        """
        #
        res = {i: 0 for i in range(0, nbJoueur+1)}
        if not (self.voleur):
            # Parcours des croisements bordant la tuile
            for i in range(-1, 2, 2):
                for j in range(-2, 3, 2):
                    croisement = plateau.plateau[self.pos[0]+i][self.pos[1]+j]
                    assert type(
                        croisement) == Croisement, "produit: probleme dans le tableau"
                    res[croisement.joueur] += 1 * \
                        croisement.niveau  # Production
        return self.ressource, res


class Chemin:
    """
    Un chemin entre deux croisements
    """
    pos = 0, 0
    route = 0  # 0: pas de route, sinon numero du joueur
    type = "Chemin"
    marque = {}

    def __init__(self, i, j):
        """
        Initialisation d'un objeet Chemin
        i,j: position du chemin
        """
        self.pos = i, j
        self.marque = {j: False for j in range(1, nbJoueur+1)}

    def copie(self):
        nouveauChemin = Chemin(self.pos[0], self.pos[1])
        nouveauChemin.route = self.route
        nouveauChemin.marque = self.marque.copy()
        return nouveauChemin

    def construction(self, joueur):
        """
        Construction d'une route sur le chemin
        joueur: numero du joueur propriétaire de la route
        """
        # assert self.route == 0 , "route deja construite"
        if self.route == 0:
            self.route = joueur


class Croisement:
    """
    Un croisement, là où les joueurs pourront construire des colonies et des villes
    """
    pos = 0, 0
    niveau = 0  # 0: pas construit, 1: colonie, 2: ville
    joueur = 0  # 0: pas construit, sinon numero joueur
    # liste des ressources accessibles depuis ce croisement et de leur numéro de production
    lstRessourcesAdjacentes = []
    type = "Croisement"
    marque = {}

    def copie(self):
        nouveauCroisement = Croisement(self.pos[0], self.pos[1])
        nouveauCroisement.niveau = self.niveau
        nouveauCroisement.joueur = self.joueur
        nouveauCroisement.lstRessourcesAdjacentes = self.lstRessourcesAdjacentes.copy()
        nouveauCroisement.marque = self.marque.copy()
        return nouveauCroisement

    def __init__(self, i, j):
        """
        Initialisation d'un Croisement
        i,j: positions du croisement
        """
        self.pos = i, j
        self.lstRessourcesAdjacentes = []
        self.marque = {j: False for j in range(1, nbJoueur+1)}

    def construction(self, numJoueur):
        """
        construction d'une ville à partir d'un terrain vague
        numJoueur: numero du joueur propriétaire de la désormais colonie
        """
        assert self.niveau == 0, "colonie deja construite"
        self.niveau = 1
        self.joueur = numJoueur

    def amelioration(self):
        """
        Amélioration d'une colonie en ville 
        """
        assert self.niveau == 1, "amelioration de pas une colonie"
        self.niveau += 1

    def ajouteBordureTuile(self, ressource, nb):
        """
        complete la liste des ressources adjacentes 
        ressource: ressource à ajouter
        nb : numero de ladite ressource
        """
        self.lstRessourcesAdjacentes.append((ressource, nb))


def ElmtAleatoire(L):
    """
    retourne un element aleatoire de L en l'enlevant de la liste
    L: liste
    """
    i = rd.randint(0, len(L) - 1)
    return L.pop(i)


class Plateau:
    """ Le plateu de jeu  """
    plateau = []  # la grille de jeu
    nbTour = 0

    def copie(self):
        nouveauPlateau = Plateau([], False)
        nouveauPlateau.nbTour = self.nbTour
        nouveauPlateau.plateau = [[None for _ in range(
            dimensions[1])] for _ in range(dimensions[0])]
        for i in range(len(nouveauPlateau.plateau)):
            for j in range(len(nouveauPlateau.plateau[0])):
                case = self.plateau[i][j]
                if case != None:
                    nouveauPlateau.plateau[i][j] = case.copie()
        return nouveauPlateau

    def creeTuile(self, i, j, numsAAttribuer, ressourcesAAttribuer, lstTuilesNum, desert=False):
        """
        Crée une tuile dans le plateau
        i,j : position de la tuile
        numsAAttribuer: liste des numéros non encore attribués à une tuile
        ressourcesAAttribuer: liste des ressources non encore attribués à une tuile (il y a plusieurs occurences de chaque)
        lstTuilesNum : liste des coordonnées des tuiles indicée par leurs numéros (à completer dans la fonction)
        desert: si la tuile est la tuile désert, auquel cas elle ne produit rien
        """
        if desert:
            self.plateau[i][j] = Tuile(i, j, 0)
        else:  # on attribue une ressource et un numéro à la tuile, et on met a jour lstTuilesNum
            nb = ElmtAleatoire(numsAAttribuer)
            r = ElmtAleatoire(ressourcesAAttribuer)
            lstTuilesNum[nb].append((i, j))
            self.plateau[i][j] = Tuile(i, j, nb, r)

    def __init__(self, lstTuilesNum, creePlateau=True):
        """
        Initialisation du plateau, cree le plateau si creePlateau est vrai(on ne revréé pas toute la grille)
        lstTuilesNum: liste des coordonnées des tuiles indicée par leurs numéros (à completer dans la fonction)
        """
        # Initialisation du plateau
        self.plateau = [[None for _ in range(
            dimensions[1])] for _ in range(dimensions[0])]

        if creePlateau:
            # listes des numéros et ressources à attribuer aux tuiles
            numsAAttribuer = [2, 12] + 2 * \
                [i for i in range(3, 7)] + 2*[i for i in range(8, 12)]
            ressourcesAAttribuer = 3 * \
                ["bois", "pierre", "brique", "bétail",
                    "blé"] + ["bois", "blé", "bétail"]

            # Remplissage du plateau
            for i in range(0, dimensions[0], 2):
                # ce qu'on met sous les croisements, 0 = chemin, 1 = tuile (il y a une alternance)
                aAjouter = 0
                for j in range(dimensions[1]):
                    if i+j >= 4 and i+j <= 26 and j-i <= 16 and i-j <= 6:  # plateau exagonal
                        if j % 2 == 0:  # colonnes paires, alternance croisement - tuile/chemin
                            self.plateau[i][j] = Croisement(i, j)
                            if i < dimensions[0]//2:
                                if aAjouter == 0:
                                    self.plateau[i+1][j] = Chemin(i+1, j)
                                else:
                                    if i == 4 and j == 10:  # desert
                                        self.creeTuile(
                                            i+1, j, numsAAttribuer, ressourcesAAttribuer, lstTuilesNum, True)
                                    else:
                                        self.creeTuile(
                                            i+1, j, numsAAttribuer, ressourcesAAttribuer, lstTuilesNum)
                                aAjouter = 1-aAjouter
                            elif i > dimensions[0]//2 + 1:
                                if aAjouter == 0:
                                    self.plateau[i-1][j] = Chemin(i-1, j)
                                else:
                                    self.creeTuile(
                                        i-1, j, numsAAttribuer, ressourcesAAttribuer, lstTuilesNum)
                                aAjouter = 1-aAjouter
                        else:  # colonnes impaires, que des chemins
                            self.plateau[i][j] = Chemin(i, j)

            # ajoute les bordures de tuiles des croisements
            for i in range(1, 10, 2):
                ecart = abs(i-5)
                for j in range(2 + ecart, dimensions[1] - (2 + ecart), 4):
                    tuile = self.plateau[i][j]
                    if tuile.ressource != "desert":
                        for di in range(-1, 2, 2):
                            for dj in range(-2, 3, 2):
                                self.plateau[i + di][j +
                                                     dj].ajouteBordureTuile(tuile.ressource, tuile.num)

    def appartientRouteAuJoueur(self, i, j, numJoueur):
        """
        Renvoie True ou False selon que la route indicée par i,j appartient au joueur numJoueur
        i,j: coordonnées dans la grille, int * int
        numJoueur: numero du joueur, int
        """
        if i >= 0 and i < dimensions[0] and j >= 0 and j < dimensions[1]:
            case = self.plateau[i][j]
            if type(case) == Chemin and case.route == numJoueur:
                return True
        return False

    def appartientColonieAuJoueur(self, i, j, numJoueur):
        """
        Renvoie True ou False selon que la colonie indicée par i,j appartient ou non au joueur numJoueur
        i,j: coordonnées dans la grille, int * int
        numJoueur: numéro du joueur, int
        """
        if i >= 0 and i < dimensions[0] and j >= 0 and j < dimensions[1]:
            case = self.plateau[i][j]
            if type(case) == Croisement and case.joueur == numJoueur:
                return True
        return False

    def estColonieConstruite(self, i, j):
        """
        Renvoie True ou False selon qu'une colonie ou une ville est construite sur le croisement d'indices i,j
        i,j: coordonnées dans la grille, int * int
        """
        if i >= 0 and i <= dimensions[0] and j >= 0 and j <= dimensions[1]:
            case = self.plateau[i][j]
            if type(case) == Croisement and case.joueur != 0:
                return True
        return False

    def estPlacementColoniePossible(self, lig, col, numJoueur, estDansPlacementInitial):
        """
        Renvoie True ou False selon qu'une colonie peut etre construite par le joueur numJoueur au croisement d'indice lig, col
        lig, col: coordonnées dans la grille, int * int
        numJoueur: numéro du joueur concerné, int
        estDansPlacementInitial: si on est dans le placement initial, bool
        """
        case = self.plateau[lig][col]
        if type(case) == Croisement:
            if case.joueur == 0 and case.niveau == 0:  # si la case est vide
                # on a deux configurations possibles: celles avec une tuile au dessous(1) et celles avec une tuile au dessus(-1)
                configuration = int((-1)**((case.pos[0] + case.pos[1])//2))
                # verifie presence d'une route adjacente
                if not (estDansPlacementInitial):
                    if not (self.appartientRouteAuJoueur(lig, col-1, numJoueur) or self.appartientRouteAuJoueur(lig, col+1, numJoueur) or self.appartientRouteAuJoueur(lig+configuration, col, numJoueur)):
                        return False

                # verifie qu'il n'y a pas de colonie deja construite à cote de l'emplacement (cf regle des distances)
                if self.estColonieConstruite(lig, col-2) or self.estColonieConstruite(lig, col+2) or self.estColonieConstruite(lig+2*configuration, col):
                    return False

                return True
        return False

    def estPlacementRoutePossible(self, i, j, numJoueur):
        """
        Renvoie True ou False selon qu'il est légal pour le joueur numJoueur de construire une route en i,j
        i,j; coordonnées dans la grille, int*int
        numJoueur: numero du joueur, int
        """
        case = self.plateau[i][j]
        if type(case) == Chemin:
            if case.route == 0:  # case vide
                # verifie la presence d'une route ou d'une colonie adjacente
                if i % 2 == 0:  # ligne paire, routes horizontales
                    # deux configurations de routes
                    configuration = int((-1)**((i + j)//2))
                    if self.appartientColonieAuJoueur(i, j-1, numJoueur):
                        return True
                    if self.appartientColonieAuJoueur(i, j-1, 0) and (self.appartientRouteAuJoueur(i, j-2, numJoueur) or self.appartientRouteAuJoueur(i+configuration, j-1, numJoueur)):
                        return True
                    if self.appartientColonieAuJoueur(i, j+1, numJoueur):
                        return True
                    if self.appartientColonieAuJoueur(i, j+1, 0) and (self.appartientRouteAuJoueur(i, j+2, numJoueur) or self.appartientRouteAuJoueur(i-configuration, j+1, numJoueur)):
                        return True

                else:  # lignes impaires, routes verticales
                    if self.appartientColonieAuJoueur(i-1, j, numJoueur):
                        return True
                    if self.appartientColonieAuJoueur(i-1, j, 0) and (self.appartientRouteAuJoueur(i-1, j-1, numJoueur) or self.appartientRouteAuJoueur(i-1, j+1, numJoueur)):
                        return True
                    if self.appartientColonieAuJoueur(i+1, j, numJoueur):
                        return True
                    if self.appartientColonieAuJoueur(i+1, j, 0) and (self.appartientRouteAuJoueur(i+1, j-1, numJoueur) or self.appartientRouteAuJoueur(i+1, j+1, numJoueur)):
                        return True
        return False

    def lstColoniesPossiblesDepuisRoute(self, lig, col, numJoueur, estDansPlacementInitial):
        """
        renvoie la liste des croisements adjacents a la route d'indices lig, col constructibles par le joueur numJoueur
        lig, col: coordonées de la route, int * int
        numJoueur: numero du joueur, int
        estDansPlacement initial: si on est dans la phase de pkacement initiale, bool
        """
        res = []
        if lig % 2 == 0:  # ligne paire, chemins horizontaux
            if self.estPlacementColoniePossible(lig, col+1, numJoueur, estDansPlacementInitial) and not (self.plateau[lig][col+1].marque[numJoueur]):
                res += [(lig, col+1)]
                self.plateau[lig][col+1].marque[numJoueur] = True
            elif self.estPlacementColoniePossible(lig, col-1, numJoueur, estDansPlacementInitial) and not (self.plateau[lig][col-1].marque[numJoueur]):
                res += [(lig, col-1)]
                self.plateau[lig][col-1].marque[numJoueur] = True
        else:  # ligne impaire, chemins verticaux
            if self.estPlacementColoniePossible(lig+1, col, numJoueur, estDansPlacementInitial) and not (self.plateau[lig+1][col].marque[numJoueur]):
                res += [(lig+1, col)]
                self.plateau[lig+1][col].marque[numJoueur] = True
            elif self.estPlacementColoniePossible(lig-1, col, numJoueur, estDansPlacementInitial) and not (self.plateau[lig-1][col].marque[numJoueur]):
                res += [(lig-1, col)]
                self.plateau[lig-1][col].marque[numJoueur] = True
        return res

    def lstRoutesPossiblesDepuisColonie(self, lig, col, numJoueur):
        """
        Renvoie la liste des chemins constructibles adjacents au croisement d'indice lig, col
        (Utile seulement pour l'IA)
        lig, col: coordonnées du croisement, int * int
        """
        res = []
        assert type(
            self.plateau[lig][col]) == Croisement, "plateau.lstRoutesPossiblesDepuisColonies: pas des coord de colonie"
        # on teste les quatres cases adjacentes et on ajoutes les chemins non construits à res
        if lig != 0:
            case = self.plateau[lig-1][col]
            if type(case) == Chemin and case.route == 0:
                res.append((lig-1, col))
                case.marque[numJoueur] = True
        if lig != dimensions[0]-1:
            case = self.plateau[lig+1][col]
            if type(case) == Chemin and case.route == 0:
                res.append((lig+1, col))
                case.marque[numJoueur] = True
        if col != 0:
            case = self.plateau[lig][col-1]
            if type(case) == Chemin and case.route == 0:
                res.append((lig, col-1))
                case.marque[numJoueur] = True
        if col != dimensions[1]-1:
            case = self.plateau[lig][col+1]
            if type(case) == Chemin and case.route == 0:
                res.append((lig, col+1))
                case.marque[numJoueur] = True
        return res

    def lstRoutesPossiblesDepuisRoute(self, lig, col, numJoueur):
        """
        Revoie la liste des chemins constructibles accessibles depuis un autre chemin
        lig, col: coordonnée du chemin en question, int * int
        """
        res = []
        assert type(
            self.plateau[lig][col]) == Chemin, "plateau.lstRoutesPossiblesDepuisRoute: pas des coord de chemin"
        if lig % 2 == 1:  # ligne impaire, routes verticales
            if col != 0:
                if self.estPlacementRoutePossible(lig-1, col-1, numJoueur) and not (self.plateau[lig-1][col-1].marque[numJoueur]):
                    res.append((lig-1, col-1))
                    self.plateau[lig-1][col-1].marque[numJoueur] = True
            if self.estPlacementRoutePossible(lig+1, col-1, numJoueur) and not (self.plateau[lig+1][col-1].marque[numJoueur]):
                res.append((lig+1, col-1))
                self.plateau[lig+1][col-1].marque[numJoueur] = True
            if col != dimensions[1]-1:
                if self.estPlacementRoutePossible(lig-1, col+1, numJoueur) and not (self.plateau[lig-1][col+1].marque[numJoueur]):
                    res.append((lig-1, col+1))
                    self.plateau[lig-1][col+1].marque[numJoueur] = True
                if self.estPlacementRoutePossible(lig+1, col+1, numJoueur) and not (self.plateau[lig+1][col+1].marque[numJoueur]):
                    res.append((lig+1, col+1))
                    self.plateau[lig+1][col+1].marque[numJoueur] = True
        else:  # lignes paires, routes horizontales
            configuration = int((-1)**((lig + col)//2))
            if col != 1:
                if self.estPlacementRoutePossible(lig, col-2, numJoueur) and not (self.plateau[lig][col-2].marque[numJoueur]):
                    res.append((lig, col-2))
                    self.plateau[lig][col-2].marque[numJoueur] = True
            if col != dimensions[1] - 2:
                if self.estPlacementRoutePossible(lig, col+2, numJoueur) and not (self.plateau[lig][col+2].marque[numJoueur]):
                    res.append((lig, col+2))
                    self.plateau[lig][col+2].marque[numJoueur] = True
            if lig-configuration >= 0 and lig-configuration < dimensions[0]:
                if self.estPlacementRoutePossible(lig-configuration, col+1, numJoueur) and not (self.plateau[lig-configuration][col+1].marque[numJoueur]):
                    res.append((lig-configuration, col+1))
                    self.plateau[lig-configuration][col +
                                                    1].marque[numJoueur] = True
            if lig+configuration >= 0 and lig+configuration < dimensions[0]:
                if self.estPlacementRoutePossible(lig+configuration, col-1, numJoueur) and not (self.plateau[lig+configuration][col-1].marque[numJoueur]):
                    res.append((lig+configuration, col-1))
                    self.plateau[lig+configuration][col -
                                                    1].marque[numJoueur] = True
        return res


class Joueur:
    """
    Un joueur, que ce soit un humain ou une IA
    """
    numJoueur = 0
    pointsDeVictoire = 0
    ressources = {}  # quantite de chaque ressource
    estUneIA = False
    coloniesPossibles = []
    routesPossibles = []
    villesPossibles = []
    nbRoutes = 0
    nbColonies = 0
    nbVilles = 0
    # jeu dans lequel joue le joueur, le jeu global ou un jeu simule par monte carlo
    jeuAuquelJeJoue = []

    def __init__(self, num, pJeu):
        """
        initialisation d'un joueur
        num: numero du joueur, int
        """
        self.numJoueur = num
        self.ressources = {"bois": 0, "pierre": 0,
                           "brique": 0, "bétail": 0, "blé": 0}
        self.coloniesPossibles = []
        self.routesPossibles = []
        self.villesPossibles = []
        self.jeuAuquelJeJoue = pJeu

    def equilibreRessourcesVoleurs(self):
        n = 0
        for r, i in self.ressources.items():
            n += i
        if n > 7:
            for r, i in self.ressources.items():
                if i > 4:
                    self.ressources[r] = 4

    def ajoutePointDeVictoire(self):
        self.pointsDeVictoire += 1
        if self.pointsDeVictoire >= 10:
            self.jeuAuquelJeJoue.victoire()

    def ajouteRessource(self, ressource, nb):
        self.ressources[ressource] += nb

    def joue(self):
        """
        Joue, fonction à modifier dans les IA
        """
        return True

    def deplaceVoleur(self):
        """
        Deplace les voleurs, fonction à modifier dans les IA
        """
        return True

    def placementInitial(self):
        """
        Place une route et une colonie, fonction a modifier dans les IA
        """
        return True

    def croisement(self, case, estDansPlacementInitial=False):
        """
        Interaction avec un croisement
        case: le croisement en question, Croisement
        estDansPlacementInitial: si on est dans la phase initiale de déploiement, bool
        """

        if case.niveau == 0 and case.joueur == 0:  # Si c'est une case vide
            if estDansPlacementInitial or (self.ressources["bois"] >= 1 and self.ressources["brique"] >= 1 and self.ressources["bétail"] >= 1 and self.ressources["blé"] >= 1):
                if not (estDansPlacementInitial):  # on paie le cout de construction
                    self.ajouteRessource("bois", -1)
                    self.ajouteRessource("brique", -1)
                    self.ajouteRessource("bétail", -1)
                    self.ajouteRessource("blé", -1)
                else:
                    # on gagne une ressource de chaque tuile adjacente
                    for r, _ in case.lstRessourcesAdjacentes:
                        self.ajouteRessource(r, 1)

                # construction de la colonie
                case.construction(self.numJoueur)

                self.ajoutePointDeVictoire()
                self.nbColonies += 1
                if estDansPlacementInitial:
                    self.routesPossibles += self.jeuAuquelJeJoue.plateau.lstRoutesPossiblesDepuisColonie(
                        case.pos[0], case.pos[1], self.numJoueur)
                else:
                    try:
                        self.coloniesPossibles.remove(case.pos)
                    except:
                        print("Position pas conforme")
                self.villesPossibles.append(case.pos)

        # si c'est une colonie appartenant au joueur (et qu'on veut améliorer en ville)
        elif case.niveau == 1 and case.joueur == self.numJoueur:
            if self.ressources["pierre"] >= 3 and self.ressources["blé"] >= 2:
                self.ajouteRessource("pierre", -3)
                self.ajouteRessource("blé", -2)
                case.amelioration()
                self.villesPossibles.remove(case.pos)
                self.ajoutePointDeVictoire()

    def chemin(self, case, estDansPlacementInitial=False):
        """
        Interaction avec un chemin
        case: chemin en question, Chemin
        estDansPlacementInitial: si on est dans la phase de déploiement initiale
        """
        if estDansPlacementInitial or (self.ressources["brique"] >= 1 and self.ressources["bois"] >= 1):
            if not (estDansPlacementInitial):
                self.ajouteRessource("brique", -1)
                self.ajouteRessource("bois", -1)
            case.construction(self.numJoueur)
            self.coloniesPossibles += self.jeuAuquelJeJoue.plateau.lstColoniesPossiblesDepuisRoute(
                case.pos[0], case.pos[1], self.numJoueur, estDansPlacementInitial)
            self.routesPossibles += self.jeuAuquelJeJoue.plateau.lstRoutesPossiblesDepuisRoute(
                case.pos[0], case.pos[1], self.numJoueur)
            try:
                self.routesPossibles.remove(case.pos)
            except:
                None
            self.nbRoutes += 1

    def echange(self, ressourceDonnee, ressourceRecue):
        """
        echange 4 ressourceDonnee contre 1 ressourceRecue
        ressourceDonnee: ressource donnee en echange, str
        ressourceRecue: ressource recue par l'echange, str 
        """
        if self.ressources[ressourceDonnee] >= 4 and ressourceDonnee != ressourceRecue:
            self.ajouteRessource(ressourceDonnee, -4)
            self.ajouteRessource(ressourceRecue, 1)


class Jeu:
    phase = "init"  # "init", "placement initial", "distribution ressources", "jeu", "changement joueurs", "deplacement voleurs", "fini", "simulation"
    joueurQuiDebute = rd.randint(1, nbJoueur)
    joueurActuel = joueurQuiDebute
    dicoJoueurs = {}
    # liste de coordonnées des tuiles fonction de leur numero, pour la distribution des ressources.
    lstTuilesNum = [[] for _ in range(13)]
    plateau = Plateau(lstTuilesNum)
    ordreJoueurs = [i for i in range(joueurQuiDebute, joueurQuiDebute + nbJoueur)] + [
        i for i in range(joueurQuiDebute + nbJoueur - 1, joueurQuiDebute-1, - 1)]
    echangeRessource = ""
    posVoleur = (5, 10)
    estJeuPrincipal = True
    laisseJouerIA = True

    # pour placement initial
    aPlaceRoute = False
    aPlaceColonie = False

    # pourMCTS
    MCTS_joue = False
    id_MCTS = -1
    MCTS_dicoEchangeDonne = {"bois": 0, "brique": 0,
                             "bétail": 0, "pierre": 0, "blé": 0}
    MCTS_dicoEchangeRecu = {"bois": 0, "brique": 0,
                            "bétail": 0, "pierre": 0, "blé": 0}
    MCTS_action = ""
    MCTS_pos = None
    MCTS_adversaireAAgit = False

    def copie(self):
        # Renvoie une copie du jeu, avec plateau et tt, mais pas les joueurs puisqu'on ne les utilise pas
        nouveauJeu = Jeu()
        nouveauJeu.phase = self.phase
        nouveauJeu.joueurQuiDebute = self.joueurQuiDebute
        nouveauJeu.joueurActuel = self.joueurActuel
        nouveauJeu.lstTuilesNum = self.lstTuilesNum.copy()
        nouveauJeu.plateau = self.plateau.copie()
        nouveauJeu.ordreJoueurs = self.ordreJoueurs.copy()
        nouveauJeu.echangeRessource = self.echangeRessource
        nouveauJeu.posVoleur = self.posVoleur
        nouveauJeu.aPlaceRoute = self.aPlaceRoute
        nouveauJeu.aPlaceColonie = self.aPlaceColonie
        nouveauJeu.MCTS_joue = False

        nouveauJeu.estJeuPrincipal = False
        nouveauJeu.dicoJoueurs = {i: Copie_aleatoire_joueur(
            j, nouveauJeu) for i, j in self.dicoJoueurs.items()}

        return nouveauJeu

    def classement(self):
        res = [(j, self.dicoJoueurs[j].pointsDeVictoire)
               for j in range(1, nbJoueur+1)]
        for i in range(1, len(res)):
            cle = res[i]
            j = i-1
            while j >= 0 and res[j][1] > cle[1]:
                res[j+1] = res[j]  # decalage
                j = j-1
            res[j+1] = cle
        return res

    def __init__(self):
        # IA_MCTS(2, 500, 100, self)}
        self.dicoJoueurs = {1: Joueur(1, self), 2: IA_aleatoire(2, self)}
        self.MCTS_joue = False
        self.id_MCTS = 2 - 1
        self.MCTS_dicoEchangeDonne = {
            "bois": 0, "brique": 0, "bétail": 0, "pierre": 0, "blé": 0}
        self.MCTS_dicoEchangeRecu = {
            "bois": 0, "brique": 0, "bétail": 0, "pierre": 0, "blé": 0}
        self.MCTS_action = ""
        self.MCTS_pos = None

    def placementInitial(self):
        self.phase = "placement initial"

        if self.ordreJoueurs == []:
            self.phase = "jeu"
            print("placement init")
        else:
            numJoueur = self.ordreJoueurs.pop()
            self.aPlaceColonie = False
            self.aPlaceRoute = False
            if numJoueur > nbJoueur:
                numJoueur -= nbJoueur
            # joueur qui doit placer sa colonie et sa route
            joueur = self.dicoJoueurs[numJoueur]
            self.joueurActuel = numJoueur
            if joueur.estUneIA:
                self.aPlaceColonie, self.aPlaceRoute = joueur.placementInitial()
                if self.aPlaceColonie and self.aPlaceRoute:
                    self.placementInitial()
                else:
                    print("BUG placement initial: IA joue pas entierement")

    def changementDeJoueur(self):
        if self.phase != "fini":
            self.phase = "changement joueurs"
            if self.MCTS_joue and not (self.MCTS_adversaireAAgit) and self.joueurActuel != self.id_MCTS:
                self.MCTS_dicoEchangeRecu = {
                    "bois": 0, "brique": 0, "bétail": 0, "pierre": 0, "blé": 0}
                self.MCTS_dicoEchangeDonne = {
                    "bois": 0, "brique": 0, "bétail": 0, "pierre": 0, "blé": 0}

            self.joueurActuel += 1
            if self.joueurActuel > nbJoueur:
                self.joueurActuel = 1
                self.plateau.nbTour += 1
            self.distributionRessources()

    def voleur(self):
        self.phase = "deplacement voleurs"
        if self.estJeuPrincipal:
            print("VOLEURS")
        self.dicoJoueurs[self.joueurActuel].deplaceVoleur()
        for i in range(nbJoueur):
            self.dicoJoueurs[i+1].equilibreRessourcesVoleurs()

    def distributionRessources(self):
        self.phase = "distribution ressources"
        de1 = rd.randint(1, 6)
        de2 = rd.randint(1, 6)
        numRessourceProduite = de1 + de2
        if numRessourceProduite == 7:
            self.voleur()
        else:
            for (i, j) in self.lstTuilesNum[numRessourceProduite]:
                t = self.plateau.plateau[i][j]
                r, dicoJoueurGain = t.produit(self.plateau)
                for nbJ in range(1, nbJoueur + 1):
                    self.dicoJoueurs[nbJ].ajouteRessource(
                        r, dicoJoueurGain[nbJ])
            self.phase = "jeu"

    def estDeplacementVoleursPossible(self, pos):
        return ((abs(self.posVoleur[0] - pos[0]) + abs(self.posVoleur[1] - pos[1])) == 4 and abs(self.posVoleur[0] - pos[0]) != 4)

    def IA_lstDeplacementVoleurPossible(self):
        res = []
        pos0 = (self.posVoleur[0], self.posVoleur[1])
        for i in range(-2, 3, 2):
            j = 4 - abs(i)
            pos = (pos0[0] + i, pos0[1] + j)
            # verification du type necessaire car on peut atterir sur une case dans la mer
            if estCoordonnesValide(pos) and type(self.plateau.plateau[pos[0]][pos[1]]) == Tuile:
                res.append(pos)
            pos = (pos0[0] + i, pos0[1] - j)
            if estCoordonnesValide(pos) and type(self.plateau.plateau[pos[0]][pos[1]]) == Tuile:
                res.append(pos)
        return res

    def IA_estActionPossible(self, pos, numJoueur):
        if pos == (-1, -1):
            return True
        case = self.plateau.plateau[pos[0]][pos[1]]
        if type(case) == Chemin and case.route == 0:
            return True
        if type(case) == Croisement and (case.joueur == 0 or (case.joueur == numJoueur and case.niveau < 2)):
            return True
        return False

    def deplacementVoleur(self, lig, col):
        case = self.plateau.plateau[lig][col]
        if type(case) == Tuile and self.estDeplacementVoleursPossible(case.pos):
            self.plateau.plateau[self.posVoleur[0]
                                 ][self.posVoleur[1]].voleur = False
            self.posVoleur = lig, col
            case.voleur = True
            self.phase = "jeu"

    def action(self, lig, col):
        # gere clic d'un joueur dans la grille
        joueurCourant = self.dicoJoueurs[self.joueurActuel]
        if not (joueurCourant.estUneIA):
            if self.phase == "jeu":
                if lig != None and col != None:
                    case = self.plateau.plateau[lig][col]
                    if type(case) == Croisement:
                        if (case.joueur == 0 and self.plateau.estPlacementColoniePossible(lig, col, self.joueurActuel, False)) or case.joueur == self.joueurActuel:
                            joueurCourant.croisement(case)

                    elif type(case) == Chemin:
                        if case.route == 0 and self.plateau.estPlacementRoutePossible(lig, col, self.joueurActuel):
                            joueurCourant.chemin(case)

            elif self.phase == "deplacement voleurs":
                if lig != None and col != None:
                    self.deplacementVoleur(lig, col)

            elif self.phase == "placement initial":
                if lig != None and col != None:
                    case = self.plateau.plateau[lig][col]
                    if type(case) == Croisement:
                        if not (self.aPlaceColonie) and case.joueur == 0 and self.plateau.estPlacementColoniePossible(lig, col, self.joueurActuel, True):
                            joueurCourant.croisement(case, True)
                            self.aPlaceColonie = True
                            if self.aPlaceRoute:
                                self.placementInitial()
                    elif type(case) == Chemin:
                        if not (self.aPlaceRoute) and case.route == 0 and self.plateau.estPlacementRoutePossible(lig, col, self.joueurActuel):
                            joueurCourant.chemin(case, True)
                            self.aPlaceRoute = True
                            if self.aPlaceColonie:
                                self.placementInitial()

    def echange(self, ressource):
        if self.echangeRessource == "":
            self.echangeRessource = ressource
        else:
            self.dicoJoueurs[self.joueurActuel].echange(
                self.echangeRessource, ressource)
            self.MCTS_dicoEchangeDonne[self.echangeRessource] += 1
            self.MCTS_dicoEchangeRecu[ressource] += 1
            self.echangeRessource = ""

    def jeu(self):
        if self.phase == "jeu" and self.laisseJouerIA:
            self.dicoJoueurs[self.joueurActuel].joue()

    def victoire(self):
        self.phase = "fini"
        if self.estJeuPrincipal:
            Victoire(self.classement())


###########################
###         IAs         ###
###########################

class IA_aleatoire(Joueur):
    """
    Une IA jouant avec un systeme d'aléatoire pondéré
    """
    # poids données a chaque action dans le choix aleatoire
    poids = {}
    # score donnée à chaque croisement lors du placement initial (qui est tres important, donc choisi non aléatoire
    scoresPlacementInitial = []

    # modificateurs dans le score des croisements liés à la nature des ressources accessibles (si un bois est plus interessant qu'un bétail par exemple)
    modificateursScoresRessource = {}

    def __init__(self, num, pJeu, poids={"route": 300, "colonie": 10000, "ville": 10000, "passer": 100}, modificateursScoresRessource={"brique": 5, "bois": 5, "pierre": 5, "blé": 5, "bétail": 4}):
        """
        Initialisation de l'IA
        num: numero de joueur
        poids : poids donnés a chaque action dans le choix aleatoire
        modificateurScoresRessource: modificateurs dans le score des croisements
        """
        Joueur.__init__(self, num, pJeu)
        self.scoresPlacementInitial = []
        self.estUneIA = True
        self.modificateursScoresRessource = modificateursScoresRessource
        self.poids = poids.copy()
        self.poidsRouteInit = self.poids["route"]

    def deplaceVoleur(self):
        """
        Deplace le voleur aléatoirement
        """
        l = self.jeuAuquelJeJoue.IA_lstDeplacementVoleurPossible()
        scoreVoleurs = {pos: 0 for pos in l}
        for pos in l:
            score = 0
            num = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]].num
            for i in range(pos[0]-1, pos[0]+2):
                for j in range(pos[1]-2, pos[1]+3):  # pour chaque croisement autour
                    case = self.jeuAuquelJeJoue.plateau.plateau[i][j]
                    if type(case) == Chemin:
                        if case.route == self.numJoueur:
                            score -= 1
                        elif case.route != 0:
                            score += 1
                    elif type(case) == Croisement:
                        if case.joueur == self.numJoueur:
                            score -= case.niveau * 3  # on veut pas se bloquer une case
                        elif case.joueur != 0:
                            score += case.niveau * 3
            # routes a droite et a gauche
            case = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]-2]
            if case.route == self.numJoueur:
                score -= 1
            elif case.route != 0:
                score += 1
            case = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]+2]
            if case.route == self.numJoueur:
                score -= 1
            elif case.route != 0:
                score += 1
            scoreVoleurs[pos] = score * 1/abs(7-num)

        # on cherche la pos avec le score max
        posMax, scoreMax = l[0], scoreVoleurs[l[0]]
        for pos, score in scoreVoleurs.items():
            if score > scoreMax:
                scoreMax = score
                posMax = pos
        self.jeuAuquelJeJoue.deplacementVoleur(posMax[0], posMax[1])
        if self.jeuAuquelJeJoue.estJeuPrincipal:
            print("finDeplaceVoleur")

    def placementInitial(self):
        print("PLACEMENT INITIAL IA")
        if self.scoresPlacementInitial == []:
            for i in range(0, dimensions[0], 2):
                marge = 0
                if i <= 4:
                    marge = 4-i
                else:
                    marge = i-6
                for j in range(marge, dimensions[1]-marge, 2):
                    score = 0
                    for ressource, nb in self.jeuAuquelJeJoue.plateau.plateau[i][j].lstRessourcesAdjacentes:
                        score += 1 / \
                            abs(7-nb) * \
                            self.modificateursScoresRessource[ressource]
                    self.scoresPlacementInitial.append(((i, j), score))

            lstTriee = []
            for x in self.scoresPlacementInitial:
                lstTriee.insert(0, x)
                i = 0
                while i < len(lstTriee)-1 and lstTriee[i][1] > lstTriee[i+1][1]:
                    lstTriee[i], lstTriee[i+1] = lstTriee[i+1], lstTriee[i]
                    i += 1
            self.scoresPlacementInitial = lstTriee

        emplacementChoisi = ((0, 0), float('inf'))
        while not (self.jeuAuquelJeJoue.plateau.estPlacementColoniePossible(emplacementChoisi[0][0], emplacementChoisi[0][1], self.numJoueur, True)):
            emplacementChoisi = self.scoresPlacementInitial.pop()
        case = self.jeuAuquelJeJoue.plateau.plateau[emplacementChoisi[0]
                                                    [0]][emplacementChoisi[0][1]]
        self.croisement(case, True)
        i = rd.randint(0, len(self.routesPossibles)-1)
        routeChoisie = self.routesPossibles[i]
        self.chemin(
            self.jeuAuquelJeJoue.plateau.plateau[routeChoisie[0]][routeChoisie[1]], True)
        return True, True

    def echange(self, dicoDonne, dicoRecu):
        # On suppose l'echange possible, normalement c'est bon
        for ressource, nb in dicoDonne.items():
            self.ressources[ressource] -= 4 * nb
            if self.ressources[ressource] < 0:
                self.ressources[ressource] = 0
            # assert self.ressources[ressource] >= 0, "echange: echange pas possible"
        for ressource, nb in dicoRecu.items():
            self.ressources[ressource] += nb

    def peutConstruire(self, pDicoVoulu):
        """
        Renvoie un couple contenant un booleen, une liste de dictionnaires, et un dictionnaire
        Le booleen indique si oui ou non il est possible de réunir les ressources de pDicoVoulu avec des echanges
        La liste est la liste des dictionnaires représentant pour chaque ressource le nombre d'échanges à réaliser en donnant cette ressource
        le dictionnaire associe a chaque ressource le nombre de cette ressource a recevoir.
        """
        l = ["bétail", "blé", "pierre", "brique", "bois"]
        dicoRessources = self.ressources.copy()
        dicoEchangesPossibles = {ressource: 0 for ressource in dicoRessources}
        dicoRessourcesNecessaires = {
            ressource: 0 for ressource in dicoRessources}
        nbEchangeDispo = 0
        nbEchangeNecessaire = 0

        def lstEchanges(r, nbVoulu):
            """
            fonction récursive renvoyant la liste des echanges possibles pour avoir nbVoulu echanges
            r: int indice de la ressource qu'on est en train de traiter (entre 0 et 4 donc)
            nbVoulu: int nombre d'echanges qu'on veut faire
            retourne res, possible avec
            res: liste des echanges possible, liste de dictionnaires (vide si aucun echange satisfaisant)
            """
            if nbVoulu == 0:  # on n'a plus d'echange a faire, on a fini. (le == permet en outre de ne pas faire plus d'echange que necessaire)
                return [{"bétail": 0, "blé": 0, "pierre": 0, "brique": 0, "bois": 0}]
            elif r >= 5 or nbVoulu < 0:  # il reste des echanges a placer, mais on arrive au bout des ressources
                return []
            else:
                ressouce = l[r]
                res = []
                # on regarde tous les cas possibles: si on fait 0 echange, 1 echange, ... jsuqu'au nb max d'echanges possibles avec cette ressource
                for i in range(dicoEchangesPossibles[ressouce]+1):
                    lst = lstEchanges(r+1, nbVoulu-i)
                    for echange in lst:
                        echange[ressouce] = i
                        res.append(echange)
                return res

        for ressource in l:  # on replie dicoEchangesPossibles et dicoRessourcesNecessaires
            if dicoRessources[ressource] >= pDicoVoulu[ressource]:
                dicoRessources[ressource] -= pDicoVoulu[ressource]
                dicoEchangesPossibles[ressource] = dicoRessources[ressource] // 4
                nbEchangeDispo += dicoEchangesPossibles[ressource]
            else:
                dicoRessourcesNecessaires[ressource] = pDicoVoulu[ressource] - \
                    dicoRessources[ressource]
                nbEchangeNecessaire += dicoRessourcesNecessaires[ressource]

        if nbEchangeDispo < nbEchangeNecessaire:  # pas possible
            return False, [], {}
        elif nbEchangeNecessaire == nbEchangeDispo:  # une seule configuration d'echanges possible
            return True, [dicoEchangesPossibles], dicoRessourcesNecessaires
        else:  # plusieurs configurations d'echanges possibles
            return True, lstEchanges(0, nbEchangeNecessaire), dicoRessourcesNecessaires

    def DonneLstActionsPossibles(self):
        lstActionsPossibles = [("passer", None, {}, {})]

        dico = {"bois": 1, "brique": 1, "bétail": 0, "blé": 0, "pierre": 0}
        possible, lstDonsEchange, dicoGainEchange = self.peutConstruire(dico)
        if possible:
            for coord in self.routesPossibles:
                if self.jeuAuquelJeJoue.plateau.estPlacementRoutePossible(coord[0], coord[1], self.numJoueur):
                    lstActionsPossibles += [("route", coord, don, dicoGainEchange)
                                            for don in lstDonsEchange]
                else:
                    self.routesPossibles.remove(coord)

        dico = {"bois": 1, "brique": 1, "bétail": 1, "blé": 1, "pierre": 0}
        possible, lstDonsEchange, dicoGainEchange = self.peutConstruire(dico)
        if possible:
            for coord in self.coloniesPossibles:
                if self.jeuAuquelJeJoue.plateau.estPlacementColoniePossible(coord[0], coord[1], self.numJoueur, False):
                    lstActionsPossibles += [("colonie", coord, don, dicoGainEchange)
                                            for don in lstDonsEchange]
                else:
                    self.coloniesPossibles.remove(coord)

        dico = {"bois": 0, "brique": 0, "bétail": 0, "blé": 2, "pierre": 3}
        possible, lstDonsEchange, dicoGainEchange = self.peutConstruire(dico)
        if possible:
            lstActionsPossibles += [("ville", coord, don, dicoGainEchange)
                                    for coord in self.villesPossibles for don in lstDonsEchange]
        return lstActionsPossibles

    def joueAction(self, action):
        if action[0] != "passer":
            self.echange(action[2], action[3])
            if action[0] == "route":
                self.chemin(
                    self.jeuAuquelJeJoue.plateau.plateau[action[1][0]][action[1][1]])
            elif action[0] == "colonie" or action[0] == "ville":
                self.croisement(
                    self.jeuAuquelJeJoue.plateau.plateau[action[1][0]][action[1][1]])
            else:
                print("Action pas normale")

    def joue(self):
        lstActionsPossibles = self.DonneLstActionsPossibles()

        nTotal = 0

        for i in range(len(lstActionsPossibles)):
            action = lstActionsPossibles[i]
            nTotal += self.poids[action[0]]

        nChoisi = rd.randint(1, nTotal)
        i = 0
        while nChoisi - self.poids[lstActionsPossibles[i][0]] > 0:
            nChoisi -= self.poids[lstActionsPossibles[i][0]]
            i += 1

        # On a choisi lstActionsPossibles[i]
        self.joueAction(lstActionsPossibles[i])
        self.jeuAuquelJeJoue.changementDeJoueur()


class IA_monteCarlo(Joueur):
    nbSimulations = 1

    SimulationEnCours = False
    lstActionsPossibles = []
    idActionSimulee = 0  # indice de l'action simulee dans scores
    scores = []  # list des couples (action, score)
    nbSimulationsFaites = 0  # nombre de parties simulées achevées avec l'action en cours
    jeuSimulation = ""  # jeu utilisé pour la simulation, sera du type Jeu

    # listes des coordonnées des cases où l'IA peut construire
    routesPossibles = []
    coloniesPossibles = []
    villesPossibles = []

    # score donnée à chaque croisement lors du placement initial (qui est tres important, donc choisi non aléatoire
    scoresPlacementInitial = []

    # modificateurs dans le score des croisements liés à la nature des ressources accessibles (si un bois est plus interessant qu'un bétail par exemple)
    modificateursScoresRessource = {}

    def __init__(self, num, nbSimulations, pJeu, modificateursScoresRessource={"brique": 1, "bois": 1, "pierre": 1, "blé": 1, "bétail": 1}):
        """
        Initialisation de l'IA
        num: numero de joueur
        modificateurScoresRessource: modificateurs dans le score des croisements
        nbSimulations: le nombre de simulations pour chaque action possible à chaque tour
        """
        Joueur.__init__(self, num, pJeu)
        self.routesPossibles = []
        self.coloniesPossibles = []
        self.villesPossibles = []
        self.scoresPlacementInitial = []
        self.estUneIA = True
        self.modificateursScoresRessource = modificateursScoresRessource
        self.nbSimulations = nbSimulations

        # self.ressources = {"bois": 1, "brique": 1, "bétail": 1, "blé": 1, "pierre":1}

        self.lstActionsPossibles = []
        self.scores = []
        self.jeuSimulation = self.jeuAuquelJeJoue

    def deplaceVoleur(self):
        """
        Deplace le voleur aléatoirement
        """
        print("voleur monte carlo")
        l = self.jeuAuquelJeJoue.IA_lstDeplacementVoleurPossible()
        scoreVoleurs = {pos: 0 for pos in l}
        for pos in l:
            score = 0
            num = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]].num
            for i in range(pos[0]-1, pos[0]+2):
                for j in range(pos[1]-2, pos[1]+3):  # pour chaque croisement autour
                    case = self.jeuAuquelJeJoue.plateau.plateau[i][j]
                    if type(case) == Chemin:
                        if case.route == self.numJoueur:
                            score -= 1
                        elif case.route != 0:
                            score += 1
                    elif type(case) == Croisement:
                        if case.joueur == self.numJoueur:
                            score -= case.niveau * 3  # on veut pas se bloquer une case
                        elif case.joueur != 0:
                            score += case.niveau * 3
            # routes a droite et a gauche
            case = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]-2]
            if case.route == self.numJoueur:
                score -= 1
            elif case.route != 0:
                score += 1
            case = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]+2]
            if case.route == self.numJoueur:
                score -= 1
            elif case.route != 0:
                score += 1
            scoreVoleurs[pos] = score * 1/abs(7-num)

        # on cherche la pos avec le score max
        posMax, scoreMax = l[0], scoreVoleurs[l[0]]
        for pos, score in scoreVoleurs.items():
            if score > scoreMax:
                scoreMax = score
                posMax = pos
        self.jeuAuquelJeJoue.deplacementVoleur(posMax[0], posMax[1])

    def placementInitial(self):
        print("PLACEMENT INITIAL IA")
        if self.scoresPlacementInitial == []:
            for i in range(0, dimensions[0], 2):
                marge = 0
                if i <= 4:
                    marge = 4-i
                else:
                    marge = i-6
                for j in range(marge, dimensions[1]-marge, 2):
                    score = 0
                    for ressource, nb in self.jeuAuquelJeJoue.plateau.plateau[i][j].lstRessourcesAdjacentes:
                        score += 1 / \
                            abs(7-nb) * \
                            self.modificateursScoresRessource[ressource]
                    self.scoresPlacementInitial.append(((i, j), score))

            lstTriee = []
            for x in self.scoresPlacementInitial:
                lstTriee.insert(0, x)
                i = 0
                while i < len(lstTriee)-1 and lstTriee[i][1] > lstTriee[i+1][1]:
                    lstTriee[i], lstTriee[i+1] = lstTriee[i+1], lstTriee[i]
                    i += 1
            self.scoresPlacementInitial = lstTriee

        emplacementChoisi = ((0, 0), float('inf'))
        while not (self.jeuAuquelJeJoue.plateau.estPlacementColoniePossible(emplacementChoisi[0][0], emplacementChoisi[0][1], self.numJoueur, True)):
            emplacementChoisi = self.scoresPlacementInitial.pop()
        case = self.jeuAuquelJeJoue.plateau.plateau[emplacementChoisi[0]
                                                    [0]][emplacementChoisi[0][1]]
        self.croisement(case, True)
        i = rd.randint(0, len(self.routesPossibles)-1)
        routeChoisie = self.routesPossibles[i]
        self.chemin(
            self.jeuAuquelJeJoue.plateau.plateau[routeChoisie[0]][routeChoisie[1]], True)
        return True, True

    def echange(self, dicoDonne, dicoRecu):
        # On suppose l'echange possible, normalement c'est bon
        for ressource, nb in dicoDonne.items():
            self.ressources[ressource] -= 4 * nb
            if self.ressources[ressource] < 0:
                self.ressources[ressource] = 0
            # assert self.ressources[ressource] >= 0, "echange: echange pas possible"
        for ressource, nb in dicoRecu.items():
            self.ressources[ressource] += nb

    def joueAction(self, action):
        print(action)
        if action[0] != "passer":
            self.echange(action[2], action[3])
            if action[0] == "route":
                self.chemin(
                    self.jeuAuquelJeJoue.plateau.plateau[action[1][0]][action[1][1]])
            elif action[0] == "colonie" or action[0] == "ville":
                self.croisement(
                    self.jeuAuquelJeJoue.plateau.plateau[action[1][0]][action[1][1]])
            else:
                print("Action pas normale")

    def peutConstruire(self, pDicoVoulu):
        """
        Renvoie un couple contenant un booleen, une liste de dictionnaires, et un dictionnaire
        Le booleen indique si oui ou non il est possible de réunir les ressources de pDicoVoulu avec des echanges
        La liste est la liste des dictionnaires représentant pour chaque ressource le nombre d'échanges à réaliser en donnant cette ressource
        le dictionnaire associe a chaque ressource le nombre de cette ressource a recevoir.
        """
        l = ["bétail", "blé", "pierre", "brique", "bois"]
        dicoRessources = self.ressources.copy()
        dicoEchangesPossibles = {ressource: 0 for ressource in dicoRessources}
        dicoRessourcesNecessaires = {
            ressource: 0 for ressource in dicoRessources}
        nbEchangeDispo = 0
        nbEchangeNecessaire = 0

        def lstEchanges(r, nbVoulu):
            """
            fonction récursive renvoyant la liste des echanges possibles pour avoir nbVoulu echanges
            r: int indice de la ressource qu'on est en train de traiter (entre 0 et 4 donc)
            nbVoulu: int nombre d'echanges qu'on veut faire
            retourne res, possible avec
            res: liste des echanges possible, liste de dictionnaires (vide si aucun echange satisfaisant)
            """
            if nbVoulu == 0:  # on n'a plus d'echange a faire, on a fini. (le == permet en outre de ne pas faire plus d'echange que necessaire)
                return [{"bétail": 0, "blé": 0, "pierre": 0, "brique": 0, "bois": 0}]
            elif r >= 5 or nbVoulu < 0:  # il reste des echanges a placer, mais on arrive au bout des ressources
                return []
            else:
                ressouce = l[r]
                res = []
                # on regarde tous les cas possibles: si on fait 0 echange, 1 echange, ... jsuqu'au nb max d'echanges possibles avec cette ressource
                for i in range(dicoEchangesPossibles[ressouce]+1):
                    lst = lstEchanges(r+1, nbVoulu-i)
                    for echange in lst:
                        echange[ressouce] = i
                        res.append(echange)
                return res

        for ressource in l:  # on replie dicoEchangesPossibles et dicoRessourcesNecessaires
            if dicoRessources[ressource] >= pDicoVoulu[ressource]:
                dicoRessources[ressource] -= pDicoVoulu[ressource]
                dicoEchangesPossibles[ressource] = dicoRessources[ressource] // 4
                nbEchangeDispo += dicoEchangesPossibles[ressource]
            else:
                dicoRessourcesNecessaires[ressource] = pDicoVoulu[ressource] - \
                    dicoRessources[ressource]
                nbEchangeNecessaire += dicoRessourcesNecessaires[ressource]

        if nbEchangeDispo < nbEchangeNecessaire:  # pas possible
            return False, [], {}
        elif nbEchangeNecessaire == nbEchangeDispo:  # une seule configuration d'echanges possible
            return True, [dicoEchangesPossibles], dicoRessourcesNecessaires
        else:  # plusieurs configurations d'echanges possibles
            return True, lstEchanges(0, nbEchangeNecessaire), dicoRessourcesNecessaires

    def joue(self):
        if not (self.SimulationEnCours):
            print("debut simulation")
            self.lstActionsPossibles = [("passer", None, {}, {})]

            dico = {"bois": 1, "brique": 1, "bétail": 0, "blé": 0, "pierre": 0}
            possible, lstDonsEchange, dicoGainEchange = self.peutConstruire(
                dico)
            if possible:
                for coord in self.routesPossibles:
                    if self.jeuAuquelJeJoue.plateau.estPlacementRoutePossible(coord[0], coord[1], self.numJoueur):
                        self.lstActionsPossibles += [
                            ("route", coord, don, dicoGainEchange) for don in lstDonsEchange]
                    else:
                        self.routesPossibles.remove(coord)

            dico = {"bois": 1, "brique": 1, "bétail": 1, "blé": 1, "pierre": 0}
            possible, lstDonsEchange, dicoGainEchange = self.peutConstruire(
                dico)
            if possible:
                for coord in self.coloniesPossibles:
                    if self.jeuAuquelJeJoue.plateau.estPlacementColoniePossible(coord[0], coord[1], self.numJoueur, False):
                        self.lstActionsPossibles += [
                            ("colonie", coord, don, dicoGainEchange) for don in lstDonsEchange]
                    else:
                        self.coloniesPossibles.remove(coord)

            dico = {"bois": 0, "brique": 0, "bétail": 0, "blé": 2, "pierre": 3}
            possible, lstDonsEchange, dicoGainEchange = self.peutConstruire(
                dico)
            if possible:
                self.lstActionsPossibles += [("ville", coord, don, dicoGainEchange)
                                             for coord in self.villesPossibles for don in lstDonsEchange]

            # si on a pas le choix et qu'on doit passer son tour, pas la peine de faire une simulation
            if len(self.lstActionsPossibles) <= 1:
                print("pas le choix, l'ia passe son tour")
                self.joueAction(("passer", None, {}, {}))
                self.jeuAuquelJeJoue.changementDeJoueur()

            self.score = [[action, 0] for action in self.lstActionsPossibles]
            self.idActionSimulee = 0  # indice de l'action en train d'etre simulee
            self.nbSimulationsFaites = 0  # nombre de simulations faites avec cette action
            self.SimulationEnCours = True
            self.jeuSimulation = self.jeuAuquelJeJoue.copie()
            self.jeuSimulation.dicoJoueurs[self.numJoueur].poids = {
                "passer": 1, "route": 1, "ville": 1, "colonie": 1}
            self.jeuSimulation.dicoJoueurs[self.numJoueur].poidsRouteInit = 1
            # on commence toujours par simuler un passage de tour
            self.jeuSimulation.changementDeJoueur()
        else:
            global affichage
            affichage = False
            self.jeuSimulation.jeu()
            if self.jeuSimulation.phase == "fini":
                ordreVictoire = self.jeuSimulation.classement()
                if ordreVictoire[-1][0] == self.numJoueur:  # 20 pt si on a gagné
                    self.score[self.idActionSimulee][1] += 20
                # le nombre de pt qu'on a marqué si on est 2e
                elif nbJoueur >= 3 and ordreVictoire[-2][0] == self.numJoueur:
                    self.score[self.idActionSimulee][1] += ordreVictoire[-2][1]

                self.nbSimulationsFaites += 1
                if self.nbSimulationsFaites >= self.nbSimulations:
                    # change d'action
                    print("En jouant ", self.score[self.idActionSimulee][0],
                          "l'ia a obtenu un score de", self.score[self.idActionSimulee][1])
                    self.nbSimulationsFaites = 0
                    self.idActionSimulee += 1
                    # si on a fini les simulations
                    if self.idActionSimulee >= len(self.score):
                        actionChoisie, scoreMax = self.score[0]
                        for action, score in self.score:
                            if score >= scoreMax:
                                scoreMax = score
                                actionChoisie = action
                        print("Finalement, l'ia a choisi l'action: ", actionChoisie)
                        self.SimulationEnCours = False
                        self.joueAction(actionChoisie)
                        affichage = True
                        self.jeuAuquelJeJoue.changementDeJoueur()

                if self.idActionSimulee < len(self.score):
                    self.jeuSimulation = self.jeuAuquelJeJoue.copie()
                    self.jeuSimulation.dicoJoueurs[self.numJoueur].poids = {
                        "passer": 1, "route": 1, "ville": 1, "colonie": 1}
                    self.jeuSimulation.dicoJoueurs[self.numJoueur].poidsRouteInit = 1
                    action = self.score[self.idActionSimulee][0][0]
                    if action != "passer":
                        # coordonnées de l'action
                        self.jeuSimulation.action(
                            self.score[self.idActionSimulee][0][1][0], self.score[self.idActionSimulee][0][1][1])
                    self.jeuSimulation.changementDeJoueur()


class Arbre():
    Proba = 0
    nbVisites = 0
    nbVictoires = 0
    numJoueur = 0
    lstFils = []
    pere = None
    actionPrecedente = None
    hauteur = 0

    def __init__(self, pNumJoueur, pProba, pAction, pPere):
        self.numJoueur = pNumJoueur
        self.Proba = pProba
        self.lstFils = []
        self.actionPrecedente = pAction
        self.pere = pPere
        self.hauteur = 0


class IA_MCTS(Joueur):
    """ Une IA jouant avec un systeme de recharche arborescente de monte-carlo  """
    # score donnée à chaque croisement lors du placement initial
    scoresPlacementInitial = []

    # modificateurs dans le score des croisements liés à la nature des ressources accessibles (si un bois est plus interessant qu'un bétail par exemple)
    modificateursScoresRessource = {}

    # listes des coordonnées des cases où l'IA peut construire
    routesPossibles = []
    coloniesPossibles = []
    villesPossibles = []

    # MCTS
    nbSimulations = 0
    nbGraines = 0
    c = 1
    b = 0.995

    def __init__(self, num, pNbSimulations, pNbGrainesTestee, pJeu, modificateursScoresRessource={"brique": 1, "bois": 1, "pierre": 1, "blé": 1, "bétail": 1}):
        """
        Initialisation de l'IA
        num: numero de joueur
        poids : poids donnés a chaque action dans le choix aleatoire
        modificateurScoresRessource: modificateurs dans le score des croisements
        """
        Joueur.__init__(self, num, pJeu)
        self.scoresPlacementInitial = []
        self.estUneIA = True
        self.modificateursScoresRessource = modificateursScoresRessource
        self.nbSimulations = pNbSimulations
        self.nbGraines = pNbGrainesTestee

    def deplaceVoleur(self):
        """
        Deplace le voleur aléatoirement
        """
        l = self.jeuAuquelJeJoue.IA_lstDeplacementVoleurPossible()
        scoreVoleurs = {pos: 0 for pos in l}
        for pos in l:
            score = 0
            num = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]].num
            for i in range(pos[0]-1, pos[0]+2):
                for j in range(pos[1]-2, pos[1]+3):  # pour chaque croisement autour
                    case = self.jeuAuquelJeJoue.plateau.plateau[i][j]
                    if type(case) == Chemin:
                        if case.route == self.numJoueur:
                            score -= 1
                        elif case.route != 0:
                            score += 1
                    elif type(case) == Croisement:
                        if case.joueur == self.numJoueur:
                            score -= case.niveau * 3  # on veut pas se bloquer une case
                        elif case.joueur != 0:
                            score += case.niveau * 3
            # routes a droite et a gauche
            case = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]-2]
            if case.route == self.numJoueur:
                score -= 1
            elif case.route != 0:
                score += 1
            case = self.jeuAuquelJeJoue.plateau.plateau[pos[0]][pos[1]+2]
            if case.route == self.numJoueur:
                score -= 1
            elif case.route != 0:
                score += 1
            scoreVoleurs[pos] = score * 1/abs(7-num)

        # on cherche la pos avec le score max
        posMax, scoreMax = l[0], scoreVoleurs[l[0]]
        for pos, score in scoreVoleurs.items():
            if score > scoreMax:
                scoreMax = score
                posMax = pos
        self.jeuAuquelJeJoue.deplacementVoleur(posMax[0], posMax[1])
        if self.jeuAuquelJeJoue.estJeuPrincipal:
            print("finDeplaceVoleur")

    def placementInitial(self):
        print("PLACEMENT INITIAL IA")
        if self.scoresPlacementInitial == []:
            for i in range(0, dimensions[0], 2):
                marge = 0
                if i <= 4:
                    marge = 4-i
                else:
                    marge = i-6
                for j in range(marge, dimensions[1]-marge, 2):
                    score = 0
                    for ressource, nb in self.jeuAuquelJeJoue.plateau.plateau[i][j].lstRessourcesAdjacentes:
                        score += 1 / \
                            abs(7-nb) * \
                            self.modificateursScoresRessource[ressource]
                    self.scoresPlacementInitial.append(((i, j), score))

            lstTriee = []
            for x in self.scoresPlacementInitial:
                lstTriee.insert(0, x)
                i = 0
                while i < len(lstTriee)-1 and lstTriee[i][1] > lstTriee[i+1][1]:
                    lstTriee[i], lstTriee[i+1] = lstTriee[i+1], lstTriee[i]
                    i += 1
            self.scoresPlacementInitial = lstTriee

        emplacementChoisi = ((0, 0), float('inf'))
        while not (self.jeuAuquelJeJoue.plateau.estPlacementColoniePossible(emplacementChoisi[0][0], emplacementChoisi[0][1], self.numJoueur, True)):
            emplacementChoisi = self.scoresPlacementInitial.pop()
        case = self.jeuAuquelJeJoue.plateau.plateau[emplacementChoisi[0]
                                                    [0]][emplacementChoisi[0][1]]
        self.croisement(case, True)
        i = rd.randint(0, len(self.routesPossibles)-1)
        routeChoisie = self.routesPossibles[i]
        print(routeChoisie)
        self.chemin(
            self.jeuAuquelJeJoue.plateau.plateau[routeChoisie[0]][routeChoisie[1]], True)
        return True, True

    def echange(self, dicoDonne, dicoRecu):
        # On suppose l'echange possible, normalement c'est bon
        for ressource, nb in dicoDonne.items():
            self.ressources[ressource] -= 4 * nb
            assert self.ressources[ressource] >= 0, "echange: echange pas possible"
        for ressource, nb in dicoRecu.items():
            self.ressources[ressource] += nb

    def selection(self, a, i, lstActrionsPrecedentes):
        """a: arbre auquel on est, i: numero de l'iteration de selection, h: hauteur de a, lstActionsPrecedente: transparent"""
        if a.lstFils == []:
            return a, lstActrionsPrecedentes
        else:
            idSommetChoisi = -1
            scoreSommetChoisi = 0
            n = len(a.lstFils)

            for i in range(n):
                f = a.lstFils[i]
                V = 0
                if f.nbVisites != 0:
                    V = f.nbVictoires/f.nbVisites  # coefficient d'exploitation
                # coefficient d'exploration
                U = f.Proba * a.nbVisites**(1/2) / (f.nbVisites + 1)
                score = V + self.c * self.b**(a.hauteur - i) * U

                if score > scoreSommetChoisi:
                    scoreSommetChoisi = score
                    idSommetChoisi = i
            return self.selection(a.lstFils[idSommetChoisi], i+1, lstActrionsPrecedentes + [a.lstFils[idSommetChoisi].actionPrecedente])

    def backPropagation(self, a, j, h):
        a.nbVisites += 1
        nouveau_h = max(a.hauteur, h)
        a.hauteur = nouveau_h
        if a.numJoueur != j:
            a.nbVictoires += 1

        if a.pere:
            self.backPropagation(a.pere, j, nouveau_h + 1)

    def joueAction(self, action):
        print("action choisie par MCTS:", action)
        if action[0] != "passer":
            self.echange(action[2], action[3])
            if action[0] == "route":
                self.chemin(
                    self.jeuAuquelJeJoue.plateau.plateau[action[1][0]][action[1][1]])
            elif action[0] == "colonie" or action[0] == "ville":
                self.croisement(
                    self.jeuAuquelJeJoue.plateau.plateau[action[1][0]][action[1][1]])
            else:
                print("Action pas normale")

    def descend_arbre(self, pJeu, lstActions):
        n = len(lstActions)
        numJoueur = pJeu.joueurActuel
        for i in range(n):
            action = lstActions[i]
            joueur = pJeu.dicoJoueurs[numJoueur]
            if action[0] != "passer":
                joueur.echange(action[2], action[3])
                if action[0] == "route":
                    joueur.chemin(
                        pJeu.plateau.plateau[action[1][0]][action[1][1]])
                elif action[0] == "colonie" or action[0] == "ville":
                    joueur.croisement(
                        pJeu.plateau.plateau[action[1][0]][action[1][1]])
                else:
                    print("Action pas normale")

            numJoueur = 3-numJoueur
            pJeu.changementDeJoueur()

    def LstActionsPossibles(self, pJeu, numJoueur):

        def peutConstruire(pRessources, pDicoVoulu):
            """
            Renvoie un couple contenant un booleen, une liste de dictionnaires, et un dictionnaire
            Le booleen indique si oui ou non il est possible de réunir les ressources de pDicoVoulu avec des echanges
            La liste est la liste des dictionnaires représentant pour chaque ressource le nombre d'échanges à réaliser en donnant cette ressource
            le dictionnaire associe a chaque ressource le nombre de cette ressource a recevoir.
            """
            l = ["bétail", "blé", "pierre", "brique", "bois"]
            dicoRessources = pRessources.copy()
            dicoEchangesPossibles = {
                ressource: 0 for ressource in dicoRessources}
            dicoRessourcesNecessaires = {
                ressource: 0 for ressource in dicoRessources}
            nbEchangeDispo = 0
            nbEchangeNecessaire = 0

            def lstEchanges(r, nbVoulu):
                """
                fonction récursive renvoyant la liste des echanges possibles pour avoir nbVoulu echanges
                r: int indice de la ressource qu'on est en train de traiter (entre 0 et 4 donc)
                nbVoulu: int nombre d'echanges qu'on veut faire
                retourne res, possible avec
                res: liste des echanges possible, liste de dictionnaires (vide si aucun echange satisfaisant)
                """
                if nbVoulu == 0:  # on n'a plus d'echange a faire, on a fini. (le == permet en outre de ne pas faire plus d'echange que necessaire)
                    return [{"bétail": 0, "blé": 0, "pierre": 0, "brique": 0, "bois": 0}]
                elif r >= 5 or nbVoulu < 0:  # il reste des echanges a placer, mais on arrive au bout des ressources
                    return []
                else:
                    ressouce = l[r]
                    res = []
                    # on regarde tous les cas possibles: si on fait 0 echange, 1 echange, ... jsuqu'au nb max d'echanges possibles avec cette ressource
                    for i in range(dicoEchangesPossibles[ressouce]+1):
                        lst = lstEchanges(r+1, nbVoulu-i)
                        for echange in lst:
                            echange[ressouce] = i
                            res.append(echange)
                    return res

            for ressource in l:  # on replie dicoEchangesPossibles et dicoRessourcesNecessaires
                if dicoRessources[ressource] >= pDicoVoulu[ressource]:
                    dicoRessources[ressource] -= pDicoVoulu[ressource]
                    dicoEchangesPossibles[ressource] = dicoRessources[ressource] // 4
                    nbEchangeDispo += dicoEchangesPossibles[ressource]
                else:
                    dicoRessourcesNecessaires[ressource] = pDicoVoulu[ressource] - \
                        dicoRessources[ressource]
                    nbEchangeNecessaire += dicoRessourcesNecessaires[ressource]

            if nbEchangeDispo < nbEchangeNecessaire:  # pas possible
                return False, [], {}
            elif nbEchangeNecessaire == nbEchangeDispo:  # une seule configuration d'echanges possible
                return True, [dicoEchangesPossibles], dicoRessourcesNecessaires
            else:  # plusieurs configurations d'echanges possibles
                return True, lstEchanges(0, nbEchangeNecessaire), dicoRessourcesNecessaires

        # Gros de la fonction
        lstActionsPossibles = [("passer", None, {}, {})]
        joueur = pJeu.dicoJoueurs[numJoueur]

        dico = {"bois": 1, "brique": 1, "bétail": 0, "blé": 0, "pierre": 0}
        possible, lstDonsEchange, dicoGainEchange = peutConstruire(
            joueur.ressources, dico)
        if possible:
            for coord in joueur.routesPossibles:
                if pJeu.plateau.estPlacementRoutePossible(coord[0], coord[1], numJoueur):
                    lstActionsPossibles += [("route", coord, don, dicoGainEchange)
                                            for don in lstDonsEchange]
                else:
                    joueur.routesPossibles.remove(coord)

        dico = {"bois": 1, "brique": 1, "bétail": 1, "blé": 1, "pierre": 0}
        possible, lstDonsEchange, dicoGainEchange = peutConstruire(
            joueur.ressources, dico)
        if possible:
            for coord in joueur.coloniesPossibles:
                if pJeu.plateau.estPlacementColoniePossible(coord[0], coord[1], numJoueur, False):
                    lstActionsPossibles += [("colonie", coord, don, dicoGainEchange)
                                            for don in lstDonsEchange]
                else:
                    joueur.coloniesPossibles.remove(coord)

        dico = {"bois": 0, "brique": 0, "bétail": 0, "blé": 2, "pierre": 3}
        possible, lstDonsEchange, dicoGainEchange = peutConstruire(
            joueur.ressources, dico)
        if possible:
            lstActionsPossibles += [("ville", coord, don, dicoGainEchange)
                                    for coord in joueur.villesPossibles for don in lstDonsEchange]

        return lstActionsPossibles

    def simulationAleatoire(self, pJeu):
        while pJeu.phase != "fini":
            pJeu.jeu()
        return pJeu.classement()[-1][0]

    def joue(self):
        print(self.ressources)
        actionChoisie, scoreMax = ["passer"], 0
        arbre_MCTS = Arbre(self.numJoueur, 1, None, None)
        L = self.LstActionsPossibles(self.jeuAuquelJeJoue, self.numJoueur)
        if len(L) >= 2:
            for g in range(self.nbGraines):
                seed = rd.getstate()  # La graine random
                print("newseed", g, actionChoisie, scoreMax)

                for m in range(self.nbSimulations):
                    # print("simulation n°", m )
                    rd.setstate(seed)

                    # selection
                    feuille, lstActions = self.selection(arbre_MCTS, 0, [])

                    # expension
                    nvJeu = self.jeuAuquelJeJoue.copie()
                    nvJeu.laisseJouerIA = False

                    self.descend_arbre(nvJeu, lstActions)
                    l = self.LstActionsPossibles(nvJeu, feuille.numJoueur)

                    # Proba a priori
                    poidsTotal = 0
                    poidsAction = {"colonie": 2,
                                   "ville": 2, "route": 1, "passer": 1}
                    for a in l:
                        poidsTotal += poidsAction[a[0]]

                    for a in l:
                        feuille.lstFils.append(
                            Arbre(3 - feuille.numJoueur, poidsAction[a[0]]/poidsTotal, a, feuille))

                    pChoisi = rd.randint(0, poidsTotal)
                    iChoisi = 0
                    while pChoisi - poidsAction[l[iChoisi][0]] > 0:
                        iChoisi += 1
                        pChoisi -= poidsAction[l[iChoisi][0]]

                    sommetChoisi = feuille.lstFils[iChoisi]

                    self.descend_arbre(nvJeu, [sommetChoisi.actionPrecedente])

                    # Simulation
                    nvJeu.laisseJouerIA = True
                    gagnant = self.simulationAleatoire(nvJeu)

                    # Backpropagation
                    self.backPropagation(sommetChoisi, gagnant, 0)

                for f in arbre_MCTS.lstFils:
                    if f.nbVisites > 0:
                        score = f.nbVictoires/f.nbVisites * \
                            (1-exp(-f.nbVisites/10))
                        if score > scoreMax:
                            actionChoisie, scoreMax = f.actionPrecedente, score

            actionChoisie, scoreMax = (
                "passer", None, {}, {}), scoreMax["passer"]

            self.joueAction(actionChoisie)
        self.jeuAuquelJeJoue.changementDeJoueur()


def Copie_aleatoire_joueur(joueur, pJeu):
    nouveauJoueur = IA_aleatoire(joueur.numJoueur, pJeu, {
                                 "route": 1, "colonie": 1, "ville": 1, "passer": 1})

    nouveauJoueur.routesPossibles = joueur.routesPossibles.copy()
    nouveauJoueur.coloniesPossibles = joueur.coloniesPossibles.copy()
    nouveauJoueur.villesPossibles = joueur.villesPossibles.copy()
    nouveauJoueur.nbRoutes = joueur.nbRoutes
    nouveauJoueur.nbColonies = joueur.nbColonies
    nouveauJoueur.ressources = joueur.ressources.copy()

    return nouveauJoueur


###################################
###         Boucle de jeu       ###
###################################

continuer = True


def Victoire(classement):
    global continuer
    continuer = False
    print("partie terminée. classement:", classement)


jeu = Jeu()
jeu.placementInitial()

continuer = True

# UPDATE
while continuer:
    jeu.jeu()
    if affichage:  # on fait pas l'affichage pendant la simulation, ca va plus vite
        # Affichage global
        IG_draw(jeu.plateau, background, font,
                jeu.dicoJoueurs[jeu.joueurActuel])
        screen.blit(background, (0, 0))
        pygame.display.flip()

    # KEYS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = 0
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            configuration, res = IG_clic(x, y)
            if configuration == "dans la grille":
                jeu.action(res[0], res[1])
            elif configuration == "echange":
                jeu.echange(res)
        elif event.type == pygame.KEYDOWN:
            if event.key == 13:  # entrée
                print(jeu.phase, jeu.joueurActuel)
                if jeu.phase == "jeu" and jeu.joueurActuel == 1:
                    jeu.changementDeJoueur()
