# File identification, renaming, and then if applicable, extraction
# of embedded/attached files

import os, sys
import argparse
import subprocess
import hashlib
import email
import shutil

import lib.msg as msg
import lib.eml as eml

try:
    import re2 as re
except:
    import re


output_path = "_OUTPUT"

def processTrid(trid_output):
    # Trid output is very wordy. Filter to extract determined file type only
    reg = re.compile("([0-9\.]+% \([a-zA-Z0-9\.]+\))") # regex for highest percentage, followed by file type
    a = reg.search(trid_output)
    if a:
        return a.group(0).split()[1]
    else:
        return False

def shutilCopy(new_out, myfile_full):
    fo = open(myfile_full, "rb")
    newfile = str(hashlib.sha256(fo.read()).hexdigest())
    fo.close()
    dest_file = "{0}/{1}".format(new_out, newfile)
    if not os.path.exists(dest_file):
        shutil.copyfile(myfile_full, dest_file)


def main():
    parser = argparse.ArgumentParser(description="Copy, rename, and extract files and their corresponding embedded/attached files")
    parser.add_argument("-p", "--path", help="Folder containing files to process")
    args = parser.parse_args()

    if args.path:
        input_path = args.path
    else:
        print "\nPlease specify path of files to process.\n"
        sys.exit()

    new_out = "{0}/{1}".format(input_path, output_path)
    if not os.path.exists(new_out):
        os.makedirs(new_out)
        
    for root, dirs, files in os.walk(input_path):
        for ffile in files:
            myfile = os.path.join(root, ffile)
            myfile_full = os.path.join(os.getcwd(), myfile)
            print "\n----- Processing {0}".format(myfile_full)

            # Call trid.exe for file type identification
            trid_output = subprocess.Popen(["trid.exe", myfile_full], stdout=subprocess.PIPE).communicate()[0]
            res = processTrid(trid_output)

            if res:
                if ".EML" in res:
                    content = email.message_from_file(open(myfile_full))
                    eml.extractAttachment(content, myfile_full, new_out)
                elif ".MSG" in res:
                    content = msg.Message(myfile_full, new_out)
                    content.save_attachments()
                else:
                    shutilCopy(new_out, myfile_full)
            else:
                shutilCopy(new_out, myfile_full)

if __name__ == "__main__":
    main()
