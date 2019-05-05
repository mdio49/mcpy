# mcpy
mcpy is a lightweight Python template engine for Minecraft functions. It allows the insertion of Python snippets into Minecraft function files which can be parsed separately to produce working function files for Minecraft.

## Getting Started
Download the repository and place the 'mcpy' folder into your world directory. To compile .mcpy files, run the following Python script.
```
python mcpy/compile.py .\datapacks\
```
The Python script 'compile.py' takes in a list of directories as a command line argument corresponding to directories which the program will walk through and look for .mcpy files to parse and convert into .mcfunction files. A batch file for Windows has been provided for your convenience.

## Usage
A snippet of Python code can be placed in the function file using the syntax `<% { Python code } %>`. A Minecraft function can be executed inside a Python code block using `</ { Minecraft function } />`. Both of these syntaxes can define a block over multiple lines. However, when executing a Minecraft function inside a Python block, the indentation needs to be consistent with that of the Python code.

For example, the following .mcpy file will result in the command `say Hi!` being executed 3 times.
```
<% for i in range(0, 3):
    </ say Hi! />
%>
```
The resultant output .mcfunction file is:
```
say Hi!
say Hi!
say Hi!
```
Variable names or expressions in Python can also be substituted into Minecraft commands using `% { expression } %`.
```
<% for i in range(0, 3):
    </ say %i% />
%>

- Output -
say 1
say 2
say 3
```
The same syntax can be used outside of Python blocks to substitute attributes. Attributes can be defined in the .mcpy file using a Python block and can be accessed anywhere in the file as if they were variables.
```
<% attributes['teams'] = ["red", "blue"] %>

say Team 1: %teams[0]%
say Team 2: %teams[1]%

<% for x in teams:
    execute as @a[team=%x%] at @s if entity @a[team=!%x,distance=..5] run tellraw @s {"text":"An enemy is approaching!"}
%>
```
Alternatively, attributes may be defined seperately in a file in the 'attributes/' folder of the mcpy root directory, which can be imported into an .mcpy file using `<# attributes { file } #>`. For example, the file 'teams.py' can be created:
```
{
    "teams": [
        "red",
        "blue
    ]
}
```
Then this file can be imported into the .mcpy file:
```
<# attributes teams.py #>
<% for x in teams:
    execute as @a[team=%x%] at @s if entity @a[team=!%x,distance=..5] run tellraw @s {"text":"An enemy is approaching!"}
%>
```
The file 'globals.py' can be used to define global attributes which are automatically imported into any .mcpy (provided you compile with compile.py).

Templates can also be defined which are imported into the .mcpy file during compilation. For example;

my_template.mcpy:
```
say My Template!
```
function.mcpy:
```
<# template my_template #>
say My Minecraft Function!
```
The output file 'function.mcfunction' is:
```
say My Template!
say My Minecraft Function!
```
Template files must be placed in the 'templates/' folder of the mcpy root directory. Attributes can also be inserted into templates when they are imported which can differ between function files. For example;

my_template.mcpy:
```
say Hello %name%!
```
function1.mcpy:
```
<# template my_template { 'name': "Player 1" } #>
```
function2.mcpy:
```
<# template my_template { 'name': "Player 2" } #>
```
After compilation, function1 will be `say Player 1` and function2 will be `say Player 2`.
