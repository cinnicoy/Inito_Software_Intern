class File:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content


class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = {}  # Map of name to File/Directory object

    def add_file(self, file):
        self.children[file.name] = file

    def add_directory(self, directory):
        self.children[directory.name] = directory


class InMemoryFileSystem:
    def __init__(self):
        self.root = Directory("/")
        self.current_directory = self.root

    def mkdir(self, path):
        if path[0] == '/':
            current = self.root
        else:
            current = self.current_directory

        for directory_name in path.split('/'):
            if directory_name and directory_name not in current.children:
                new_directory = Directory(directory_name, current)
                current.add_directory(new_directory)
                current = new_directory
            elif directory_name:
                current = current.children[directory_name]

    def cd(self, path):
        if path == '/':
            self.current_directory = self.root
            return
        if path[0] == '/':
            current = self.root
            path = path[1:]
        else:
            current = self.current_directory

        for directory in path.split('/'):
            if directory == '..':
                if current.parent:
                    current = current.parent
            elif directory in current.children and isinstance(current.children[directory], Directory):
                current = current.children[directory]
        self.current_directory = current

    def ls(self, path="."):
        if path == "/":
            current = self.root
        else:
            current = self.current_directory
        if path[0] == '/':
            current = self.root

        if path[-1] == '/':
            path = path[:-1]

        target = path.split("/")[-1] if path != '.' else path

        if target in current.children and isinstance(current.children[target], Directory):
            current = current.children[target]

        if isinstance(current, File):
            print(current.name)
        else:
            for item in current.children:
                if isinstance(current.children[item], Directory):
                    print(item + '/')
                else:
                    print(item)

    def grep(self, pattern, filename):
        if filename in self.current_directory.children and isinstance(self.current_directory.children[filename], File):
            content = self.current_directory.children[filename].content
            lines = content.split("\n")
            matching_lines = [line for line in lines if pattern in line]
            return "\n".join(matching_lines)
    def cat(self, filename):
        if filename in self.current_directory.children and isinstance(self.current_directory.children[filename], File):
            print(self.current_directory.children[filename].content)

    def touch(self, filename):
        new_file = File(filename)
        self.current_directory.add_file(new_file)

    def echo(self, content, filename):
        if filename in self.current_directory.children and isinstance(self.current_directory.children[filename], File):
            self.current_directory.children[filename].content = content

    def mv(self, source, destination):
        if source in self.current_directory.children:
            item = self.current_directory.children[source]
            self.current_directory.children.pop(source)
            target_dir = destination.split('/')
            target = target_dir[-1] if destination != '/' else '/'
            for dir in target_dir[:-1]:
                if dir == "..":
                    self.current_directory = self.current_directory.parent
                else:
                    self.cd(dir)
            if isinstance(item, File):
                self.current_directory.add_file(item)
            elif isinstance(item, Directory):
                self.current_directory.add_directory(item)

    def cp(self, source, destination):
        if source in self.current_directory.children:
            item = self.current_directory.children[source]
            target_dir = destination.split('/')
            target = target_dir[-1] if destination != '/' else '/'
            for dir in target_dir[:-1]:
                if dir == "..":
                    self.current_directory = self.current_directory.parent
                else:
                    self.cd(dir)
            if isinstance(item, File):
                new_file = File(item.name, item.content)
                self.current_directory.add_file(new_file)
            elif isinstance(item, Directory):
                new_dir = Directory(item.name)
                for child_item in item.children:
                    if isinstance(item.children[child_item], File):
                        file_copy = File(item.children[child_item].name, item.children[child_item].content)
                        new_dir.add_file(file_copy)
                    else:
                        dir_copy = Directory(item.children[child_item].name)
                        new_dir.add_directory(dir_copy)
                self.current_directory.add_directory(new_dir)

    def rm(self, item):
        if item in self.current_directory.children:
            if isinstance(self.current_directory.children[item], Directory):
                self.current_directory.children.pop(item)
            else:
                self.current_directory.children.pop(item)


# Test the file system
fs = InMemoryFileSystem()

# Command-line interface
while True:
    command = input("$ ")  # Display the command prompt
    command_parts = command.split(" ")

    if command_parts[0] == "mkdir":
        fs.mkdir(command_parts[1])
    elif command_parts[0] == "cd":
        fs.cd(command_parts[1])
    elif command_parts[0] == "ls":
        fs.ls(command_parts[1] if len(command_parts) > 1 else ".")
    elif command_parts[0] == "cat":
        fs.cat(command_parts[1])
    elif command_parts[0] == "touch":
        fs.touch(command_parts[1])
    elif command_parts[0] == "echo":
        content = " ".join(command_parts[2:])
        fs.echo(content, command_parts[1])
    elif command_parts[0] == "mv":
        fs.mv(command_parts[1], command_parts[2])
    elif command_parts[0] == "cp":
        fs.cp(command_parts[1], command_parts[2])
    elif command_parts[0] == "rm":
        fs.rm(command_parts[1])
    elif command_parts[0] == "exit":
        break
    elif command_parts[0] == "grep":
        pattern = command_parts[1]
        filename = command_parts[2]
        result = fs.grep(pattern, filename)
        print(result if result else f"No matching lines found for pattern '{pattern}' in file '{filename}'")

    else:
        print("Invalid command. Supported commands: mkdir, cd, ls, cat, touch, echo, mv, cp, rm, exit")
