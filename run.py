import pygame
import time
from rrt import *
from rrt.file_reader import FileReader

scale = 10
DISPLAY_X, DISPLAY_Y = (1000, 400)


def run():
	reader = FileReader(start_tag='start', final_tag='finish', poly_tag='polygons')
	# start_vertex, final_vertex, poly_shapes = reader.read('custom_config.txt')
	start_vertex, final_vertex, poly_shapes = reader.read('inputs.txt')
	
	print(start_vertex, final_vertex)
	all_poly_vertices = reader.get_objects_from_str('vertices', poly_shapes)
	polygons = []
	
	for poly_vertices in all_poly_vertices:
		vertices = []
		for vertex_index in range(len(poly_vertices) - 1):
			vertices.append(
				(Vertex(poly_vertices[vertex_index]['x'] * scale, poly_vertices[vertex_index]['y'] * scale),
				 Vertex(poly_vertices[vertex_index + 1]['x'] * scale, poly_vertices[vertex_index + 1]['y'] * scale))
			)
		polygons.append(PolygonShape(vertices))

	tree = GlobalTree()
	card = Card([(0, DISPLAY_X), (0, DISPLAY_Y)])
	
	N_TRIES = 0
	N_SUCCESS_TRIES = 0
	NEED_CHANGE = False
	N_RANDOM_TRIES = 0
	MAX_N_RANDOM_TRIES = 200
	
	# start vertex
	tree.add_vertex(Vertex(start_vertex['x'] * scale, start_vertex['y'] * scale))
	final = Vertex(final_vertex['x'] * scale, final_vertex['y'] * scale)
	n_verts = 1
	
	pygame.init()
	screen = pygame.display.set_mode((DISPLAY_X, DISPLAY_Y))
	done = False
	
	pygame.draw.circle(screen, (128, 128, 128), (final.x, final.y), 5)
	
	for polygon in polygons:
		card.add_shape(polygon)
		pygame.draw.polygon(screen, (255, 255, 0), [(line[0].x, line[0].y) for line in polygon.get_lines()])
	
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
	
		for edge in tree.edges:
			pygame.draw.circle(screen, (0, 128, 255), (int(edge.v1.x), int(edge.v1.y)), 5)
			pygame.draw.circle(screen, (0, 128, 255), (int(edge.v2.x), int(edge.v2.y)), 5)
			pygame.draw.line(screen, (0, 255, 0), (edge.v1.x, edge.v1.y), (edge.v2.x, edge.v2.y), 3)
	
			"""
			1 - путь
			2 - статистика (время от числа вершин)  (2й генератор)
			3 - док-во распределения
			4 - демонстрация rrt на узком проходе
			"""
		# search
		time.sleep(0.05)
		distance_to_final, base_vertex_index = tree.find_nearest(final)
		if NEED_CHANGE:
			base_vertex = tree.get_vertex_by_index(-1)
			if N_RANDOM_TRIES >= MAX_N_RANDOM_TRIES:
				NEED_CHANGE = False
				N_RANDOM_TRIES = 0
			N_RANDOM_TRIES += 1
		else:
			base_vertex = tree.get_vertex_by_index(int(base_vertex_index[0]))
		pygame.draw.circle(screen, (255, 0, 0), (int(base_vertex.x), int(base_vertex.y)), 5)
		new_pos = tree.generate(base_vertex, radius=(distance_to_final / 3, distance_to_final / 3), samples=1)[0]
		new_pos = new_pos.astype(int)
		vertex = Vertex(*new_pos)
		N_TRIES += 1
		if N_TRIES % 1000 == 0:
			print('remove last step')
			# tree.remove_last_step(1)
			print('N_TRIES', N_TRIES)
			NEED_CHANGE = True
			print('NEED_CHANGE', NEED_CHANGE)
		if N_TRIES > 20000:
			pygame.quit()
			return (0, 0, 0)
		if card.is_available(base_vertex, vertex):
			# print('can PLACE')
			# expand
			_, indexes = tree.find_nearest(vertex)
			nn_vertex = tree.get_vertex_by_index(int(indexes[0]))
			if card.is_available(vertex, nn_vertex):
				# print('can place with NEAREST')
				N_SUCCESS_TRIES += 1
				pygame.draw.line(screen, (0, 255, 0), (nn_vertex.x, nn_vertex.y), (vertex.x, vertex.y), 3)
				tree.add_vertex(vertex)
				n_verts += 1
				tree.add_edge(nn_vertex, vertex)
				if vertex.is_available(final, eps=5):
					done = True
					way = tree.find_way_to_start(vertex)
					print(len(way))
					for vert_index in range(len(way) - 1):
						v_start = way[vert_index]
						v_to = way[vert_index + 1]
						pygame.draw.line(screen, (255, 0, 0), (v_start.x, v_start.y), (v_to.x, v_to.y), 5)
						pygame.display.flip()
					pygame.display.flip()
					time.sleep(1)
		pygame.display.flip()
	pygame.quit()
	print(N_TRIES)
	return len(way), N_TRIES, N_SUCCESS_TRIES / N_TRIES * 100


if __name__ == '__main__':
	way_lens = []
	n_tries = []
	success_place_rates = []
	num_fails = 0
	num_rounds = 1
	for _ in range(num_rounds):
		len_way, n_try, success_place_rate = run()
		if len_way != 0:
			way_lens.append(len_way)
			n_tries.append(n_try)
			success_place_rates.append(success_place_rate)
		else:
			num_fails += 1
	print('WAY STATISTIC', np.mean(way_lens), np.std(way_lens))
	print('WAY MIN MAX', np.min(way_lens), np.max(way_lens))
	print('N TRIES STATISTIC', np.mean(n_tries), np.std(n_tries))
	print('N TRIES MIN MAX', np.min(n_tries), np.max(n_tries))
	print('PLACE RATE STATISTIC', np.mean(success_place_rates), np.std(success_place_rates))
	print('FAIL PERCENT', num_fails / num_rounds)
