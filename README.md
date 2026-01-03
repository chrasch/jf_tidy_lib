# **jf_tidy_lib**

This is a litte helper for tidying up a movie/series library.
It can process files and folders, rename those and add the release year. In case of files, new directories will be created and the files moved there.

---
How to use:
---

###Step 1:

Provide a directory and the mode with the -d and -m (files or folder) argument respectively. Optional: Set the flag --anime if you want to process anime content. In this case the ChatGPT prompt will be altered for better results.

### Step 2:

Let the script generate a LLM prompt (option 1 in menu). You will find a 'prompt.txt' file in same directory as this script.

### Step 3:

Copy the prompt into ChatGPT and let it generate the names and years. Sometimes it helps to prompt ChatGPT a few times until everything is correct.

### Step 4:

Copy the output of ChatGPT into 'output.txt', save the file, and continue with option 2 in the menu. This will generate a 'dry-run.txt' file. Review this file and make changes if needed. Don't forget to save!

### Step 5:

Continue with Step 3 in the menu. The script will use the data in 'dry-run.txt' and rename/move things accordingly. After finishing, a 'log.log' will be generated and the other files will be removed.
