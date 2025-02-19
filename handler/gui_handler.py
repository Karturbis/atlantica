# Example file showing a circle moving on screen
import pygame



class GuiHandler():

    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(420, 42)
        self.__screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.__clock = pygame.time.Clock()
        self.__dt = 0
        self.__font = pygame.font.Font(None, 32)

    def startup(self):
        pass

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
                # window resize action (make a minimum window size):
                elif event.type == pygame.VIDEORESIZE:
                    width, height = event.size
                    if width < 600:
                        width = 600
                    if height < 400:
                        height = 400
                    self.__screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            

                        
            self.__screen.fill("black")
            text_surface = self.__font.render(user_input, True, pygame.Color('green'))
            self.__screen.blit(text_surface, (200, 200))

            pygame.draw.circle(self.__screen, "red", (50, 300), 40)

            keys = pygame.key.get_pressed()

            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.__clock.tick(60) / 1000

pg = GuiHandler()
pg.main_loop()

pygame.quit()
