import pygame,sys,re
from math import *

window = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

projection_matrix = [[1,0,0],[0,1,0],[0,0,0]]

#cube_points = [n for n in range(8)];cube_points[0] = [[-1], [-1], [1]];cube_points[1] = [[1],[-1],[1]];cube_points[2] = [[1],[1],[1]];cube_points[3] = [[-1],[1],[1]];cube_points[4] = [[-1],[-1],[-1]];cube_points[5] = [[1],[-1],[-1]];cube_points[6] = [[1],[1],[-1]];cube_points[7] = [[-1],[1],[-1]]

scale = 100

angle_x = angle_y = angle_z = 0
angle_y = 60

def connect_points(i, j, points):
    pygame.draw.line(window, (255, 255, 255), (points[i][0], points[i][1]) , (points[j][0], points[j][1]))

def multiply_m(a, b):
    a_rows = len(a)
    a_cols = len(a[0])
    b_rows = len(b)
    b_cols = len(b[0])
    product = [[0 for _ in range(b_cols)] for _ in range(a_rows)]
    if a_cols == b_rows:
        for i in range(a_rows):
            for j in range(b_cols):
                for k in range(b_rows):
                    product[i][j] += a[i][k] * b[k][j]
    return product
    
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action
        
class ImportOBJ:
    def __init__(self, filename):
        self.filename = filename
    def importobj(self):
        reComp = re.compile("(?<=^)(v |vn |vt |f )(.*)(?=$)", re.MULTILINE)
        with open(self.filename) as f:
            data = [txt.group() for txt in reComp.finditer(f.read())]
        v_arr, vn_arr, f_arr = [], [], []
        for line in data:
            tokens = line.split(' ')
            if tokens[0] == 'v':
                v_arr.append([float(c) for c in tokens[1:]])
            elif tokens[0] == 'vn':
                vn_arr.append([float(c) for c in tokens[1:]])
            elif tokens[0] == 'vt':
                vn_arr.append([float(c) for c in tokens[1:]])
            elif tokens[0] == 'f':
                f_arr.append([[int(i) if len(i) else 0 for i in c.split('/')] for c in tokens[1:]])
        vertices = []
        for face in f_arr:
            for tp in face:
                for i in v_arr[tp[0]-1]:
                    vertices.append([i])
        return list(zip(*[iter(vertices)]*3))

cube_points = ImportOBJ("C:\\Users\\pengu\\Downloads\\sphere.obj").importobj()

fast_button = Button(120, 515, pygame.image.load("fast.png"), 4)
slow_button = Button(550, 515, pygame.image.load("slow.png"), 4)

rotate_speed = 0.5

debug = False
weird = False

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)

def drawText(text, x, y):
    text_surface = font.render(text, False, (255, 255, 255))
    window.blit(text_surface, (x,y))

def truncate(n):
    multiplier = 10 ** 3
    return int(n * multiplier) / multiplier

while True:
    clock.tick(60)
    
    if weird == False:
        window.fill((0,0,0))

    if debug == True:
        drawText(f"Mouse Pos: {pygame.mouse.get_pos()}", 5, 5)
        drawText(f"Rotation speed: {int(rotate_speed*100)}", 5, 35)
        drawText(f"XYZ Rotation: {truncate(angle_x)}, {truncate(angle_y)}, {truncate(angle_z)}", 5, 65)

    if fast_button.draw(window):
        rotate_speed += 0.5
    if slow_button.draw(window):
        rotate_speed -= 0.5

    angle_x += rotate_speed
    angle_y += rotate_speed
    angle_z += rotate_speed

    rotation_x = [[1, 0, 0],[0, cos(angle_x/60), -sin(angle_x/60)],[0, sin(angle_x/60), cos(angle_x/60)]]

    rotation_y = [[cos(angle_y/60), 0, sin(angle_y/60)],[0, 1, 0],[-sin(angle_y/60), 0, cos(angle_y/60)]]

    rotation_z = [[cos(angle_z/60), -sin(angle_z/60), 0],[sin(angle_z/60), cos(angle_z/60), 0],[0, 0, 1]]

    points = [0 for _ in range(len(cube_points))]

    i=0
    for point in cube_points:
        rotate_x = multiply_m(rotation_x, point)
        rotate_y = multiply_m(rotation_y, rotate_x)
        rotate_z = multiply_m(rotation_z, rotate_y)
        point_2d = multiply_m(projection_matrix, rotate_z)

        x = (point_2d[0][0] * scale) + 400
        y = (point_2d[1][0] * scale) + 300
        
        points[i] = (x,y)
        i+=1

        pygame.draw.circle(window, (255, 0, 0), (x,y), 5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                debug = not debug
            if event.key == pygame.K_j:
                weird = not weird
    pygame.display.update()
