import numpy as np
import matplotlib.pyplot as plt
import os
import json

names = ['Direct', 'FirstContact', 'Prophetrouter', 'Spray', 'Epidemic']

def get_fileName(prefix):
	base_dir = os.path.join("..", "data_reports")
	base_dir = os.path.join("..", base_dir)
	fileName = prefix + '_DeliveredMessagesReport'
	return os.path.join(base_dir, "{}.txt".format(str(fileName)))

def get_data():
	res = { } 
	for name in names:
		fileName = get_fileName(name)
		alist  = []
		with open(fileName,'r') as f : 
			f.readline()
			for line in f : 
				line = line.strip()
				parts = [p.strip() for p in line.split(" ")] 
				alist.append((parts[0],parts[4]))
		res[name]=alist

	return res

def get_distime(data, name):
	temp = data[name]
	return [int(float(elm[1])) for elm in temp]

def plot_distribution():
	data = get_data()

	# name = names[2]
	# dis_time = get_distime(data, name)
	# # dis_time = []
	# # for i in range(300):
	# # 	dis_time.append(np.random.randint(0,8627))

	# dis_time = np.asarray(dis_time)
	# # the histogram of the data
	# n, bins, patches = 


	# # plt.show()
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax1 = fig.add_subplot(511)
	ax2 = fig.add_subplot(512)
	ax3 = fig.add_subplot(513)
	ax4 = fig.add_subplot(514)
	ax5 = fig.add_subplot(515)

	# Turn off axis lines and ticks of the big subplot
	ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_color('none')
	ax.spines['left'].set_color('none')
	ax.spines['right'].set_color('none')
	ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

	# f, ((ax1, ax2, ax3, ax4, ax5)) = fig.add_subplot(5, 1, sharey='row')
	funcList = [ax1, ax2, ax3,ax4, ax5]
	for i in range(5):
		name = names[i]
		dis_time = get_distime(data, name)
		# print len(dis_time)
		funcList[i].hist(dis_time, 120,facecolor='g', alpha=0.75)
		# ax1.set_title('Sharing x per column, y per row')
		# funcList[i].xlabel('Delivery Time/s')
		# funcList[i].ylabel('Number of Instance')
		# funcList[i].title('Delivery Time Distribution')
		funcList[i].axis([0, 4000, 0, 130])
		funcList[i].text(3000, 50, name, fontsize=15)
		funcList[i].grid(True)

	ax.set_ylabel('Number of Messages')
	ax.set_xlabel('Delivery Time/s')

	plt.show()






plot_distribution()