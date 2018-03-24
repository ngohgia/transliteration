def create_syls_from_split_test_file(fi_name, fo_name):
  syls = []

  fi = open(fi_name, "r")

  for line in fi:
    for syl in [part.strip() for part in line.split(".")]:
      if syl not in syls:
        syls.append(syl)

  fo = open(fo_name, "w")
  for syl in syls:
    fo.write(syl + "\n")

  fi.close()
  fo.close()
