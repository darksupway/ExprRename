from pathlib import Path
import re
import shutil as su
from datetime import datetime

def read_config():
    """Reads the config file in working directory, creates it from the default file or prints exeption.

    Returns:
        List: Read lines if config file was successfully read. Empty if not.
        Bool: True if file exists/could be read. False if not."""

    try:
        with open("!exprrename.config") as config_file:
            config = config_file.readlines()
        config = [x.rstrip("\n") for x in config if not x.startswith('#')] # removin comments and newlines
        return config, True
    except FileNotFoundError:
        print("Configuration file was not found. Creating new file from default...\n")
        default_config_path = Path(__file__).parent / "default.config"
        config_path = Path.cwd() / "!exprrename.config"
        su.copyfile(default_config_path, config_path)
        print("The configuration file was created.")
    except Exception as ex:
        print(ex)
    return [], False

def parse_config(config: list[str]):
    """Parse content of config file.
    
    Returns:
        Pattern: The regular expression for the file names of the files which should be renamed
        Tuple: Name group, substraction group, Output format (group1, separator, group2)
        List: Renaming rules"""

    arguments = [x.lstrip("~ ") for x in config if x.startswith("~ ")]
    rules = [x for x in config if not x.startswith("~ ")]

    if (arguments):
        file_rx = re.compile(arguments[0])

        try:
            namegr, subgr, gr_one, sep, gr_two = re.match("(\d), (\d), \"(\d)(.*)(\d)\"", arguments[1]).groups()
            output = (int(namegr), int(subgr), int(gr_one), sep, int(gr_two))
        except:
            output = None
    else:
        print("No arguments given. Empty RegEx and substraction number.")
        file_rx = None
        output = None
    
    return file_rx, output, rules

def parse_rules(rules: list[str]):
    """Parses rules and splits them in the substraction numbers, the old filename and the new filename with eventual subdir(s)

    Returns:
        Dict: Key ist 'oldname' and value is tuple ('newname','subnum')"""

    rx = re.compile("(?:\[([\d]+)\])?(.+)\|(.+)")
    rules_groups = [rx.match(x).groups() for x in rules if rx.match(x)]

    rule_dict = {}

    for rule in rules_groups:
        try:
            rule_dict.update({rule[1]: (rule[2], int(rule[0]))})
            #                 oldname: (newname, subnum)
        except:
            rule_dict.update({rule[1]: (rule[2], 0)})

    return rule_dict

def parse_filenames(rx: re.Pattern, subgr: int):
    """Parses files in current directory and splits filename of matches in its groups.

    Returns:
        List: full match, gr1, gr2, extention, len(subgr)   (subgr also converted to int)
        
    Exeptions:
        SyntaxError: Raised when subgroup is over 2 or is not a digit"""

    files = []

    for file in Path.cwd().iterdir():
        if file.is_file():
            files.append(file)
    
    m_files = [rx.match(x.name) for x in files if rx.match(x.name)]
    ext = [x.suffix for x in files if rx.match(x.name)]

    file_list = []

    for i in range(len(m_files)):
        file_list.append([m_files[i][0], m_files[i][1], m_files[i][2], ext[i]])
        
        if (subgr <= 2 and m_files[i][subgr].isdigit()):
            file_list[i].append(len(m_files[i][subgr]))
            file_list[i][subgr] = int(m_files[i][subgr])
        else:
            raise SyntaxError("Output format in config file faulty.")

    return file_list

def apply_rules(rule_dict: dict, file_list: list[list], namegr: int, subgr: int):
    """Applies rules from config file to filenames and numbers."""
    
    for i in range(len(file_list)):
        file_list[i][subgr] -= rule_dict[file_list[i][namegr]][1] #substract substraction number from number
        file_list[i][subgr] = str(file_list[i][subgr]).zfill(file_list[i][4])
        file_list[i][namegr] = rule_dict[file_list[i][namegr]][0] #change filename to newname

def split_namegroup(newname: str):
    """Splits directory and filename in namegroup.
    
    Returns:
        str: Subdirectory(s)
        str: Filenames"""

    newpath = Path(newname)

    subdir = newpath.parent
    name = newpath.stem

    return subdir, name

def rename_files(file_list: list, output: tuple):
    """Renames file with given output format. Creates subfolders if they do not exist."""

    namegr, subgr, gr_one, sep, gr_two = output
    #Name group: int, substraction group: int, Output format (group1: int, separator: str, group2: int)

    log = []

    for file in file_list:
        subdir, file[namegr] = split_namegroup(file[namegr])

        subdir_path = Path(subdir)

        if (not subdir_path.exists()):
            subdir_path.mkdir()

        current_file_location = Path(file[0]).resolve()
        new_file_location = subdir_path.resolve() / (file[gr_one] + sep + file[gr_two] + file[3])

        su.move(current_file_location, new_file_location)

        print("'" + current_file_location.name + "'\nwas moved to\n'" + new_file_location.parent.stem + "/" + new_file_location.name + "\n")

        log.append("\t'" + current_file_location.name + "' was moved to '" + new_file_location.parent.stem + "/" + new_file_location.name)

    Path("exprrename.log").write_text(datetime.now().strftime("%d.%m.%Y (%X)") + ":\n" + "\n".join(log))

############### Main ###############
config, config_exists = read_config()

if (config_exists and config):
    file_rx, output, rules = parse_config(config)

    if (rules and output):
        rule_dict = parse_rules(rules)

        try:
            file_list = parse_filenames(file_rx, output[1])
        except SyntaxError as ex:
            print(ex.msg)
            file_list = False

        if (file_list):
            # TODO: rename files
            apply_rules(rule_dict, file_list, output[0], output[1])
            rename_files(file_list, output)
    elif (not rules and output):
        print("There where no renaming rules in the configuration file. Aborting...")
    elif (rules and not output):
        print("There was no/a faulty output format in the configuration file. Aborting...")
    else:
        print("There where no rules and no/a faulty output format in the configuration file. Aborting...")
elif (config_exists and not config):
    print("The configuration file is empty or only consists of comments.")

print("-----\n End")