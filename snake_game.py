from turtle import Turtle, Screen
from functools import partial
from random import randint
import time


# Global Variables (starts with g_)
g_screen = None
g_snake = None
g_snake_length = 6
g_snake_body_pos = []  # snake's body positions
g_head_size = 0
g_monster = None
g_paused = False
g_last_pressed_key = None
g_numbers = {}
g_contacted_count = 0
g_time_started = None
g_intro = None

# All Global constants
KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT, KEY_SPACE = (
    "Up", "Down", "Right", "Left", "space")
heading_key = {KEY_UP: 90, KEY_DOWN: 270, KEY_RIGHT: 0, KEY_LEFT: 180}
heading_degree = {0: 0, 1: 90, 2: 90, 3: 180, 4: 180, 5: 270, 6: 270, 7: 0}
game_dimension = 500
snake_speed = 200
monster_speed = 300


def configure_turtle(shape="square", hide=None, color="black", x=0, y=0):
    turtle = Turtle(shape)
    turtle.color(color)
    turtle.penup()
    if hide:
        turtle.hideturtle()
    turtle.setposition(x, y)
    return turtle


def create_snake():
    return configure_turtle(color="red", x=0, y=0)


def create_monster():
    x, y = randint(-220, -150), randint(-220, 220)
    return configure_turtle(color="purple", x=x, y=y)


def configure_numbers():
    for i in range(1, 10):
        x, y = randint(-220, 220), randint(-220, 220)
        turtle = configure_turtle(x=x, y=y, hide=True)
        turtle.write(str(i), False, "center")
        g_numbers[turtle.pos()] = i


def configure_intro():
    intro = configure_turtle(x=-150, y=100, hide=True)
    intro.write("Welcome to Bernaldy's snake game! \n" +
                "Use the 4 arrow keys (Up, down, left, right)\n" + "to move the snake \n" +
                "Use the spacebar to pause \n" +
                "Consume all of the food items by touching them \n" +
                "Don't let the monster catch you \n" +
                "Click anywhere to start the game.",
                font="calibri 10 bold")
    return intro


def key_pressed(key):
    global g_last_pressed_key, g_paused
    if key == KEY_SPACE:
        if g_paused == False:
            g_paused = True
            print('Game is Paused')
        elif g_paused == True:
            g_paused = False
    else:
        g_last_pressed_key = key
        print('key_pressed', key)


def configure_screen():
    screen = Screen()
    screen.tracer(0)
    screen.title("Snake Game by Bernaldy")
    screen.setup(game_dimension, game_dimension)
    screen.mode('standard')
    screen.onkey(partial(key_pressed, KEY_UP), KEY_UP)
    screen.onkey(partial(key_pressed, KEY_DOWN), KEY_DOWN)
    screen.onkey(partial(key_pressed, KEY_LEFT), KEY_LEFT)
    screen.onkey(partial(key_pressed, KEY_RIGHT), KEY_RIGHT)
    screen.onkey(partial(key_pressed, KEY_SPACE), KEY_SPACE)
    return screen


def calculate_body_size(snake):
    snake_poly = snake.get_shapepoly()
    size = abs(snake_poly[0][1] - snake_poly[1][1])
    return size


def is_collided(t1, t2):
    if type(t1) is Turtle:
        dist = t1.distance(t2)
        return dist <= g_head_size
    return False


def move_snake(move):
    if g_paused or g_last_pressed_key is None or \
            is_valid_move(move) == False:
        return

    # Create the body
    g_snake.color("blue", "black")
    g_snake.stamp()
    g_snake_body_pos.insert(0, g_snake.position())

    # set the movement direction according to the key pressed
    g_snake.setheading(heading_key[move])
    g_snake.forward(g_head_size)
    g_snake.color("red")

    # Extending snake tail
    if len(g_snake.stampItems) >= g_snake_length:
        g_snake.clearstamps(1)
        g_snake_body_pos.pop()

    g_screen.update()


def is_valid_move(move):
    x, y = g_snake.pos()
    bound = (game_dimension - g_head_size)/2 - 1
    print("is_valid_move()", x, y, bound)
    if move == KEY_UP:
        return y < bound
    elif move == KEY_DOWN:
        return y > -bound
    elif move == KEY_RIGHT:
        return x < bound
    elif move == KEY_LEFT:
        return x > -bound


def update_snake():

    global g_snake_length, g_contacted_count

    if is_collided(g_snake, g_monster):
        return

    print("update_snake", len(g_numbers.keys()))

    move_snake(g_last_pressed_key)

    # Check if snake consumes an item
    for number in g_screen.turtles():
        pos = number.position()
        if pos in g_numbers:
            if is_collided(g_snake, number):
                number.clear()  # clear the text string
                g_snake_length += g_numbers[pos]
                g_numbers.pop(pos)
                break

    update_game("snake")


def win_condition():
    return len(g_snake.stampItems) == (g_snake_length-1) and len(g_numbers.keys()) == 0


def update_game(type="monster"):

    # Update the status
    title = "Snake: Contacted: {}, Time: {}".format(
        g_contacted_count, int(time.time() - g_time_started))
    g_screen.title(title)
    g_screen.update()

    if is_collided(g_snake, g_monster):
        game_over = configure_turtle(x=-65, y=20, hide=True)
        game_over.write("Game over!", font="Calibri 20 bold")
        return

    # Winner: Snake is fully extended after eating all of the numbers
    if win_condition():
        win = configure_turtle(x=-50, y=20, hide=True)
        win.write("Winner!", font="calibri 20 bold")
        return

    if type == "snake":
        spd = snake_speed * \
            2 if len(g_snake.stampItems) < g_snake_length-1 else snake_speed
        g_screen.ontimer(update_snake, spd)
    else:
        g_screen.ontimer(update_monster, randint(
            monster_speed, monster_speed+100))


def count_body_contact_with_snake(monster):
    global g_contacted_count
    for bdy in g_snake_body_pos:
        if is_collided(monster, bdy):
            g_contacted_count += 1
            print('Monster touched the body of snake!')
            break


def update_monster():

    # Determine the direction of monster movement
    deg = g_monster.towards(g_snake)

    # Chase the snake
    angle = int(deg/45)
    heading = heading_degree[angle]
    g_monster.setheading(heading)
    g_monster.forward(g_head_size)

    count_body_contact_with_snake(g_monster)

    update_game()


def start(x, y):
    global g_time_started
    g_intro.clear()
    configure_numbers()
    g_time_started = time.time()
    g_screen.ontimer(update_snake, snake_speed)
    g_screen.ontimer(update_monster, monster_speed)
    g_screen.onscreenclick(None)


if __name__ == "__main__":
    g_screen = configure_screen()
    g_snake = create_snake()
    g_monster = create_monster()
    g_intro = configure_intro()
    g_head_size = calculate_body_size(g_snake)
    g_screen.update()
    g_screen.onscreenclick(start)
    g_screen.listen()
    g_screen.mainloop()
