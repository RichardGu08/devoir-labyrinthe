# Hoang Quan Tran, 20249088
# Richard Gu, 20211389

# This script generates a labyrinth in OpensCAD using Kruskal's Algorithm or DFS Algorithm
# --------------------ATTENTION: REFERENCE --------------------
# Reference: ChatGPT with summarization and proofreading, and Maze for Programmers by Jamis Buck
import sys
import random

maze = []
maze_width = 13
maze_height = 13

cell_size = 10  # mm
wall_height = 10  # mm
wall_thickness = 1  # mm

strategy_choice = 1
output_file = f"labyrinth_{maze_width}x{maze_height}_"\
                f"size{cell_size}_height{wall_height}_thickness{wall_thickness}_"\
                f"algo{strategy_choice}_Quan.scad"


class Cell:
    def __init__(self):
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}


class KruskalCell(Cell):
    def __init__(self):
        super().__init__()
        self.parent = self
        self.rank = 0


class DFSCell(Cell):
    def __init__(self):
        super().__init__()
        self.visited = False


class Strategy:
    def __init__(self, width=maze_width, height=maze_height, CellType=Cell):
        self.cells = [[CellType() for _ in range(height)] for _ in range(width)]
        self.width = width
        self.height = height

    def Apply(self):
        pass

    @staticmethod
    def remove_wall(current, next_cell, direction):
        current.walls[direction] = False
        opposite_directions = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
        next_cell.walls[opposite_directions[direction]] = False


class Algorithm1(Strategy):
    # Kruskal's Algorithm
    def __init__(self):
        global maze_width, maze_height
        super().__init__(maze_width, maze_height, KruskalCell)

    def find(self, cell):
        if cell.parent != cell:
            cell.parent = self.find(cell.parent)
        return cell.parent

    def union(self, c1, c2):
        root1 = self.find(c1)
        root2 = self.find(c2)
        if root1 != root2:
            if root1.rank < root2.rank:
                root1.parent = root2
            elif root1.rank > root2.rank:
                root2.parent = root1
            else:
                root2.parent = root1
                root1.rank += 1

    def Apply(self):
        global maze
        edges = []

        for x in range(self.width):
            for y in range(self.height):
                if x > 0:
                    edges.append(((x, y), (x - 1, y), 'W'))
                if y > 0:
                    edges.append(((x, y), (x, y - 1), 'N'))

        random.shuffle(edges)

        for (x1, y1), (x2, y2), direction in edges:
            cell1 = self.cells[x1][y1]
            cell2 = self.cells[x2][y2]
            if self.find(cell1) != self.find(cell2):
                self.union(cell1, cell2)
                self.remove_wall(cell1, cell2, direction)

        maze = self.cells


class Algorithm2(Strategy):
    def __init__(self):
        global maze_width, maze_height
        super().__init__(maze_width, maze_height, DFSCell)

    @staticmethod
    def get_neighbors(x, y, cells):
        neighbors = []
        directions = ['N', 'S', 'E', 'W']
        dx = [0, 0, 1, -1]
        dy = [-1, 1, 0, 0]

        for i, direction in enumerate(directions):
            nx, ny = x + dx[i], y + dy[i]
            if 0 <= nx < len(cells) and 0 <= ny < len(cells[0]) and not cells[nx][ny].visited:
                neighbors.append((cells[nx][ny], direction, nx, ny))

        return neighbors

    def dfs(self, x=0, y=0):
        stack = [(x, y)]
        self.cells[x][y].visited = True

        while stack:
            x, y = stack[-1]
            neighbors = Algorithm2.get_neighbors(x, y, self.cells)

            if not neighbors:
                stack.pop()
                continue

            next_cell, direction, nx, ny = random.choice(neighbors)
            self.remove_wall(self.cells[x][y], next_cell, direction)
            next_cell.visited = True
            stack.append((nx, ny))

    def Apply(self):
        global maze
        # Start DFS from the upper-left cell
        self.dfs()
        maze = self.cells


class Generator:
    strategy = None

    def __init__(self):
        pass

    def SetStrategy(self, new_strategy):
        self.strategy = new_strategy

    def Generate(self):
        self.strategy.Apply()


class Creator:
    def __init__(self):
        pass

    @staticmethod
    def generate_cad_cell(cell, x_cell, y_cell):
        global cell_size, wall_thickness, wall_height

        def cube_code(x, y, z, rotate=False):
            cube = f"cube([{wall_thickness + wall_height}, {wall_thickness}, {wall_height}], center = true);\n"
            if rotate:
                cube = f"rotate([0, 0, 90]) {{\n{cube}}}\n"
            code = f"translate([{x}, {y}, {z}]) {{\n{cube}}}\n"
            return code

        x_coord, y_coord = x_cell * cell_size, y_cell * cell_size
        z = wall_height / 2

        cell_code = ""
        for direction, (dx, dy, rotate) in {
            'N': (0.5, 0, False), 'S': (0.5, 1, False),
            'E': (1, 0.5, True), 'W': (0, 0.5, True)
        }.items():
            if cell.walls[direction]:
                x = x_coord + dx * cell_size
                y = y_coord + dy * cell_size
                cell_code += cube_code(x, -y, z, rotate)

        return cell_code

    @staticmethod
    def generate_cad_baseplate():
        global cell_size, wall_thickness, wall_height, maze

        width = len(maze)
        height = len(maze[0])

        x, y = width * cell_size, height * cell_size
        offset = wall_thickness / 2
        baseplate = f"cube([{x}, {y}, {wall_thickness}], center = false);"
        return f"translate([{-offset}, {-(offset + y)}, 0]) {{\n{baseplate}\n}}\n"

    def PrintLabyrinth(self):
        global maze, maze_height, maze_width, cell_size, wall_height

        maze[0][0].walls['N'] = False
        maze[maze_width - 1][maze_height - 1].walls['S'] = False

        cad = ("difference(){\n"
               "union(){\n")
        cad += self.generate_cad_baseplate()

        for x in range(maze_width):
            for y in range(maze_height):
                cad += self.generate_cad_cell(maze[x][y], x, y)

        font_size = 7.0
        cad += (
            "}\n"
            f"translate([{maze_width * cell_size},-0.2,{(wall_height - font_size) / 2}]){{\n"
            "rotate([90,0,180]){{\n"
            f"linear_extrude(1) text(\"IFT2125 Quan-Richard\", size={font_size});}}\n"
            "}}\n"
            "}"
        )

        return cad


# main call
def main():
    global strategy_choice
    args = sys.argv[:]
    if len(args) >= 2:
        strategy_choice = int(args[1])

    # Generator
    my_generator = Generator()
    if strategy_choice == 1:
        my_generator.SetStrategy(Algorithm1())
    elif strategy_choice == 2:
        my_generator.SetStrategy(Algorithm2())
    else:
        print("error strategy choice")
    my_generator.Generate()

    # Creator
    my_creator = Creator()
    output = my_creator.PrintLabyrinth()

    with open(output_file, 'w') as f:
        f.write(output)


if __name__ == "__main__":
    main()
