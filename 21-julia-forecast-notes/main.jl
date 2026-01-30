input = isfile("input.txt") ? strip(read("input.txt", String)) : ""
if isempty(input)
    println(stderr, "No input provided. Edit input.txt.")
    exit(1)
end
println("# Forecast Notes\n")
println("## Assumptions\n- \n\n## Signals\n- \n\n## Actions\n- \n")
println("## Raw Notes\n```text\n" * input * "\n```")
