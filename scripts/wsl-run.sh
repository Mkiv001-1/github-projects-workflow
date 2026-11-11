#!/usr/bin/env bash
# wsl-run.sh <file> [args...] — execute a payload FILE inside WSL.
#
# The F-008-safe pattern: write the payload to _tmp/ or %TEMP% with the
# write tool, then run the file — no metacharacters ever cross a shell
# boundary inside a `wsl ... -c "..."` string.
#
# Path handling: resolves relative paths against $PWD, then maps
#   //wsl.localhost/<distro>/<path>  ->  /<path>          (UNC cwd)
#   /<drive>/...                     ->  /mnt/<drive>/...  (Git Bash /c/)
#   /mnt/*, /home/*, /tmp/*          ->  passed through
set -euo pipefail

file="${1:?usage: wsl-run.sh <file> [args...]}"
shift

case "$file" in
  /*|?:*|?:\\*) abs="$file" ;;
  *)          abs="$PWD/$file" ;;
esac

case "$abs" in
  //wsl.localhost/*|//wsl\$/*)
    # //wsl.localhost/Ubuntu/home/wsl/x -> /home/wsl/x (drop //host/distro)
    wsl_path="/$(printf '%s' "$abs" | cut -d/ -f5-)" ;;
  /mnt/*|/home/*|/tmp/*|/etc/*|/usr/*|/var/*|/opt/*)
    wsl_path="$abs" ;;
  /[A-Za-z]/*)
    # Git Bash drive path: /c/Users/... -> /mnt/c/Users/...
    wsl_path="/mnt/${abs:1:1}${abs:2}" ;;
  *)
    wsl_path="$abs" ;;
esac

# MSYS_NO_PATHCONV: Git Bash would rewrite the POSIX path argument to a
# C:\Program Files\Git\... path when handing it to wsl.exe (F-008-family).
# WSL_DISTRO overrides the default distro for non-Ubuntu setups.
MSYS_NO_PATHCONV=1 exec wsl -d "${WSL_DISTRO:-Ubuntu}" -e bash -- "$wsl_path" "$@"
