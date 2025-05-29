'''
miniprint - a medium interaction printer honeypot
Copyright (C) 2019 Dan Salmon - salmon@protonmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


from pyfakefs import fake_filesystem
import re
from datetime import datetime

class Printer:
    def __init__(self, logger, printer_id="hp LaserJet 4200", code=10001, ready_msg="Ready", online=True):
        self.printer_id = printer_id
        self.code = code
        self.ready_msg = ready_msg
        self.online = online
        self.logger = logger
        self.rexp = re.compile(r'\s+(\S+)\s+=\s+(?:"([^=]+)"|(\S+))')  # Compile once to decrease match time over multiple uses
        self.fs = fake_filesystem.FakeFilesystem()
        self.fos = fake_filesystem.FakeOsModule(self.fs)
        self.printing_raw_job = False
        self.current_raw_print_job = ''
        self.receiving_postscript = False
        self.postscript_data = ''

        # Filesystem from HP LaserJet 4200n
        self.fs.create_dir("/PJL")
        self.fs.create_dir("/PostScript")
        self.fs.create_dir("/saveDevice/SavedJobs/InProgress")
        self.fs.create_dir("/saveDevice/SavedJobs/KeepJob")
        self.fs.create_dir("/webServer/default")
        self.fs.create_dir("/webServer/home")
        self.fs.create_dir("/webServer/lib")
        self.fs.create_dir("/webServer/objects")
        self.fs.create_dir("/webServer/permanent")
        self.fs.add_real_file(source_path="fake-files/csconfig", read_only=True, target_path="/webServer/default/csconfig")
        self.fs.add_real_file(source_path="fake-files/device.html", read_only=True, target_path="/webServer/home/device.html")
        self.fs.add_real_file(source_path="fake-files/hostmanifest", read_only=True, target_path="/webServer/home/hostmanifest")
        self.fs.create_file("/webServer/lib/keys")
        self.fs.create_file("/webServer/lib/security")
    

    def append_raw_print_job(self, text):
        self.logger.debug(
            "Appending raw print job",
            extra={'action': 'append', 'event': 'append_raw_print_job', 'job_text': repr(text.encode('utf-8'))}
        )
        self.printing_raw_job = True
        self.current_raw_print_job += text
        self.logger.info(
            "Sending empty response",
            extra={'action': 'response', 'event': 'empty_response'}
        )
        return ''


    def get_parameters(self, command):
        '''
            Gets key=value pairs separated by either '=' or ' = '
            Notes:
                - Whitespace can be either a space charater or a \t
                - Whitespace is only required before a key
                    - Example: Immediately after the D in "@PJL COMMAND a=1"
                - Whitespace surrounding the equal sign is optional and may be 0 or many characters
                - String values must be surrounded by double quotes (")

            Valid inputs:
                @PJL COMMAND a = "b" b=2
                @PJL COMMAND a = "asf" b = "asdf"
                @PJL COMMAND a=2 b = "asd"
                @PJL COMMAND DISPLAY = "rdymsg"
                @PJL COMMAND DISPLAY = "rdymsg" OTHER = "asdf"
                @PJL COMMAND A = 1 B = 2
                @PJL COMMAND    A = 1     B = 2
                @PJL COMMAND A = 1 B    =   2
                @PJL COMMAND A=1 B="asdf"\r\nother data

            Invalid inputs:
                @PJL COMMANDA=1
        '''
        request_parameters = {}

        # Get a=b value pairs
        for x in command.split(" "):
            if "=" in x and len(x) > 1:
                key = x.split("=")[0]
                value = x.split("=")[1]

                if value[0] == '"':  # Handle params like: KEY="VALUE"\r\nsome other data
                    value = value[0:value[1:].index('"')+2]
                request_parameters[key] = value

        # Get a = "b" value pairs
        results = self.rexp.finditer(command)
        if results is not None:
            for r in results:
                key = r.group(1)
                value = r.group(2) if r.group(2) is not None else r.group(3)
                if key not in request_parameters:
                    request_parameters[key] = value
    
        return request_parameters
    
    
    def does_path_exist(self, path):
        return self.fos.path.exists(path)
        
    
    def command_fsdownload(self, request):
        request_parameters = self.get_parameters(request)
        file_contents = request[request.index(request_parameters["NAME"])+len(request_parameters["NAME"]):]
        file_name = request_parameters["NAME"].replace('"', '').split(":")[1]
        
        self.logger.debug(
            "Processing download",
            extra={'action': 'process', 'event': 'fsdownload', 'file_contents': file_contents}
        )

        if file_contents[0:2] == '\r\n':  # Trim leading newline
            self.logger.debug("Leading newline found", extra={'action': 'process', 'event': 'fsdownload'})
            file_contents = file_contents[2:]

        if file_contents[-2:] == '\r\n':  # Trim trailing newline
            self.logger.debug("Trailing newline found", extra={'action': 'process', 'event': 'fsdownload'})
            file_contents = file_contents[0:-2]

        # Check if path exists and is file
        if self.fos.path.exists(file_name):
            a = self.fs.get_object(file_name)
            if isinstance(a, fake_filesystem.FakeFile) or isinstance(a, fake_filesystem.FakeFileFromRealFile):
                self.fos.remove(file_name)

        self.fs.create_file(file_path=file_name, contents=file_contents)  # TODO: Handle errors if file exists or containing directory doesn't exist
        self.logger.info("Sending empty response", extra={'action': 'response', 'event': 'fsdownload'})
        return ''


    def command_echo(self, request):
        self.logger.info("Received request for delimiter", extra={'action': 'request', 'event': 'echo'})
        response = "@PJL " + request
        response += '\x1b'
        self.logger.info("Responding with echo", extra={'action': 'response', 'event': 'echo', 'response': str(response.encode('UTF-8'))})
        return response
    
    
    def command_fsdirlist(self, request):
        request_parameters = self.get_parameters(request)
        requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
    
        self.logger.debug("Requested directory listing", extra={'action': 'request', 'event': 'fsdirlist', 'dir': requested_dir})
        return_entries = ""
    
        if self.fos.path.exists(requested_dir):
            return_entries = ' ENTRY=1\r\n. TYPE=DIR\r\n.. TYPE=DIR'
            for entry in self.fos.scandir(requested_dir):
                if entry.is_file():
                    size = self.fos.stat(requested_dir + "/" + str(entry.name)).st_size
                    return_entries += "\r\n" + entry.name + " TYPE=FILE SIZE=" + str(size)
                elif entry.is_dir():
                    return_entries += "\r\n" + entry.name + " TYPE=DIR"
        else:
            return_entries = "FILEERROR = 3" # "file not found"
    
        response = '@PJL FSDIRLIST NAME=' + request_parameters['NAME'] + return_entries
        self.logger.info("Directory listing response", extra={'action': 'response', 'event': 'fsdirlist', 'response': str(response.encode('UTF-8'))})
        return response
        

    def command_fsmkdir(self, request):
        request_parameters = self.get_parameters(request)
        requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
        self.logger.info("Creating directory", extra={'action': 'request', 'event': 'fsmkdir', 'dir': requested_dir})
    
        if not self.fos.path.exists(requested_dir):
            self.fs.create_dir(requested_dir)
    
        self.logger.info("Directory created", extra={'action': 'response', 'event': 'fsmkdir'})
        return ''
    
    
    def command_fsquery(self, request):
        request_parameters = self.get_parameters(request)
        requested_item = request_parameters["NAME"].replace('"', '').split(":")[1]
        self.logger.debug("Requested item", extra={'action': 'request', 'event': 'fsquery', 'item': requested_item})
        return_data = ''
    
        if self.fos.path.exists(requested_item):
            if self.fos.path.isfile(requested_item):
                size = self.fos.stat(requested_item).st_size
                return_data = "NAME=" + request_parameters["NAME"] + " TYPE=FILE SIZE=" + str(size)
            elif self.fos.path.isdir(requested_item):
                return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"
        else:
            return_data = "NAME=" + request_parameters["NAME"] + " FILEERROR=3\r\n" # File not found
    
        response = '@PJL FSQUERY ' + return_data
        self.logger.info("FSQUERY response", extra={'action': 'response', 'event': 'fsquery', 'response': str(return_data.encode('UTF-8'))})
        return response
    

    def command_fsupload(self, request):
        request_parameters = self.get_parameters(request)
        upload_file = request_parameters["NAME"].replace('"', '').split(":")[1]
        self.logger.info("Upload file", extra={'action': 'request', 'event': 'fsupload', 'upload_file': upload_file})
        return_data = ''

        if self.fos.path.exists(upload_file):
            contents = ''
            file_module = fake_filesystem.FakeFileOpen(self.fs)
            for line in file_module(upload_file):
                contents += line

            size = self.fos.stat(upload_file).st_size
            return_data = 'FORMAT:BINARY NAME=' + request_parameters['NAME'] + ' OFFSET=0 SIZE=' + str(size) + '\r\n' + contents
        else:
            return_data = 'NAME=' + request_parameters['NAME'] + '\r\nFILEERROR=3\r\n'

        response = '@PJL FSUPLOAD ' + return_data
        self.logger.info("Upload response", extra={'action': 'response', 'event': 'fsupload', 'response': str(response.encode('UTF-8'))})
        return response

    
    def command_info_id(self, request):
        self.logger.info("ID requested", extra={'action': 'request', 'event': 'info_id'})
        response = '@PJL INFO ID\r\n' + self.printer_id + '\r\n\x1b'
        self.logger.info("ID response", extra={'action': 'response', 'event': 'info_id', 'response': str(response.encode('UTF-8'))})
        return response
        

    def command_info_status(self, request):
        self.logger.info("Client requests status", extra={'action': 'request', 'event': 'info_status'})
        response = '@PJL INFO STATUS\r\nCODE=' + str(self.code) + '\r\nDISPLAY="' + self.ready_msg + '"\r\nONLINE=' + str(self.online)
        self.logger.info("Status response", extra={'action': 'response', 'event': 'info_status', 'response': str(response.encode('UTF-8'))})
        return response


    def command_rdymsg(self, request):
        request_parameters = self.get_parameters(request)
        rdymsg = request_parameters["DISPLAY"]
        self.logger.info("Ready message", extra={'action': 'request', 'event': 'rdymsg', 'rdymsg': str(rdymsg.encode('UTF-8'))})

        self.ready_msg = rdymsg.replace('"', '')
        self.logger.info("Ready message response", extra={'action': 'response', 'event': 'rdymsg'})
        return ''


    def command_ustatusoff(self, request):
        self.logger.info("Request received", extra={'action': 'request', 'event': 'ustatusoff'})
        self.logger.info("Sending empty reply", extra={'action': 'response', 'event': 'ustatusoff'})
        return ''
            

    def save_postscript(self):
        file_name = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f") + ".ps"
        if self.receiving_postscript:
            self.logger.info("Saving postscript file", extra={'action': 'saving', 'event': 'save_postscript', 'file_name': file_name})
            with open("./uploads/" + file_name, 'w') as f:
                f.write(self.postscript_data)
            self.postscript_data = ''
            self.receiving_postscript = False
        else:
            self.logger.info("Nothing to save", extra={'action': 'saving', 'event': 'save_postscript'})


    def save_raw_print_job(self):
        file_name = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f") + ".txt"
        if self.current_raw_print_job:
            self.logger.info("Saving raw print job", extra={'action': 'saving', 'event': 'save_raw_print_job', 'file_name': file_name})
            with open("./uploads/" + file_name, 'w') as f:
                f.write(self.current_raw_print_job)
            self.current_raw_print_job = ''
            self.printing_raw_job = False
        else:
            self.logger.info("Nothing to save", extra={'action': 'saving', 'event': 'save_raw_print_job'})
