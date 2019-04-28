import sys, ctypes

import os
from os import path

import numpy as np

from OpenGL import GL
from OpenGL.GL import shaders
from OpenGL.arrays import vbo

import PIL
from PIL import Image

import sdl2
from sdl2 import ext, video

import pyrr
from pyrr import Matrix44


class Window:

    class Quad:
        vao = 0
        vbo = 0
        n_vertices = 0
        shader = 0 # Index
        textures = {} # Unit : index
        model_mat = pyrr.Matrix44.identity()
        light_dir = np.array([0,0,1,0],np.float32)

        def __init__(self):
            vertex_data = np.array([
               # X,    Y,   Z     NX,  NY,  NZ,   U,   V
               -1.0,  1.0, 0.0, -0.1, 0.1, 1.0,  0.0, 1.0,
               -1.0, -1.0, 0.0, -0.1,-0.1, 1.0,  0.0, 0.0,
                1.0,  1.0, 0.0,  0.1, 0.1, 1.0,  1.0, 1.0,
                1.0, -1.0, 0.0,  0.1,-0.1, 1.0,  1.0, 0.0,
               ], dtype=np.float32)
            self.vao = GL.glGenVertexArrays(1)
            GL.glBindVertexArray(self.vao)
            self.vbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL.GL_STATIC_DRAW)
            position_attrib = 0 # GL.glGetAttribLocation(self.shader, 'position')
            GL.glEnableVertexAttribArray(0) # position - vec3(x,y,z)
            GL.glVertexAttribPointer(position_attrib, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, None) # the last parameter is a pointer
            normal_attrib = 1 # GL.glGetAttribLocation(self.shader, 'normal')
            GL.glEnableVertexAttribArray(1) # normal - vec3(nx,ny,nz)
            GL.glVertexAttribPointer(normal_attrib, 3, GL.GL_FLOAT, GL.GL_TRUE, 32, ctypes.c_void_p(12))
            tex_coords_attrib = 2 # GL.glGetAttribLocation(self.shader, 'tex_coords')
            GL.glEnableVertexAttribArray(2) # tex_coord - vec2(u,v)
            GL.glVertexAttribPointer(tex_coords_attrib, 2, GL.GL_FLOAT, GL.GL_FALSE, 32, ctypes.c_void_p(24))
            self.n_vertices = 4
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
            GL.glBindVertexArray(0)

        def draw(self, view_mat, proj_mat):
            try:
                GL.glUseProgram(self.shader)
                mv_loc = GL.glGetUniformLocation(self.shader, 'mv')
                mvp_loc = GL.glGetUniformLocation(self.shader, 'mvp')
                if mv_loc>=0 or mvp_loc>=0:
                    mv = np.matmul(self.model_mat,view_mat)
                if mv_loc>=0:
                    GL.glUniformMatrix4fv(mv_loc, 1, GL.GL_FALSE, mv)
                if mvp_loc>=0:
                    mvp = np.matmul(mv,proj_mat)
                    GL.glUniformMatrix4fv(mvp_loc, 1, GL.GL_FALSE, mvp)
                ldir_loc = GL.glGetUniformLocation(self.shader, 'light_direction')
                if ldir_loc>=0:
                    ldc = np.matmul(self.light_dir,view_mat)
                    GL.glUniform4f(ldir_loc, *ldc)
                        
                for unit, idx in self.textures.items():
                    GL.glActiveTexture(GL.GL_TEXTURE0 + unit)
                    GL.glBindTexture(GL.GL_TEXTURE_2D, idx)
                GL.glBindVertexArray(self.vao)
                GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, self.n_vertices)
            finally:
                GL.glBindVertexArray(0)
                GL.glUseProgram(0)

    shaders = {}
    textures = {}
    quads = []
    background = [0.0, 0.0, 0.0, 1.0]
    view_mat = pyrr.Matrix44.identity()
    proj_mat = pyrr.Matrix44.identity()
    window = None
    context = None
    aspect = 4/3

    def __init__(self, width, height, fullscreen = False, gl_version = None):
        sdl2.ext.init()
        # Create SDL Window
        flags = sdl2.SDL_WINDOW_OPENGL
        if fullscreen: flags |= sdl2.SDL_WINDOW_FULLSCREEN
        else: flags |= sdl2.SDL_WINDOW_RESIZABLE
        self.window = sdl2.SDL_CreateWindow(b"OpenGL demo", sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED, width, height, flags)
        if not self.window: raise sdl2.ext.SDLError()
        self.aspect = width/height
        # Create OpenGL context
        if gl_version:
            video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MAJOR_VERSION, gl_version[0])
            video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MINOR_VERSION, gl_version[1])
            if len(gl_version)>=3 and gl_version[2]: 
                video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_PROFILE_MASK, video.SDL_GL_CONTEXT_PROFILE_COMPATIBILITY)
            else:
                video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_PROFILE_MASK, video.SDL_GL_CONTEXT_PROFILE_CORE)
        self.context = sdl2.SDL_GL_CreateContext(self.window)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def __del__(self):
        if self.context: sdl2.SDL_GL_DeleteContext(self.context)
        if self.window: sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def load_texture(self, imgpath, name = None):
        if not name: # default texture name is the stem of the filename
            dirname, filename = path.split(imgpath)
            name, ext = path.splitext(filename)
        if name: # make sure the texture id can be stored
            if name in self.textures: # free texture first if you overwrite its name
                GL.glDeleteTextures(1, self.textures[name])
            img = Image.open(imgpath).transpose(Image.FLIP_TOP_BOTTOM) # (0, 0) is top-left in an image file, but bottom-left in a GL texture
            img_data = np.frombuffer(img.tobytes(), np.uint8)
            width, height = img.size
            texture = GL.glGenTextures(1)
            GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0,
                GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data)
            GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
            self.textures[name]=texture

    def load_shader(self, vertpath, fragpath, name = None):
        if not name: # default shader name is the stem of the fragment shader filename
            dirname, filename = path.split(fragpath)
            name, ext = path.splitext(filename)
        if name: # make sure the shader id can be stored
            with open(vertpath,'r') as vsfile, open(fragpath,'r') as fsfile:
                if name in self.shaders: # free shader first if you overwrite its name
                    GL.glDeleteProgram(self.shaders[name])
                vertex_shader = shaders.compileShader(vsfile.read(), GL.GL_VERTEX_SHADER)
                fragment_shader = shaders.compileShader(fsfile.read(), GL.GL_FRAGMENT_SHADER)
                shader_program = shaders.compileProgram(vertex_shader, fragment_shader)
                GL.glDeleteShader(vertex_shader) # flag for deletion for when program is deleted
                GL.glDeleteShader(fragment_shader)
                self.shaders[name]=shader_program

    def render(self):
        GL.glClearColor(*self.background)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        for q in self.quads:
            q.draw(self.view_mat, self.proj_mat)

    def flip(self):
        sdl2.SDL_GL_SwapWindow(self.window)
        
    def resize(self, w, h):
        sdl2.SDL_SetWindowSize(self.window, w, h)
        GL.glViewport(0, 0, w, h)

def run():

    window = Window(800, 600, gl_version=(3, 3))
    #window = Window(1920, 1080, fullscreen=True, gl_version=(3, 3))
    window.load_texture('texture/asterisk.png')
    window.load_shader('shader/perspective.vs', 'shader/phong.fs')
    window.quads.append(Window.Quad())
    window.quads[0].shader = window.shaders['phong']
    window.quads[0].textures[0] = window.textures['asterisk']

    translate = [0.0, 3.0, -1.0]
    rotate = [0.0, 0.0, 0.0]
    scale = 1.0

    # Init Model, View and Projection matrices
    window.quads[0].model_mat = pyrr.matrix44.create_from_translation(translate)
    window.view_mat = pyrr.matrix44.create_look_at(np.array([0.0, 0.0, 0.0], dtype="float32"), # from
                                                   np.array([0.0, 3.0, -1.0], dtype="float32"), # to
                                                   np.array([0.0, 0.0, 1.0], dtype="float32")) # up
    window.proj_mat = pyrr.matrix44.create_perspective_projection(45.0, window.aspect, 0.1, 200.0)

    event = sdl2.SDL_Event()
    running = True
    while running:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif (event.type == sdl2.SDL_KEYDOWN):
                key = event.key.keysym.sym
                if (sdl2.SDLK_ESCAPE == key):
                    running = False
                elif (sdl2.SDLK_RIGHT == key):
                    translate[0] += 0.1
                elif (sdl2.SDLK_LEFT == key):
                    translate[0] -= 0.1
                elif (sdl2.SDLK_UP == key):
                    translate[1] += 0.1
                elif (sdl2.SDLK_DOWN == key):
                    translate[1] -= 0.1
                elif (sdl2.SDLK_PAGEUP == key):
                    translate[2] += 0.1
                elif (sdl2.SDLK_PAGEDOWN == key):
                    translate[2] -= 0.1
                elif (sdl2.SDLK_w == key):
                    rotate[0] += 0.1
                elif (sdl2.SDLK_s == key):
                    rotate[0] -= 0.1
                elif (sdl2.SDLK_a == key):
                    rotate[1] += 0.1
                elif (sdl2.SDLK_d == key):
                    rotate[1] -= 0.1
                elif (sdl2.SDLK_e == key):
                    rotate[2] += 0.1
                elif (sdl2.SDLK_q == key):
                    rotate[2] -= 0.1
                elif (sdl2.SDLK_r == key):
                    scale *= 1.1
                elif (sdl2.SDLK_f == key):
                    scale /= 1.1
                elif (sdl2.SDLK_SPACE == key):
                    window.view_mat = pyrr.matrix44.create_look_at(np.array([0.0, 0.0, 0.0], dtype="float32"), # from
                                                                   np.array(translate, dtype="float32"), # to
                                                                   np.array([0.0, 0.0, 1.0], dtype="float32")) # up
                
                trans_matrix = pyrr.matrix44.create_from_translation(translate)
                rot_x_matrix = pyrr.matrix44.create_from_x_rotation(rotate[0])
                rot_y_matrix = pyrr.matrix44.create_from_y_rotation(rotate[1])
                rot_z_matrix = pyrr.matrix44.create_from_z_rotation(rotate[2])
                rot_matrix = np.matmul(np.matmul(rot_x_matrix,rot_y_matrix),rot_z_matrix)
                scale_matrix = pyrr.matrix44.create_from_scale([scale, scale, scale])
                window.quads[0].model_mat = np.matmul(np.matmul(scale_matrix,rot_matrix),trans_matrix)

        window.render()
        window.flip()
        sdl2.SDL_Delay(10)
    
    return 0

if __name__ == "__main__":
    sys.exit(run())
