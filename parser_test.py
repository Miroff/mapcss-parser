#!/usr/bin/python

import unittest
import re

from mapcss_parser import MapCSSParser

class TestMapCSSParser(unittest.TestCase):

	def setUp(self):
		self.parser = MapCSSParser(debug=False)

	def test_canvas(self):
		self.check("""
canvas {
	antialiasing: full;
	fill-color: #000;
	fill-opacity: #0.2;
	fill-image: fills/grass.png;
}
		""")
		
	def test_line_style(self):
		self.check("""
way {		
	z-index: 1;
	width: 5;
	color: blue;
	opacity: 0.5;
	dashes: 2,2,4,2;
	image: fills/grass.png;
	linecap: square;
	linejoin: bevel;
	fill-color: lightgreen;
	fill-opacity: 0.2;
	fill-image: fills/grass.png;
	casing-width: 9;
	casing-color: red;
	casing-opacity: 0.4;
	casing-dashes: 2,3,4;
	casing-linecap: square;
	casing-linejoin: bevel;
	extrude: 10;
	extrude-edge-color: #fff;
	extrude-edge-opacity: 0.9;
	extrude-face-color: #fff;
	extrude-face-opacity: 0.4;
}
		""")
		
	def test_point_style(self):
		self.check("""
node {		
	icon-image: icons/pharmacy.png;
	icon-width: 25;
	icon-height: 25;
	icon-opacity: 0.3;
}
		""")
		
	def test_point_style(self):
		self.check("""
node {		
	font-family: DejaVu;
	font-size: 12;
	font-weight: bold;
	font-style: italic;
	font-variant:	small-caps;
	text-decoration: underline;
	text-transform: uppercase;
	text-color: #07CF20;
	text-position: center;
	text-offset: -5;
	max-width: 30;
	text: name;
	text-halo-color: white;
	text-halo-radius: 2;
}
		""")
		
	def test_shield_style(self):
		self.check("""
way {		
	shield-color: blue;
	shield-color: #0000FF;
	shield-opacity: 0.5;
	shield-frame-color: #fff;
	shield-frame-width: 12;
	shield-casing-color: #000000;
	shield-casing-width: 1;
	shield-text: ref;
	shield-image: fills/grass.png;
	shield-shape: rounded;
}
		""")

	def test_empty_action(self):
		self.check("""
canvas {}
		""")
		
	def test_multiple_rules(self):
		self.check("""
way {
	color: #000;
}
way {
	fill-color: #000;
}
		""")        
		
	def test_exit_statement(self):
		self.check("""
canvas {
	exit;
}
		""")

	def test_multiple_statements(self):
		self.check("""
way {
	color: #000;
	width: 1px;
}
		""")

	def test_multiple_actions(self):
		self.check("""
way {
	color: #999;
	width: 5px;
}
{
	color: #fff;
	width: 4px;
}
		""")
		
	def test_condition_tag(self):
		self.check("""
way[building] {}
		""")

	def test_condition_tag(self):
		self.check("""
way[!building] {}
		""")

	def test_condition_check(self):
		self.check("""
way[building=yes] {}
		""")

	def test_multiple_conditions_and(self):
		self.check("""
way[highway][tunnel!=yes] {}
		""")

	def test_multiple_conditions_or(self):
		self.check("""
way[highway][tunnel!=yes], 
way[railway][tunnel!=yes]
{}
		""")

	def test_multiple_conditions_within(self):
		self.check("""
relation[type=restriction] way[highway]
{}
		""")

	def test_multiple_conditions_within_triple(self):
		self.check("""
relation[type=restriction] way[highway] node[highway=traffic_signals]
{}
		""")
		
	def test_empty_condition_with_zoom_start(self):
		self.check("""
way|z1 {
}
		""")

	def test_empty_condition_with_zoom_range(self):
		self.check("""
way|z1-16 {
}
		""")
	def test_zoom_start(self):
		self.check("""
way|z1 [highway]{
}
		""")

	def test_zoom_range(self):
		self.check("""
way|z1-16 [building=yes]{
}
		""")
		
	def test_set_tag(self):
		self.check("""
way {
	set minor_road;
}
		""")

	def test_set_tag_value(self):
		self.check("""
way {
	set type = minor;
}
		""")

	def test_class_set(self):
		self.check("""
way {
	set .minor_road;
}
		""")
		
	def test_class_selector(self):
		self.check("""
way .minor_road {
}
		""")

	def test_import(self):
		self.check("""
@import url("osmtags.css") osmtags;
		""")

	def test_import_with_rules(self):
		self.check("""
@import url("osmtags.css") osmtags;
way {    
}
		""")
		
	def test_pseudo_class_selector(self):
		self.check("""
way :area {
}
		""")
		
	def test_comment(self):
		self.check("""
/* Comment */
/* Multiline
   Comment
*/
way /* Comment */
{
/* Comment */
	exit; /* Comment */
}
		""", 'way{exit}')
		
	def test_eval_statement(self):
		self.check("""
way 
{ opacity: eval(tag("population")/100000); }
		""")

	def test_eval_operation(self):
		self.check("""
way {
	width: eval(1 + 2 * 3 - 4 / 5);
}		
		""")
		
#	def test_kothik_style(self):
#		self.check("""
#""")
		

	def check(self, css, expected=None):
		parsed_mapcss = str(self.parser.parse(css))
		mapcss = css
		result = parsed_mapcss.strip()
		result = re.sub(r'\s+', '', result)
		result = re.sub(r';}', '}', result)

		css = css.strip()
		css = re.sub(r'\s+', '', css)
		css = re.sub(r';}', '}', css)
		if expected:
			css = expected
		
		css = css.replace("\n", '').strip()
		
		if result != css:
			print "\nOriginal:"
			print "------------------------------------------"
			print mapcss.strip()
			print "\nParsed:"
			print "------------------------------------------"
			print parsed_mapcss.strip()
		self.assertTrue(result == css, "Parsed MapCSS doesn't match to original one")
			
		#self.assertEqual(result, )

if __name__ == '__main__':
	unittest.main()