import csv
import os
import yaml
from pathlib import Path

cwd = os.getcwd()
duplicate_pairs = []

with open(str(Path.home()) + '/files.csv', 'r') as csvfile: # TODO: just check modified/added files?
    csvreader = csv.reader(csvfile)
    changed_files = next(csvreader)

    for file in changed_files:
        file_basename = os.path.basename(file)
        file_directory = os.path.dirname(file)
        print("\n\nChecking new changed file: " + file)

        # TODO: check for profile names being different

        if '/profiles/' in file:
            print('This is a profile! Comparing to other profiles...')
            os.chdir(file_directory)
            for current_profile in os.listdir("./"):
                new_profile = file_basename

                # compare to YAML files that are not the same file
                if current_profile != new_profile and Path(current_profile).suffix == ".yml":
                    print("\n---------COMPARISON-----------\ncomparing %s vs %s" % (new_profile, current_profile))
                    is_duplicate = False
                    with open(new_profile) as new_data, open(current_profile) as current_data:
                        new_profile_map = yaml.safe_load(new_data)
                        current_profile_map = yaml.safe_load(current_data)

                        # compare each component
                        if len(new_profile_map["components"]) == len(current_profile_map["components"]):
                            for y, new_component in enumerate(new_profile_map["components"]):
                                current_component = current_profile_map["components"][y]
                                print("checking component: " + new_component["id"])

                                # compare capabilities - top capability must match to be a duplicate
                                if  ((len(new_component["capabilities"]) == len(current_component["capabilities"])) and
                                    (new_component["capabilities"][0] == current_component["capabilities"][0])):
                                        # check if capabilities are a direct match with ordering
                                        if new_component["capabilities"] == current_component["capabilities"]:
                                            print("capabilities are the exact same with same ordering")
                                            is_duplicate = True
                                        # check if capabilities are the same with same top capability but different subsequent ordering
                                        # TODO: don't match for differing embedded configs
                                        else:
                                            new_cap_set = set(capability["id"] for capability in new_component["capabilities"])
                                            current_cap_set = set(capability["id"] for capability in current_component["capabilities"])

                                            if( new_cap_set == current_cap_set ):
                                                print ("capabilities are the same with different ordering")
                                                is_duplicate = True

                    if is_duplicate:
                        print("profiles are duplicates!")
                        duplicate_pairs.append((new_profile, current_profile))
                    else:
                        print("profiles are NOT duplicates!")
            print("\nEnd of comparison\n")


        else:
            print('not a profile, skipping...\n\n')

        os.chdir(cwd)
if duplicate_pairs:
    print("Duplicate profiles: ", duplicate_pairs)
    f = open("profile-comment-body.md", "w")
    f.write("Duplicate profile(s) detected:\n")
    for duplicate in duplicate_pairs:
        f.write("%s == %s\n" % (duplicate[0], duplicate [1]))
    f.write("\nPlease see [documenation] for more information on duplicate profiles.")
    f.close()
    exit("Duplicate profile detected.")
