import sdl2, OpenGL as gl

class window:
    def __init__(self, width, height, title = "Pythons", borders = True):
        self.width, self.height = width, height
        self.show_borders = borders
        self.title = title.encode()
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            print(sdl2.SDL_GetError())
            return -1
        sdl2.sdlttf.TTF_Init()
        sdl2.sdlimg.IMG_Init(sdl2img.IMG_INIT_PNG)

        self.window = sdl2.SDL_CreateWindow(self.title, sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED, self.width, self.height, sdl2.SDL_WINDOW_OPENGL)
        sdl2.SDL_SetWindowBordered(self.window, self.show_borders)
        if not self.window:
            print(sdl2.SDL_GetError())
            return -1

        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1,
            sdl2.SDL_RENDERER_ACCELERATED|sdl2.SDL_RENDERER_PRESENTVSYNC)
        
if __name__ == "__main__":
    win = window(800, 600)
