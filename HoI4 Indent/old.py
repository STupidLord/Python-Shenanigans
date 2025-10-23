import os
from os import path as pth
import sys
import re
import json
import shutil
import logging
from time import strftime, localtime

def configure():
    configf = open("config.json") # Load the config file
    config = json.load(configf)
    configf.close()
    
    global origin_dir # Declare the config vars as global vars
    origin_dir = config["origin"]
    global mod_dir
    mod_dir = config["output"]
    
    if not pth.exists('.\\logs\\'): # Make a folder for logs if there is not already one
        os.makedirs('.\\logs\\')
    
    log_time = strftime("%d.%m.%y-%I.%M.%S", localtime()) # Current date and time for log name
    log_dir = pth.join(pth.normpath(os.getcwd() + pth.sep), 'logs') # Log directory
    log_fname = pth.join(log_dir, log_time + '.log') # Lod directory plus log file name plus .log
    global logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=log_fname, level=logging.NOTSET,
                        format='[%(asctime)s;%(msecs)03d] [%(levelname)s]\n%(message)s',
                        datefmt='%I:%M:%S')
    copy_tree()

def copy_tree():
    # Make sure the output folder doesn't already exist as otherwise the script doesn't work
    if pth.exists("." + mod_dir):
        while True: # While loop for incase user inputs something invalid, either closes or breaks out of loop after valid input 
            print(mod_dir + " already exists and needs to be deleted to continue, make sure nothing important is there.\n\nDelete? y/n") # Warn user that output already exists and needs to be removed
            user_input = input()
            if (re.match(r'y+e*s*', user_input, flags=re.I)): # Regex for user input qol, since I already have to use re anyways
                shutil.rmtree("." + mod_dir)
                break
            elif (re.match(r'n+o*', user_input, flags=re.I)):
                sys.exit("Aborting")
            print("Invalid input, try again")

    # Copy files from origin to output folder
    shutil.copytree(origin_dir, "." + mod_dir)
    print("Copied " + origin_dir + " to " + mod_dir)
    
    indent()

def indent():
    for directory, subdirectories, files in os.walk("." + mod_dir):
        for file in files:
            edited_file = open(pth.join(directory, file), "r")
            logger.info("Indenting: " + pth.join(directory, file) + "\n")
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
                debug_remove_spaces = "No"
                debug_unqoute_name = "No"
                debug_unfold_curly_brackets = "No"
                debug_indent = "No"
                
                # Temp Strings
                temp_content = ""
                temp2_content = ""
                
                # Function vars
                refactoring = 0
                x = 0
                
                if not (re.search(r'\{|\}', line)): # indent once if it does NOT have any curly brackets
                    x += 1
                else: # Count num of curly brackets
                    if (re.search(r'\{.*\}', line)):
                        open_curly += 1
                        close_curly += 1
                    elif (re.search(r'\{', line)):
                        open_curly += 1
                    else:
                        close_curly += 1
                        
                if re.search(r'=[ \t]*\n', line):
                    debug_missing_curly = "Yes"
                    temp_content += re.sub(r'=[ \t]+\n', '= {\n', line)
                    open_curly += 1
                    x -= 1
                    refactoring = 1
                    if (re.search(r'\s*[=+*-/#]+\s*', temp_content)):
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
                    
                if (re.search(r'\s*[=+*-/#]+\s*', line)) and refactoring < 1:
                    debug_spacing = "Yes"
                    temp_content += re.sub(r'(\s*)([=+*-/#]+)(\s*)', ' \\2 ', line)
                    refactoring = 1
                
                if (re.match(r'(^[ \t]+)(.+)', line)):
                    match refactoring:
                        case 0:
                            debug_remove_spaces = "Yes"
                            temp_content += re.sub(r'(^[ \t]+)(.+)', '\\2', line) # Make sure lines have no spaces or tabs before them already
                            refactoring = 1
                        case 1:
                            debug_remove_spaces = "Yes - Refractor"
                            temp2_content += temp_content
                            temp_content = ""
                            temp_content += re.sub(r'(^[ \t]+)(.+)', '\\2', temp2_content)
                            temp2_content = ""
                            
                if (re.search(r'name[ \t]*=[ \t]*".+"', line)):
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
                            
                if open_curly > 1:
                    debug_additional_tabbing = "Yes"

                    detab_amount = close_curly - 1 # Subtract one level of indent per close curly bracket (-1)
                    for i in range(detab_amount):
                        x -= 1
                        
                    match open_curly: # Additional indent for open curly brackets
                        case 2:
                            x += 1
                        case 3:
                            x += 2
                        case 4:
                            x += 3
                        case 5:
                            x += 4
                            
                if (re.search(r'.*\{[ \t]*\w+[ \t]*\}', line)):
                    debug_unfold_curly_brackets = "Yes"
                    match refactoring:
                        case 0:
                            match x:
                                case 1:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\1\\n\\t\\t\\3\\n\\t\\5', line)
                                case 2:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\1\\n\\t\\t\\t\\3\\n\\t\\t\\5', line)
                                case 3:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\t\\1\\n\\t\\t\\t\\t\\3\\n\\t\\t\\t\\5', line)
                                case 4:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\t\\t\\1\\n\\t\\t\\t\\t\\t\\3\\n\\t\\t\\t\\t\\5', line)
                                case 5:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\t\\t\\t\\1\\n\\t\\t\\t\\t\\t\\t\\3\\n\\t\\t\\t\\t\\t\\5', line)
                                case _:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\1\\n\\t\\3\\n\\5', line)
                            refactoring = 2
                        case 1:
                            match x:
                                case 1:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\1\\n\\t\\t\\3\\n\\t\\5', temp_content)
                                case 2:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\1\\n\\t\\t\\t\\3\\n\\t\\t\\5', temp_content)
                                case 3:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\t\\1\\n\\t\\t\\t\\t\\3\\n\\t\\t\\t\\5', temp_content)
                                case 4:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\t\\t\\1\\n\\t\\t\\t\\t\\t\\3\\n\\t\\t\\t\\t\\5', temp_content)
                                case 5:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\t\\t\\t\\t\\t\\1\\n\\t\\t\\t\\t\\t\\t\\3\\n\\t\\t\\t\\t\\t\\5', temp_content)
                                case _:
                                    new_content += re.sub(r'(.*\{)([ \t]*)(\w+)([ \t]*)(\})', '\\1\\n\\t\\3\\n\\5', temp_content)
                            refactoring = 2
                
                match refactoring: # Indent normally if not refactoring, otherwise indent with temp content (helps avoid duped lines) In this case 'refractoring' is used to refer to having to use the var temp_content
                    case 0:
                        debug_indent = "Yes"
                        match x:
                            case 1:
                                new_content += re.sub(r'(^.+)', '\\t\\1', line) # Level 1 indent
                            case 2:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\1', line) # Level 2
                            case 3:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\t\\1', line) # Level 3
                            case 4:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\t\\t\\1', line) # Level 4
                            case 5:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\t\\t\\t\\1', line) # Level 5 (Max since it realistically shouldn't be any higher than this)
                            case _:
                                new_content += re.sub(r'(^.+)', '\\1', line) # No indent           
                    case 1:
                        debug_indent = "Yes"
                        match x:
                            case 1:
                                new_content += re.sub(r'(^.+)', '\\t\\1', temp_content) # Level 1 indent
                            case 2:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\1', temp_content) # Level 2
                            case 3:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\t\\1', temp_content) # Level 3
                            case 4:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\t\\t\\1', temp_content) # Level 4
                            case 5:
                                new_content += re.sub(r'(^.+)', '\\t\\t\\t\\t\\t\\1', temp_content) # Level 5 (Max since it realistically shouldn't be any higher than this)
                            case _:
                                new_content += re.sub(r'(^.+)', '\\1', temp_content) # No indent
                                
                # Logging; is this a bit exessive? Yes. But does it look good? Yes.
                logger.info("----------------------------------------\nLine: " + str(debug_line) + "\n'" + line + "'" +
                            "\nMissing curly bracket: " + debug_missing_curly +
                            "\nMissing curly bracket - Spacing: " + debug_missing_curly_spacing +
                            "\nRemove curly bracket: " + debug_remove_curly +
                            "\nRemove empty line: " + debug_remove_empty_line +
                            "\nSpacing: " + debug_spacing +
                            "\nAdditional tabbing: " + debug_additional_tabbing + 
                            "\nRemove spaces: " + debug_remove_spaces + 
                            "\nUnqoute name: " + debug_unqoute_name +
                            "\nUnfold curly brackets: " + debug_unfold_curly_brackets +
                            "\nIndented: " + debug_indent +
                            "\nRefractor level: " + str(refactoring) + " Indent level: " + str(x) +
                            "\n----------------------------------------\n")
                                        
            logger.info("Open curly: " + str(open_curly) + ", Closed curly: " + str(close_curly) + "\n----------------------------------------\n\n\n")
            #print(new_content)
                
            edited_file.close()
            edited_file = open(pth.join(directory, file), "w")
            edited_file.write(new_content)

if __name__ == "__main__":
    configure()