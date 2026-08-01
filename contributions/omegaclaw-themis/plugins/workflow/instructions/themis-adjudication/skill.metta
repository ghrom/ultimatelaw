; Themis adjudication workflow skills for OmegaClaw
; Loaded with (workflow-load-instructions "themis-adjudication")

(skill themis-case-start "Create Themis case folders" (case_name_in_quotes topic_in_quotes))
(skill themis-step "Mark Themis adjudication step done" (case_name_in_quotes step_in_quotes result_in_quotes next_action_in_quotes))
(skill themis-checkpoint "Pause for user approval on a Themis case" (case_name_in_quotes message_in_quotes))
(skill themis-complete "Finish Themis case and unload workflow" (case_name_in_quotes))
(skill themis-case-dir "Get Themis cases directory" ())

(= (themis-case-dir)
   (let $dir (get-existing-dir (pluginWorkflowMemoryDir))
     (joinPath ($dir "themis-cases"))))

(= (themis-case-start $case-name $topic)
   (if (valid-file-or-folder-name $case-name)
       (progn (shell (strings-concat ("mkdir -p " (themis-case-dir) "/" $case-name)))
              (write-file (strings-concat ((themis-case-dir) "/" $case-name "/topic.txt")) $topic)
              (send (strings-concat ("Created Themis case: " (themis-case-dir) "/" $case-name)))
              )
       (send (strings-concat ("Invalid case name: " $case-name ". Only a-z, 0-9, - and _ allowed.")))
    )
)

(= (themis-step $case-name $step $result $next)
   (if (valid-file-or-folder-name $case-name)
       (progn
           (send (strings-concat ("[themis:" $case-name "] done: " $step)))
           (appendToHistory ((get_time_as_string) (newline)
               (strings-concat ("THEMIS [" $case-name "] done: " $step " — " $result "; next: " $next)) (newline)))
           (strings-concat ("Done: " $step)))
       (send (strings-concat ("Invalid case name: " $case-name)))
    )
)

(= (themis-checkpoint $case-name $message)
   (progn
       (send (strings-concat ("[themis:" $case-name "] CHECKPOINT: " $message)))
       (appendToHistory ((get_time_as_string) (newline)
           (strings-concat ("THEMIS [" $case-name "] CHECKPOINT: " $message)) (newline)))
       (pin (strings-concat ("themis-checkpoint case=" $case-name " waiting=user")))
       True))

(= (themis-complete $case-name)
   (progn
       (send (strings-concat ("[themis:" $case-name "] complete. Unloading workflow.")))
       (appendToHistory ((get_time_as_string) (newline)
           (strings-concat ("THEMIS [" $case-name "] complete")) (newline)))
       (workflow-unload-instructions)))
