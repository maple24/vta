*** Variables ***
${NAME}         Robot Framework
# list
@{NAMES}        Matti       Teppo
@{NAMES2}       @{NAMES}    Seppo
# dictionary
&{MANY}         first=1       second=${2}         ${3}=third
&{EVEN MORE}    &{MANY}       first=override      empty=
...             =empty        key\=here=value