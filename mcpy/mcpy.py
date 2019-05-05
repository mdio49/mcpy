import ast, os, re
from enum import Enum
class MCPyParseMode(Enum):
    Standard = 0,
    Python = 1,
    Command = 2,
    Import = 3

class MCPyParser:
    def __init__(self):
        self.__attributes = {}

    @property
    def attributes(self):
        return self.__attributes
    
    # Parses the .mcpy file at the specified path to the given output stream.
    def parse(self, path, output, attributes={}):
        file = open(path, "r")   
        mode = MCPyParseMode.Standard
        code = ""
        indent = ""
        import_body = ""

        for line in file:
            text = line
            while len(text) > 0:
                if mode == MCPyParseMode.Command:
                    cmd = text.strip()
                    end_index = text.find("/>")
                    if end_index >= 0:
                        cmd = text[0:end_index].rstrip()
                        mode = MCPyParseMode.Python
                    text = ""
                    
                    # Don't write if there is no command and the end delimiter is on the current line.
                    if end_index == -1 or not cmd == "":
                        cmd = self.__parse_command(cmd)
                        code += indent + f'output.write(\"{cmd}\\n\")\n'
                elif mode == MCPyParseMode.Python:
                    end_index = text.find("%>")
                    if text.lstrip().startswith("</"):
                        # Enter command mode.
                        cmd_index = text.index("</")
                        indent = text[0:cmd_index]
                        text = text[(cmd_index + 2):].lstrip()
                        mode = MCPyParseMode.Command
                    elif end_index >= 0:
                        # Execute the Python code and exit Python mode.
                        code += text[0:end_index].rstrip()
                        text = ""
                        mode = MCPyParseMode.Standard
                        exec(code, globals(), self.__get_locals(attributes, output))
                    else:
                        # Append the text to the code.
                        code += text
                        text = ""
                elif mode == MCPyParseMode.Import:
                    end_index = text.find("#>")
                    if end_index >= 0:
                        # Exit import mode.
                        import_body += text[0:end_index].rstrip()
                        mode = MCPyParseMode.Standard
                        self.__parse_import(output, import_body)
                    else:
                        import_body += text
                    text = ""
                    pass
                else:
                    if text.lstrip().startswith("<%"):
                        # Enter Python mode.
                        text = text.replace("<%", "", 1).lstrip()
                        code = ""
                        mode = MCPyParseMode.Python
                    elif text.lstrip().startswith("<#"):
                        # Enter import mode.
                        text = text.replace("<#", "", 1).lstrip()
                        import_body = ""
                        mode = MCPyParseMode.Import
                    else:
                        # Parse the command and write it to the file.
                        cmd = self.__parse_command(text.strip())
                        exec(f'output.write(\"{cmd}\\n\")', globals(), self.__get_locals(attributes, output))
                        text = ""

        file.close()
    
    def __get_locals(self, attributes, output):
        return {**self.attributes, **attributes, "output": output, "attributes": self.attributes}

    # Parses a command, performing any Python substitutions that can be executed separately.
    def __parse_command(self, text):
        text = text.replace("\\", "\\\\")
        text = text.replace('\"', "\\\"")
        text = re.sub(r'%([^%]*)%', r'" + str(\1) + "', text)
        return text

    def __parse_import(self, output, body):
        match = re.search(r'([^\s]*) ([^{]*)(\{[^}]*\})?', body)
        method = match.group(1).strip()
        name = match.group(2).strip()
        if method == "attributes":
            path = os.path.join("mcpy/attributes", name) 
            file = open(path, "r")
            self.attributes.update(ast.literal_eval(file.read()))
            file.close()
        elif method == "template":
            attributes = ast.literal_eval(match.group(3) or "{}")
            path = os.path.join("mcpy/templates", name) + ".mcpy"
            self.parse(path, output, attributes=attributes)
