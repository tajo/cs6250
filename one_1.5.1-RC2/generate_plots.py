import scripts.generate_msgstats_plots as msgstats
import scripts.generate_energy_plots as energystats
import sys

if 'help' in sys.argv:
	print (
		"""
		Available args:
		\tplot\tIf this is given, plots are showed but not stored
		\tprune\tFor energy plots - if level stagnates at 0, cuts the graph,
		\t\te.g. if all nodes reach energy level 0 after half the time,
		\t\twe don't show the entire graph.
		\twnd=X\tIf given, will use this window (sec) for msgstats plots
		"""
	)
else:
	energystats.generate_energy_plots(sys.argv)
	msgstats.check_generate_msgstats_report(sys.argv)