import ast, sys, os
from mcpy import MCPyParser

def parse_file(parser, path):
    filename = os.path.basename(path)
    name = os.path.splitext(filename)[0]
    directory = os.path.dirname(path)
    output_path = os.path.join(directory, name + ".mcfunction")
    output = open(output_path, "w")
    parser.parse(path, output)
    output.close()

if len(sys.argv) <= 1:
    print("Please enter at least one directory.")
    quit()

mcpy_parser = MCPyParser()

# Insert global attributes.
file = open("mcpy/attributes/globals.py", "r")
mcpy_parser.attributes.update(ast.literal_eval(file.read()))
file.close()

success = 0
fail = 0

for path in sys.argv[1:]:
    for r, d, f in os.walk(path):
        for file in f:
            if '.mcpy' in file:
                current_path = os.path.join(r, file)
                try:
                    parse_file(mcpy_parser, current_path)
                except Exception as e:
                    print(f"Failed to parse file '{current_path}': " + str(e))
                    fail += 1
                else:
                    print(f"Parsed file '{current_path}' successfully!")
                    success += 1

print(f"Compilation completed with {success} successful parse(s) and {fail} failure(s).")