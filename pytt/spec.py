from lark import Lark

spec = Lark(
    r"""

    start: (default_hours default_project default_text project* day* include*)

    _NEWLINE    : NEWLINE
    COMMENT     : /;.*/

    _PROJECT_KEY : "project"
    PROJECT_KEY_VALUE : /[\w\-_]+/
    // PROJECT_ATTR: "key" | "name" | "alias" | "ticket"

    proj_attr_key       : "key"     PROJECT_KEY_VALUE
    proj_attr_alias     : "alias"   PROJECT_KEY_VALUE
    proj_attr_ticket    : "ticket"  ESCAPED_STRING
    proj_attr_name      : "name"    ESCAPED_STRING

    _proj_attr   : proj_attr_key
                 | proj_attr_alias 
                 | proj_attr_ticket 
                 | proj_attr_name 


    project       : _PROJECT_KEY ( proj_short | proj_compl )
    proj_short    : WORD ESCAPED_STRING* ESCAPED_STRING*
    proj_compl    : "{" [ _proj_attr+  ] "}"

    DAY_KEY     : /\d{4}\-\d{2}\-\d{2}/
    day         : DAY_KEY "{" [ work_start* work_end* task_entry* task_project_entry* ] "}"

    WORK_START_RUNE : ">"
    WORK_END_RUNE   : "<"

    TIME : /\d{2}:\d{2}/

    DURATION_TIME : /\d{1,2}h(\d{1,2}m)?|\d{1,2}m/
    DURATION_DOTS : /\.+/

    _DURATION_SEP : "  "

    _duration            : (DURATION_TIME | DURATION_DOTS)
    task_entry          : WORD* _DURATION_SEP _duration _NEWLINE
    task_project_entry  : PROJECT_KEY_VALUE "{" [ task_entry* ] "}"
    work_start          : WORK_START_RUNE TIME
    work_end            : WORK_END_RUNE TIME

    include             : "include" ESCAPED_STRING

    day_inner : work_start work_end task_entry

    _default_project_key : "default project"
    _default_hours_key   : "default hours"
    _default_text_key    : "default text"

    default_project : _default_project_key WORD
    default_hours   : _default_hours_key DURATION_TIME
    default_text    : _default_text_key ESCAPED_STRING

    %import common (WS, WORD, ESCAPED_STRING, NEWLINE)
    %ignore COMMENT
    %ignore WS

"""
)
