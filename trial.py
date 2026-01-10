import time
from collections import deque

GRID_WIDTH = 20
GRID_HEIGHT = 20

# Cell types
HALL       = "HALL"
HUB        = "HUB"
ICU        = "ICU"
ER         = "ER"
MATERNITY  = "MATERNITY"
OR         = "OR"
WAITING    = "WAITING"
ROOMS      = "ROOMS"


def build_floor_plan():
    """Return the hardcoded 20×20 hospital."""
    plan = [[HALL for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    # HUB: x 0..3, y 0..3
    for y in range(0, 4):
        for x in range(0, 4):
            plan[y][x] = HUB

    # WAITING: x 12..19, y 0..3
    for y in range(0, 4):
        for x in range(12, 20):
            plan[y][x] = WAITING

    # ICU: x 4..7, y 4..7
    for y in range(4, 8):
        for x in range(4, 8):
            plan[y][x] = ICU

    # ER: x 12..19, y 8..11
    for y in range(8, 12):
        for x in range(12, 20):
            plan[y][x] = ER

    # MATERNITY: x 0..7, y 12..15
    for y in range(12, 16):
        for x in range(0, 8):
            plan[y][x] = MATERNITY

    # OR: x 12..15, y 16..19
    for y in range(16, 20):
        for x in range(12, 16):
            plan[y][x] = OR

    # ROOMS: x 16..19, y 16..19
    for y in range(16, 20):
        for x in range(16, 20):
            plan[y][x] = ROOMS

    return plan


def pretty_print(plan):
    symbols = {
        HUB:"H", WAITING:"W", ICU:"I", ER:"E",
        MATERNITY:"M", OR:"O", ROOMS:"R", HALL:"."
    }
    for y in range(GRID_HEIGHT):
        print("".join(symbols[plan[y][x]] for x in range(GRID_WIDTH)))


# Region “centers”
REGION_CENTERS = {
    "HUB": (1, 1),
    "WAITING": (15, 1),
    "ICU": (5, 5),
    "ER": (15, 9),
    "MATERNITY": (3, 13),
    "OR": (13, 17),
    "ROOMS": (17, 17)
}

def is_walkable(cell, start_region, goal_region):
    """Only hallways + start room + destination room are walkable."""
    if cell == HALL: return True
    if cell == start_region: return True
    if cell == goal_region: return True
    return False


def bfs_shortest_path(grid, start, goal):
    (sx, sy) = start
    (gx, gy) = goal

    start_region = grid[sy][sx]
    goal_region  = grid[gy][gx]

    queue = deque([(start, [start])])
    visited = set([start])

    while queue:
        (x,y), path = queue.popleft()

        if (x,y) == goal:
            return path

        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                cell = grid[ny][nx]
                if not is_walkable(cell, start_region, goal_region):
                    continue
                if (nx,ny) not in visited:
                    visited.add((nx,ny))
                    queue.append(((nx,ny), path + [(nx,ny)]))

    return None

def print_live_board(floor, drones):
    """Print hospital grid with drones shown as '9'."""
    symbols = {
        HUB:"H", WAITING:"W", ICU:"I", ER:"E",
        MATERNITY:"M", OR:"O", ROOMS:"R", HALL:"."
    }
    board = [[symbols[floor[y][x]] for x in range(GRID_WIDTH)]
             for y in range(GRID_HEIGHT)]

    for drone in drones:
        x = drone.xposition
        y = drone.yposition
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            board[y][x] = "9"

    print("\n=== LIVE HOSPITAL GRID ===")
    for y in range(GRID_HEIGHT):
        print("".join(board[y]))


class Supply:
    def __init__(self, name, weight_kg):
        self.name = name
        self.weight = weight_kg
    def __repr__(self):
        return f"{self.name} ({self.weight} kg)"


def weight_to_multiplier(weight):
    if weight < 0.5: return 1.0
    elif weight < 2: return 1.2
    elif weight < 5: return 1.5
    elif weight < 15: return 2.0
    else: return None


class Drone:
    def __init__(self, name, home_x, home_y):
        self.name = name
        self.home_x = home_x
        self.home_y = home_y

        self.xposition = home_x
        self.yposition = home_y

        self.battery  = 100.0
        self.supply   = None
        self.multiplier = 1.0

        self.state = "idle"   # idle, outbound, returning
        self.path = None
        self.path_index = None
        self.current_region = None

    def at_hub(self):
        return self.xposition == self.home_x and self.yposition == self.home_y

    def load_supply(self, supply_obj):
        mult = weight_to_multiplier(supply_obj.weight)
        if mult is None:
            print(f" {self.name} cannot carry {supply_obj} (too heavy)")
            return False
        self.supply = supply_obj
        self.multiplier = mult
        print(f"✔️ {self.name} loaded {supply_obj} → drain x{mult}")
        return True

    def unload_supply(self):
        print(f" {self.name} delivered {self.supply} at {self.current_region}")
        self.supply = None

    def start_mission(self, region_name, path, supply):
        if self.state != "idle" or not self.at_hub():
            return False
        if not self.load_supply(supply):
            return False

        self.current_region = region_name
        self.path = path
        self.path_index = 0
        self.state = "outbound"

        print(f" {self.name} starting mission → {region_name}")
        return True

    def update(self):
        # Recharge at hub
        if self.state == "idle":
            if self.at_hub() and self.battery < 100:
                self.battery = min(100.0, self.battery + 0.5)
                print(f"   {self.name} recharging → {self.battery:.1f}%")
            else:
                print(f"   {self.name} idle")
            return

        if self.battery <= 0:
            print(f"   {self.name} is out of battery!")
            return

        if self.state == "outbound":
            if self.path_index >= len(self.path) - 1:
                # Arrived
                self.unload_supply()
                self.state = "returning"
                self.path_index = len(self.path) - 1
                self.multiplier = 1.0
                return

            next_x, next_y = self.path[self.path_index + 1]
            self.xposition, self.yposition = next_x, next_y
            self.path_index += 1

            self.battery -= 0.5 * self.multiplier
            print(f"   {self.name} OUTBOUND → ({next_x},{next_y}), "
                  f"battery={self.battery:.1f}%")
            return

        if self.state == "returning":
            if self.path_index == 0:
                # Reached hub
                self.state = "idle"
                self.path = None
                self.path_index = None
                print(f" {self.name} returned to HUB")
                return

            next_x, next_y = self.path[self.path_index - 1]
            self.xposition, self.yposition = next_x, next_y
            self.path_index -= 1

            self.battery -= 0.5
            print(f"   {self.name} RETURNING → ({next_x},{next_y}), "
                  f"battery={self.battery:.1f}%")
            return


class Task:
    def __init__(self, region_name, supply):
        self.region_name = region_name
        self.supply = supply
    def __repr__(self):
        return f"Task(to={self.region_name}, supply={self.supply})"


class Dispatcher:
    def __init__(self, floor, drones):
        self.floor = floor
        self.drones = drones
        self.tasks = []
        self.hub = REGION_CENTERS["HUB"]

    def add_task(self, task):
        print(f" New task added: {task}")
        self.tasks.append(task)

    def update(self):
        if not self.tasks:
            return

        remaining = []
        for task in self.tasks:
            if not self.try_assign(task):
                remaining.append(task)
        self.tasks = remaining

    def try_assign(self, task):
        region = task.region_name
        dest = REGION_CENTERS[region]

        path = bfs_shortest_path(self.floor, self.hub, dest)
        steps = len(path) - 1

        mult = weight_to_multiplier(task.supply.weight)
        outbound = steps * 0.5 * mult
        returning = steps * 0.5
        required = outbound + returning

        for d in self.drones:
            if d.state == "idle" and d.at_hub():
                if d.battery >= required:
                    print(f"{d.name} assigned to {task} (needs {required:.1f}%)")
                    d.start_mission(region, path, task.supply)
                    return True
                else:
                    print(f"{d.name} has {d.battery:.1f}% but needs {required:.1f}%")

        return False


class Clock:
    def __init__(self, floor, drones, dispatcher):
        self.floor = floor
        self.drones = drones
        self.dispatcher = dispatcher
        self.time_elapsed = 0

    def start(self):
        while True:
            print(f"\n Time: {self.time_elapsed}s")

            # LIVE GRID DISPLAY
            print_live_board(self.floor, self.drones)

            # Dispatcher assigns tasks
            self.dispatcher.update()

            # Update each drone
            for d in self.drones:
                d.update()

            self.time_elapsed += 1
            time.sleep(1)

if __name__ == "__main__":
    floor = build_floor_plan()

   
    print("=== HOSPITAL MAP ===")
    pretty_print(floor)

    hubx, huby = REGION_CENTERS["HUB"]
    d1 = Drone("Drone A", hubx, huby)
    d2 = Drone("Drone B", hubx, huby)

    drones = [d1, d2]

    dispatcher = Dispatcher(floor, drones)

   
    dispatcher.add_task(Task("ICU",       Supply("Blood Sample", 0.3)))
    dispatcher.add_task(Task("ER",        Supply("IV Pack", 1.2)))
    dispatcher.add_task(Task("MATERNITY", Supply("Incubator Part", 4.0)))
    dispatcher.add_task(Task("OR",        Supply("Surgical Kit", 3.0)))
    dispatcher.add_task(Task("ROOMS",     Supply("Medication Box", 1.0)))

    clock = Clock(floor, drones, dispatcher)
    clock.start()
