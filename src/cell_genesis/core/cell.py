class Cell:
    def __init__(self, x=0, y=0, vx=0, vy=0, energy=100, radius=5):

        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.energy = energy
        self.radius = radius

        self.genes = {
            'speed': 1.0,
            'size': 1.0
        }

        self.metabolism_cost = 0.5

    def update(self):

        self.energy -= self.metabolism_cost

        self.x += self.vx * self.genes['speed']
        self.y += self.vy * self.genes['speed']

        self.radius = 5 * self.genes['size']

        return self.get_state()

    def get_state(self):

        return {
            'position': (self.x, self.y),
            'velocity': (self.vx, self.vy),
            'energy': self.energy,
            'radius': self.radius,
            'genes': self.genes.copy()
        }

    def set_velocity(self, vx, vy):

        self.vx = vx
        self.vy = vy

    def set_genes(self, speed=None, size=None):

        if speed is not None:
            self.genes['speed'] = speed
        if size is not None:
            self.genes['size'] = size

    def add_energy(self, amount):

        self.energy += amount

    def is_alive(self):

        return self.energy > 0