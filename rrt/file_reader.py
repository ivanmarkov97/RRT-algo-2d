import json

class FileReader:
	def __init__(self, start_tag: str, final_tag: str, poly_tag: str):
		self.start_tag = start_tag
		self.final_tag = final_tag
		self.poly_tag = poly_tag
		self.start_vertex = dict.fromkeys([start_tag], None)
		self.final_vertex = dict.fromkeys([final_tag], None)
		self.polygons = dict.fromkeys([poly_tag], None)
		
	def read(self, file_name: str):
		f = open(file_name, 'r')
		json_result = json.loads(f.read())
		return (
			json_result[self.start_tag],
			json_result[self.final_tag],
			json_result[self.poly_tag]
		)
	
	@staticmethod
	def get_objects_from_str(key, json_data) -> list:
		return [json_object[key] for json_object in json_data if key in json_object]
	
#print(reader.get_objects_from_str('vertices', result[-1]))
