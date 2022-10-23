import pygame
import numpy

class Engine:
    def __init__(self, width, height, filename, maxfps=0):
        self.width, self.height = width, height
        self.fovV = numpy.pi/4
        self.fovH = self.fovV*self.height/self.width

        self.screen = pygame.display.set_mode((width, height))
        self.running = True
        self.clock = pygame.time.Clock()
        self.maxfps = maxfps
        self.surface = pygame.surface.Surface((self.width, self.height))
        
        self.points, self.triangles = self.read_obj(filename)

        self.camera = numpy.asarray([13, 0.5, 2, 3.3, 0])
        self.lightdirection = numpy.asarray([0, 1, 1])

        self.z_order = numpy.zeros(len(self.triangles))
        self.shade = self.z_order.copy()

    def limitFPS(self):
        self.clock.tick(self.maxfps)
    
    def getFPS(self):
        print(self.clock.get_fps())

    def movement(self):
        if pygame.mouse.get_focused():
            p_mouse = pygame.mouse.get_pos()
            self.camera[3] = (self.camera[3] + 10*self.elapsed_time*numpy.clip((p_mouse[0]-self.width/2)/self.width, -0.2, .2))%(2*numpy.pi)
            self.camera[4] = self.camera[4] + 10*self.elapsed_time*numpy.clip((p_mouse[1]-self.height/2)/self.height, -0.2, .2)
            self.camera[4] = numpy.clip(self.camera[4], -.3, .3)
    
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[ord('e')]: self.camera[1] += self.elapsed_time
        elif pressed_keys[ord('q')]: self.camera[1] -= self.elapsed_time

        if (pressed_keys[ord('w')] or pressed_keys[ord('s')]) and (pressed_keys[ord('a')] or pressed_keys[ord('d')]):
            self.elapsed_time *= 0.707
        
        if pressed_keys[pygame.K_UP] or pressed_keys[ord('w')]:
            self.camera[0] += self.elapsed_time*numpy.cos(self.camera[3])
            self.camera[2] += self.elapsed_time*numpy.sin(self.camera[3])

        elif pressed_keys[pygame.K_DOWN] or pressed_keys[ord('s')]:
            self.camera[0] -= self.elapsed_time*numpy.cos(self.camera[3])
            self.camera[2] -= self.elapsed_time*numpy.sin(self.camera[3])
        
        if pressed_keys[pygame.K_LEFT] or pressed_keys[ord('a')]:
            self.camera[0] += self.elapsed_time*numpy.sin(self.camera[3])
            self.camera[2] -= self.elapsed_time*numpy.cos(self.camera[3])
        
        elif pressed_keys[pygame.K_RIGHT] or pressed_keys[ord('d')]:
            self.camera[0] -= self.elapsed_time*numpy.sin(self.camera[3])
            self.camera[2] += self.elapsed_time*numpy.cos(self.camera[3])

    def sort_triangles(self):
        for i in range(len(self.triangles)):
            triangle = self.triangles[i]

            vet1 = self.points[triangle[1]][:3] - self.camera[:3]
            vet2 = self.points[triangle[2]][:3] - self.camera[:3]

            normal = numpy.cross(vet1, vet2)
            normal = normal/numpy.sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2])

            CameraRay = self.points[triangle[0]][:3] - self.camera[:3]
            dist2cam = numpy.sqrt(CameraRay[0]*CameraRay[0] + CameraRay[1]*CameraRay[1] + CameraRay[2]*CameraRay[2])
            CameraRay = CameraRay/dist2cam

            if numpy.dot(normal, CameraRay) < 0:
                self.z_order[i] = -dist2cam
                self.shade[i] = 0.5*numpy.dot(self.lightdirection, normal)+0.5
            else:
                self.z_order[i] = 9999

    def read_obj(self, fileName):
        vertices = []
        triangles = []
        f = open(fileName)
        for line in f:
            if line[:2] == "v ":
                index1 = line.find(" ") + 1
                index2 = line.find(" ", index1 + 1)
                index3 = line.find(" ", index2 + 1)
            
                vertex = [float(line[index1:index2]), float(line[index2:index3]), float(line[index3:-1]), 1, 1]
                vertices.append(vertex)

            elif line[0] == "f":
                index1 = line.find(" ") + 1
                index2 = line.find(" ", index1 + 1)
                index3 = line.find(" ", index2 + 1)

                triangles.append([int(line[index1:index2]) - 1, int(line[index2:index3]) - 1, int(line[index3:-1]) - 1])

        f.close()

        return numpy.asarray(vertices), numpy.asarray(triangles)

    def update(self):
        self.surface.fill([50,127,200])
        self.elapsed_time = self.clock.tick()*0.001
        self.lightdirection = numpy.asarray([numpy.sin(pygame.time.get_ticks()/1000), 1, 1])
        self.lightdirection = self.lightdirection/numpy.linalg.norm(self.lightdirection)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
        self.project_points()
        self.sort_triangles()
        for index in numpy.argsort(self.z_order):
            if self.z_order[index] == 9999: break
            triangle = [self.points[self.triangles[index][0]][3:], self.points[self.triangles[index][1]][3:], self.points[self.triangles[index][2]][3:]]
            color = self.shade[index]*numpy.abs(self.points[self.triangles[index][0]][:3])*45+25
            pygame.draw.polygon(self.surface, color, triangle)
        self.screen.blit(self.surface, (0, 0))
        pygame.display.set_caption(str(round(1/(self.elapsed_time+1e-16), 1)) + ' ' + str(self.camera))
        pygame.display.update()
        self.movement()

    def project_points(self):
        for point in self.points:
            h_angle_camera_point = numpy.arctan((point[2]-self.camera[2])/(point[0]-self.camera[0] + 1e-16))
            if abs(self.camera[0]+numpy.cos(h_angle_camera_point)-point[0]) > abs(self.camera[0]-point[0]):
                h_angle_camera_point = (h_angle_camera_point - numpy.pi) % (2*numpy.pi)
            h_angle = (h_angle_camera_point - self.camera[3]) % (2*numpy.pi)
            if h_angle > numpy.pi:
                h_angle = h_angle - 2*numpy.pi
            point[3] = self.width*h_angle/self.fovH+self.width/2
            distance = numpy.sqrt((point[0]-self.camera[0])**2 + (point[1]-self.camera[1])**2 + (point[2]-self.camera[2])**2)
            v_angle_camera_point = numpy.arcsin((self.camera[1]-point[1])/distance)
            v_angle = (v_angle_camera_point - self.camera[4])%(2*numpy.pi)
            if v_angle > numpy.pi:
                v_angle = v_angle - 2*numpy.pi
            point[4] = self.height*v_angle/self.fovV+self.height/2

engine = Engine(800, 600, input("OBJ model: "))
while engine.running:
    engine.update()
