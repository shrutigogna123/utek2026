import time

# Grid boundaries (width x height)
GRID_WIDTH = 10
GRID_HEIGHT = 10


# Global Clock
class Clock:
    def __init__(self):
        self.time_elapsed = 0      # seconds
        self.subscribers = []      # objects that update every tick

    def subscribe(self, obj):
        self.subscribers.append(obj)

    def start(self):
        while True:
            print(f"\n⏱️ Time: {self.time_elapsed}s")

            # Update all drones (or any subscriber)
            for obj in self.subscribers:
                obj.update()

            self.time_elapsed += 1
            time.sleep(1)          # 1 tick = 1 second


# Drone Class

class Drone:
    def __init__(self, name):
        self.name = name
        self.xposition = 0  
        self.yposition = 0         # coordinates
        self.battery = 100         # percentage
        self.command = None        # current move command: 'up', 'down', 'left', 'right'

    def set_command(self, direction):
        """Set next movement command. Use None to hold position."""
        if direction is None:
            self.command = None
            return
        d = str(direction).lower()
        if d in ("up", "down", "left", "right"):
            self.command = d
        else:
            # invalid commands are ignored
            self.command = None

    def update(self):
        # SIMPLE update rule: move according to self.command but stay inside grid
        dx = dy = 0
        if self.command == "up":
            dy = -1
        elif self.command == "down":
            dy = 1
        elif self.command == "left":
            dx = -1
        elif self.command == "right":
            dx = 1
        # compute candidate position
        new_x = self.xposition + dx
        new_y = self.yposition + dy
        # enforce grid bounds (0..WIDTH-1, 0..HEIGHT-1)
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            self.xposition = new_x
            self.yposition = new_y
        else:
            # out-of-bounds move ignored; keep position
            pass

        self.battery -= 0.5        # battery drains 0.5% per second

        print(f"   🚁 {self.name} → position=({self.xposition},{self.yposition}), battery={self.battery:.1f}%")


# -------------------------
# MAIN PROGRAM
# -------------------------
if __name__ == "__main__":
    clock = Clock()

    # Create drones
    d1 = Drone("Drone A")
    d2 = Drone("Drone B")

    # Subscribe drones to the clock
    clock.subscribe(d1)
    clock.subscribe(d2)

    # Start ticking
    clock.start()
