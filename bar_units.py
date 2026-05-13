import csv
import sys
from src import github, db, output

default = (
  [],
  [
        "id", "name","description", "faction", "techlevel", "unitgroup", "built_by",
        "buildcostmetal", "buildcostenergy", "buildtime", "energymake", "metalmake", "workertime",
        "health_total", "speed",
        "dps_surface","dps_air", "dps_torpedo",
        "range_surface","range_air", "range_torpedo", "weapon_energy_per_sec",
        "explosion_damage", "explosion_aoe","selfdestruct_damage", "selfdestruct_aoe",
        "health", "health_reactive_armor", "emp_mult",
        "sightdistance","airsightdistance","radardistance", "sonardistance","jamdistance",
        "weapon1_name","weapon1_dps","weapon1_range","weapon1_target_only",
        "weapon2_name","weapon2_dps","weapon2_range","weapon2_target_only",
        "weapon3_name","weapon3_dps","weapon3_range","weapon3_target_only",
        "weapon4_name","weapon4_dps","weapon4_range","weapon4_target_only",
        "weapon5_name","weapon5_dps","weapon5_range","weapon5_target_only",
        "weapon6_name","weapon6_dps","weapon6_range","weapon6_target_only",
        "weapon7_name","weapon7_dps","weapon7_range","weapon7_target_only",
  ]
)

site = (
    [["armorcore", "is", True]],
    [
        "id", "name", "faction", "categories",
        "buildoptions", "buildcostmetal", "buildcostenergy", "energymake", "metalmake", "buildtime",
        "dps", "range", "dps_per_metal", "speed", "health",
        "radardistance", "height"
    ]
)

metalmake = (
    [
      ["armorcore", "is", True],
      ["energymake", ">", 5],
      ["type", "is", "building"]
    ],
    [
        "id", "name", "faction", "buildcostmetal", "buildcostenergy", "energymake"
    ]
)

"""
Example filters
All T2 tanks
filters = [
  ["type", "is", "tank"],
  ["techlevel", "is", 2],
  ["dps1", ">", 0]
] + default_filters,

Two specific tanks
filters = [
  ["name", "in", ["Bulldog", "Reaper"]],
],

# All T1 arm bots
filters = [
  ["type", "is", "bot"],
  ["techlevel", "is", 1],
  ["arm", "is", True],
] + default_filters,
"""

def main(filters, selection):
  # github._check_rate_limit()
  github.get_all_unit_files()

  output.write(
    filters = filters,
    select = selection
  )

if __name__ == '__main__':
  if len(sys.argv) == 1:
    filters, selection = default
  elif len(sys.argv) == 2:
    fname = sys.argv[1]
    if fname == "site":
      filters, selection = site
    elif fname == "metalmake":
      filters, selection = metalmake
    else:
      filters, selection = default
  
  main(filters, selection)
