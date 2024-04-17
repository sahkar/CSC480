from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random
import streamlit as st
import numpy as np
import time


# PyPi dependencies: 
#     pip install streamlit
#     pip instlal numpy (if needed)
# bash command to run: streamlit run lab2-visualization.py


PLACEHOLDER_POS = (0,0)
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
        prey_agents = [agent for agent in prey_neighbors if isinstance(agent, Prey)]
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
            predator_agents = [agent for agent in predator_neighbors if isinstance(agent, Predator)]
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

# Converts the grid into a 2D numpy array with emojis representing the agents. 
def visualize_grid(grid, height, width):
    arr = np.empty((height, width), dtype=np.object_)
    for i in range(1, height + 1):
        for j in range(1, width + 1):
            try:
                if isinstance(grid[i, j][0], Prey):
                    arr[height - i, width - j] = '🐄'
                elif isinstance(grid[i, j][0], Predator):
                    arr[height - i, width - j] = '🐅'
                elif isinstance(grid[i, j][0], Poacher):
                    arr[height - i, width - j] = '🔫'
            except IndexError:
                arr[height - i, width - j] = ''
    return arr


def main():
    st.set_page_config(page_title='Lab 2')
    st.title('Lab 2: Multi Agent Systems')
    st.subheader('Sahith Karra')
    # uses a form + number_input to retrieve model params from the user
    with st.form('Input Parameters'):
        cols = st.columns(4)
        height = cols[0].number_input('Height', min_value=0, max_value=25, value=5)
        width = cols[1].number_input('Width', min_value=0, max_value=25, value=5)
        prey = cols[2].number_input('Prey', min_value=0, max_value=(height * width), value=10)
        predators = cols[3].number_input('Predators', min_value=0, max_value=(height * width ), value=2)
        poachers = cols[0].number_input('Poachers', min_value=0, max_value=(height * width), value=1)
        step_count = cols[1].number_input('Steps', min_value=0, value=10) 
        step_time = cols[2].number_input('Step time', min_value=0.0, max_value=10.0, value=0.5, step=0.5)

        submit = st.form_submit_button('Submit')

    # Check if form has been submitted
    if submit:
        # Create the model
        model = PreyPredatorModel(height=height, width=width, prey_count=prey, predator_count=predators, poacher_count=poachers)
        # Dispaly the model grid as a dataframe
        agent_grid = st.dataframe(visualize_grid(model.grid, height, width))
        
        # Display the counts as a dataframe
        counts = st.dataframe({'Step': 0, 'Prey Count': prey, 'Predators Count': predators, 'Poacher Count': poachers})

        # Step through the model `step_count` times
        steps = 0
        while steps < step_count:
            time.sleep(step_time)
            model.step()
            # Update the agent_grid dataframe
            agent_grid.dataframe(visualize_grid(model.grid, model.height, model.width))

            # Calculate the counts
            prey_count=sum(isinstance(agent, Prey) for agent in model.schedule.agents)
            predator_count = sum(isinstance(agent, Predator) for agent in model.schedule.agents)
            poacher_count = sum(isinstance(agent, Poacher) for agent in model.schedule.agents)

            # Update the counts dataframe 
            counts.dataframe({'Step': steps, 'Prey Count': prey_count, 'Predator Count': predator_count, 'Poacher': poacher_count})
            
            # Increment the step counter
            steps += 1

if __name__ == '__main__':
    main() 