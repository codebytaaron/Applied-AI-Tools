-module(main).
-export([main/0]).

main() ->
    {ok, Bin} = file:read_file("input.txt"),
    Str = string:trim(binary_to_list(Bin)),
    case Str of
      "" -> io:format(standard_error, "No input provided. Edit input.txt.~n", []), halt(1);
      _  ->
        io:format("# Incident Status Update~n~n", []),
        io:format("## Current status~n- ~n~n## Impact~n- ~n~n## Next update~n- ~n~n", []),
        io:format("## Raw Notes~n```text~n~s~n```~n", [Str])
    end.
