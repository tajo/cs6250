import sys
import os

errtemplate = "Failed to create average energy report as "

def process_energy_report(test_name):
    INPUT_PATH = "reports/%s_EnergyLevelReport.txt" % test_name
    if not os.path.exists(INPUT_PATH):
        print "Failed to create average energy report as no energy report was found for scenario \"%s\"." % test_name
        return

    OUTPUT_PATH = "reports/%s_AverageEnergyLevelReport.txt" % test_name

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

def process_file(filename):
    if not os.path.exists(filename):
        print "%sthe given settings file does not exist." % errtemplate
        return False, None
    file_content = os.popen('cat %s' % filename).read()
    for line in file_content.split('\n'):
        if line.startswith("Scenario.name"):
            eq_sign_index = line.index('=')
            if eq_sign_index == -1:
                print "%sthe settings file's field with Scenario.name has no equal sign..." % errtemplate
                return False, None
            scenario_name = line[eq_sign_index+1:].strip()
            return True, scenario_name
    print "%sScenario.name was not found in %s" % (errtemplate, filename)
    return False, None

def check_generate_energy_report(sysargs):
    # Find what scenario is used
    args = [x for x in sysargs if x[-4:] == ".txt"]
    filename = "default_settings.txt"
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
