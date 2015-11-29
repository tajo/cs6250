import sys
import os
import process_energy_report as proc
import matplotlib.pyplot as plt

PLOTS_FILENAME_PREFIX = "plots/"
HOURLY = 1
MINUTELY = 2

def generate_energy_plots(args):
	energy_report = proc.check_generate_energy_report(args, write=False)
	if energy_report is None:
		print ("Energy report not enabled. Aborting")
		return
	SAVE_FIGURES = 'plot' not in args
	PRUNE = 'prune' in args
	if PRUNE:
		print "Pruning plots"

	filename, (avg_level_by_type_time, dead_nodes_by_type_time) = energy_report
	result = parseFiles(filename)
	if result is None:
		return
	scenario_name, num_groups, group_to_id, group_to_initial_energy = result
	if not values_ok(num_groups, group_to_id, group_to_initial_energy):
		return
	groups = group_to_id.keys()

	avg_level_by_type_time[0] = {}
	dead_nodes_by_type_0 = {}
	total_node_count = {}
	
	for group in groups:
		group_id = group_to_id[group]
		group_initial_energy = group_to_initial_energy[group]
		avg_level_by_type_time[0][group_id] = group_initial_energy
		some_time = dead_nodes_by_type_time.keys()[0]
		group_total_nodes = (dead_nodes_by_type_time[some_time][group_id]['dead'] +
							 dead_nodes_by_type_time[some_time][group_id]['alive'])
		total_node_count[group_id] = group_total_nodes
		dead_nodes_by_type_0[group_id] = {'dead': 0, 'alive': group_total_nodes}
	dead_nodes_by_type_time[0] = dead_nodes_by_type_0

	## PLOT AVG ENERGY LEVELS
	group_ids = group_to_id.values()
	x_orig = sorted(avg_level_by_type_time.keys())
	ys = {}
	for group in groups:
		group_id = group_to_id[group]
		ys[group_id] = [avg_level_by_type_time[t][group_id] for t in x_orig]
	if PRUNE:
		for i, t in enumerate(x_orig):
			all_dead = True
			for group in groups:
				group_id = group_to_id[group]
				if avg_level_by_type_time[t][group_id] != 0:
					all_dead = False
			if all_dead:
				x_orig = x_orig[:min(i+2, len(x_orig))]
				for group in groups:
					group_id = group_to_id[group]
					ys[group_id] = ys[group_id][:min(i+2, len(x_orig))]
				break

	# Plot vs hours
	unit = HOURLY
	time_unit = 'hours'

	if unit==HOURLY:
		x = [t/3600.0 for t in x_orig]
	elif unit==MINUTELY:
		x = [t/60.0 for t in x_orig]

	plot(group_ids, x, ys, "AVG Energy Levels", "Energy Level", savefig=SAVE_FIGURES,
		 filename="%s_AVG_ENERGY_LEVELS" % scenario_name if SAVE_FIGURES else None,
		 time_unit=time_unit)

	## PLOT AVG PERCENT OF ENERGY LEFT
	for group_id in ys:
		ys[group_id] = [0 if ys[group_id][0] == 0.0 else 100.0*level / float(ys[group_id][0])
				        for level in ys[group_id]]
	plot(group_ids, x, ys, "AVG Energy Percentage", "Energy Percentage", savefig=SAVE_FIGURES,
		 filename="%s_AVG_ENERGY_PERCENTAGES" % scenario_name if SAVE_FIGURES else None,
		 time_unit=time_unit)
	print "Percent of Energy Left at End of Run:"
	for group_id in group_ids:
		print "%s:\t%.1f%%" % (
			group_id, 0 if ys[group_id][0] == 0.0 else 100*ys[group_id][-1] / ys[group_id][0]
		)

	### PLOT AVG ENERGY COMSUMPTION
	if unit==HOURLY:
		x_avg = [t/3600.0 for t in x_orig[1:]]
	elif unit==MINUTELY:
		x_avg = [t/60.0 for t in x_orig[1:]]

	ys = {}
	for group in groups:
		group_id = group_to_id[group]
		consumption_rates = []
		for i in xrange(1, len(x_orig)):
			prev = x_orig[i-1]
			current = x_orig[i]
			change = avg_level_by_type_time[prev][group_id] - avg_level_by_type_time[current][group_id]
			consumption_rates.append(change)
		ys[group_id] = consumption_rates
	plot(group_ids, x_avg, ys, "AVG Energy Consumption", "Energy Consumption", savefig=SAVE_FIGURES,
		 filename="%s_AVG_ENERGY_CONSUMPTION" % scenario_name if SAVE_FIGURES else None,
		 time_unit=time_unit)

	### PLOT NUM DEAD NODES
	x_orig = sorted(dead_nodes_by_type_time.keys())
	for group in groups:
		group_id = group_to_id[group]
		ys[group_id] = [dead_nodes_by_type_time[t][group_id]['dead'] for t in x_orig]
	if PRUNE:
		for i, t in enumerate(x_orig):
			all_dead = True
			for group in groups:
				group_id = group_to_id[group]
				if dead_nodes_by_type_time[t][group_id]['alive'] != 0:
					all_dead = False
			if all_dead:
				x_orig = x_orig[:min(i+2, len(x_orig))]
				for group in groups:
					group_id = group_to_id[group]
					ys[group_id] = ys[group_id][:min(i+2, len(x_orig))]
				break

	if unit==HOURLY:
		x = [t/3600.0 for t in x_orig]
	elif unit==MINUTELY:
		x = [t/60.0 for t in x_orig]

	plot(group_ids, x, ys, "# Dead Nodes", savefig=SAVE_FIGURES,
		 filename="%s_NUM_DEAD_NODES" % scenario_name if SAVE_FIGURES else None,
		 time_unit=time_unit)

	# PLOT PERCENT OF NODES ALIVE
	for group in groups:
		group_id = group_to_id[group]
		ys[group_id] = [100.0*dead_nodes_by_type_time[t][group_id]['alive'] /
						float(total_node_count[group_id]) for t in x_orig]
	for group in groups:
				group_id = group_to_id[group]
	plot(group_ids, x, ys, "% Alive Nodes", savefig=SAVE_FIGURES,
		 filename="%s_PERCENT_DEAD_NODES" % scenario_name if SAVE_FIGURES else None,
		 time_unit=time_unit)

def plot(group_ids, x, ys, title, ylabel=None, time_unit='min', savefig=False, filename=None):
	plt.figure(figsize=(10,8))
	plt.title(title, fontsize=12)
	plt.xlabel('Time (%s)' % time_unit)
	if ylabel is not None:
		plt.ylabel(ylabel)
	colors = ['b', 'g', 'r', 'c', 'm', 'k', 'y']
	lines = []
	for group_id, color in zip(group_ids, colors[:len(group_ids)]):
		group_line, = plt.plot(x, ys[group_id], color)
		lines.append(group_line)
		plt.plot(x, ys[group_id], "%so" % color)

	plt.legend(lines, group_ids, loc=0)
	plt.margins(0.02)
	if savefig:
		if filename is None:
			print "Ambiguous: asked to save figure but not given a filename. Fix this."
			return
		plt.savefig("%s%s" % (PLOTS_FILENAME_PREFIX, filename))
	else:
		if filename is not None:
			print "Ambiguous: asked not to save figure but given a filename. Fix this."
		plt.show()

def values_ok(num_groups, group_to_id, group_to_initial_energy):
	if num_groups == -1:
		print "Didn't find entry Scenario.nrofHostGroups, aborting"
		return False
	elif set(group_to_id.keys()) != set(group_to_initial_energy.keys()):
		print "Found different groups for groupIDs and groups' initial energy!"
		print "Group IDs: %s" % group_to_id
		print "Groups' initial energy levels: %s" % group_to_initial_energy
		return False
	elif len(group_to_id) > num_groups:
		print ("Found more entries for group IDs than there are supposed to be "
		       "groups. Is everything OK?")
		print "number of groups: %d" % num_groups
		print "group IDs: %s" % group_to_id
		return False
	elif len(group_to_initial_energy) > num_groups:
		print ("Found more entries for groups' initial energy levels than there "
			   "are supposed to be groups. Is everything OK?")
		return False
	return True

def parseFiles(filename):
	default_file_content = get_file_contents(proc.DEFAULT_SETTINGS_FILE)
	num_groups, group_to_id, group_to_initial_energy =\
		get_groups_values(default_file_content)
	scenario_name = None

	if filename != proc.DEFAULT_SETTINGS_FILE:
		file_content = get_file_contents(filename)
		scenario_name = get_scenario_name(file_content)
		num_groups2, group_to_id2, group_to_initial_energy2 =\
			get_groups_values(file_content)
		if num_groups2 != -1:
			num_groups = num_groups2
		if group_to_id2 is not None:
			for group in group_to_id2:
				group_to_id[group] = group_to_id2[group]
		if group_to_initial_energy2 is not None:
			for group in group_to_initial_energy2:
				group_to_initial_energy[group] = group_to_initial_energy2[group]
	else:
		scenario_name = get_scenario_name(default_file_content)
	if scenario_name is None:
		print ("Error: No scenario name (Scenario.name) found in %s!" %
			   filename if filename else proc.DEFAULT_SETTINGS_FILE)
		return None

	return scenario_name, num_groups, group_to_id, group_to_initial_energy

def get_scenario_name(file_content):
	scenario_name = None
	for line in file_content:
		if '=' in line:
			eq_sign_index = line.index('=')
			if line[:eq_sign_index].strip() == "Scenario.name":
				scenario_name = line[eq_sign_index+1:].strip()
				break
	return scenario_name

def get_groups_values(file_content):
	num_groups = -1
	group_to_id = {}
	group_to_initial_energy = {}
	if file_content is None:
		return num_groups, group_to_id, group_to_initial_energy
	for line in file_content:
		if '=' not in line:
			continue
		eq_sign_index = line.index('=')
		field = line[:eq_sign_index].strip()
		val = line[eq_sign_index+1:].strip()

		if field == 'Scenario.nrofHostGroups':
				num_groups = int(val)
		
		elif field.startswith('Group'):
			# Find initial energy, groupID of groups
			if field.endswith('.initialEnergy'):
				group_name = field[:field.index('.')]
				group_to_initial_energy[group_name] = float(val)

			elif field.endswith('.groupID'):
				group_name = field[:field.index('.')]
				group_to_id[group_name] = val

	return num_groups, group_to_id, group_to_initial_energy

def get_file_contents(filename):
	if not os.path.exists(filename):
		print "%sthe given settings file does not exist." % errtemplate
		return None
	file_content = os.popen('cat %s' % filename).read().split('\n')
	return file_content

if __name__ == "__main__":
	generate_energy_plots(sys.argv)