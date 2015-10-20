#RO_gue

import random

#########
#Classes#
#########

#The single entity class holds the hero, the enemies, and the environment
class entity_object(object):
	def __init__ (self, pos_x, pos_y, symbol, inventory, base_power, base_toughness, speed, color, entity_type, flying):
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.symbol = symbol
		self.inventory = inventory
		self.base_power = base_power
		self.base_toughness = base_toughness
		self.speed = speed
		self.turn = speed
		#Stored as a string
		self.color = color
		#'actor' (either the HERO or NPCs), 'item', or 'wall'
		self.entity_type = entity_type
		self.flying = flying
		self.damage = 0
	#Returns the entity's effective power
	def get_power(self):
		effective_power = int(self.base_power - (0.5 * self.damage))
		if effective_power >  0:
			return effective_power
		else:
			return 0
	#Returns the entity's effective toughness
	def get_toughness(self):
		effective_toughness = int(self.base_toughness - (1.0 * self.damage))
		if effective_toughness >  0:
			return effective_toughness
		else:
			return 0

#Entity_object type for items
class item_object(entity_object):
	def __init__(self, pos_x, pos_y, symbol):
		entity_object.__init__(self, pos_x, pos_y, symbol, None, None, None, None, 'blink', 'item', None)
		self.name = 'goblin'
		self.symbol = symbol

#Entity_object type for walls
class wall_object(entity_object):
	def __init__(self, pos_x, pos_y):
		entity_object.__init__(self, pos_x, pos_y, '#', None, None, None, None, 'black', 'wall', None)
		self.name = 'goblin'

#Entity_object tpye for chests
#Treated as an actor so that they can be 'killed' and drop their items, speed is -1 so that they never have a turn
class chest(entity_object):
	def __init__(self, pos_x, pos_y, inventory):
		entity_object.__init__(self, pos_x, pos_y, '=', inventory, 0, 1, -1, 'grey', 'actor', False)
		self.name = 'chest'

#Different enemy types follow
class bat(entity_object):
	def __init__(self, pos_x, pos_y, inventory):
		entity_object.__init__(self, pos_x, pos_y, 'b', inventory, 1, 5, 5, 'red', 'actor', True)
		self.name = 'bat'

class goblin(entity_object):
	def __init__(self, pos_x, pos_y, inventory):
		entity_object.__init__(self, pos_x, pos_y, 'g', inventory, 2, 10, 10, 'red', 'actor', False)
		self.name = 'goblin'

class kobold(entity_object):
	def __init__(self, pos_x, pos_y, inventory):
		entity_object.__init__(self, pos_x, pos_y, 'k', inventory, 5, 25, 20, 'red', 'actor', False)
		self.name = 'kobold'

class slime(entity_object):
	def __init__(self, pos_x, pos_y, inventory):
		entity_object.__init__(self, pos_x, pos_y, 's', inventory, 1, 100, 30, 'red', 'actor', False)
		self.name = 'slime'

class dragon(entity_object):
	def __init__(self, pos_x, pos_y, inventory):
		entity_object.__init__(self, pos_x, pos_y, 'd', inventory, 10, 100, 15, 'red', 'actor', True)
		self.name = 'slime'

###########
#Functions#
###########

#Returns a string surrounded by the appropriate color tags
#arg1 is the string, arg2 is the color
def color(arg1,arg2):
	return colors[arg2] + arg1 + colors['black']

#Renders the current game state
def render():
	#Generates an empty list of view_range * view_range
	render_world = list(list(color('+','white') for x in range(view_range * 2 + 1)) for y in range(view_range * 2 + 1))
	#Loops through the entity list
	for entity in entities:
		#Checks to make sure that the entity is within view range of the HERO
		if abs(HERO.pos_x - entity.pos_x) <= view_range and abs(HERO.pos_y - entity.pos_y) <= view_range:
			#Places the entity in the correct spot in render_world
			render_world[HERO.pos_y + view_range - entity.pos_y][(view_range * 2) - (HERO.pos_x + view_range - entity.pos_x)] = color(entity.symbol,entity.color)
	#Clears the terminal
	print ('\x1b[2J\x1b[H')
	#Prints render_world with a border around it
	print (color('+ ','grey') * (view_range * 2 + 3))
	for row in render_world:
		print (color('+ ','grey') + ' '.join(row) + color(' +','grey'))
	print (color('+ ','grey') * (view_range * 2 + 3))
	#Displays the HERO's current status
	print ('')
	print ('Location  : [%s,%s]' %(str(HERO.pos_x), str(HERO.pos_y)))
	print ('Inventory : [%s]'    %(' '.join(HERO.inventory)))
	print ('Power     : [%s%s]'  %('+' * HERO.get_power(), '_' * (HERO.base_power - HERO.get_power())))
	print ('Toughness : [%s%s]'  %('+' * HERO.get_toughness(), '_' * (HERO.base_toughness - HERO.get_toughness())))

#Moves the hero based on user input
def HERO_move():
	global alive
	#Takes and stores the player's keyboard input
	user_input = input('\n' + color('INPUT','blink') + '\n')
	#If the input isn't correct, the player is prompted for input
	while user_input not in ('w','a','s','d'):
		if user_input in input_table:
			HERO_action(user_input)
			break
		else:	
			render()
			user_input = input('\nw,a,s,d to move; item names to use items;\nspace to wait; quit to end the game\n')
	#If the user input is w,a,s,d and there is no collision then the HERO is moved
	if user_input in ('w','a','s','d'):
		check_collision(HERO,input_table[user_input])
	#Takes the 'quit' user input and ends the game
	if user_input == 'quit':
		alive = False

#Controls hero actions besides movement
def HERO_action(arg):
	#Use potion
	if arg == 'p' and 'p' in HERO.inventory:
		HERO.damage = 0
		HERO.inventory.remove('p')
	#Use rock (it calls the throw function)
	if arg == 'r' and 'r' in HERO.inventory:
		direction_input = None
		while direction_input not in ('w','a','s','d'):
			render()
			direction_input = input('\n' + color('DIRECTION','blink') + '\n')
		throw(HERO,'r',direction_input)
		HERO.inventory.remove('r')
	if arg == '!' and '!' in HERO.inventory:
		HERO.speed = 1
		HERO.base_power += 10
		HERO.base_toughness += 10
		HERO.flying = True
		HERO.color = 'blink'
		HERO.inventory.remove('!')

#Controls the throwing action for actors
def throw(arg1, arg2, arg3):
	#A table that holds throwing directions
	throw_table = {
	'w' : [arg1.pos_x, arg1.pos_y + view_range],
	'a' : [arg1.pos_x - view_range, arg1.pos_y],
	's' : [arg1.pos_x, arg1.pos_y - view_range],
	'd' : [arg1.pos_x + view_range, arg1.pos_y],
	}
	#For each entity:
	for entity in entities:
		#Removes the input entity from the loop, i.e. stop hitting yourself
		#Also makes sure to only check 'actor' entities, I had problems with crashing when rocks tried to take damage ;_;
		if entity != arg1 and entity.entity_type == 'actor':
			#Checks to see whether the entity lies between the start and end of the rock's path
			#Currently kind of messy because range only accepts the smaller value before the larger value
			if entity.pos_x in range(sorted([arg1.pos_x,throw_table[arg3][0]])[0], sorted([arg1.pos_x,throw_table[arg3][0]])[1] + 1) and entity.pos_y in range(sorted([arg1.pos_y,throw_table[arg3][1]])[0], sorted([arg1.pos_y,throw_table[arg3][1]])[1] + 1):
				#Does damage based on the throw_damage variable and then checks for entity death
				entity.damage += random.randrange(throw_damage[0],throw_damage[1])
				check_death(entity)
	#Puts the thrown item as an entity on the ground where it landed, thrown items currently penetrate multiple enemies
	#The thrown item has a 30% chance of breaking
	if random.randrange(0,3) != 0:
		entities.append(item_object(throw_table[arg3][0],throw_table[arg3][1],arg2))

#Defines AI movement
def AI_move(arg):
	#Only moves entities that the are within the render range
	if abs(HERO.pos_x - arg.pos_x) <= view_range and abs(HERO.pos_y - arg.pos_y) <= view_range:
		#If the difference in x distance between the entity and the HERO is greater, the entity moves towards the HERO in the x direction
		if abs(HERO.pos_x - arg.pos_x) >  abs(HERO.pos_y - arg.pos_y):
			if HERO.pos_x > arg.pos_x:
				check_collision(arg,[ 1, 0])
			if HERO.pos_x < arg.pos_x:
				check_collision(arg,[-1, 0])
		#If the difference in y distance between the entity and the HERO is greater, the entity moves towards the HERO in the y direction
		if abs(HERO.pos_y - arg.pos_y) >  abs(HERO.pos_x - arg.pos_x):
			if HERO.pos_y > arg.pos_y:
				check_collision(arg,[ 0, 1])
			if HERO.pos_y < arg.pos_y:
				check_collision(arg,[ 0,-1])
		#If the x and y distance to the HERO is the same, the entity randomly advances in either the x or y direction
		if abs(HERO.pos_x - arg.pos_x) == abs(HERO.pos_y - arg.pos_y):
			random_move = random.randrange(0,1)
			if random_move == 0:
				if HERO.pos_x > arg.pos_x:
					check_collision(arg,[ 1, 0])
				if HERO.pos_x < arg.pos_x:
					check_collision(arg,[-1, 0])
			if random_move == 1:
				if HERO.pos_y > arg.pos_y:
					check_collision(arg,[ 0, 1])
				if HERO.pos_y < arg.pos_y:
					check_collision(arg,[ 0,-1])

#Takes an entity and a list [x,y] for coordinates as arguments
def check_collision(arg1,arg2):
	collisions_actor = False
	collisions_wall = False
	#Checks the intended destination against all other entity locations
	for entity in entities:
		#If the intended destination is a match for any other entity, 
		if arg1.pos_x+arg2[0] == entity.pos_x and arg1.pos_y+arg2[1] == entity.pos_y:
			#If the checked entity is an item, it's added to the moving entity's inventory and removed from the entity list
			if entity.entity_type == 'item':
				arg1.inventory.append(entity.symbol)
				entities.remove(entity)
			#If the checked entity is not an item, the moving entity deals daamage to it equal to its get_power
			if entity.entity_type == 'actor':
				collisions_actor = True
				entity.damage += arg1.get_power()
				check_death(entity)
			if entity.entity_type == 'wall':
				collisions_wall = True
	#An object will move if it isn't colliding with an actor AND either it isn't colliding witha  wall or it is flying
	if collisions_actor == False and (collisions_wall == False or arg1.flying == True):
		arg1.pos_x += arg2[0]
		arg1.pos_y += arg2[1]

#Checks to see if an entity is dead, if so then it drops its inventory
def check_death(arg):
	#Check to see if its get_toughness is 0 or less
	if arg.get_toughness() <= 0:
		#Drops all items from its inventory on the ground
		for inventory_item in arg.inventory:
			entities.append(item_object(arg.pos_x,arg.pos_y,inventory_item))
		#Removes the entity from the entities list
		entities.remove(arg)

###########
#Variables#
###########

#The variable that records whether the player is alive or not
alive = True

#The radius around the HERO that will be rendered by the render function
view_range = 5

#List of colors to be referenced by the color function
colors = {
	'black'  :'\033[00m',
	'grey'   :'\033[90m',
	'white'  :'\033[97m',
	'blink'  :'\033[05m',
	'red'    :'\033[91m',
	}

#Holds all possible player input and converts player input into change in HERO coordinates
input_table = {
	'w'    : [ 0, 1],
	'a'    : [-1, 0],
	's'    : [ 0,-1],
	'd'    : [ 1, 0],
	' '    : 'wait',
	'p'    : 'potion',
	'r'    : 'r',
	'quit' : 'quit',
	'!'    : 'god_mode',
	}

#The upper and lower damage limits for rocks
throw_damage = [5,11]

#Establishes the HERO entity, the player character
#(pos_x,pos_y,symbol,inventory,base_power,base_toughness,speed,color,entity_type)
HERO = entity_object(0,0,'@',['p','r','!'],10,10,10,'black','actor', False)

#Establishes a list of entities to be looped through
entities = [HERO]

#World generation 
#World Size
world_size = 25

#Builds a box that surrounds the world
for value in range(-world_size,world_size + 1):
	entities.append(wall_object(value, world_size))
	entities.append(wall_object(value,-world_size))
	entities.append(wall_object( world_size,value))
	entities.append(wall_object(-world_size,value))

num_random_walls = 100
for random_wall in range(num_random_walls):
	random_orientation = random.randrange(2)
	random_length = random.randrange(1,10)
	if random_orientation == 0:
		random_location = [random.randrange(-world_size,world_size-random_length),random.randrange(-world_size,world_size)]
		for value in range(random_length):
			entities.append(wall_object(random_location[0] + value,random_location[1]))
	if random_orientation == 1:
		random_location = [random.randrange(-world_size,world_size),random.randrange(-world_size,world_size-random_length)]
		for value in range(random_length):
			entities.append(wall_object(random_location[0],random_location[1] + value))

#Populates the world with entities
for value in range(15):
	entity_position = [random.randrange(-world_size+1,world_size-1),random.randrange(-world_size+1,world_size-1)]
	entities.append(bat(entity_position[0], entity_position[1],list('r' for x in range(random.randrange(2)))))
for value in range(10):
	entity_position = [random.randrange(-world_size+1,world_size-1),random.randrange(-world_size+1,world_size-1)]
	entities.append(goblin(entity_position[0], entity_position[1],list('r' for x in range(random.randrange(2)))))
for value in range(10):
	entity_position = [random.randrange(-world_size+1,world_size-1),random.randrange(-world_size+1,world_size-1)]
	entities.append(kobold(entity_position[0], entity_position[1],list('r' for x in range(random.randrange(2)))))
for value in range(5):
	entity_position = [random.randrange(-world_size+1,world_size-1),random.randrange(-world_size+1,world_size-1)]
	entities.append(slime(entity_position[0], entity_position[1],list('r' for x in range(random.randrange(2)))))
for value in range(5):
	entity_position = [random.randrange(-world_size+1,world_size-1),random.randrange(-world_size+1,world_size-1)]
	entities.append(chest(entity_position[0], entity_position[1],list('p' for x in range(random.randrange(1,3)))))
for value in range(1):
	entity_position = [random.randrange(-world_size+1,world_size-1),random.randrange(-world_size+1,world_size-1)]
	entities.append(dragon(entity_position[0], entity_position[1],['!']))


################
#Main Game Loop#
################

#Clears the terminal window
print ('\x1b[2J\x1b[H')

#A loop that holds all of the main game functions
while alive == True:
	#Loops through the entity list
	for entity in entities:
		#Only iterates through entities that are 'actors', i.e. NPCs
		if entity.entity_type == 'actor':
			#Advances each enemy forward by one turn
			entity.turn -= 1
			#If the enemy's turn counter is at 0, it does stuff!
			if entity.turn == 0:
				#First the entity's turn counter is reset
				entity.turn = entity.speed
				#If the entity is the HERO, it does stuff
				if entity == HERO:
					#Renders the current game state
					render()
					#Requests user input and tries to execute it
					HERO_move()
				#Otherwise if the entity isn't the HERO, it does other stuff
				if entity != HERO:
					#Removes the entity from the entity list if its net toughness <= 0
					check_death(entity)
					#Calls the AI to move the entity
					AI_move(entity)
					#Removes the entity from the entity list if its net toughness <= 0
					check_death(entity)
	#At the end of every loop, checks to see whether the HERO is dead
	if HERO.get_toughness() <= 0:
		alive = False

render()
print ('\n')
print ('Congratulations, you lost!')