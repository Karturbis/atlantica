# Example file showing a circle moving on screen
import pygame



class GuiHandler():

    def __init__(self):
        self.__screen_height = 720
        self.__screen_width = 1280
        self.__text_color = pygame.Color("white")
        self.__bg_color = pygame.Color("black")
        pygame.init()
        pygame.key.set_repeat(420, 42)  # enable repeating key input, if key is constantly pressed
        self.__screen = pygame.display.set_mode((self.__screen_width, self.__screen_height))
        self.__std_text_font = pygame.font.Font(None, 20)
        self.__clock = pygame.time.Clock()
        self.__dt = 0
        self.__to_blit = []
        self.__terminal_content = []
        self.__title_rect = pygame.Rect(0, 0, self.__screen_width, self.__screen_height//10)
        self.__stats_rect = pygame.Rect(0, self.__screen_height - self.__screen_height//7, self.__screen_width, self.__screen_height//7)
        self.__in_rect = pygame.Rect(0, self.__screen_height - self.__screen_height//7 - self.__screen_height//10, self.__screen_width, self.__screen_height//10)

    def startup(self):
        font = pygame.font.Font(None, 150)
        running = True
        time = 0
        print_str = "S t a r t i n g . . ."
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

    def debug_rects(self):
        """prints the different sections
        of the window in bright colors"""
        # define colors:
        bg_color = pygame.Color("black")
        fg_color = pygame.Color("green")
        out_color = pygame.Color("yellow")
        in_color = pygame.Color("red")
        stats_color = pygame.Color("blue")
        # define rects
        
        # draw rects:
        pygame.draw.rect(self.__screen, fg_color, self.__title_rect)
        pygame.draw.rect(self.__screen, in_color, self.__in_rect)
        pygame.draw.rect(self.__screen, stats_color, self.__stats_rect)

    def new_print(self, text):
        self.__terminal_content.append(text)
        line_height = pygame.font.Font.size(self.__std_text_font, "TEST")
        text_surface = self.__std_text_font.render(text, True, self.__text_color)
        font = pygame.font.Font(None, 20)
        text_surface = font.render(text, True, self.__text_color)
        self.__to_blit.append((text_surface, (10, self.__screen_height - 200)))

    def new_input(self):
        pass

    def main_loop(self):
        font = self.__std_text_font
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
                        self.new_print(user_input)
                    elif event.key == pygame.K_RETURN:
                        print(user_input)
                        user_input = ''
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode
            self.__screen.fill(self.__bg_color)
            self.debug_rects()
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
