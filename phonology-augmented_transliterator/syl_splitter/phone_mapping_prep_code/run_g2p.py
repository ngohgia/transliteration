import os
import shutil
import subprocess

# Prepare translation models
def prep_models(path_to_g2p, models_path, max_order, train_dev_lex_file):
  if not os.path.exists(models_path):
    os.makedirs(models_path)

  models_file_path = os.path.join(models_path, "model")

  print("\t --- 1. Preparing translation model in: %s" % models_path)

  max_order = int(max_order)
  for i in range(max_order):
    print("\t--------------- Training Model %d---------------" % (i+1))
    if i == 0:
      training_cmd = "python " + path_to_g2p + "/g2p.py" + \
      "  --train " + train_dev_lex_file + \
      "  --devel 20% " + \
      "  --write-model " + models_file_path + "-1"
    else:
      training_cmd = "python " + path_to_g2p + "/g2p.py" + \
      "  --model " + models_file_path + "-" + str(i) + \
      "  --ramp-up" + \
      "  --train " + train_dev_lex_file + \
      "  --devel 20% " + \
      "  --write-model " + models_file_path + "-" + str(i+1)
    run_shell_command(training_cmd)

    print training_cmd

  print("\t--- PREPARING MODEL DONE!")

# Run test
def test_model(path_to_g2p, models_path, model_order, test_en_file, test_out):
  print("\n\t --- 2. Running tests")
  models_file_path = os.path.join(models_path, "model")
  
  test_cmd = "python " + path_to_g2p + "/g2p.py " + \
  "  --model " + models_file_path + "-" + str(model_order) + \
  "  --apply " + test_en_file + \
  "  > " + test_out

  run_shell_command(test_cmd)

  print("\t--- TEST DONE!")

# Helper function to run a shell command
def run_shell_command(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()