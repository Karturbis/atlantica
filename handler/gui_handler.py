# Example file showing a circle moving on screen
import pygame



class GuiHandler():

    def __init__(self):
        self.__screen_height = 720
        self.__screen_width = 1280
        self.__text_color = pygame.Color("green")
        pygame.init()
        pygame.key.set_repeat(420, 42)
        self.__screen = pygame.display.set_mode((self.__screen_width, self.__screen_height))
        self.__clock = pygame.time.Clock()
        self.__dt = 0
        self.__to_blit = []

    def startup(self):
        font = pygame.font.Font(None, 150)
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
            text_surface = font.render(sliced_str, True, pygame.Color("green"))
            self.__screen.blit(text_surface, (60, self.__screen_height//2))
            pygame.display.flip()
            time += self.__clock.tick(60) / 420

    def print_text(self, text):
        font = pygame.font.Font(None, 42)
        text_surface = font.render(text, True, self.__text_color)
        self.__to_blit.append((text_surface, (10, self.__screen_height - 200)))

    def main_loop(self):
        font = pygame.font.Font(None, 42)
        running = True
        user_input = ""
        title_font = pygame.font.Font(None, 90)
        title = "Atlantica"
        title_surface = title_font.render(title, True, self.__text_color)
        title_rect = title_surface.get_rect(center=(self.__screen_width//2, 50))
        while running:
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # keyboard input:
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.print_text("DEBUG: KEY UP")
                    elif event.key == pygame.K_RETURN:
                        print(user_input)
                        user_input = ''
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode
            self.__screen.fill("black")
            text_surface = font.render(user_input, True, self.__text_color)
            for blitter in self.__to_blit:
                self.__screen.blit(*blitter)
            self.__screen.blit(text_surface, (10, self.__screen_height-100))
            self.__screen.blit(title_surface, title_rect)
            # flip() the display to put your work on screen
            pygame.display.flip()
            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.__clock.tick(60) / 1000

gui_handler = GuiHandler()
#gui_handler.startup()
gui_handler.main_loop()

pygame.quit()
