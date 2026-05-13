# I've made this into a module with getter/setter functions so
# this can be changed into an actual DB later with less effort

from . import calculator, github

_data = {}

def put(key, value):
  value["id"] = key
  _data[key] = value

def get(key):
  return _data[key]

def getAllData():
  return _data

def preprocess_data(d):
  unit_explosions = github.get_explosions()
  print(unit_explosions)
  for k, row in d.items():
    yield (k, calculator.preprocess(k, row, unit_explosions, _data))

def query(**kwargs):
  d = preprocess_data(_data)

  d = _filter_commander_reachable(d)
  # filters = kwargs.get("filters", [])
  #
  # for f in filters:
  #   [field, comp, value] = f
  #
  #   if comp in ("eq", "is", "==", "="):
  #     d = _search_eq(d, field, value)
  #   elif comp == ">":
  #     d = _search_gt(d, field, value)
  #   elif comp == "in":
  #     d = _search_in(d, field, value)
  #   elif comp in ("not", "not eq"):
  #     d = _search_not_eq(d, field, value)
  #   elif comp == "not in":
  #     d = _search_not_in(d, field, value)
  #   elif comp == "does not contain":
  #     d = _search_not_contain(d, field, value)

  d = _post_process(dict(d))

  return d.items()

def _post_process(d):
  _add_built_by(d)
  return d

def _add_built_by(d):
  for k, v in d.items():
    buildables = v.get("buildoptions")
    if buildables is not None:
      for buildable in buildables:
        d[buildable]["built_by"].append(k)

def _filter_commander_reachable(d):
  commander_reachable = ["armcom", "corcom", "legcom"]
  for commander in map(get, commander_reachable):
    _add_all_buildable(commander_reachable, commander)
  for k, v in d:
    if k in commander_reachable:
      yield (k, v)

def _add_all_buildable(add_to, unit):
  if unit.get("buildoptions") is None: return

  for buildable in unit["buildoptions"].values():
    if not buildable in add_to:
      add_to.append(buildable)
      _add_all_buildable(add_to, get(buildable))

# def select(d, selection):
#   result = []
#   for k, row in d:
#     result.append(_get_fields(row, selection))
#   return result

# def _get_fields(row, selection):
#   return {k:v for k, v in row.items() if k in selection}

def _search_in(d, key, value_list):
  for k, v in d:
    if v[key] in value_list:
      yield (k, v)

def _search_gt(d, key, value):
  for k, v in d:
    if v[key] == None:
      continue
    if v[key] > value:
      yield (k, v)

def _search_eq(d, key, value):
  for k, v in d:
    if v[key] == value:
      yield (k, v)

def _search_not_in(d, key, value_list):
  for k, v in d:
    if v[key] == None:
      continue
    if v[key] not in value_list:
      yield (k, v)

def _search_not_eq(d, key, value):
  for k, v in d:
    if v[key] != value:
      yield (k, v)

def _search_not_contain(d, key, value):
  for k, v in d:
    if value not in v[key]:
      yield (k, v)
