set shell := ["zsh", "-cu"]

tq := require("tq")
ruff := require("ruff")
find := require("find")
cat := require("cat")
cut := require("cut")
rm := require("rm")
echo := require("echo")
chmod := require("chmod")

default:
  @just --list

script:
  #!/usr/bin/env bash
  set -euo pipefail
  if [[ -n "${DEBUG:-}" ]]; then
    set -x
  fi
  echo "Creating a script file..."
  PROJECT_NAME="$(tq --file pyproject.toml --raw '.project.name')"
  PROJECT="${PROJECT_NAME//-/_}"
  CONCAT_FILE="${PROJECT_NAME}_concat.py"
  TMP_SCRIPT_FILE="${PROJECT_NAME}_tmp.py"
  just clean "${PROJECT_NAME}"
  just clean "${CONCAT_FILE}"
  just clean "${TMP_SCRIPT_FILE}"
  find "{{ justfile_directory() }}/src/${PROJECT}/" \
    \( -type d -name .git -prune \) -o \
    \( -name "*.py" -type f \) \
    -exec /bin/cat {} + >> "${CONCAT_FILE}"
  sed -i '' "/import ${PROJECT}/d" "${CONCAT_FILE}"
  sed -i '' "/from ${PROJECT}/d" "${CONCAT_FILE}"
  sed -i '' "/import \./d" "${CONCAT_FILE}"
  sed -i '' "/from \./d" "${CONCAT_FILE}"
  sed -i '' '/__all__/d' "${CONCAT_FILE}"
  grep -E '^(import |from )' ${CONCAT_FILE} | sort -u > "${TMP_SCRIPT_FILE}"
  grep -E -v '^(import |from )' "${CONCAT_FILE}" >> "${TMP_SCRIPT_FILE}"
  rm -f "${CONCAT_FILE}"
  REQ_PY="$(tq --file pyproject.toml '.project.requires-python')"
  DEPS="$(tq --file pyproject.toml '.project.dependencies')"
  {
    echo "#!/usr/bin/env -S uv run --script"
    echo "# /// script"
    echo "# requires-python = $REQ_PY"
    echo "# dependencies = $DEPS"
    echo "# ///"
    echo ""
  } >> "${PROJECT_NAME}"
  /bin/cat "${TMP_SCRIPT_FILE}" >> "${PROJECT_NAME}"
  rm -f "${TMP_SCRIPT_FILE}"
  ENTRYPOINT="$(tq --file pyproject.toml --raw ".project.scripts.${PROJECT_NAME}" | cut -d':' -f2-)"
  {
    echo ""
    echo ""
    echo 'if __name__ == "__main__":'
    echo "    ${ENTRYPOINT}()"
    echo -n "# "
    echo -n "vim"
    echo -n ": "
    echo -n "set "
    echo -n "ft=python"
    echo ":"
  } >> "${PROJECT_NAME}"
  ruff format "${PROJECT_NAME}"
  ruff check --fix "${PROJECT_NAME}"
  chmod +x "${PROJECT_NAME}"

clean file:
  if [[ -f "{{ file }}" ]]; then \
    rm -f "{{ file }}"; \
  fi
