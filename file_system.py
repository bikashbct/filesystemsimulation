import os
import readline

class TrieNode:
    def __init__(self, name, is_file=False, parent=None):
        self.name = name
        self.is_file = is_file
        self.children = {}
        self.parent = parent
        self.content = ""  # Add content attribute for files

class FileSystem:
    def __init__(self):
        self.root = TrieNode("", parent=None)
        self.current = self.root

    def mkdir(self, path):
        """Create directory at specified path"""
        components = self._parse_path(path)
        node = self._traverse(components)
        if node is None:
            self._create_directory(components)
    
    def touch(self, path):
        """Create file at specified path"""
        components = self._parse_path(path)
        if not components:
            print("Invalid file name")
            return
        
        dir_components = components[:-1]
        file_name = components[-1]
        
        dir_node = self._traverse(dir_components)
        if dir_node and not dir_node.is_file:
            if file_name not in dir_node.children:
                dir_node.children[file_name] = TrieNode(file_name, is_file=True, parent=dir_node)
                print(f"File '{file_name}' created")
            else:
                print(f"File '{file_name}' already exists")
        else:
            print(f"Invalid path: {'/'.join(components)}")

    def ls(self, path=""):
        """List directory contents"""
        components = self._parse_path(path)
        target_node = self._traverse(components) if components else self.current
        
        if not target_node:
            print(f"Path not found: {'/'.join(components)}")
            return
        if target_node.is_file:
            print(target_node.name)
        else:
            contents = [f"{name}/" if not node.is_file else name 
                       for name, node in target_node.children.items()]
            print('\n'.join(sorted(contents)) or "Empty directory")

    def cd(self, path):
        """Change current directory"""
        if path == "/":
            self.current = self.root
            return
        
        components = self._parse_path(path)
        target_node = self._traverse(components)
        
        if target_node and not target_node.is_file:
            self.current = target_node
        else:
            print(f"Directory not found: {'/'.join(components)}")

    def pwd(self):
        """Print current working directory"""
        path = []
        node = self.current
        while node.parent:
            path.append(node.name)
            node = node.parent
        print('/' + '/'.join(reversed(path)))

    def cat(self, path):
        """Display file contents"""
        components = self._parse_path(path)
        file_node = self._traverse(components)
        
        if file_node and file_node.is_file:
            print(file_node.content)
        else:
            print(f"File not found: {'/'.join(components)}")

    def rm(self, path):
        """Remove file or directory"""
        components = self._parse_path(path)
        if not components:
            print("Invalid path")
            return
        
        node = self._traverse(components[:-1])
        if node and components[-1] in node.children:
            del node.children[components[-1]]
            print(f"Removed: {'/'.join(components)}")
        else:
            print(f"Path not found: {'/'.join(components)}")

    def _parse_path(self, path):
        """Convert path string to list of components"""
        if not path:
            return []
        
        # Handle absolute and relative paths
        if path.startswith('/'):
            components = path[1:].split('/')
            current_node = self.root
        else:
            components = path.split('/')
            current_node = self.current
        
        # Filter out empty components from consecutive slashes
        return [c for c in components if c]

    def _traverse(self, components):
        """Navigate through the trie based on path components"""
        current_node = self.root if components and components[0] == '' else self.current
        
        for comp in components:
            if comp == '..':
                if current_node.parent:
                    current_node = current_node.parent
            elif comp == '.':
                continue  # Stay in current directory
            elif comp in current_node.children:
                current_node = current_node.children[comp]
                if current_node.is_file and comp != components[-1]:
                    return None  # Can't traverse through files
            else:
                return None
        return current_node

    def _create_directory(self, components):
        """Helper to create directory hierarchy"""
        current_node = self.root if components[0] == '' else self.current
        
        for comp in components:
            if comp == '..':
                if current_node.parent:
                    current_node = current_node.parent
            elif comp == '.':
                continue
            elif comp not in current_node.children:
                new_node = TrieNode(comp, parent=current_node)
                current_node.children[comp] = new_node
                current_node = new_node
            else:
                current_node = current_node.children[comp]

def complete(text, state):
    """Tab completion function"""
    buffer = readline.get_line_buffer()
    components = buffer.split()
    if len(components) == 1:
        return [cmd + ' ' for cmd in ["mkdir", "touch", "ls", "cd", "pwd", "exit", "echo", "clear", "cat", "rm"] if cmd.startswith(text)][state]
    else:
        path = components[-1]
        fs = FileSystem()
        node = fs._traverse(fs._parse_path(path))
        if node:
            return [name + ('/' if not node.children[name].is_file else '') for name in node.children if name.startswith(text)][state]
        return None

def main():
    fs = FileSystem()
    print("Linux File System Simulator")
    print("Commands: mkdir, touch, ls, cd, pwd, exit, echo, clear, cat, rm")
    
    readline.set_completer(complete)
    readline.parse_and_bind("tab: complete")
    
    while True:
        try:
            command = input("\n$ ").strip().split(' ', 1)
            cmd = command[0].lower()
            
            if cmd == "exit":
                print("Exiting file system")
                break
            elif cmd == "pwd":
                fs.pwd()
            elif cmd == "ls":
                path = command[1] if len(command) > 1 else ""
                fs.ls(path)
            elif cmd in ("mkdir", "touch", "cd"):
                if len(command) < 2:
                    print(f"Usage: {cmd} <path>")
                    continue
                if cmd == "mkdir":
                    fs.mkdir(command[1])
                elif cmd == "touch":
                    fs.touch(command[1])
                elif cmd == "cd":
                    fs.cd(command[1])
            elif cmd == "echo":
                if len(command) > 1:
                    parts = command[1].split('>', 1)
                    if len(parts) > 1:
                        text, filepath = parts[0].strip(), parts[1].strip()
                        components = fs._parse_path(filepath)
                        file_node = fs._traverse(components)
                        if file_node and file_node.is_file:
                            file_node.content = text
                            print(f"Written to {filepath}")
                        else:
                            print(f"File not found: {filepath}")
                    else:
                        print(command[1])
                else:
                    print()
            elif cmd == "clear":
                os.system('clear')
            elif cmd == "cat":
                if len(command) < 2:
                    print("Usage: cat <path>")
                else:
                    fs.cat(command[1])
            elif cmd == "rm":
                if len(command) < 2:
                    print("Usage: rm <path>")
                else:
                    fs.rm(command[1])
            else:
                print("Invalid command. Available commands: mkdir, touch, ls, cd, pwd, exit, echo, clear, cat, rm")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
