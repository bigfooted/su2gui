import vtk
from su2_json import *
from datetime import date

from pathlib import Path
BASE = Path(__file__).parent

# remove empty lists from dictlist object
def remove_empty_lists(d):
  final_dict = {}
  for a, b in d.items():
     if b:
       if isinstance(b, dict):
         final_dict[a] = remove_empty_lists(b)
       elif isinstance(b, list):
         final_dict[a] = list(filter(None, [remove_empty_lists(i) for i in b]))
       else:
         final_dict[a] = b
  return final_dict


print("base = ",BASE)
# step 1: open .cfg file and read all lines that are not comments or empty
# step 2: couple multiline commands together
# step 3: convert to a uniform format: remove all opening and closing brackets and remove all commas
# step 4: split every line and make a proper list or value, also convert YES/NO and TRUE/FALSE
#         to true/false.