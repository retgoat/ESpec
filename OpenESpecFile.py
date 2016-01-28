import sublime
import sublime_plugin
import re, inspect, os

if str(sublime.version()).startswith("3"):
  from . import ESpecShared
else
  from ESpec import ESpecShared

class OpenEspecFileCommand(sublime_plugin.WindowCommand):

    def run(self):
        if not self.window.active_view():
            return

        current_file_path = self.window.active_view().file_name()
        if current_file_path is None: return

        print("Current file: " + current_file_path)

        if current_file_path.endswith(".exs"):
            if self.quick_find(current_file_path):
                return

            current_file_name = re.search(r"[/\\]([\w.]+)$", current_file_path).group(1)
            base_name = re.search(r"(\w+)\.exs$", current_file_name).group(1)
            base_name = re.sub(r"_spec$", "", base_name)

            if current_file_name.endswith("_spec.exs"):
                source_matcher = re.compile(r"[/\\]" + base_name + "\.exs$")
                self.open_project_file(source_matcher, current_file_path)
            else:
                test_matcher = re.compile(r"[/\\]" + base_name + "_spec\.exs$")
                self.open_project_file(test_matcher, current_file_path)
        else:
            print("Error: current file is not a elixir file")

    def open_project_file(self, file_matcher, file_path):
        for path, dirs, filenames in self.walk_project_folder(file_path):
            for filename in filter(lambda f: f.endswith(".exs"), filenames):
                current_file = os.path.join(path, filename)
                if file_matcher.search(current_file):
                    return self.switch_to(os.path.join(path, filename))
        print("ESpec: No matching files found")

    def spec_paths(self, file_path):
        return [
            self.batch_replace(file_path,
                (r"\b(?:app|lib)\b", "spec"), (r"\b(\w+)\.exs", r"\1_spec.exs")),
            self.batch_replace(file_path,
                (r"\blib\b", os.path.join("spec", "lib")), (r"\b(\w+)\.exs", r"\1_spec.exs"))
        ]

    def code_paths(self, file_path):
        file_path = re.sub(r"\b(\w+)_spec\.exs$", r"\1.exs", file_path)
        return [
            re.sub(r"\bspec\b", "app", file_path),
            re.sub(r"\bspec\b", "lib", file_path),
            re.sub(r"\b{}\b".format(os.path.join("spec", "lib")), "lib", file_path)
        ]

    def quick_find(self, file_path):
        if re.search(r"\bspec\b|_spec\.exs$", file_path):
            for path in self.code_paths(file_path):
                if os.path.exists(path):
                    return self.switch_to(path)
        elif re.search(r"\b(?:app|lib)\b", file_path):
            for path in self.spec_paths(file_path):
                if os.path.exists(path):
                    return self.switch_to(path)
        print("ESpec: quick find failed, doing regular find")

    def batch_replace(self, string, *pairs):
        for target, replacement in pairs:
            string = re.sub(target, replacement, string)
        return string

    def switch_to(self, file_path):
        group = shared.other_group_in_pair(self.window)
        file_view = self.window.open_file(file_path)
        self.window.run_command("move_to_group", { "group": group })
        print("Opened: " + file_path)
        return True

    def walk_project_folder(self, file_path):
        for folder in self.window.folders():
            if not file_path.startswith(folder):
                continue
            yield from os.walk(folder)
