from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random

PLACEHOLDER_POS = (0, 0)

# Prey Agent. Moves Randomly.
class Prey(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = 100

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def eat(self):
        self.energy += 10

    def breed(self):
        if self.energy >= 200:
            self.energy -= 100
            new_prey = Prey(self.model.next_id(), self.model)
            self.model.grid.place_agent(new_prey, PLACEHOLDER_POS)
            self.model.grid.move_to_empty(new_prey)
            self.model.schedule.add(new_prey)

    def step(self):
        if self.pos is None:
            return
        self.move()
        self.breed()
        self.energy -= 1

# Predator Agent. Moves Randomly. Eats Prey.
class Predator(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = 100

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def eat(self):
        prey_neighbors = self.model.grid.get_cell_list_contents(
            [self.pos]
        )
        prey_agents = [
            agent for agent in prey_neighbors if isinstance(agent, Prey)]
        if prey_agents:
            prey_to_eat = random.choice(prey_agents)
            self.model.grid.remove_agent(prey_to_eat)
            self.model.schedule.remove(prey_to_eat)
            self.energy += 100

    def breed(self):
        if self.energy >= 200:
            self.energy -= 100
            new_predator = Predator(self.model.next_id(), self.model)
            self.model.grid.place_agent(new_predator, PLACEHOLDER_POS)
            self.model.grid.move_to_empty(new_predator)
            self.model.schedule.add(new_predator)

    def step(self):
        if self.pos is None:
            return
        self.move()
        self.eat()
        self.breed()
        self.energy -= 1

# Poacher Agent. Moves randomly. Kills predators.
class Poacher(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = 50

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def poach(self):
        if self.energy >= 5:
            predator_neighbors = self.model.grid.get_cell_list_contents(
                [self.pos]
            )
            predator_agents = [
                agent for agent in predator_neighbors if isinstance(agent, Predator)]
            if predator_agents:
                predator_to_poach = random.choice(predator_agents)
                self.model.grid.remove_agent(predator_to_poach)
                self.model.schedule.remove(predator_to_poach)
                self.energy -= 5

    def step(self):
        if self.pos is None:
            return
        self.move()
        self.poach()
        self.energy -= 1


class PreyPredatorModel(Model):
    def __init__(self, height, width, prey_count, predator_count, poacher_count):
        super().__init__()
        self.current_id = 0
        self.height = height
        self.width = width
        self.grid = MultiGrid(height, width, torus=True)
        self.schedule = RandomActivation(self)
        self.running = True

        for i in range(prey_count):
            prey = Prey(self.next_id(), self)
            self.grid.place_agent(prey, PLACEHOLDER_POS)
            self.grid.move_to_empty(prey)
            self.schedule.add(prey)

        for i in range(predator_count):
            predator = Predator(self.next_id(), self)
            self.grid.place_agent(predator, PLACEHOLDER_POS)
            self.grid.move_to_empty(predator)
            self.schedule.add(predator)

        for i in range(poacher_count):
            poacher = Poacher(self.next_id(), self)
            self.grid.place_agent(poacher, PLACEHOLDER_POS)
            self.grid.move_to_empty(poacher)
            self.schedule.add(poacher)

    def step(self):
        self.schedule.step()


def main():
    model = PreyPredatorModel(
        height=10, width=10, prey_count=20, predator_count=7, poacher_count=3)
    step_count = 100
    steps = 0

    while steps < step_count:
        model.step()
        prey_count = sum(isinstance(agent, Prey)
                         for agent in model.schedule.agents)
        predator_count = sum(isinstance(agent, Predator)
                             for agent in model.schedule.agents)
        poacher_count = sum(isinstance(agent, Poacher)
                            for agent in model.schedule.agents)
        print(
            f'Prey Count: {prey_count}, Predator Count: {predator_count}, Poacher Count: {poacher_count}')
        steps += 1


if __name__ == '__main__':
    main()
