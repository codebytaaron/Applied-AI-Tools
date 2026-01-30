import std/[os, strutils]

let input = if fileExists("input.txt"): readFile("input.txt").strip else: ""
if input.len == 0:
  stderr.writeLine "No input provided. Edit input.txt."
  quit(1)

echo "# Change Order\n"
echo "## Reason\n- \n\n## Cost Impact\n- \n\n## Schedule Impact\n- \n"
echo "## Raw Notes\n```text\n" & input & "\n```"
