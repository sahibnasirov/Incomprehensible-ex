import os
import sublime
import subprocess
import sublime_plugin
# import threading

class IncomprehensibleEx (sublime_plugin.EventListener):

    print("** Incomprehensible Extensions Started **")
    # known extensions for read mode
    extensions = ['mp3','odt','ogg','pdf','pptx','ps','psv','rtf','tff','tif','tiff','tsv','wav','xls','xlsx','doc','docx','eml','epub']
    # extensions can be editable
    editable_extensions = ['asciidoc', 'beamer', 'commonmark', 'context', 'docbook', 'docx', 'dokuwiki', 'dzslides', 'fb2', 'haddock', 'html', 'html5', 'icml', 'latex', 'man', 'markdown', 'markdown_github', 'markdown_mmd', 'markdown_phpextra', 'markdown_strict', 'mediawiki', 'native', 'odt', 'opendocument', 'opml', 'org', 'plain', 'revealjs', 'rst', 'rtf', 's5', 'slideous', 'slidy', 'texinfo', 'textile']
    # mode
    editMode = False
    # thread = False

    # def __init__(self):
    #     self.stdout = None
    #     self.stderr = None
    #     threading.Thread.__init__(self)

    def run(self):
        # load Inconprehensible Ex user settings
        fileSettings = sublime.load_settings('incomprehensibleex.sublime-settings')
        # set Inconprehensible Ex user settings if removed
        if not fileSettings.has('extensions'):
            fileSettings.set('extensions', extensions)
        else:
            extensions = fileSettings.get('extensions')

        if not fileSettings.has('edit_mode'):
            fileSettings.set('edit_mode', editMode)
        else:
            editMode = fileSettings.get('edit_mode')

        sublime.save_settings('incomprehensibleex.sublime-settings')

    # listeners
    def on_load(self, view):
        if sublime.active_window().extract_variables()['file_extension'] in self.extensions:
            self.handle_active(view)

    def on_pre_close(self, view):
        if not (view.is_scratch()):
            if sublime.active_window().extract_variables()['file_extension'] == 'inex':
                self.deleteTemp(view)

    def on_post_save(self, view):
        if not (view.is_scratch()):
            if sublime.active_window().extract_variables()['file_extension'] == 'inex':
                self.saveTemp(self)

    # function to set the variables
    def initVariables(self, view):
        self.path = sublime.active_window().extract_variables()['file_path']
        self.file = sublime.active_window().extract_variables()['file_name']
        self.ext = sublime.active_window().extract_variables()['file_extension']
        self.target = os.path.join(os.path.realpath(sublime.packages_path()), "User")

    # Function for delete temporary file
    def deleteTemp(self, view):
        self.initVariables(view)
        # delete temp file
        os.remove(os.path.join(self.path, self.file))

    # Function to save the temp file in original file
    def saveTemp(self, view):
        try:
            self.initVariables(view)
            # set file paths to input and output
            inp = os.path.join(self.path, self.file)
            out = os.path.join(self.path, self.file[:-5])
            # set original extension
            ext = self.file.find('.')
            ext = self.file[ext+1:-5]
            # verify if can be editable
            if ext in self.editable_extensions:
                # convert file
                self.convert(self, inp, out, ext, True)
            else:
                print(ext + "Is not supported for edit mode")
        except Exception as error:
            print(error)

    # Function to convert file
    def convert(self, view, inp, out, ext, save):
        try:
            # verify for save
            if not save:
                # verify if exists textract instaled
                result, errors = subprocess.Popen('textract -o '+out+' '+inp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
            else:
                # verify if exists pandoc instaled
                result, errors = subprocess.Popen('pandoc -s -o '+out+' -w '+ext+' '+inp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
        except Exception as error:
            print(error)

    # Function for process the file
    def handle_active(self, view):
        try:
            # set common variables
            self.initVariables(view)
            # close original docx file opened
            sublime.active_window().run_command('close')
            # verify if it's editable
            if self.editMode and self.ext in self.editable_extensions:
                # set file paths to input and output
                inp = os.path.join(self.path, self.file)
                out = os.path.join(self.path, self.file+'.inex')
                # convert file
                # @TODO: epub | testar as extensoes e setar as melhores visoes de acordo com a extensao original.
                self.convert(self, inp, out, self.ext, False)
                # open new file
                sublime.active_window().open_file(os.path.join(self.path, self.file)+'.inex')
            else:
                # set file paths to input and output
                inp = os.path.join(self.path, self.file)
                out = os.path.join(self.target, self.file)
                # convert file
                self.convert(self, inp, out, self.ext, False)
                # create new file to recive the text
                output_view = sublime.active_window().new_file()
                output_view.set_name(self.file)
                output_view.set_scratch(True)
                # open,read and close the file converted
                file = open(os.path.join(self.target, self.file), 'r')
                output_view.run_command("insert",{"characters": file.read()})
                file.close()
                #  move the cursor to the top of the page
                output_view.run_command("move_to",{"to": "bof"})
                # remove converted file
                os.remove(os.path.join(self.target, self.file))
        except KeyError as error:
            print(error)

class IncomprehensibleExEditModeOnCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        try:
            IncomprehensibleEx.editMode = True
            IncomprehensibleEx.fileSettings.set('edit_mode', True)
            sublime.active_window().status_message("Incomprehensible Ex | Edit Mode ON")
        except Exception as e:
            print(e)

class IncomprehensibleExEditModeOffCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        try:
            IncomprehensibleEx.editMode = False
            IncomprehensibleEx.fileSettings.set('edit_mode', False)
            sublime.active_window().status_message("Incomprehensible Ex | Edit Mode OFF")
        except Exception as e:
            print(e)
