import sys
import os

errtemplate = "Failed to create average energy report as "
ENERGY_LEVEL_REPORT = "EnergyLevelReport"
DEFAULT_SETTINGS_FILE = "default_settings.txt"

def process_energy_report(test_name):
    INPUT_PATH = "reports/%s_%s.txt" % (test_name, ENERGY_LEVEL_REPORT)
    if not os.path.exists(INPUT_PATH):
        print "Failed to create average energy report as no energy report was found for scenario \"%s\"." % test_name
        return

    OUTPUT_PATH = "reports/%s_Average%s.txt" % (test_name, ENERGY_LEVEL_REPORT)

    f_in = open(INPUT_PATH, 'r')
    avg_level_by_type_time = {}
    current_time = -1
    levels_by_type = {}
    for line in f_in:
        if line.startswith('['):
            if current_time != -1:
                # Store avg by type for each node type
                avg_level_by_type = {}
                for node_type in levels_by_type:
                    avg_level_by_type[node_type] = (
                        sum(levels_by_type[node_type]) /
                        len(levels_by_type[node_type]))
                avg_level_by_type_time[current_time] = avg_level_by_type
            current_time = int(line.strip().strip('[').strip(']'))
            levels_by_type = {}
        else:
            node, energy_level_str = line.strip().split(' ')
            energy_level = float(energy_level_str)
            node_type_length = 0
            while not node[node_type_length].isdigit():
                node_type_length += 1
            node_type = node[:node_type_length]
            if node_type not in levels_by_type:
                levels_by_type[node_type] = []
            levels_by_type[node_type].append(energy_level)

    if current_time != -1:
        avg_level_by_type = {}
        for node_type in levels_by_type:
            avg_level_by_type[node_type] = (
                sum(levels_by_type[node_type]) /
                len(levels_by_type[node_type]))
        avg_level_by_type_time[current_time] = avg_level_by_type

    f_in.close()

    f_out = open(OUTPUT_PATH, 'w')
    
    for time in sorted(avg_level_by_type_time):
        f_out.write("[%d]\n" % time)
        for node_type in avg_level_by_type_time[time]:
            f_out.write("%s\t%.4f\n" % (node_type, avg_level_by_type_time[time][node_type]))

    f_out.close()

def parse_settings(filename):
    file_content = os.popen('cat %s' % filename).read()
    scenario_name = None
    num_reports = -1
    reports = {}
    for line in file_content.split('\n'):
        if line.startswith("Scenario.name"):
            eq_sign_index = line.index('=')
            if eq_sign_index == -1:
                print "%sthe settings file's field with Scenario.name has no equal sign..." % errtemplate
                return False, None
            scenario_name = line[eq_sign_index+1:].strip()

        if line.startswith("Report.report"):
            eq_sign_index = line.index('=')
            if eq_sign_index == -1:
                print "%sone of the settings file's fields with Report.report* has no equal sign..." % errtemplate
                return False, None
            if not line[13:eq_sign_index].strip().isdigit():
                # Not a Report.reportX entry
                continue
            report_number = int(line[13:eq_sign_index].strip())
            report_name = line[eq_sign_index+1:].strip()
            if report_name not in reports:
                reports[report_name] = []
            reports[report_name].append(report_number)
    return scenario_name, num_reports, reports

def process_file(filename):
    if not os.path.exists(filename):
        print "%sthe given settings file does not exist." % errtemplate
        return False, None

    scenario_name, num_reports, reports = parse_settings(filename)

    if scenario_name is None:
        print "%sScenario.name was not found in %s" % (errtemplate, filename)
        return False, None

    if ENERGY_LEVEL_REPORT in reports:
        return True, scenario_name

    _, def_num_reports, def_reports = parse_settings(DEFAULT_SETTINGS_FILE)

    if ENERGY_LEVEL_REPORT not in def_reports:
        return False, scenario_name

    energy_level_report_number = def_reports[ENERGY_LEVEL_REPORT]
    if (energy_level_report_number not in reports.values() and
        num_reports == -1 or energy_level_report_number <= num_reports):
        return True, scenario_name
    return False, scenario_name

def check_generate_energy_report(sysargs):
    # Find what scenario is used
    args = [x for x in sysargs if x[-4:] == ".txt"]
    filename = DEFAULT_SETTINGS_FILE
    if len(args) == 1:
        filename = args[0]
    elif len(args) != 0:
        print "%sseveral .txt files were given as params." % errtemplate
        return

    # Find out if energy report is enabled
    energy_report_enabled, scenario_name = process_file(filename)
    if energy_report_enabled:
        process_energy_report(scenario_name)

if __name__ == "__main__":
    check_generate_energy_report(sys.argv)
