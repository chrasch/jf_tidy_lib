import os
import sys
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime


prompt_header = (
  "Please clean up the following list of films and/or series and return the english names if possible. "
  "Use the most widely accepted English release titles if possible, if not, preserve the old name. "
  "The output pattern must be <name> <(year)>. "
  "The output must be in the same order as the input. "
  "Remove all extra dots, tags, release info or alternate names. "
  "Preserve following file extentions: .mp4, .mkv, .divx, .avi, .flv, .vob. "
  "Provide the output in a code box as plain text to copy to the clipboard."
)


prompt_header_anime = (
  "Please parse and/or clean up the following list of films and/or series and return the romanized titles if possible. "
  "Use the most widely accepted japanese release titles if possible, if not, preserve the old name. "
  "The output pattern must be <name> <(year)>. "
  "The output must be in the same order as the input. "
  "Remove all extra dots, tags, release info or alternate names. "
  "Preserve following file extentions: .mp4, .mkv, .divx, .avi, .flv, .vob. "
  "If possible, use the following sources: anisearch.de, myanimelist.net, anidb.net in this order. Do NOT translate yourself. "
  "Do NOT enumerate. Do NOT provide sources. Provide the output in a code box as plain text to copy to the clipboard."
)


def print_menu():
  print("\n\n----- Tidy Script -----")
  print("1) Generate prompt for LLM.")
  print("2) Paste LLM output in output.txt. Read in the LLM output. Create a dry-run.txt for checking.")
  print("3) Rename and/or create the folders in the specified directory. Files will be moved to the new directories.")
  print("4) Exit\n\n")


def clear():
  os.system("cls" if os.name == "nt" else "clear")


def cleanup():
  working_files = ("./prompt.txt", "./output.txt", "./dry-run.txt")
  for file in working_files:
    if os.path.exists(file):
      os.remove(file)
    else:
      print(f"File '{file}' does not exist.")


def sanitize_names(name):
  name = name.strip()
  name = name.replace(": ", " - ")
  name = name.replace("/", "-")
  out = re.sub(r"\s+", " ", name)
  return out


def read_folder(path, content_type):
  video_format = (".mp4", ".mkv", ".divx", ".avi", ".flv", ".vob") 
  collected_files = []
  collected_folders = []

  try:
    match content_type:
      case "files":
        folder_content = os.listdir(path)
        for file in folder_content:
          full_path = os.path.join(path, file)
          if os.path.isfile(full_path) and file.lower().endswith(video_format):
            collected_files.append(file)
        return collected_files
      case "folder":
        folder_content = os.listdir(path)
        for folder in folder_content:
          full_path = os.path.join(path, folder)
          if os.path.isdir(full_path):
            collected_folders.append(folder)
        return collected_folders
      case "_":
        print("No content type specified.")
  except FileNotFoundError:
    print(f"Directory '{path}' not found.")
  except PermissionError:
    print(f"No permission in {path}")
  except Exception as e:
    print(f"Error: {e}")


def read_file(path, ignore_header = False, sanitize = False):
  output = []

  try:
    if ignore_header and sanitize:
      with open(path, 'r') as file:
        next(file)
        for line in file:
          tmp = sanitize_names(line)
          output.append(tmp)
    elif sanitize:
      with open(path, 'r') as file:
        for line in file:
          tmp = sanitize_names(line)
          output.append(tmp)
    elif ignore_header:
      with open(path, 'r') as file:
        next(file)
        for line in file:
          tmp = line.strip()
          output.append(tmp)
    else:
      with open(path, 'r') as file:
        for line in file:
          tmp = line.strip()
          output.append(tmp)
    return output
  except FileNotFoundError:
    print(f"File '{path}' not found.")
  except PermissionError:
    print("No permission to read the file.")
  except Exception as e:
    print(f"Error: {e}")


def write_to_file(output, f_type, flag = False):
  try:
    if f_type == "prompt" and flag:
      with open('prompt.txt', 'w') as file:
        file.write(prompt_header_anime + '\n')
        for f in output:
          file.write(f + '\n')
      print("prompt.txt for anime written...")
    elif f_type == "prompt":
      with open('prompt.txt', 'w') as file:
        file.write(prompt_header + '\n')
        for f in output:
          file.write(f + '\n')
      print("prompt.txt for movies written...")
    elif f_type == "log":
      with open(f_type + '.log', 'a') as file:
        file.write(output + '\n')
    else:
      with open(f_type + '.txt', 'w') as file:
        for f in output:
          file.write(f + '\n')
      print(f_type + ".txt written...")
  except Exception as e:
    print(f"Error while writing file: {e}")


def main(args):
  given_path = args.d
  content_type = args.m


  while True:
    print_menu()
    menu_choice = input("Please choose one option: ").strip()

    if menu_choice == "1":
      clear()
      print("Generating prompt for LLM (see prompt.txt)...\nCopy the content of prompt.txt in ChatGPT.")
      collected_data = read_folder(given_path, content_type)
      if collected_data:
        write_to_file(collected_data, 'prompt', args.anime)
        open("output.txt", "w").close()
      else:
        print("No data found in directory.")
        break
    elif menu_choice =="2":
      clear()
      print("Reading output of LLM...\n")
      renamed_data = read_file("./output.txt", False, True)
      old_data = read_file("./prompt.txt", True, False)
      if len(old_data) != len(renamed_data):
        clear()
        print("Lines old names: " + str(len(old_data)) + "\n")
        print("Lines renamed data: " + str(len(renamed_data)) + "\n")
        print("Content of the folder changed or the output of the LLM is wrong. Please redo the first step.")
        break
      else:
        clear()
        print("Generating a dry-run output for your review (dry-run.txt). You can edit dry-run.txt if you are not satisfied with the LLM output (don't forget to save). If the dry-run output is correct and ready, continue with step 3.")
        dry_run = [f"{x} --> {y}" for x, y in zip(old_data, renamed_data)]
        write_to_file(dry_run, 'dry-run')
    elif menu_choice == "3":
      confirm = input("Are you sure? Did you check the dry-run file? Confirm y/n: ").strip().lower()
      if confirm =="y":
        tmp = read_file("dry-run.txt", False, False)
        tidy_data = [item.split(" --> ") for item in tmp]
        if content_type == "folder":
          for folder_name in tidy_data:
            old_path = os.path.join(given_path, folder_name[0])
            new_path = os.path.join(given_path, folder_name[1])
            Path(old_path).rename(new_path)
            write_to_file(str(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ": " + old_path + " renamed to " + new_path), "log")
          print("Logfile written: log.log")
          cleanup()
          break
        elif content_type == "files":
          for file_names in tidy_data:
            old_path = os.path.join(given_path, file_names[0])
            name_for_folder = os.path.splitext(file_names[1])
            new_path = os.path.join(given_path, name_for_folder[0])
            new_path = os.path.join(new_path, file_names[1])
            new_folder_path = os.path.join(given_path, name_for_folder[0])
            os.makedirs(new_folder_path, exist_ok=True)
            write_to_file(str(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ": " + "Folder " + new_folder_path + " created."), "log")
            shutil.move(old_path, new_path)
            write_to_file(str(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ": " + old_path + " renamed and moved to " + new_path), "log")
          print("Logfile written: log.log")
          cleanup()
          break
      else:
        break
    elif menu_choice == "4":
      break         
    else:
      print("Invalid choice. Please choose a valid option: ")


if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser(
    description = """This is a litte helper for tidying up a movie/series library.
It can process files and folders, rename those and add the release year. In case of files, new directories will be created and the files moved there.
Usage:
Step 1: Provide a directory and the mode with the -d and -m (files or folder) argument respectively. Optional: Set the flag --anime if you want to process anime content. In this case the ChatGPT prompt will be altered for better results.
Step 2: Let the script generate a LLM prompt (option 1 in menu). You will find a 'prompt.txt' file in same directory as this script.
Step 3: Copy the prompt into ChatGPT and let it generate the names and years. Sometimes it helps to prompt ChatGPT a few times until everything is correct.
Step 4: Copy the output of ChatGPT into 'output.txt', save the file, and continue with option 2 in the menu. This will generate a 'dry-run.txt' file. Review this file and make changes if needed. Don't forget to save!
Step 5: Continue with Step 3 in the menu. The script will use the data in 'dry-run.txt' and rename/move things accordingly. After finishing, a 'log.log' will be generated and the other files will be removed. """,
    formatter_class = argparse.RawTextHelpFormatter
    )

  arg_parser.add_argument(
    "-d", "-directory",
    required = True,
    help = "Provide the directory which should be processed."
    )

  arg_parser.add_argument(
    "-m", "-mode",
    choices = ["files", "folder"],
    default = "",
    required = True,
    help = "What should be processed? 'files' or 'folders'"
    )

  arg_parser.add_argument(
    "--anime", "--a",
    help = "Use this flag if you want to process Anime content. The output will be largely in romanized, which works better with Anime metadata search.",
    action = "store_true",
    default = False
    )

  args = arg_parser.parse_args()

  main(args)
