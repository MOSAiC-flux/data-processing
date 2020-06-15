#!/usr/local/bin/python3
# -*- coding: utf-8 -*-  

# ############################################################################################
# AUTHORS:
#
#   Michael Gallagher (CIRES/NOAA)  michael.r.gallagher@noaa.gov
#
# PURPOSE:
#
# This is a quick and dirty script that will find and replace all instances of a string
# in our source code files with another instance of a string. Yes this can be done with
# an IDE/text editor but it will save some time if you can run "./change_var_name.py" and
# be prompted quickly. It searches inside quotes and only works with variable names
# 
# HOWTO:
#
# Make sure you don't have the files open in an editor, then run this program! It will prompt
# you for input... maybe make sure you have a backup of the code just in case.
# 
# ###############################################################################################
import re

def main(): 

    asfs_files  = ("asfs_data_definitions.py", "create_level1_product_asfs.py", "create_level2_product_asfs.py")
    tower_files  = ("tower_data_definitions.py", "create_level1_product_tower.py", "create_level2_product_towerblevel.py")

    printline()
    print("\nThis is pretty stupid software, it will do exactly what you ask it to do...")
    print(" ... and maybe that's a problem, I put this together really quick\n")
    printline()

    code_one = "flux stations"
    code_two = "tower"
    print("Would you like to change a variable for: \n   1) {}\n   2) {}\n".format(code_one,code_two))
    source_choice = input(" ---> ")
    while source_choice != "1" and source_choice != "2":
        source_choice = input(" ... I'm sorry, please type 1 or 2 and press enter:")

    while True:

        source_choice = int(source_choice)
        if source_choice == 1 :
            data_name  = code_one
            code_files = asfs_files
        elif source_choice == 2 :
            data_name  = code_two
            code_files = tower_files

        file_in    = open(code_files[0], "rt")
        code_lines = file_in.read()
        file_in.close()

        while True:
            printline()
            print("Using a search string, what variable would you like to replace? \n")
            search_str = input(" ---> ")

            # if you have need: https://regex101.com/
            str_matches     = re.findall(r"'([a-zA-Z\d:_]*{}[a-zA-Z\d:_]*)'".format(search_str), code_lines, re.DOTALL)
            matches_nodupes = set(str_matches)

            while len(matches_nodupes) < 1 :
                printline()
                print("\nI'm sorry, we didn't find anything using your search string, try again? ")
                search_str      = input("\n ---> ")
                str_matches     = re.findall(r"'([a-zA-Z\d:_]*{}[a-zA-Z\d:_]*)'".format(search_str), code_lines, re.DOTALL)
                matches_nodupes = set(str_matches)

            printline()
            print("Which variable would you like to replace?\n")
            for i, match in enumerate(matches_nodupes):
                print("   {}) {}".format(i,match))
            print("   {}) NONE OF THE ABOVE".format(i+1))
            while True:
                try : choice_ind = int(input("\n ---> "))
                except ValueError: print("Try again, select a number above please!"); continue
                break

            if choice_ind != i+1:
                 break

        while True:
            old_str = "'{}'".format(list(matches_nodupes)[choice_ind])
            printline(startline="\n")
            print("What would you like to replace {} with?".format(old_str))
            str_choice = input("\n ---> ")
            str_choice = str_choice.replace('\'', '') # remove quotes 
            str_choice = str_choice.replace('"', '')
            new_str = "'{}'".format(str_choice)

            printline()
            print("\n !!! Replacing {}{}{} with {}{}{} !!! for lines:\n".format(bcolors.BOLD, old_str, bcolors.ENDC, \
                                                                                bcolors.BOLD, new_str, bcolors.ENDC))

            match_list = [] # list of line#s for each file [i_file][line_num] 
            for i_file, code_file in enumerate(code_files):
                match_list.append([])
                file_in    = open(code_file, "rt")
                code_lines = file_in.readlines()
                for i_line, code_line in enumerate(code_lines):
                    if code_line.rfind(old_str)  > -1: match_list[i_file].append(i_line)
                file_in.close()

            for i_file, code_file in enumerate(code_files):
                file_in    = open(code_file, "rt")
                code_lines = file_in.readlines()
                print("In {} file".format(code_files[i_file]))
                print("======================================")
                if len(match_list[i_file]) == 0 : print(" {} not found in this file\n".format(old_str))
                for i_match, line_num in enumerate(match_list[i_file]):
                    code_lines[line_num] = code_lines[line_num].replace(old_str, new_str) 
                    print("    {} -->\n{}".format(match_list[i_file][i_match], code_lines[line_num]))
                file_in.close()
                    
            yn_question = "!!! ARE YOU SURE YOU WANT TO CHANGE THESE LINES ??? (y/n)".format(bcolors.BOLD, old_str, bcolors.ENDC, \
                                                                                             bcolors.BOLD, new_str, bcolors.ENDC)
            
            if not ask_yn(yn_question): 
                printline()
                if ask_yn("Would you like to start from the beginning?"): continue
            else: break

        for i_file, code_file in enumerate(code_files):
            file_in    = open(code_file, "rt")
            code_lines = file_in.readlines()
            for i_match, line_num in enumerate(match_list[i_file]):
                code_lines[line_num] = code_lines[line_num].replace(old_str, new_str) 
                print("    {} -->\n{}".format(match_list[i_file][i_match], code_lines[line_num]))
            file_in.close()
            file_out = open(code_file, "wt")
            file_out.writelines(code_lines)
            file_out.close()

        printline()
        print("OK, you asked for it, all done.")
        printline()
        yn_answer = ask_yn("Would you like to rename another variable for the {} ? (y/n)".format(data_name))
        if not yn_answer: 
            printline()
            print("\n OK... thanks for your changes!!! Goodbye.\n")
            printline()
            exit()


def ask_yn(question):
    valid  = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    while True:
        print(question)
        choice = input("\n ---> ").lower()
        if choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n\n")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def printline(startline='',endline=''):
    print('{}--------------------------------------------------------------------------------------------{}'
    .format(startline, endline))

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
