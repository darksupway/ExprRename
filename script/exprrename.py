import sys
import os
import re
import shutil as su
import pandas as pd
from pandas.core.frame import DataFrame

def read_config():
    """Reads the config file in working directory, creates it from the default file or prints exeption.

    Returns:
        List: Read lines if config file was successfully read. Empty if not."""

    try:
        config_file = open("!exprrename.config", "r")
        config = config_file.readlines()
        config_file.close()
        return config
    except FileNotFoundError:
        print("Configuration file was not found. Creating new file from default...\n")
        default_config_path = os.path.join(os.path.dirname(__file__), "default.config")
        config_path = os.path.join(os.getcwd(), "!exprrename.config")
        su.copyfile(default_config_path, config_path)
    except Exception as ex:
        print(ex)
    return []

def parse_config(conf: list[str]):
    """Parse content of config file.
    
    Returns:
        List: Renaming rules
        Pattern: The regular expression for the file names of the files which should be renamed
        List: Groups consisting of numbers where something gets substracted"""

    config = [x.rstrip("\n") for x in conf]

    arguments = [x for x in config if x.startswith("~ ")]
    rules = [x for x in config if not x.startswith("~ ")]

    if (len(arguments) >= 1):
        file_rx = re.compile(arguments[0].lstrip("~ "))

        try:
            subgroup = arguments[1].lstrip("~ ")
            subgroup = int(subgroup)
        except:
            print("Could not parse the substraction number. Replaced with zero.")
            subgroup = 0
    else:
        print("No arguments given. Empty RegEx and substraction number.")
        file_rx = re.compile('')
        subgroup = 0
    
    return rules, file_rx, subgroup

def read_rules(rl):
    """Parses rules and splits them in the substraction numbers, the old filename and the new filename with eventual subdir(s)

    Returns:
        DataFrame: Rules split in columes: 'subnum', 'oldname' and 'newname'"""
    rx = re.compile("(?:\[([\d,]+)\])?(.+)\|(.+)")
    rules = [rx.match(x).groups() for x in rl if rx.match(x)]

    rules_df = pd.DataFrame(data=rules, columns=["subnum", "oldname", "newname"])
    rules_df["subnum"] = rules_df["subnum"].apply(lambda x: '0' if x == None else x)
    rules_df = rules_df.astype({"subnum": int})

    return rules_df

def read_filenames(rx):
    """Parses files in current directory and splits filename of matches in its groups.

    Returns:
        DataFrame: Matched filenames split in groups"""
    current_dir = os.scandir()
    files = []
    ext = []

    for element in current_dir:
        if element.is_file():
            files.append(element.name)
            ext.append(element.name)

    current_dir.close()

    files = [x for x in files if rx.match(x)]
    matched_files = [rx.match(x).groups() for x in files]
    ext = [os.path.splitext(x)[1] for x in ext if rx.match(x)]
    df = pd.DataFrame(data=matched_files, columns=range(1, len(matched_files[0])+1))

    return df, files, ext

def create_subnum_len_df(sg, df):
    """Creates dataframe which contains the length of the number strings in filenames."""
    len_df = pd.DataFrame(data=[len(x) for x in df[sg]], columns=[sg])
    df[sg] = [int(x) for x in df[sg]]
    return len_df

def apply_rules(sg, f_df: DataFrame, r_df: DataFrame):
    """Applies rules from config file. Substract substraction numbers and add 'newname' column in files_df."""
    len_df = create_subnum_len_df(sg, f_df)
    f_df["newname"] = ""

    for rule in r_df.itertuples():
        f_df.loc[f_df[1] == rule[2], sg] = f_df.loc[f_df[1] == rule[2], sg]-rule[1]
        f_df.loc[f_df[1] == rule[2], "newname"] = rule[3]
    
    f_df[sg] = f_df[sg].apply(str)

    for i in range(len(f_df)):
        f_df.loc[i, sg] = f_df.loc[i, sg].zfill(len_df.loc[i, sg])

def rename_files(root, files, ext, f_df, sg):
    for i in range(len(ext)):
        new_file = f_df.loc[i, "newname"] + " - " + f_df.loc[i, sg] + ext[i]
        
        if not os.path.exists(os.path.dirname(new_file)):
            os.mkdir(os.path.dirname(new_file))

        su.move(os.path.join(root, files[i]), os.path.join(root, new_file))
        print("'{}' was moved.".format(files[i]))

##### Main #####
current_dir = os.getcwd()
configlines = read_config()
config = [x for x in configlines if not x.startswith('#')]

if (config):
    rules, file_rx, subgroup = parse_config(config)

    if (rules):
        rules_df = read_rules(rules)
        files_df, files, ext = read_filenames(file_rx)
        
        apply_rules(subgroup, files_df, rules_df)

        rename_files(current_dir, files, ext, files_df, subgroup)
    else:
        print("There where no renaming rules in the config file. Aborting...")
elif (configlines and not config):
    print("The configuration file is empty or only consists of comments.")
else:
    print("The configuration file was created.")