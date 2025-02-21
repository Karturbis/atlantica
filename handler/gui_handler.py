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
        self.__std_text_font = pygame.font.Font(None, 42)
        self.__clock = pygame.time.Clock()
        self.__dt = 0
        self.__to_blit = []
        self.__terminal_content = []
        # define window part heights:
        title_height = self.__screen_height//10
        in_rect_height = self.__screen_height//20
        stats_rect_height = self.__screen_height//7
        out_rect_height = self.__screen_height-in_rect_height-stats_rect_height-title_height
        # define window part positions (by defining top left corner):
        self.__out_rect_top = self.__screen_height//10
        self.__in_rect_top = self.__screen_height - stats_rect_height - in_rect_height
        stats_rect_top = self.__screen_height - stats_rect_height
        # initialize the window parts as pygame rects:
        self.__title_rect = pygame.Rect(0, 0, self.__screen_width, title_height)
        self.__out_rect = pygame.Rect(0, self.__out_rect_top, self.__screen_width, out_rect_height)
        self.__in_rect = pygame.Rect(0, self.__in_rect_top, self.__screen_width, in_rect_height)
        self.__stats_rect = pygame.Rect(0, stats_rect_top, self.__screen_width, stats_rect_height)

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
        # draw rects:
        pygame.draw.rect(self.__screen, fg_color, self.__title_rect)
        pygame.draw.rect(self.__screen, in_color, self.__in_rect)
        pygame.draw.rect(self.__screen, stats_color, self.__stats_rect)
        #pygame.draw.rect(self.__screen, out_color, self.__out_rect)

    def new_print(self, text):
        self.__terminal_content.append(text)
        line_height = pygame.font.Font.size(self.__std_text_font, "Tqpg")[1]
        upper_bound = self.__out_rect_top
        lower_bound = self.__in_rect_top
        while len(self.__terminal_content)*line_height > lower_bound -upper_bound:  # check if content fits in out_rect
            self.__terminal_content.pop(0)  # pop oldest content
        # render text to a list of text_surfaces:
        text_surfaces = [self.__std_text_font.render(i, True, self.__text_color) for i in self.__terminal_content]
        self.__to_blit = []  # reset self.__to_blit
        for index, text_surface in enumerate(reversed(text_surfaces)):
            self.__to_blit.append((text_surface, (10, lower_bound - (index+1) * line_height)))

    def clear(self):
        self.__terminal_content = []
        self.__to_blit = []

    def new_input(self, prompt = "input>"):
        prompt = f"{prompt.strip(" ")} " # make sure promt contains exactly one space at the end
        font = self.__std_text_font
        running = True
        user_input = prompt
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
                        self.new_print(user_input[len(prompt):])
                    elif event.key == pygame.K_RETURN:
                        if user_input[len(prompt):].lower() == "clear":
                            self.clear()
                        else:
                            return user_input[len(prompt):]
                        user_input = prompt
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode
            self.__screen.fill(self.__bg_color)
            self.debug_rects()
            text_surface = font.render(user_input, True, self.__text_color)
            self.__screen.blits(self.__to_blit)
            self.__screen.blit(text_surface, (10, self.__in_rect_top))
            self.__screen.blit(title_surface, title_rect)
            # flip() the display to put your work on screen
            pygame.display.flip()
            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.__clock.tick(60) / 1000



gui_handler = GuiHandler()
#gui_handler.startup()
while True:
    text = gui_handler.new_input()
    if text.lower() == "exit":
        break
    else:
        gui_handler.new_print(text)

pygame.quit()
