import pygame
import numpy as np
import math
import pyads
import ctypes
from ctypes import windll
SetWindowPos = windll.user32.SetWindowPos


# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((800, 600))    
pygame.display.set_caption("gearsim")

# Colors
LSPIN_COLOR = (218, 119, 109)
RSPIN_COLOR = (245, 241, 238)
COLLISION_COLOR = (218, 119, 109)
BACKGROUND_COLOR = (71, 91, 120)

# PLC
netid = None
port = 851

# Gear parameters
gear_radius = 50
tooth_count = 16
tooth_depth = 10
gear1_pos = np.array([400, 300])
gear2_pos = np.array([600, 300])
gear3_pos = np.array([200, 300])
orbital_angle1 = 0
orbital_angle2 = 0

def draw_gear(screen, pos, radius, tooth_count, tooth_depth, rotation, color):
    angle_step = 2 * np.pi / tooth_count
    points = []
    for i in range(tooth_count * 2):
        angle = i * (angle_step / 2) + rotation
        if i % 2 == 0:
            r = radius + tooth_depth  # Tooth
        else:
            r = radius  # Base circle
        x = pos[0] + r * math.cos(angle)
        y = pos[1] + r * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(screen, color, points)
    
def draw_rail_with_inner_slot(screen, pos1, pos2, outer_width=15, inner_width=5, hole_radius=20, color=COLLISION_COLOR):
    """ Draws a rail with a transparent inner slot and a hole in the middle """
    # Calculate the angle of the rail
    angle = math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])
    
    # Calculate the offsets for outer and inner rails
    half_outer_width = outer_width / 2
    half_inner_width = inner_width / 2
    outer_offset_x = half_outer_width * math.sin(angle)
    outer_offset_y = half_outer_width * math.cos(angle)
    inner_offset_x = half_inner_width * math.sin(angle)
    inner_offset_y = half_inner_width * math.cos(angle)

    # Points of the outer rail (four corners)
    outer_points = [
        (pos1[0] - outer_offset_x, pos1[1] + outer_offset_y),
        (pos1[0] + outer_offset_x, pos1[1] - outer_offset_y),
        (pos2[0] + outer_offset_x, pos2[1] - outer_offset_y),
        (pos2[0] - outer_offset_x, pos2[1] + outer_offset_y)
    ]
    
    # Points of the inner transparent slot (four corners)
    inner_points = [
        (pos1[0] - inner_offset_x, pos1[1] + inner_offset_y),
        (pos1[0] + inner_offset_x, pos1[1] - inner_offset_y),
        (pos2[0] + inner_offset_x, pos2[1] - inner_offset_y),
        (pos2[0] - inner_offset_x, pos2[1] + inner_offset_y)
    ]
    
    # Draw the outer rail
    pygame.draw.polygon(screen, color, outer_points)

    # Create a transparent surface for the inner slot
    rail_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    pygame.draw.polygon(rail_surface, BACKGROUND_COLOR, inner_points)
    screen.blit(rail_surface, (0, 0))

    # Draw circles at the endpoints for rounded edges of the outer rail
    pygame.draw.circle(screen, color, pos1.astype(int), half_outer_width)
    pygame.draw.circle(screen, color, pos2.astype(int), half_outer_width)   

def line_intersect(p1, p2, q1, q2):
    """ Check if two line segments (p1, p2) and (q1, q2) intersect """
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

def detect_collision(gear1_pos, gear2_pos, rotation1, rotation2, radius1, radius2, tooth_depth, tooth_count):
    angle_step = 2 * np.pi / tooth_count
    # Generate the polygon vertices for both gears
    gear1_vertices = []
    gear2_vertices = []
    for i in range(tooth_count * 2):
        angle1 = i * (angle_step / 2) + rotation1
        angle2 = i * (angle_step / 2) + rotation2
        r1 = radius1 + (tooth_depth if i % 2 == 0 else 0)
        r2 = radius2 + (tooth_depth if i % 2 == 0 else 0)
        x1 = gear1_pos[0] + r1 * math.cos(angle1)
        y1 = gear1_pos[1] + r1 * math.sin(angle1)
        x2 = gear2_pos[0] + r2 * math.cos(angle2)
        y2 = gear2_pos[1] + r2 * math.sin(angle2)
        gear1_vertices.append((x1, y1))
        gear2_vertices.append((x2, y2))

    # Check if any edges from gear 1 intersect with gear 2
    for i in range(len(gear1_vertices)):
        p1 = gear1_vertices[i]
        p2 = gear1_vertices[(i + 1) % len(gear1_vertices)]
        for j in range(len(gear2_vertices)):
            q1 = gear2_vertices[j]
            q2 = gear2_vertices[(j + 1) % len(gear2_vertices)]
            if line_intersect(p1, p2, q1, q2):
                return True

    return False


def read_gear_pos(plc, name):
    return plc.read_by_name(f"ZGlobal.Com.Unit.{name}.Publish.Equipment.PositionX.Base.ActualPosition", pyads.PLCTYPE_LREAL)

def read_gear_rot(plc, name):    
    return plc.read_by_name(f"ZGlobal.Com.Unit.{name}.Publish.Equipment.RotationC.Base.ActualPosition", pyads.PLCTYPE_LREAL)

# Connect to PLC
if netid is None:
    pyads.ads.open_port()
    netid = pyads.ads.get_local_address().netid
    pyads.ads.close_port()

plc = pyads.Connection("127.0.0.1.1.1", 851)
plc.open()

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BACKGROUND_COLOR)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle keyboard input for gear2 movement and offset change
    keys = pygame.key.get_pressed()
    
    # Update positions with PLC data
    gear1_pos[0] = 400 + read_gear_pos(plc, "PrimaryGear")
    
    gear2_distance = 200 + read_gear_pos(plc, "SimpleGear")
    gear3_distance = -200 - read_gear_pos(plc, "StruckigGear")
    
    orbital_angle1 += 0.006
    orbital_angle2 -= 0.009
    gear2_pos = np.array([gear1_pos[0] + gear2_distance * np.cos(orbital_angle1), gear1_pos[1] + gear2_distance * np.sin(orbital_angle1)])
    gear3_pos = np.array([gear1_pos[0] + gear3_distance * np.cos(orbital_angle2), gear1_pos[1] + gear3_distance * np.sin(orbital_angle2)])
    
    gear1_rotation = read_gear_rot(plc, "PrimaryGear")  / 180 * np.pi
    gear2_rotation = -read_gear_rot(plc, "SimpleGear")  / 180 * np.pi
    gear3_rotation = -read_gear_rot(plc, "StruckigGear")  / 180 * np.pi

    # Detect collisions and adjust color
    gear2_color = COLLISION_COLOR if detect_collision(gear1_pos, gear2_pos, gear1_rotation, gear2_rotation, gear_radius, gear_radius, tooth_depth, tooth_count) else RSPIN_COLOR
    gear3_color = COLLISION_COLOR if detect_collision(gear1_pos, gear3_pos, gear1_rotation, gear3_rotation, gear_radius, gear_radius, tooth_depth, tooth_count) else RSPIN_COLOR

    # Draw gears
    draw_gear(screen, gear1_pos, gear_radius, tooth_count, tooth_depth, gear1_rotation, LSPIN_COLOR)
    draw_gear(screen, gear3_pos, gear_radius, tooth_count, tooth_depth, gear3_rotation, gear3_color)
    draw_gear(screen, gear2_pos, gear_radius, tooth_count, tooth_depth, gear2_rotation, gear2_color)
    
    draw_rail_with_inner_slot(screen, gear1_pos, np.array([gear1_pos[0] + 170 * np.cos(orbital_angle1), gear1_pos[1] + 170 * np.sin(orbital_angle1)]), outer_width=30, inner_width=10, hole_radius=25, color=LSPIN_COLOR)
    draw_rail_with_inner_slot(screen, gear1_pos, np.array([gear1_pos[0] - 190 * np.cos(orbital_angle2), gear1_pos[1] - 190 * np.sin(orbital_angle2)]), outer_width=30, inner_width=10, hole_radius=25, color=LSPIN_COLOR)


    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
