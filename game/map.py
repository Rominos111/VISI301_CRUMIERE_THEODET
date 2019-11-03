"""Terrain de jeu"""

import time
import random

if __name__ == "__main__":
    import sys
    sys.path.append("..")

from view.display import Display
from view.camera import Camera

from util.vector import Vect2d
from util.color import Color

from entity.cell import Cell
from entity.player import Player
from entity.enemy import Enemy
from entity.creature import Creature

import config

class Map:
    """Terrain de jeu

    Attributs:
        size
        all_cells
        DELTA_T_NEW_CELL
        ref_time
        MAX_CELLS
        NB_CELL_PER_SECOND
        grille_size
        grille
        player
        enemies
        ENEMIES_MAX_SIZE
    """

    @classmethod
    def init(cls, width: int, height: int) -> None:
        """Initialisation de la map

        Args:
            width (int): largeur de la map
            height (int): hauteur de la map
        """

        cls.size = Vect2d(width, height)
        cls.all_cells = []

        cls.DELTA_T_NEW_CELL = 0.2
        cls.ref_time = -1*cls.DELTA_T_NEW_CELL

        cls.MAX_CELLS = 100

        cls.NB_CELL_PER_SECOND = 2

        cls.grille_size = Vect2d(10, 10)

        cls.grille = [[[] for y in range(cls.grille_size.y)] for x in range(cls.grille_size.x)]

        cls.player = Player(Vect2d(cls.size.x/2, cls.size.y/2))
        # Création du joueur

        cls.enemies = []

        cls.ENEMIES_MAX_SIZE = 5

    @classmethod
    def createEnemy(cls):
        v = Vect2d(random.randrange(Creature.BASE_RADIUS*2, cls.size.x -Creature.BASE_RADIUS*2),
                   random.randrange(Creature.BASE_RADIUS*2, cls.size.y-Creature.BASE_RADIUS*2))

        cls.enemies.append(Enemy(v, "Ennemi "+str(len(cls.enemies)), Color.randomColor()))

    @classmethod
    def setMousePos(cls, mouse_pos: Vect2d):
        cls.player.mouse_pos = mouse_pos - Vect2d(Display.size.x/2, Display.size.y/2)

    @classmethod
    def update(cls):
        if len(cls.enemies) < cls.ENEMIES_MAX_SIZE:
            cls.createEnemy()

        cls.player.update(cls.size)

        enemies_info = []

        for i in range(len(cls.enemies)):
            v = cls.enemies[i].getMapPos(cls.size, cls.grille_size)

            enemies_info.append((cls.enemies[i].pos.copy(), cls.enemies[i].score))

        v = cls.player.getMapPos(cls.size, cls.grille_size)
        enemies_info.append((cls.player.pos.copy(), cls.player.score))

        for i in range(len(cls.enemies)):
            map_pos = cls.enemies[i].getMapPos(cls.size, cls.grille_size)
            cls.enemies[i].map = cls.getCenteredSubMap(map_pos)
            cls.enemies[i].creature_info = enemies_info
            cls.enemies[i].update(cls.size)

        creatures = cls.enemies + [cls.player]

        for i in range(len(creatures)):
            cls.detectCellHitbox(creatures[i])

        cls.detectEnemyHitbox(creatures)

        for i in range(len(cls.enemies)-1, -1, -1):
            if not cls.enemies[i].is_alive:
                del cls.enemies[i]

        if not cls.player.is_alive:
            print("dead")

        for i in range(cls.NB_CELL_PER_SECOND):
            cls.createNewCell()

    @classmethod
    def detectEnemyHitbox(cls, creatures):
        for i in range(len(creatures)):
            v = creatures[i].getMapPos(cls.size, cls.grille_size)

            for j in range(i+1, len(creatures)):
                if creatures[i].is_alive and creatures[j].is_alive:
                    if Vect2d.dist(creatures[i].pos, creatures[j].pos) <= creatures[i].radius + creatures[j].radius:
                        if creatures[i].score > creatures[j].score + Creature.BASE_SCORE:
                            creatures[i].score += creatures[j].score
                            creatures[j].is_alive = False
                        elif creatures[i].score + Creature.BASE_SCORE < creatures[j].score:
                            creatures[j].score += creatures[i].score
                            creatures[i].is_alive = False

    @classmethod
    def getCenteredSubMap(cls, map_pos):
        res = [[None for i in range(cls.grille_size.y)] for j in range(cls.grille_size.x)]

        for x in range(map_pos.x-cls.grille_size.x, map_pos.x+cls.grille_size.x+1):
            for y in range(map_pos.y-cls.grille_size.y, map_pos.y+cls.grille_size.y+1):
                if x >= 0 and x < cls.grille_size.x and y >= 0 and y < cls.grille_size.y:
                    content = []

                    for i in range(len(cls.grille[x][y])):
                        content.append(cls.grille[x][y][i].pos.copy())

                    res[x][y] = tuple(content)
        return res

    @classmethod
    def createNewCell(cls) -> None:
        if time.time() - cls.ref_time > cls.DELTA_T_NEW_CELL:
            cls.ref_time = time.time()

            x = random.randrange(0, cls.size.x)
            y = random.randrange(0, cls.size.y)
            cell = Cell(Vect2d(x, y))

            x = int(cell.pos.x / cls.size.x  * cls.grille_size.x )
            y = int(cell.pos.y / cls.size.y * cls.grille_size.y)

            cls.all_cells.append(cell)
            cls.grille[x][y].append(cell)

            if len(cls.all_cells) >= cls.MAX_CELLS:
                cls.deleteCell(0)

    @classmethod
    def display(cls):
        w = cls.size.x
        h = cls.size.y

        if config.DEBUG:
            for x in range(cls.grille_size.x):
                for y in range(cls.grille_size.y):
                    Display.drawText(len(cls.grille[x][y]),
                                     Vect2d((x+0.5)*cls.size.x/cls.grille_size.x, (y+0.5)*cls.size.y/cls.grille_size.y),
                                     base_pos=Camera.pos)

        for x in range(1, cls.grille_size.x):
            Display.drawLine(Vect2d(x*w/cls.grille_size.x, 0),
                             Vect2d(x*w/cls.grille_size.x, h),
                             color=Color.DARK_GRAY,
                             base_pos=Camera.pos)

        for y in range(1, cls.grille_size.y):
            Display.drawLine(Vect2d(0, y*h/cls.grille_size.y),
                             Vect2d(w, y*h/cls.grille_size.y),
                             color=Color.DARK_GRAY,
                             base_pos=Camera.pos)

        Display.drawLine(Vect2d(0, 0), Vect2d(w, 0), color=Color.RED, base_pos=Camera.pos)
        Display.drawLine(Vect2d(w, 0), Vect2d(w, h), color=Color.RED, base_pos=Camera.pos)
        Display.drawLine(Vect2d(w, h), Vect2d(0, h), color=Color.RED, base_pos=Camera.pos)
        Display.drawLine(Vect2d(0, h), Vect2d(0, 0), color=Color.RED, base_pos=Camera.pos)

        cls.displayCell()

        for i in range(len(cls.enemies)):
            cls.enemies[i].display()

        cls.player.display()

    @classmethod
    def displayCell(cls) -> None:
        for i in range(0,len(cls.all_cells)):
            cls.all_cells[i].display()

    @classmethod
    def detectCellHitbox(cls, creature:"Creature") -> None:
        """

        INPUT :

        OUTPUT :
            None
        """

        for i in range(len(cls.all_cells)-1, -1, -1):
            cell_i = cls.all_cells[i]

            if Vect2d.distSq(creature.pos, cell_i.pos) < (creature.radius+cell_i.radius)**2:
                creature.score += cell_i.score
                cls.deleteCell(i)

    @classmethod
    def deleteCell(cls, index:int):
        cell = cls.all_cells[index]

        x = int(cell.pos.x / cls.size.x  * cls.grille_size.x )
        y = int(cell.pos.y / cls.size.y * cls.grille_size.y)

        for i in range(len(cls.grille[x][y])-1, -1, -1):
            if cell == cls.grille[x][y][i]:
                del cls.grille[x][y][i]

        del cls.all_cells[index]
