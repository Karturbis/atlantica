# Example file showing a circle moving on screen
import pygame



class GuiHandler():

    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(420, 42)
        self.__screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.__clock = pygame.time.Clock()
        self.__dt = 0
        self.__font = pygame.font.Font(None, 150)

    def startup(self):
        running = True
        time = 0
        print_str = "Starting..."
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            sliced_str = print_str[:int(time)]
            if int(time) == len(print_str) + 1:
                running = False
            self.__screen.fill("black")
            text_surface = self.__font.render(sliced_str, True, pygame.Color("green"))
            self.__screen.blit(text_surface, (60, 350))
            pygame.display.flip() 
            time += self.__clock.tick(60) / 420


    def main_loop(self):
        running = True
        user_input = ""
        while running:
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # keyboard input:
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        print("DEBUG: KEY UP")
                    elif event.key == pygame.K_RETURN:
                        print(user_input)
                        user_input = ''
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode
            self.__screen.fill("black")
            text_surface = self.__font.render(user_input, True, pygame.Color('green'))
            self.__screen.blit(text_surface, (200, 200))
            pygame.draw.circle(self.__screen, "red", (50, 300), 40)
            # flip() the display to put your work on screen
            pygame.display.flip()
            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.__clock.tick(60) / 1000

gui_handler = GuiHandler()
gui_handler.startup()
gui_handler.main_loop()

pygame.quit()
