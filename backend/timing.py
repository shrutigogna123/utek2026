import time

# Grid boundaries
GRID_WIDTH = 20
GRID_HEIGHT = 20


# -------------------------
# Supply Class
# -------------------------
class Supply:
    def __init__(self, name, weight_kg):
        self.name = name
        self.weight = weight_kg

    def __repr__(self):
        return f"{self.name} ({self.weight} kg)"


# -------------------------
# Weight → battery multiplier
# -------------------------
def weight_to_multiplier(weight):
    if weight < 0.5:
        return 1.0
    elif weight < 2:
        return 1.2
    elif weight < 5:
        return 1.5
    elif weight < 15:
        return 2.0
    else:
        return None  # too heavy


# -------------------------
# Clock Class
# -------------------------
class Clock:
    def __init__(self):
        self.time_elapsed = 0
        self.subscribers = []

    def subscribe(self, obj):
        self.subscribers.append(obj)

    def start(self):
        while True:
            print(f"\n⏱️ Time: {self.time_elapsed}s", flush=True)
            for obj in self.subscribers:
                obj.update()
            self.time_elapsed += 1
            time.sleep(1)


# -------------------------
# Drone Class
# -------------------------
class Drone:
    def __init__(self, name):
        self.name = name
        self.xposition = 0
        self.yposition = 0
        self.battery = 100
        self.command = None
        self.supply = None
        self.multiplier = 1.0
        self.xdestination = None
        self.ydestination = None

    def set_destination(self, x, y):
        """Set dynamic destination from user."""
        self.xdestination = x
        self.ydestination = y
        print(f"📍 {self.name} destination set to ({x}, {y})")

    def load_supply(self, supply_obj):
        """Give the drone a Supply object with weight."""
        mult = weight_to_multiplier(supply_obj.weight)

        if mult is None:
            print(f"❌ {self.name} cannot carry {supply_obj} — too heavy!")
            return False

        self.supply = supply_obj
        self.multiplier = mult
        print(f"✔️ {self.name} loaded {supply_obj} → drain x{mult}")
        return True

    def unload_supply(self):
        print(f"📦 {self.name} delivered {self.supply}")
        self.supply = None
        self.multiplier = 1.0

    def set_command(self, direction):
        if isinstance(direction, int):
            mapping = {1:"up", 2:"down", 3:"left", 4:"right"}
            direction = mapping.get(direction)

        if direction is None:
            self.command = None
            return

        d = direction.lower()
        if d in ("up","down","left","right"):
            self.command = d
        else:
            self.command = None

    def update(self):
        dx = dy = 0

        if self.command == "up": dy = -1
        elif self.command == "down": dy = 1
        elif self.command == "left": dx = -1
        elif self.command == "right": dx = 1
        else:
            print(f"   {self.name} → ({self.xposition},{self.yposition}), idle, battery={self.battery:.1f}%")
            return

        # Compute new position
        new_x = self.xposition + dx
        new_y = self.yposition + dy

        # Inside grid?
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            self.xposition = new_x
            self.yposition = new_y
            self.battery -= 0.5 * self.multiplier

        # Check if destination reached
        if (
            self.xdestination is not None and
            self.ydestination is not None and
            self.xposition == self.xdestination and
            self.yposition == self.ydestination
        ):
            self.unload_supply()

        print(f"   {self.name} → ({self.xposition},{self.yposition}), "
              f"battery={self.battery:.1f}%, carrying={self.supply}")


# -------------------------
# MAIN PROGRAM
# -------------------------
if __name__ == "__main__":
    clock = Clock()

    d1 = Drone("Drone A")
    d2 = Drone("Drone B")

    # Dynamic supplies
    s1 = Supply("Blood Sample", 0.3)
    s2 = Supply("IV Pack", 1.2)

    d1.load_supply(s1)
    d2.load_supply(s2)

    # Dynamic destinations (user-defined)
    d1.set_destination(10, 0)
    d2.set_destination(0, 10)

    # Movement
    d1.set_command("right")
    d2.set_command("down")

    clock.subscribe(d1)
    clock.subscribe(d2)

    clock.start()
