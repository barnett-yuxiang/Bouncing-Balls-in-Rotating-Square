import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Balls in Rotating Square")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Square properties
square_size = 300
square_x = width // 2 - square_size // 2
square_y = height // 2 - square_size // 2
square_color = white
rotation_speed = 0.1  # Radians per frame

# Ball properties
ball_radius = 15
balls = []


# Function to rotate a point around the center
def rotate_point(point, angle, center):
    x, y = point
    cx, cy = center
    x -= cx
    y -= cy
    rotated_x = x * math.cos(angle) - y * math.sin(angle)
    rotated_y = x * math.sin(angle) + y * math.cos(angle)
    return rotated_x + cx, rotated_y + cy


# Function to get rotated square vertices
def get_rotated_square(x, y, size, angle):
    half_size = size // 2
    center = (x + half_size, y + half_size)
    vertices = [
        (x, y),
        (x + size, y),
        (x + size, y + size),
        (x, y + size),
    ]
    return [rotate_point(v, angle, center) for v in vertices]


# Function for collision detection (Separating Axis Theorem - simplified for rectangle)
def is_inside_square(ball_pos, vertices):
    x, y = ball_pos

    for i in range(4):
        # Edge vector
        v1 = vertices[i]
        v2 = vertices[(i + 1) % 4]
        edge_x = v2[0] - v1[0]
        edge_y = v2[1] - v1[1]

        # Normal vector (perpendicular to edge)
        normal_x = -edge_y
        normal_y = edge_x

        # Project ball center onto normal
        dot_product_ball = (x - v1[0]) * normal_x + (y - v1[1]) * normal_y

        # Project vertices onto normal
        dot_products_vertices = []
        for vx, vy in vertices:
            dot_products_vertices.append(
                (vx - v1[0]) * normal_x + (vy - v1[1]) * normal_y
            )

        # Check for overlap
        min_v = min(dot_products_vertices)
        max_v = max(dot_products_vertices)

        if dot_product_ball < min_v or dot_product_ball > max_v:
            return False, None  # No collision on this axis

    return True, (normal_x, normal_y)  # all axis overlap


# Function to handle ball-square collision
def handle_square_collision(ball, vertices):
    is_inside, normal = is_inside_square(ball["pos"], vertices)
    if not is_inside:
        # Find closest edge
        closest_edge_index = -1
        min_dist = float("inf")

        for i in range(4):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 4]

            # Calculate distance from point to line segment
            px, py = ball["pos"]
            x1, y1 = v1
            x2, y2 = v2

            dx = x2 - x1
            dy = y2 - y1

            if dx == 0 and dy == 0:  # It's a point, not a line segment
                dist = math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
            else:
                t = ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)
                t = max(0, min(1, t))  # Clamp t to [0, 1]
                closest_x = x1 + t * dx
                closest_y = y1 + t * dy
                dist = math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)

            if dist < min_dist:
                min_dist = dist
                closest_edge_index = i

        # Get the normal of the closest edge
        v1 = vertices[closest_edge_index]
        v2 = vertices[(closest_edge_index + 1) % 4]
        edge_x = v2[0] - v1[0]
        edge_y = v2[1] - v1[1]
        normal_x = -edge_y
        normal_y = edge_x

        # Normalize normal
        mag = math.sqrt(normal_x**2 + normal_y**2)
        if mag != 0:
            normal_x /= mag
            normal_y /= mag

        # Reflect velocity
        dot_product = ball["vel"][0] * normal_x + ball["vel"][1] * normal_y
        ball["vel"][0] -= 2 * dot_product * normal_x
        ball["vel"][1] -= 2 * dot_product * normal_y


# Function to handle ball-ball collision
def handle_ball_collision(ball1, ball2):
    x1, y1 = ball1["pos"]
    x2, y2 = ball2["pos"]
    vx1, vy1 = ball1["vel"]
    vx2, vy2 = ball2["vel"]

    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)

    if distance < 2 * ball_radius:
        # Normalize
        nx = dx / distance
        ny = dy / distance

        # Relative velocity
        dvx = vx1 - vx2
        dvy = vy1 - vy2

        # Dot product of relative velocity and normal
        dot_product = dvx * nx + dvy * ny

        # Calculate impulse
        impulse = (2 * dot_product) / 2  # Simplified for equal mass

        # Apply impulse
        ball1["vel"][0] -= impulse * nx
        ball1["vel"][1] -= impulse * ny
        ball2["vel"][0] += impulse * nx
        ball2["vel"][1] += impulse * ny

        # Separate balls to prevent sticking
        overlap = 2 * ball_radius - distance
        if overlap > 0:
            ball1["pos"][0] -= overlap / 2 * nx
            ball1["pos"][1] -= overlap / 2 * ny
            ball2["pos"][0] += overlap / 2 * nx
            ball2["pos"][1] += overlap / 2 * ny


# Game loop
running = True
angle = 0
last_ball_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(black)

    # Update rotation angle
    angle += rotation_speed

    # Get rotated square vertices
    rotated_square = get_rotated_square(square_x, square_y, square_size, angle)

    # Create new ball every 5 seconds
    current_time = time.time()
    if current_time - last_ball_time >= 5:
        new_ball = {
            "pos": [
                random.randint(
                    square_x + ball_radius, square_x + square_size - ball_radius
                ),
                random.randint(
                    square_y + ball_radius, square_y + square_size - ball_radius
                ),
            ],
            "vel": [random.uniform(-3, 3), random.uniform(-3, 3)],
            "color": (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            ),
        }
        balls.append(new_ball)
        last_ball_time = current_time

    # Update and draw balls
    for i in range(len(balls)):
        balls[i]["pos"][0] += balls[i]["vel"][0]
        balls[i]["pos"][1] += balls[i]["vel"][1]
        handle_square_collision(balls[i], rotated_square)

        # Ball-ball collision
        for j in range(i + 1, len(balls)):
            handle_ball_collision(balls[i], balls[j])

        pygame.draw.circle(
            screen,
            balls[i]["color"],
            (int(balls[i]["pos"][0]), int(balls[i]["pos"][1])),
            ball_radius,
        )

    # Draw rotated square
    pygame.draw.polygon(screen, square_color, rotated_square, 2)

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    pygame.time.Clock().tick(60)

pygame.quit()
