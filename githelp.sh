#!/bin/bash

githelp_dir="$(dirname "$0")"

# Spara den aktuella venv-miljön (om någon)
current_venv=$(echo $VIRTUAL_ENV)

# Om en venv redan är aktiverad, lämna den först
# if [ -n "$current_venv" ]; then
#   deactivate
# fi

# Aktivera githelp's venv och kör programmet

#source ~/Programmering/main_hackaping_project_2025_04_04/venv/bin/activate
#python3 ~/Programmering/main_hackaping_project_2025_04_04/main.py "$@"

source "$githelp_dir/venv/bin/activate"
python3 "$githelp_dir/main.py" "$@"

# Efter att programmet är klart, gå tillbaka till den ursprungliga venv-miljön om det fanns en
if [ -n "$current_venv" ]; then
  source "$current_venv/bin/activate"
fi
