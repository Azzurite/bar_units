import json
with open("/home/azzu/code/bar/language/en/units.json", "r") as f:
  unit_text = json.load(f)["units"]


def preprocess(key, row, unit_explosions, units):
  print("Preprocess: " + key)
  row["id"] = key
  row["name"] = unit_text["names"].get(key, "")
  row["description"] = unit_text["descriptions"].get(key, None)
  row["unitgroup"] = row.get("customparams", {}).get("unitgroup", None)
  row["subfolder"] = row.get("customparams", {}).get("subfolder", None)
  row["built_by"] = []
  row["techlevel"] = row.get("customparams", {}).get("techlevel", 1)
  row["emp_mult"] = row.get("customparams", {}).get("paralyzemultiplier", 1)
  row["health_reactive_armor"] = row.get("customparams", {}).get("reactive_armor_health", 0)
  row["reactive_armor_restore"] = row.get("customparams", {}).get("reactive_armor_restore", None)

  if "metalcost" in row:
    row["buildcostmetal"] = row["metalcost"]
  if "energycost" in row:
    row["buildcostenergy"] = row["energycost"]
  if "4" in row["id"]: row["techlevel"] = 4

  row["arm"] = key.startswith("arm")
  row["core"] = key.startswith("cor")
  row["leg"] = key.startswith("leg")
  row["armorcore"] = row["arm"] or row["core"]

  row["faction"] = key[:3]

  if "maxdamage" in row: row["health"] = row["maxdamage"]
  row["health_total"] = row["health"] + row["health_reactive_armor"]

  row["airsightdistance"] = row.get("airsightdistance", row["sightdistance"])
  row["jamdistance"] = row.get("radardistancejam", None)

  if not "workertime" in row: row["workertime"] = 0

  # TODO: Pelican has movement class HOVER5, but it is a bot. Also hovercraft are not represented.
  if "TANK" in row.get("movementclass", ""): row["type"] = "tank"
  elif "BOT" in row.get("movementclass", ""): row["type"] = "bot"
  else:
    if row.get("canfly", False) == True: row["type"] = "air"
    elif row.get("canmove", False) == True: row["type"] = "ship"
    else: row["type"] = "building"

  _define_weapons(row, units)

  cat_list = row.get("category", "").split(" ")
  row["categories"] = ", ".join(cat_list)

  build_dict = row.get("buildoptions", {})
  row["buildoptions"] = build_dict.values()

  row["metalmake"] = row.get("metalmake", None)
  row["energymake"] = row.get("energymake", None)

  row["radardistance"] = _none_if_zero(row.get("radardistance", None))
  row["sonardistance"] = _none_if_zero(row.get("sonardistance", None))
  row["maxvelocity"] = row.get("maxvelocity", None)

  row["speed"] = row["maxvelocity"] if row.get("maxvelocity") is not None else row.get("speed", None)
  row["height"] = "?"

  explosion = unit_explosions.get(row.get("explodeas", "").lower(), None)
  row["explosion_damage"] = None if explosion is None else _none_if_zero(explosion["damage"]["default"])
  if row["explosion_damage"] is not None:
    row["explosion_aoe"] = None if explosion is None else explosion["areaofeffect"] if explosion["damage"]["default"] != 0 else None

  selfdestruct = unit_explosions.get(row.get("selfdestructas", "").lower(), None)
  row["selfdestruct_damage"] = None if selfdestruct is None else _none_if_zero(selfdestruct["damage"]["default"])
  if row["selfdestruct_damage"] is not None:
    row["selfdestruct_aoe"] = None if selfdestruct is None else selfdestruct["areaofeffect"]

  return row

def _define_weapons(row, units):
  count = len(row.get("weapons", []))
  for idx in range(1, count+1):
    dps = _dps(row, idx, units)
    if dps <= 0: continue
    row[f"weapon{idx}_name"] = _name(row, idx)
    row[f"weapon{idx}_dps"] = dps
    row[f"weapon{idx}_range"] = _range(row, idx, units)
    row[f"weapon{idx}_target_only"] = row.get("weapons", {}).get(idx, {}).get("onlytargetcategory", None)
    row[f"weapon{idx}_target_bad"] = row.get("weapons", {}).get(idx, {}).get("badtargetcategory", None)

  row["dps_surface"] = _none_if_zero(_dps_ground(row, units))
  row["dps_air"] = _none_if_zero(_dps_air(row, units))
  row["dps_torpedo"] = _none_if_zero(_dps_torpedo(row, units))
  if row["dps_surface"] is not None:
    row["range_surface"] = _none_if_zero(_range_ground(row, units))
  if row["dps_air"] is not None:
    row["range_air"] = _none_if_zero(_range_air(row, units))
  if row["dps_torpedo"] is not None:
    row["range_torpedo"] = _none_if_zero(_range_torpedo(row, units))

  row["weapon_energy_per_sec"] = _none_if_zero(_weapon_energy_consumption(row))

def _none_if_zero(num):
  return num if num != 0 else None

def _weapon_energy_consumption(row):
  if "weapondefs" not in row: return 0

  eps = 0
  for key, val in row.get("weapons", {}).items():
    weapon = row["weapondefs"][val["def"].lower()]
    eps += _calc_eps(weapon)

  return eps

def _name(row, x):
  if "weapondefs" not in row: return None
  if len(row["weapons"]) < x: return None

  for key, val in row.get("weapons", {}).items():
    if key == x:
      return val["def"].lower()

  return None


def _calc_eps(weapon):
  if "reloadtime" not in weapon: return 0
  if weapon["reloadtime"] <= 0: return 0
  if "energypershot" not in weapon: return 0

  return weapon["energypershot"] / weapon["reloadtime"]

def _dps_ground(row, units):
  if "weapondefs" not in row: return 0

  dps = 0
  for key, val in row.get("weapons", {}).items():
    if val.get("onlytargetcategory", "") == "" or "SURFACE" in val.get("onlytargetcategory", "") or (not "VTOL" in val.get("onlytargetcategory", "") and not "MINE" in val.get("onlytargetcategory", "") and not "UNDERWATER" in val.get("onlytargetcategory", "")):
      weapon = row["weapondefs"][val["def"].lower()]
      dps += _calc_dps(weapon, units)

  return dps

def _dps_air(row, units):
  if "weapondefs" not in row: return 0

  dps = 0
  for key, val in row.get("weapons", {}).items():
    if val.get("onlytargetcategory", "") == "" or "VTOL" in val.get("onlytargetcategory", "") or (not "SURFACE" in val.get("onlytargetcategory", "") and not "MINE" in val.get("onlytargetcategory", "") and not "UNDERWATER" in val.get("onlytargetcategory", "")):
      weapon = row["weapondefs"][val["def"].lower()]
      dps += _calc_dps(weapon, units, "vtol")

  return dps

def _dps_torpedo(row, units):
  if "weapondefs" not in row: return 0

  dps = 0
  for key, val in row.get("weapons", {}).items():
    weapon = row["weapondefs"][val["def"].lower()]
    if "TorpedoLauncher" in weapon.get("weapontype", ""):
      dps += _calc_dps(weapon, units)

  return dps

def _range_ground(row, units):
  if "weapondefs" not in row: return 0

  r = 0
  for key, val in row.get("weapons", {}).items():
    if val.get("onlytargetcategory", "") == "" or "SURFACE" in val.get("onlytargetcategory", "") or (not "VTOL" in val.get("onlytargetcategory", "") and not "MINE" in val.get("onlytargetcategory", "") and not "UNDERWATER" in val.get("onlytargetcategory", "")):
      weapon = row["weapondefs"][val["def"].lower()]
      r = max(r, weapon.get("range", 0))

  return r

def _range_air(row, units):
  if "weapondefs" not in row: return 0

  r = 0
  for key, val in row.get("weapons", {}).items():
    if val.get("onlytargetcategory", "") == "" or "VTOL" in val.get("onlytargetcategory", "") or (not "SURFACE" in val.get("onlytargetcategory", "") and not "MINE" in val.get("onlytargetcategory", "") and not "UNDERWATER" in val.get("onlytargetcategory", "")):
      weapon = row["weapondefs"][val["def"].lower()]
      r = max(r, weapon.get("range", 0))

  return r

def _range_torpedo(row, units):
  if "weapondefs" not in row: return 0

  r = 0
  for key, val in row.get("weapons", {}).items():
    weapon = row["weapondefs"][val["def"].lower()]
    if "TorpedoLauncher" in weapon.get("weapontype", ""):
      r = max(r, weapon.get("range", 0))

  return r

def _dps(row, x, units):
  if "weapondefs" not in row: return 0
  if len(row["weapons"]) < x: return 0

  weapon = {}
  for key, val in row.get("weapons", {}).items():
    if key == x:
      damage_type = "default"
      if "VTOL" in val.get("onlytargetcategory", ""):
        damage_type = "vtol"
      weapon = row["weapondefs"][val["def"].lower()]
      return _calc_dps(weapon, units, damage_type)
  return 0


def _calc_dps(weapon, units, damage_type = "default"):
  if "reloadtime" not in weapon: return 0
  if weapon["reloadtime"] <= 0: return 0
  if damage_type not in weapon["damage"] and "default" not in weapon["damage"]: return 0
  if weapon.get("interceptor", 0) == 1: return 0

  damage = weapon["damage"].get(damage_type, weapon["damage"].get("default", 0))

  dps = damage / weapon["reloadtime"]
  dps = dps * weapon.get("burst", 1) * weapon.get("projectiles", 1)

  carried_unit = weapon.get("customparams", {}).get("carried_unit", None)
  if carried_unit is not None:
    u = units[carried_unit]
    dps += _dps(u, 1, units) * weapon["customparams"]["maxunits"]

  return dps

def _range(row, x, units):
  if "weapondefs" not in row: return 0
  if len(row["weapons"]) < x: return 0

  weapon = {}
  for key, val in row.get("weapons", {}).items():
    if key == x:
      weapon = row["weapondefs"][val["def"].lower()]

  if "range" not in weapon: return 0
  return weapon["range"]
