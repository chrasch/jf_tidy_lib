import os
import sys
import re
import shutil


prompt_header = (
  "Please clean up the following list of films and/or series and return the english names if possible."
  "The output pattern must be <name> <(year)>."
  "The output must be in the same order as the input."
  "Remove all extra dots, tags, release info or alternate names."
  "Preserve following file extentions: .mp4, .mkv, .divx, .avi, .flv, .vob."
  "Use the most widely accepted English release titles if possible, if not, preserve the old name."
  "Provide the output in plain text to copy to the clipboard."
)

def print_menu():
  print("\n----- Tidy Script -----")
  print("1) Generate output for LLM regex pattern generation")
  print("2) Read in the LLM output (create an output.txt file and paste LLM output in). Create a dry-run.txt for checking.")
  print("3) Rename and/or create the folders in the specified directory.")
  print("4) Abort")


def clear():
  os.system("cls" if os.name == "nt" else "clear")


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
          if os.path.isfile(full_path) and file.endswith(video_format):
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


def read_file(path, ignore_header, sanitize):
  output = []
  try:
    if ignore_header == "yes" and sanitize == "yes":  
      with open(path, 'r') as file:
        next(file)
        for line in file:
          tmp = sanitize_names(line)
          output.append(tmp)
    elif sanitize == "yes":
      with open(path, 'r') as file:
        for line in file:
          tmp = sanitize_names(line)
          output.append(tmp)
    elif ignore_header == "yes":
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


def streamline_names(collected_files):
  suggested_names = []
  junk_pattern = [
    r"\b\.(dvdrip|xvid|x264|x265|av1|dts|ac3|german|english|hq|dvd|rip|by.+|@\w+)\b",
    r"\b(1080p|720p|bluray|brrip|webrip)\b",
    r"\b(extended|messias)\b",
    r"(\(\))",
    r"(\[.*?\])"
  ]

  try:
    if collected_files:
      for f in collected_files:
        tmp = os.path.splitext(f)
        tmp2 = tmp[0]
        for j in junk_pattern:
          tmp2 = re.sub(j, "", tmp2, flags=re.IGNORECASE)
        tmp2 = re.sub(r"[._]", " ", tmp2)
        tmp2 = re.sub(r"\s+", " ", tmp2).strip()
        tmp2 = re.sub(r"((?<=\s)-(?!\s).+)", "", tmp2).strip()
        tmp2 = re.sub(r"-$", "", tmp2).strip()
        suggested_names.append(f + ' --> ' + tmp2 + tmp[1])
      print(suggested_names)
      return suggested_names
    else:
      print("Files not collected")
  except Exception as e:
    print(f"Error: {e}")


def write_to_file(output, f_type):
  try:
    if f_type == "prompt":
      with open('prompt.txt', 'w') as file:
        file.write(prompt_header + '\n')
        for f in output:
          file.write(f + '\n')
      print("prompt.txt written...")
    else:
      with open(f_type + '.txt', 'w') as file:
        for f in output:
          file.write(f + '\n')
      print(f_type + ".txt written...")
  except Exception as e:
    print(f"Error while writing file: {e}")


def main():
  while True:
    print_menu()
    menu_choice = input("Please choose one option: ").strip()

    if menu_choice == "1":
      print("Generating prompt for LLM (see prompt.txt)...\nCopy the content of prompt.txt in ChatGPT.")
      given_path = sys.argv[1]
      content_type = sys.argv[2]
      collected_data = read_folder(given_path, content_type)
      if collected_data:
        write_to_file(collected_data, 'prompt')
      else:
        print("No data found in directory.")
        break
    elif menu_choice =="2":
      print("Reading output of LLM...\n")
      renamed_data = read_file("./output.txt", "no", "yes")
      old_data = read_file("./prompt.txt", "yes", "no")
      if len(old_data) != len(renamed_data):
        clear()
        print("Lines old names: " + str(len(old_data)) + "\n")
        print("Lines renamed data: " + str(len(renamed_data)) + "\n")
        print("Content of the folder changed or the output of the LLM is wrong. Please redo the first step.")
        break
      else:
        clear()
        print("Generating a dry-run output for your review (see dry-run.txt). If the dry-run output is correct, continue with step 3.")
        dry_run = [f"{x} --> {y}" for x, y in zip(old_data, renamed_data)]
        write_to_file(dry_run, 'dry-run')
    elif menu_choice == "3":
      confirm = input("Are you sure? Did you check the dry-run file? Confirm y/n: ").strip().lower()
      if confirm =="y":
        print("confirm")  
      else:
        break
    elif menu_choice == "4":
      break         
    else:
      print("Invalid choice. Please choose a valid option: ")


if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Please provide a path and the content type.")
  else:
    main()
