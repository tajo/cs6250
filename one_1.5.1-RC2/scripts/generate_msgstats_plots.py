import sys
import os
import matplotlib.pyplot as plt

errtemplate = "Failed to create msgstats reports as "
PLOTS_FILENAME_PREFIX = "plots/"
DEFAULT_SETTINGS_FILE = "default_settings.txt"
TOTAL_CONTACT_TIME_REPORT = "TotalContactTimeReport"
TOTAL_CONTACT_TIME = "reports/%s_" + ("%s.txt" % TOTAL_CONTACT_TIME_REPORT)
DELIVERED_MESSAGES_REPORT = "DeliveredMessagesReport"
DELIVERED_MESSAGES = "reports/%s_" + ("%s.txt" % DELIVERED_MESSAGES_REPORT)

# VARIABLES
# Time window for plots
WND = 3600

# time_consts
MINUTELY = 1
HOURLY = 2

def generate_msgstats_plots(settings_file, args):
	global WND
	scenario_name = get_scenario_name(settings_file)
	if scenario_name is None:
		return
	savefigs = 'plot' not in args
	var_args = [arg for arg in args if '=' in arg]
	for arg in var_args:
		eq_sign_index = arg.index('=')
		if arg[:eq_sign_index] == "wnd":
			val = arg[eq_sign_index+1:].strip()
			try:
				WND = int(val)
				print "WND is now %s, changed to %d" % (val, WND)
			except ValueError:
				print (("Couldn't parse arg for wnd \"%s\", \"%s\" is " +
					   "not an int") % (arg, val))

	plot_contact_time(scenario_name, settings_file, savefigs)
	plot_delivered_msgs_stats(scenario_name, settings_file, savefigs)

def plot_delivered_msgs_stats(scenario_name, settings_file, savefigs):
	if not report_enabled(settings_file, DELIVERED_MESSAGES_REPORT):
		print ("Can't plot %s since it's not enabled in %s" %
			   (DELIVERED_MESSAGES_REPORT, settings_file))
		return
	delivered_msgs = get_file_contents(DELIVERED_MESSAGES % scenario_name)
	headers = {header: i for i, header in
			   enumerate(delivered_msgs[0][2:].split('  '))}
	body = [line.split(' ') for line in delivered_msgs[1:-1]]

	# Plot total number of delivered packets over time
	plot_tot_num_delivered_pkts(scenario_name, headers, body, savefigs)

	# Plot number of packets delivered in each WND s window over time
	plot_pkt_delivery_rate(scenario_name, headers, body, savefigs)

	# Plot average delivery time over some X second window
	plot_avg_delivery_time(scenario_name, headers, body, savefigs)

	# Plot hop count? Path length?

def plot_avg_delivery_time(scenario_name, headers, body, savefigs):
	# Plot vs hours
	unit = HOURLY
	time_unit = 'hours'
	if WND % 3600 == 0:
		wnd_str = "%dh" % (WND/3600)
	elif WND % 60 == 0:
		wnd_str = "%dmin" % (WND/60)
	else:
		wnd_str = "%ds" % WND

	x = []
	y_wnd = []
	y_tot = []
	delivery_times = {}
	delivery_times_in_wnd = {}
	for line in body:
		t = float(line[headers['time']])
		delivery_time = float(line[headers['deliveryTime']])
		delivery_times_in_wnd = {
			past_t: delivery_times_in_wnd[past_t] for past_t in
			delivery_times_in_wnd.keys() if t-WND < past_t
		}
		delivery_times_in_wnd[t] = delivery_time
		delivery_times[t] = delivery_time
		x.append(t)
		y_wnd.append(sum(delivery_times_in_wnd.values()) /
			     float(len(delivery_times_in_wnd.values())))
		y_tot.append(sum(delivery_times.values()) /
			     float(len(delivery_times.values())))

	if unit==HOURLY:
		x = [t/3600.0 for t in x]
	elif unit==MINUTELY:
		x = [t/60.0 for t in x]

	plot(x, [y_wnd], "AVG delivery time (s) in a %s window" % wnd_str,
		 savefig=savefigs, time_unit=time_unit,
		 filename="%sAVG_DELIVERY_TIME_IN_WND" % scenario_name)
	plot(x, [y_tot], "AVG delivery time (s)",
		 savefig=savefigs, time_unit=time_unit,
		 filename="%sAVG_DELIVERY_TIME" % scenario_name)

def plot_tot_num_delivered_pkts(scenario_name, headers, body, savefigs):
	# Plot vs hours
	unit = HOURLY
	time_unit = 'hours'
	if WND % 3600 == 0:
		wnd_str = "%dh" % (WND/3600)
	elif WND % 60 == 0:
		wnd_str = "%dmin" % (WND/60)
	else:
		wnd_str = "%ds" % WND

	x = [float(line[headers['time']]) for line in body]
	y = [num for num in xrange(1, len(x)+1)]

	if unit==HOURLY:
		x = [t/3600.0 for t in x]
	elif unit==MINUTELY:
		x = [t/60.0 for t in x]

	plot(x, [y], "Total # packets delivered", savefig=savefigs,
		 filename="%sTOTAL_NUM_DELIVERED_PKTS" % scenario_name)

def plot_pkt_delivery_rate(scenario_name, headers, body, savefigs):
	# Plot vs hours
	unit = HOURLY
	time_unit = 'hours'
	if WND % 3600 == 0:
		wnd_str = "%dh" % (WND/3600)
	elif WND % 60 == 0:
		wnd_str = "%dmin" % (WND/60)
	else:
		wnd_str = "%ds" % WND

	x = [float(line[headers['time']]) for line in body]
	y = []
	transmission_times_in_wnd = []
	for t in x:
		transmission_times_in_wnd = [past_t for past_t in transmission_times_in_wnd
								 if t-WND < past_t]
		transmission_times_in_wnd.append(t)
		y.append(len(transmission_times_in_wnd))

	if unit==HOURLY:
		x = [t/3600.0 for t in x]
	elif unit==MINUTELY:
		x = [t/60.0 for t in x]

	plot(x, [y], "Total # packets delivered in a %s window" % wnd_str,
		 savefig=savefigs, time_unit=time_unit,
		 filename="%sNUM_DELIVERED_PKTS_IN_WND" % scenario_name)

def plot_contact_time(scenario_name, settings_file, savefigs):
	# Plot vs hours
	unit = HOURLY
	time_unit = 'hours'
	if not report_enabled(settings_file, TOTAL_CONTACT_TIME_REPORT):
		print ("Can't plot %s since it's not enabled in %s" %
			   (TOTAL_CONTACT_TIME_REPORT, settings_file))
		return
	tot_contact_time = get_file_contents(TOTAL_CONTACT_TIME % scenario_name)
	if tot_contact_time is None:
		# File not found
		return
	vals = [[float(t) for t in pair.split(' ')]
			for pair in tot_contact_time[1:-1]]
	x = [val[0] for val in vals]
	y_tot = [val[1] for val in vals]

	vals_wnd = [[0.0,0.0]]
	for i in xrange(len(vals)-1):
		current = vals[i+1]
		past = vals[i]
		vals_wnd.append([current[0], current[1] - past[1]])

	contact_times_in_wnd = []
	y_wnd = []
	for t, contact_time in vals_wnd:
		contact_times_in_wnd = {
			past_t: contact_times_in_wnd[past_t] for past_t in
			contact_times_in_wnd if t-WND < past_t
		}
		contact_times_in_wnd[t] = contact_time
		y_wnd.append(sum(contact_times_in_wnd.values()))

	# Plot vs hours
	unit = HOURLY
	time_unit = 'hours'
	if WND % 3600 == 0:
		wnd_str = "%dh" % (WND/3600)
	elif WND % 60 == 0:
		wnd_str = "%dmin" % (WND/60)
	else:
		wnd_str = "%ds" % WND

	if unit==HOURLY:
		x = [t/3600.0 for t in x]
	elif unit==MINUTELY:
		x = [t/60.0 for t in x]

	plot(x, [y_tot], "Total Contact Time (s)", savefig=savefigs,
		 filename="%sTOTAL_CONTACT_TIME" % scenario_name,
		 time_unit=time_unit)

	plot(x, [y_wnd], "Total Contact Time (s) in a %s window" % wnd_str,
		 savefig=savefigs, filename="%sTOTAL_CONTACT_TIME" % scenario_name,
		 time_unit=time_unit)

def report_enabled(filename, report):
	if not os.path.exists(filename):
		print "%sthe given settings file does not exist." % errtemplate
		return False

	num_reports, reports = parse_reports(filename)
	if report in reports:
		return True
	elif filename == DEFAULT_SETTINGS_FILE:
		return False

	def_num_reports, def_reports = parse_reports(DEFAULT_SETTINGS_FILE)

	if report not in def_reports:
		return False

	# Report in default settings file, now check if it is overridden
	# or if its report number > the number of reports.
	report_index = def_reports[report]
	if (report_index not in reports.values() and
		(num_reports == -1 or report_index <= num_reports)):
		return True
	return False

def parse_reports(filename):
    file_content = os.popen('cat %s' % filename).read()
    num_reports = -1
    reports = {}
    report_dot_report_len = len("Report.report")
    for line in file_content.split('\n'):
        if line.startswith("Report.report"):
            eq_sign_index = line.index('=')
            if eq_sign_index == -1:
                print ("%sone of the settings file's fields with " +
                	   "Report.report* has no equal sign..." % errtemplate)
                return -1, {}
            report_number_str =\
            	line[report_dot_report_len:eq_sign_index].strip()
            if not report_number_str.isdigit():
                # Not a Report.reportX entry
                continue
            report_number = int(report_number_str)
            report_name = line[eq_sign_index+1:].strip()
            if report_name not in reports:
                reports[report_name] = []
            reports[report_name].append(report_number)
    return num_reports, reports

def plot(x, ys, title, ylabel=None, time_unit='s', savefig=False,
		 filename=None, points=False, labels=None):
	plt.figure(figsize=(10,8))
	plt.title(title, fontsize=12)
	plt.xlabel('Time (%s)' % time_unit)
	if ylabel is not None:
		plt.ylabel(ylabel)
	colors = ['b', 'g', 'r', 'c', 'm', 'k', 'y']
	if labels is None:
		for i, color in enumerate(colors[:len(ys)]):
			plt.plot(x, ys[i], color)	
	else:
		lines = []
		for label, color in zip(labels, colors[:len(labels)]):
			line, = plt.plot(x, ys[label], color)
			lines.append(line)
			if points:
				plt.plot(x, ys[label], "%so" % color)
		plt.legend(lines, labels, loc=0)

	plt.margins(0.02)
	if savefig:
		if filename is None:
			print ("Ambiguous: asked to save figure but not given a " +
				   "filename. Fix this.")
			return
		plt.savefig("%s%s.pdf" % (PLOTS_FILENAME_PREFIX, filename))
	else:
		plt.show()


def check_generate_msgstats_report(sysargs, write=True):
    # Find what scenario is used
    file_args = [x for x in sysargs if x.endswith(".txt")]
    filename = DEFAULT_SETTINGS_FILE
    if len(file_args) == 1:
        filename = file_args[0]
    elif len(file_args) != 0:
        print "%sseveral .txt files were given as params." % errtemplate
        return None
    generate_msgstats_plots(
    	filename, [arg for arg in sysargs if arg not in file_args])

def get_scenario_name(filename):
	file_content = get_file_contents(filename)
	if file_content is None:
		# File not found
		return None
	scenario_name = None
	for line in file_content:
		if '=' in line:
			eq_sign_index = line.index('=')
			if line[:eq_sign_index].strip() == "Scenario.name":
				scenario_name = line[eq_sign_index+1:].strip()
				break
	return scenario_name

def get_file_contents(filename):
	if not os.path.exists(filename):
		print ("%sthe given file \"%s\" does not exist." %
			   (errtemplate, filename))
		return None
	file_content = os.popen('cat %s' % filename).read().split('\n')
	return file_content

if __name__ == "__main__":
	check_generate_msgstats_report(sys.argv)