import csv
from src import db

filename = "units.csv"
default_fields = ["id", "name", "buildcostenergy", "buildcostmetal", "buildtime", "weapondefs"]

def write(**kwargs):
  query_args = {
    "filters": kwargs.get("filters", []),
  }
  fields = kwargs.get("select", default_fields)

  all_weapons = False
  if "all_weapons" in fields:
    fields.remove("all_weapons")
    all_weapons = True

  with open(filename, 'w', encoding="utf8") as f:
    writer = csv.writer(f)
    if all_weapons:
      writer.writerow(fields + ["weapon1", "type", "range", "aoe", "damage", "reload",
                                "weapon2", "type", "range", "aoe", "damage", "reload",
                                "weapon3", "type", "range", "aoe", "damage", "reload"])
    else:
      writer.writerow(fields)

    for (key, row) in db.query(**query_args):
      row = convert_to_list(row, fields, all_weapons)
      writer.writerow(row)
  
  print(f"Results output to {filename}")

def _format(row, key):
  if row.get(key) == None:
    return ""
  elif type(row[key]) is list:
    return ",".join(row[key])
  elif type(row[key]) is float:
    return "{:.1f}".format(row[key])
  else:
    return row[key]


def convert_to_list(row, output_fields, all_weapons):
  output = [_format(row, k) for k in output_fields]

  if all_weapons:
    for k, v in row.get("weapondefs", {}).items():
      # Filter out some weapons which do not abide by normal rules
      if k not in ["repulsor1", "disintegrator"] and "default" in v["damage"] \
          and v.get("explosiongenerator", "") != "custom:antinuke" and not v.get("paralyzer", False):
        output += [k, v["weapontype"], v["range"], v.get("areaofeffect", ""), v["damage"]["default"],
                   v.get("reloadtime", "")]

  return output

