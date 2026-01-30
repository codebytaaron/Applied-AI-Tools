(ns main
  (:require [clojure.string :as str]))

(defn -main []
  (let [input (try (-> (slurp "input.txt") str/trim) (catch Exception _ ""))]
    (when (str/blank? input)
      (binding [*out* *err*] (println "No input provided. Edit input.txt."))
      (System/exit 1))
    (println "# OKRs\n")
    (println "## Objectives\n- \n\n## Key Results\n- \n\n## Raw Notes\n```text\n" input "\n```")))

(-main)
