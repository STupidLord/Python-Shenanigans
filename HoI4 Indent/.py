import os
from os import path as pth
import sys
import re
import json
import shutil
import logging
from time import strftime, localtime

'''
This is a little script to reformat and indent HoI4 state files, check config.json for configuration options

There is a logging option as you can see in the config and if you looked through the code, however it's off by default as it was only used for debugging.

Is this code janky? Yes. Could it have been done better? Probably. Do I have the will power to try and make it better? Nope.
'''

def configure():
    configf = open("config.json") # Load the config file
    config = json.load(configf)
    configf.close()
    
    global origin_dir # Declare the config vars as global vars
    origin_dir = config["origin"]
    global mod_dir
    mod_dir = config["output"]
    global logging_switch
    logging_switch = int(config["logging"])
    
    if(re.match(r'^\\', origin_dir)): # If origin or mod dir start with backslash (\) and no dot (.), add a dot so path can be found
        origin_dir = re.sub(r'(^\\)', '.\\1', origin_dir)
    if(re.match(r'^\\', mod_dir)):
        mod_dir = re.sub(r'(^\\)', '.\\1', mod_dir)
    
    match logging_switch: # Only worry about logging if it's actually on
        case 1:
            log_dname = config["log"]
            if not pth.exists(log_dname): # Make a folder for logs if there is not already one
                os.makedirs(log_dname)
            
            log_time = strftime("%d.%m.%y-%I.%M.%S", localtime()) # Current date and time for log name
            log_dir = pth.join(pth.normpath(os.getcwd()) + log_dname) # Log directory
            log_fname = pth.join(log_dir + log_time + '.log') # Lod directory plus log file name plus .log
                
            global logger
            logger = logging.getLogger(__name__)
            logging.basicConfig(filename=log_fname, level=logging.NOTSET,
                                format='[%(asctime)s;%(msecs)03d] [%(levelname)s]\n%(message)s',
                                datefmt='%I:%M:%S')
            cull_logs(log_dir, config["cull"])
            
    copy_tree()
    format()

def copy_tree():
    # Make sure the output folder doesn't already exist as otherwise the script doesn't work
    if pth.exists(mod_dir):
        while True: # While loop for incase user inputs something invalid, either closes or breaks out of loop after valid input 
            print(mod_dir + " already exists and needs to be deleted to continue, make sure nothing important is there.\n\nDelete? y/n") # Warn user that output already exists and needs to be removed
            user_input = input()
            if (re.match(r'y+e*s*', user_input, flags=re.I)): # Regex for user input qol, since I already have to use re anyways
                shutil.rmtree(mod_dir)
                break
            elif (re.match(r'n+o*', user_input, flags=re.I)):
                sys.exit("Aborting")
            print("Invalid input, try again")

    # Copy files from origin to output folder
    shutil.copytree(origin_dir, mod_dir)
    print("\nCopied " + origin_dir + " to " + mod_dir)
    return

def format():
    for directory, subdirectories, files in os.walk(mod_dir):
        for file in files:
            edited_file = open(pth.join(directory, file), "r")
            match logging_switch:
                case 1:
                    logger.info("Formatting: " + pth.join(directory, file) + "\n")
            new_content = ""
            open_curly = 0
            close_curly = 0
            
            debug_line = 0
            for line in edited_file:
                # Debug vars
                debug_line += 1
                debug_missing_curly = "No"
                debug_missing_curly_spacing = "No"
                debug_remove_curly = "No"
                debug_remove_empty_line = "No"
                debug_spacing = "No"
                debug_additional_tabbing = "No"
                debug_unqoute_name = "No"
                debug_unfold_curly_brackets = "No"
                debug_refractor = "Deleted line"
                
                # Temp Strings
                temp_content = ""
                temp2_content = ""
                
                # Function vars
                refactoring = 0
                
                if (re.search(r'\{|\}', line)): # Count num of curly brackets
                    if (re.search(r'\{.*\}', line)):
                        open_curly += 1
                        close_curly += 1
                    elif (re.search(r'\{', line)):
                        open_curly += 1
                    else:
                        close_curly += 1
                        
                if re.search(r'=[ \t]*\n', line): # Fix missing open curly bracket ({)
                    debug_missing_curly = "Yes"
                    temp_content += re.sub(r'=[ \t]+\n', '= {\n', line)
                    open_curly += 1
                    refactoring = 1
                    if (re.search(r'\s*[=+*-/#]+\s*', temp_content)): # If needed, space out the equal sign (=)
                        debug_missing_curly_spacing = "Yes"
                        temp2_content = temp_content
                        temp_content = ""
                        temp_content += re.sub(r'\s*[=+*-/#]+\s*', ' = ', temp2_content)
                        temp2_content = ""
                
                if (re.match(r'(^[ \t]*\{[ \t]*$)', line)): # Get rid of single open curly bracket
                    debug_remove_curly = "Yes"
                    new_content += re.sub(r'(^[ \t]*\{[ \t]*\n)', '', line)
                    open_curly -= 1
                    refactoring = 1
                    
                if (re.match(r'^[ \t]*\n', line)): # Get rid of empty lines
                    debug_remove_empty_line = "Yes"
                    new_content += re.sub(r'^[ \t]*\n', '', line)
                    refactoring = 2 # No indent needed for empty line, make sure to skip indenting no matter what
                elif (re.match(r'^[ \t]*\}[ \t]*$\n', line)) and open_curly == close_curly:
                    debug_remove_empty_line = "Yes"
                    new_content += re.sub(r'(^[ \t]*)(\})([ \t]*$\n)', '\\2', line)
                    refactoring = 2
                    
                if (re.search(r'\s*[=+*/#]+\s*', line)) and refactoring < 1: # Space out the sign and the left and right
                    debug_spacing = "Yes"
                    temp_content += re.sub(r'(\s*)([=+*/#]+)(\s*)', ' \\2 ', line)
                    refactoring = 1
                elif (re.search(r'\s*-+\s*', line)) and refactoring < 1: # Minus shouldn't be seperated from numbers
                    debug_spacing = "Yes"
                    temp_content += re.sub(r'(\s*)(-+\d*)(\s*)', ' \\2\\3', line)
                    refactoring = 1
                            
                if (re.search(r'name[ \t]*=[ \t]*".+"', line)): # Unqoute name e.g. name = "STATE_1" -> name = STATE_1
                    debug_unqoute_name = "Yes"
                    match refactoring:
                        case 0:
                            new_content += re.sub(r'(name[ \t]*=[ \t]*)(")(.+)(")', '\\1\\3', line)
                            refactoring = 1
                        case 1:
                            temp2_content += temp_content
                            temp_content = ""
                            temp_content += re.sub(r'(name[ \t]*=[ \t]*)(")(.+)(")', '\\1\\3', temp2_content)
                            temp2_content = ""
                            refactoring = 1
                            
                if (re.search(r'.*\{[ \t]*\w+\s*\w*[ \t]*\}', line)): # Unfold curly brackets if need be
                    debug_unfold_curly_brackets = "Yes"
                    match refactoring:
                        case 0:
                            new_content += re.sub(r'(.*\{)([ \t]*)(\w+\s*\w*)([ \t]*)(\})', '\\1\\n\\3\\n\\5', line)
                            refactoring = 2
                        case 1:
                            new_content += re.sub(r'(.*\{)([ \t]*)(\w+\s*\w*)([ \t]*)(\})', '\\1\\n\\3\\n\\5', temp_content)
                            refactoring = 2
                            
                match refactoring: # For those cases where nothing needs to be changed, otherwise stuff would be left out.
                    case 0:
                        new_content += line
                        debug_refractor = "Identical"
                    case 1:
                        new_content += temp_content
                        debug_refractor = "Refractored"
                                
                # Logging; is this a bit exessive? Yes. But does it look good? Yes.
                match logging_switch:
                    case 1:
                        logger.info("----------------------------------------\nLine: " + str(debug_line) + "\n'" + line + "'" +
                                    "\nMissing curly bracket: " + debug_missing_curly +
                                    "\nMissing curly bracket - Spacing: " + debug_missing_curly_spacing +
                                    "\nRemove curly bracket: " + debug_remove_curly +
                                    "\nRemove empty line: " + debug_remove_empty_line +
                                    "\nSpacing: " + debug_spacing +
                                    "\nAdditional tabbing: " + debug_additional_tabbing + 
                                    "\nUnqoute name: " + debug_unqoute_name +
                                    "\nUnfold curly brackets: " + debug_unfold_curly_brackets +
                                    "\nOutcome: " + debug_refractor +
                                    "\n----------------------------------------\n")
            
            match logging_switch:
                case 1:                          
                    logger.info("Open curly: " + str(open_curly) + ", Closed curly: " + str(close_curly) + "\n----------------------------------------\n\n\n")
                
            edited_file.close()
            edited_file = open(pth.join(directory, file), "w")
            edited_file.write(new_content)
            edited_file.close()
            
            indent(directory, file)

def indent(directory, file): # Indenting is done in a seperate function because it was easier to get it to work after the other work is saved        
    edited_file = open(pth.join(directory, file), "r")
    match logging_switch:
        case 1:
            logger.info("Indenting: " + pth.join(directory, file) + "\n")
    new_content = ""
    open_curly = 0
    
    debug_line = 0
    for line in edited_file:
        debug_line += 1
        x = 0
                
        if not (re.search(r'\{|\}', line)): # Indent if not curly bracket
            x += 1
        elif (re.search(r'\{', line)): # Count open curly brackets
            open_curly += 1
                
        match open_curly: # Additional indent for open curly brackets
            case 2:
                x += 1
            case 3:
                x += 2
            case 4:
                x += 3
            case 5:
                x += 4
                    
        if (re.search(r'\}', line)): # Count closed curly brackets, this comes after addition indent so it's in line
            open_curly -= 1
                    
        match x:
            case 1:
                new_content += re.sub(r'(\s*)([\S+\s+]+)', '\\t\\2', line) # Level 1 indent
            case 2:
                new_content += re.sub(r'(\s*)([\S+\s+]+)', '\\t\\t\\2', line) # Level 2
            case 3:
                new_content += re.sub(r'(\s*)([\S+\s+]+)', '\\t\\t\\t\\2', line) # Level 3
            case 4:
                new_content += re.sub(r'(\s*)([\S+\s+]+)', '\\t\\t\\t\\t\\2', line) # Level 4
            case 5:
                new_content += re.sub(r'(\s*)([\S+\s+]+)', '\\t\\t\\t\\t\\t\\2', line) # Level 5 (Max since it realistically shouldn't be any higher than this)
            case _:
                new_content += re.sub(r'(\s*)([\S+\s+]+)', '\\2', line) # No indent
            
        match logging_switch:
            case 1:
                logger.info("Line: " + str(debug_line) + "Indent level: " + str(x) +
                            "\n----------------------------------------")
                              
    edited_file.close()
    edited_file = open(pth.join(directory, file), "w")
    edited_file.write(new_content)
    return    

def cull_logs(folder_path, cull_at): # So that logs don't bloat too much if enabled, cull them after the set threshhold
    count = 0
    
    file_to_cull = None
    oldest_file_age = float('inf')
    for _, _, files in os.walk(folder_path):
        count += len(files)
        for file in files:
            file_path = pth.join(folder_path, file)
            file_age = pth.getmtime(file_path)
            if file_age < oldest_file_age:
                file_to_cull = file_path
                oldest_file_age = file_age
                    
    if count > int(cull_at):
        os.remove(file_to_cull)
        print("Removing: " + file_to_cull)
        cull_logs(folder_path, cull_at) # Rerun script to make sure any additional files are culled
    return

if __name__ == "__main__":
    configure()