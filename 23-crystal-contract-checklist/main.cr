input = File.exists?("input.txt") ? File.read("input.txt").strip : ""
if input.empty?
  STDERR.puts "No input provided. Edit input.txt."
  exit 1
end

puts "# Contract Review Checklist\n"
puts "## Checklist\n- Parties + scope\n- Term + termination\n- Payment + late fees\n- Liability + indemnity\n- Confidentiality\n"
puts "## Raw Notes\n```text\n#{input}\n```"
