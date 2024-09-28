git submodule foreach --quiet --recursive '
  if [[ "$name" == *"'"$2"'"* ]]; then
    '"$1"'
  fi
'

if [[ $? -ne 0 ]]; then
  echo "Error executing command in submodule '$2'"
  exit 1
fi

echo "Command successfully executed in submodule '$2'"
exit 0
