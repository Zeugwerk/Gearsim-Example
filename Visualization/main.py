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
hwnd = pygame.display.get_wm_info()['window'] 
SetWindowPos(hwnd, -2, 0, 0, 0, 0, 2|1)
    
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
gear_radius = 100
tooth_count = 16
tooth_depth = 20
gear1_pos = np.array([250, 300])
gear2_pos = np.array([550, 300])

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

def line_intersect(p1, p2, q1, q2):
    """ Check if two line segments (p1, p2) and (q1, q2) intersect """
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

def detect_collision(gear1_pos, gear2_pos, rotation1, rotation2, radius, tooth_depth, tooth_count):
    angle_step = 2 * np.pi / tooth_count
    # Generate the polygon vertices for both gears
    gear1_vertices = []
    gear2_vertices = []
    for i in range(tooth_count * 2):
        angle1 = i * (angle_step / 2) + rotation1
        angle2 = i * (angle_step / 2) + rotation2
        r1 = radius + (tooth_depth if i % 2 == 0 else 0)
        r2 = radius + (tooth_depth if i % 2 == 0 else 0)
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


def read_gear1_pos(plc):
    return plc.read_by_name(f"ZGlobal.Com.Unit.LeftGear.Publish.Equipment.PositionX.Base.ActualPosition", pyads.PLCTYPE_LREAL)

def read_gear2_pos(plc):
    return plc.read_by_name(f"ZGlobal.Com.Unit.RightGear.Publish.Equipment.PositionX.Base.ActualPosition", pyads.PLCTYPE_LREAL)
    
def read_gear1_rot(plc):    
    return plc.read_by_name(f"ZGlobal.Com.Unit.LeftGear.Publish.Equipment.RotationC.Base.ActualPosition", pyads.PLCTYPE_LREAL)
    
def read_gear2_rot(plc):    
    return plc.read_by_name(f"ZGlobal.Com.Unit.RightGear.Publish.Equipment.RotationC.Base.ActualPosition", pyads.PLCTYPE_LREAL)


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
    gear1_pos[0] = 250 + read_gear1_pos(plc)    
    gear2_pos[0] = 550 + read_gear2_pos(plc)
    gear1_rotation = read_gear1_rot(plc)  / 180 * np.pi
    gear2_rotation = -read_gear2_rot(plc)  / 180 * np.pi

    # Detect collisions and adjust color
    gear_color = COLLISION_COLOR if detect_collision(gear1_pos, gear2_pos, gear1_rotation, gear2_rotation, gear_radius, tooth_depth, tooth_count) else RSPIN_COLOR

    # Draw gears
    draw_gear(screen, gear1_pos, gear_radius, tooth_count, tooth_depth, gear1_rotation, LSPIN_COLOR)
    draw_gear(screen, gear2_pos, gear_radius, tooth_count, tooth_depth, gear2_rotation, gear_color)

    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
