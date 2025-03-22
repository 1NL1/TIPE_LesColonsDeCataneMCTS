"""
Gere l'interface graphique du programme
"""
import pygame
# dimensions du plateau
longueur = 11
largeur = 21

# positions des coins superieurs gauches et inferieurs droits de la grille
grid_pos = (0, 0, 800, 800)

# Taille (en pixels) d'une tuile
TILE_SIZE = min((grid_pos[3] - grid_pos[1])/longueur,
                (grid_pos[2] - grid_pos[0])/largeur)

# epaisseur des traits de la grille
GRID_LINE_SIZE = 2

# dictionnaire contenant les images representant les 6 types de tuile
img = {"pierre": pygame.image.load("images\imgpierre.jpg"),
       "brique": pygame.image.load("images\imgbrique.jpg"),
       "bois": pygame.image.load("images\imgbois.jpg"),
       "bétail": pygame.image.load("images\imgbétail.jpg"),
       "blé": pygame.image.load("images\imgblé.jpg"),
       "desert": pygame.image.load("images\imgdesert.jpg")
       }
for i, j in img.items():  # redimentionne les images
    img[i] = pygame.transform.scale(img[i], (TILE_SIZE, TILE_SIZE))

# boutons qui permettent aux joueur de faire des echanges
lstBoutonsEchange = []

# image de la plaquette des couts de construction
imgCouts = pygame.image.load("images\imgCoutsConstruction.jpg")
imgCouts = pygame.transform.scale(imgCouts, (5*TILE_SIZE, 5*TILE_SIZE))


# liste des couleurs attribuées a chaque joueur
lstCouleurs = [(255, 255, 255), (255, 0, 0),
               (0, 255, 0), (0, 0, 255), (0, 100, 100)]


def traceTrait(posDebut, posFin, background):
    """
    trace un trait (en fait un rectangle) entre les coordonnées posDebut et posFin sur le fond background
    posDebut, posFin : coordonnées (en pixels) sous la forme de couples d'entiers
    background: fond sur lequel dessiner
    """
    pygame.draw.rect(background, (255, 255, 255), pygame.Rect(
        posDebut[0], posDebut[1], posFin[0]-posDebut[0], posFin[1]-posDebut[1]), GRID_LINE_SIZE)


def drawGrid(background):
    """
    Dessine la geille representant le plateau de jeu
    background: fond sur lequel dessiner
    """
    # traits verticaux
    debutTrait = [grid_pos[0], grid_pos[1]]
    finTrait = [grid_pos[0]+GRID_LINE_SIZE, grid_pos[1]+longueur*TILE_SIZE]
    dx = TILE_SIZE
    for _ in range(largeur + 1):
        traceTrait(debutTrait, finTrait, background)
        debutTrait[0] += dx
        finTrait[0] += dx

    # traits horizontaux
    debutTrait = [grid_pos[0], grid_pos[1]]
    finTrait = [grid_pos[2], grid_pos[3] + GRID_LINE_SIZE]
    dy = TILE_SIZE
    for _ in range(longueur + 1):
        traceTrait(debutTrait, finTrait, background)
        debutTrait[1] += dy
        finTrait[1] += dy


def drawRessources(background, font, dicoRessources):
    """
    Dessine les boutons representant les ressources, et le nombre de chaque ressource possédé
    background: find sur lequel dessiner
    font: police d'ecriture pour les chiffres
    dicoRessources: dictionnaire qui a chaque ressource associe le nombre possédé
    """
    for i in lstBoutonsEchange:
        i.draw(background, font, dicoRessources[i.ressource])


def IG_init():
    """
    Fonction d'initialisation de l'interface graphique, crée les boutons pour les echanges
    """
    pos = [400, (longueur+1)*TILE_SIZE]
    for i in img:
        if i != "desert":
            lstBoutonsEchange.append(boutonRessourcesEchange(
                pos, (TILE_SIZE, TILE_SIZE), img[i], i))
            pos[0] += 50


def drawPlateau(plateau, background, font):
    """
    Dessine les elements du plateau de jeu
    plateau: plateau a dessiner (tableau contenant des None, des Tuiles, des Croisements et des Chemins)
    background: fond sur lequel dessiner
    font: police d'ecriture
    """
    for i in range(longueur):
        for j in range(largeur):
            pos = ((j+0.25)*TILE_SIZE, (i+0.25) *
                   TILE_SIZE)  # position de dessin
            case = plateau.plateau[i][j]
            if case:
                if case.type == "Croisement":
                    couleur = lstCouleurs[case.joueur]
                    char = font.render("x", 1, couleur)
                    if case.niveau == 2:
                        char = font.render("X", 1, couleur)
                    background.blit(char, pos)
                elif case.type == "Chemin":
                    couleur = lstCouleurs[case.route]
                    char = font.render("-", 1, couleur)
                    background.blit(char, pos)
                elif case.type == "Tuile":
                    couleur = (0, 0, 0)
                    background.blit(img[str(case.ressource)],
                                    (j*TILE_SIZE, i*TILE_SIZE))
                    char = font.render(str(case.num), 1, couleur)
                    background.blit(char, pos)
                    if case.voleur:
                        posVoleur = (pos[0]+TILE_SIZE*0.4, pos[1])
                        charVoleur = font.render("V", 1, (0, 0, 0))
                        background.blit(charVoleur, posVoleur)


def efface(background):
    """
    Fait le noir sur le fond
    background: fond à effacer
    """
    pygame.draw.rect(background, (0, 0, 0), pygame.Rect(grid_pos), 800)


def drawNumJoueur(background, font, num):
    """
    Trace le numéro du joueur dont c'est le tour
    background: fond sur lequel tracer
    font: police d'écriture
    num: numéro du joueur courant
    """
    char = font.render("Tour du joueur " + str(num), 1, lstCouleurs[num])
    pos = (TILE_SIZE, (longueur + 1)*TILE_SIZE)
    background.blit(char, pos)


class boutonRessourcesEchange:
    """
    Classe des boutons qui permettent d'échanger des ressources avec la banque
    """
    pos = (0, 0)
    dim = (0, 0)  # dimensions du bouton
    img = ''  # image du bouton
    selectionne = False  # si le bouton est pressé ou non
    ressource = ""  # ressource associée au bouton

    def __init__(self, pos, dim, img, ressource):
        """
        Initialisation d'un objet de la classe boutonRessourcesEchange
        pos: position du bouton
        dim: dimensions du bouton
        img: image du bouton
        ressource: ressource associée au bouton
        """
        self.pos = pos.copy()
        self.dim = dim
        self.img = img
        self.ressource = ressource

    def clic(self, x, y):
        """
        Verifie si le bouton est cliqué lors d'un clic souris, et renvoie la ressource associée au bouton si c'est le cas
        x,y : position du clic souris
        """
        if x >= self.pos[0] and x <= self.pos[0]+self.dim[0] and y >= self.pos[1] and y <= self.pos[1]+self.dim[1]:
            return self.ressource

    def draw(self, background, font, nb):
        """
        Trace le bouton et le nombre de ressources possédées par le joueur
        background: fond sur lequel tracer
        font: police d'écriture
        nb: nombre de ressources possédé par le joueur 
        """
        background.blit(self.img, self.pos)
        char = font.render(str(nb), 1, (255, 255, 255))
        posChar = [self.pos[0] + TILE_SIZE*0.3, self.pos[1]+TILE_SIZE*1.25]
        background.blit(char, posChar)


def drawCoutsConstruction(background):
    """
    Trace la fiche des couts de construction
    background: fond sur lequel tracer
    """
    pos = (TILE_SIZE, (longueur + 2)*TILE_SIZE)
    background.blit(imgCouts, pos)


def drawNbTour(background, font, nb):
    """
    Trace la fiche des couts de construction
    background: fond sur lequel tracer
    """
    pos = ((largeur-2)*TILE_SIZE, (longueur + 2)*TILE_SIZE)
    char = font.render(str(nb), 1, (255, 255, 255))
    background.blit(char, pos)


def IG_draw(plateau, background, font, joueur):
    """
    Dessine l'interface graphique
    plateau: le plateau de jeu
    background: fond sur lequel dessiner
    font: police d'écriture
    joueur: joueur en cours (objet joueur)
    """
    efface(background)
    drawGrid(background)
    drawPlateau(plateau, background, font)
    drawRessources(background, font, joueur.ressources)
    drawNumJoueur(background, font, joueur.numJoueur)
    drawCoutsConstruction(background)
    drawNbTour(background, font, plateau.nbTour)


def IG_clic(x, y):
    """
    Gere le clic d'un joueur et renvoie le domaine du jeu cliqué et un eventuel parametre nécessaire pour réagir au clic.
    x,y : position de la souris au moment du clic
    """
    lig = int(y//TILE_SIZE)
    col = int(x//TILE_SIZE)
    if lig >= 0 and lig < longueur and col >= 0 and col < largeur:
        return "dans la grille", (lig, col)
    else:
        for boutonEchange in lstBoutonsEchange:
            ressource = boutonEchange.clic(x, y)
            if ressource:
                return "echange", ressource
    return "dans le vide", None
