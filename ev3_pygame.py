#!/usr/bin/env python

import pygame

import ev3
import ev3_vehicle


def main():
    pygame.init()
    pygame.font.init()

    pygame.display.set_caption("key capture test")

    screen = pygame.display.set_mode((240, 180))

    myfont = pygame.font.Font(pygame.font.get_default_font(), 30)
    textsurface = myfont.render('Some Text', True, (255, 0, 0))
    screen.blit(textsurface, (0, 0))
    pygame.display.update()


    vehicle = ev3_vehicle.TwoWheelVehicle(
        0.02128,                 # radius_wheel
        0.1175,                  # tread
        protocol=ev3.constants.USB,
    )


    is_driving = None
    running = True
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                # print("MOD: %s, KEY: %s" % (mods, pygame.key.name(event.key)))

                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_q:  # and mods & pygame.KMOD_META:
                    running = False
                elif event.key == pygame.K_w and mods & pygame.KMOD_META:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    running = False
                elif not is_driving:
                    if event.key == pygame.K_UP:
                        is_driving = event.key
                        print("START DRIVING FORWARD")
                        vehicle._drive_straight(25, 0.1)
                    elif event.key == pygame.K_DOWN:
                        is_driving = event.key
                        print("START DRIVING BACKWARD")

            elif event.type == pygame.KEYUP:
                # print("KEY RELEASED: %s" % pygame.key.name(event.key))
                if event.key == is_driving:
                    is_driving = None
                    print("BRAKE")
                    vehicle.stop()

    pygame.quit()


if __name__ == "__main__":
    main()
