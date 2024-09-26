import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the joystick
joystick = pygame.joystick.Joystick(0)  # Assuming the first joystick
joystick.init()

print("Joystick Name:", joystick.get_name())

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.JOYAXISMOTION:
            print("Axis {} value: {}".format(event.axis, joystick.get_axis(event.axis)))

        if event.type == pygame.JOYBUTTONDOWN:
            print("Button {} pressed".format(event.button))

        if event.type == pygame.JOYBUTTONUP:
            print("Button {} released".format(event.button))
