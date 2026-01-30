let read_file path =
  let ic = open_in path in
  let n = in_channel_length ic in
  let s = really_input_string ic n in
  close_in ic; s

let () =
  let input =
    try String.trim (read_file "input.txt") with _ -> ""
  in
  if input = "" then (prerr_endline "No input provided. Edit input.txt."; exit 1);
  print_endline "# Project Plan\n";
  print_endline "## Milestones\n- \n\n## Risks\n- \n\n## Raw Notes\n```text";
  print_endline input;
  print_endline "```"
