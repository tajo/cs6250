import sys
import os
import numpy as np
import matplotlib.pyplot as plt

names = ['Direct', 'FirstContact', 'Prophetrouter', 'Spray', 'Epidemic']

def get_fileName(prefix):
	base_dir = os.path.join("..", "data_reports")
	base_dir = os.path.join("..", base_dir)
	fileName = prefix + '_MessageStatsReport'
	return os.path.join(base_dir, "{}.txt".format(str(fileName)))


def get_number(prefix):
	# import pdb; pdb.set_trace()
	fn = get_fileName(prefix)
	f = open(fn,'r')
	res = {}
	for lines in f:
		elements = lines.split(': ')
		if elements[0] == 'delivery_prob':
			res[prefix] = elements[1].strip()
			break
	f.close()
	return res

def get_all_numbers():
	res = {}
	for name in names:
		elm = get_number(name)
		for x in elm:
			res[x] = elm[x]
	return res

def plot_message_del():
	n_groups = 5
	data = get_all_numbers()
	index = np.arange(n_groups)
	bar_width = 0.25
	barlist = plt.bar(index, map(float, data.values()), bar_width,
                 color='b',align='center', alpha=0.7)
	# barlist[0].set_color('r')
	# barlist[1].set_color('g')
	# barlist[2].set_color('m')
	# barlist[3].set_color('y')


	plt.xlabel('Routers')
	plt.ylabel('Delivered Probability')
	plt.title('Delivered Probability Chart')
	plt.xticks(index, data.keys())
	plt.show()


plot_message_del()