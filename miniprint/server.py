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


import socketserver
import logging
import select
import sys
import traceback
from printer import Printer
import argparse
import re
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Override to format time in ISO 8601 format with timezone-aware object
        # return datetime.fromtimestamp(record.created, timezone.utc).replace(tzinfo=None)
        return datetime.fromtimestamp(record.created, timezone.utc).replace(tzinfo=None).isoformat() + 'Z'

    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record),
#            'level': record.levelname,
            'info': record.getMessage()
        }

        # Add src_ip and dest_port from the filter if available
        if hasattr(record, 'src_ip') and record.src_ip:
            log_record['src_ip'] = record.src_ip
        if hasattr(record, 'dest_port') and record.dest_port:
            log_record['dest_port'] = record.dest_port

        # Add fields only if their value is not "unknown"
        additional_fields = {
            'action': getattr(record, 'action', 'unknown'),
            'command': getattr(record, 'command', 'unknown'),
            'dir': getattr(record, 'dir', 'unknown'),
            'event': getattr(record, 'event', 'unknown'),
            'file_contents': getattr(record, 'file_contents', 'unknown'),
            'file_name': getattr(record, 'file_name', 'unknown'),
            'item': getattr(record, 'item', 'unknown'),
            'job_text': getattr(record, 'job_text', 'unknown'),
            'rdymsg': getattr(record, 'rdymsg', 'unknown'),
            'response': getattr(record, 'response', 'unknown'),
            'upload_file': getattr(record, 'upload_file', 'unknown')
        }

        log_record.update({k: v for k, v in additional_fields.items() if v != 'unknown'})
        return json.dumps(log_record)


class ConnectionFilter(logging.Filter):
    def __init__(self, src_ip=None, dest_port=None):
        super().__init__()
        self.src_ip = src_ip
        self.dest_port = dest_port

    def filter(self, record):
        record.src_ip = self.src_ip
        record.dest_port = self.dest_port
        return True


parser = argparse.ArgumentParser(description='''miniprint - a medium interaction printer honeypot
       by Dan Salmon: @BLTjetpack, github.com/sa7mon ''',
        prog='miniprint',
        usage='%(prog)s [-b,--bind HOST] [-l,--log-file FILE] [-t,--time-out TIME] [-h]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False)

o = parser.add_argument_group(title='optional arguments',
        description='''-b, --bind <host>       Bind the server to <host> (default: localhost)
-l, --log-file <file>   Save all logs to <file> (default: ./miniprint.log)
-t, --timeout <time>    Wait up to <time> seconds for commands before disconnecting client (default: 120)''')

o.add_argument('-b', '--bind', dest='host', default='localhost', help=argparse.SUPPRESS)
o.add_argument("-h", "--help", action="help", help="show this help message and exit")
o.add_argument('-l', '--log-file', dest='log_file', default='./miniprint.log', help=argparse.SUPPRESS)
o.add_argument('-t' ,'--timeout', type=int, dest='timeout', default=120, help=argparse.SUPPRESS)

args = parser.parse_args()

conn_timeout = args.timeout
log_location = args.log_file

logger = logging.getLogger('miniprint')
logger.setLevel(logging.DEBUG)

# Create file handler which logs even debug messages
fh = logging.FileHandler(log_location)
fh.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = JSONFormatter()
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.
    
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    @staticmethod
    def parse_commands(text):
        '''
            Convert a string of commands to a list of commands.

            Examples:
                Input:  "@PJL USTATUSOFF\r\n@PJL INFO ID\r\n@PJL ECHO DELIMITER58494\r\n\r\n"
                Output: ['@PJL USTATUSOFF\r\n', '@PJL INFO ID\r\n', '@PJL ECHO DELIMITER58494\r\n\r\n']

                Input:  "This is my print job"
                Output: ['This is my print job']
        '''
        commands = []
        results = re.split('(@PJL)', text)
        results = [x for x in results if x]  # In case we have empty list elements
        
        for i, result in enumerate(results):
            if result == '@PJL':
                continue
            elif i > 0 and results[i-1] == '@PJL':
                commands.append('@PJL' + results[i])
            else:
                commands.append(results[i])

        return commands

    def handle(self):
        src_ip = self.client_address[0]
        global PORT
        dest_port = PORT

        # Add connection filter for logging src_ip and dest_port to every log record
        connection_filter = ConnectionFilter(src_ip=src_ip, dest_port=dest_port)
        logger.addFilter(connection_filter)

        logger.info("Connection opened", extra={'action': 'open_conn', 'event': 'connection'})
        
        printer = Printer(logger)
        emptyRequest = False
        while emptyRequest == False:
            # Wait a maximum of conn_timeout seconds for another request
            ready = select.select([self.request], [], [], conn_timeout)
            if not ready[0]:
                break

            try:
                self.data = self.request.recv(1024).strip()
            except Exception as e:
                logger.error(
                    "Possible port scan", 
                    extra={'action': 'receive', 'event': 'port_scan'}
                )
                emptyRequest = True
                break

            request = self.data.decode('UTF-8')
            request = request.replace('\\x1b%-12345X', '')

            if request[0:2] == '%!':
                printer.receiving_postscript = True
                printer.postscript_data = request

                logger.info(
                    'Received first postscript request of file', 
                    extra={'action': 'postscript', 'event': 'print_job'}
                )
                continue
            elif printer.receiving_postscript:
                printer.postscript_data += request

                if '%%EOF' in request:
                    printer.save_postscript()
                    printer.receiving_postscript = False
                continue
            
            commands = self.parse_commands(request)

            logger.debug('Request received', extra={'action': 'request', 'event': 'command_received'})

            if len(commands) == 0:
                emptyRequest = True
                break

            try:
                response = ''
                for command in commands:
                    command = command.lstrip()
                    if command.startswith("@PJL "):
                        command = command[5:]
                        if printer.printing_raw_job:
                            printer.save_raw_print_job()
                        if command.startswith("ECHO"):
                            response += printer.command_echo(command)
                        elif command.startswith("USTATUSOFF"):
                            response += printer.command_ustatusoff(command)
                        elif command.startswith("INFO ID"):
                            response += printer.command_info_id(command)
                        elif command.startswith("INFO STATUS"):
                            response += printer.command_info_status(command)
                        elif command.startswith("FSDIRLIST"):
                            response += printer.command_fsdirlist(command)
                        elif command.startswith("FSQUERY"):
                            response += printer.command_fsquery(command)
                        elif command.startswith("FSMKDIR"):
                            response += printer.command_fsmkdir(command)
                        elif command.startswith("FSUPLOAD"):
                            response += printer.command_fsupload(command)
                        elif command.startswith("FSDOWNLOAD"):
                            response += printer.command_fsdownload(command)
                        elif command.startswith("RDYMSG"):
                            response += printer.command_rdymsg(command)
                        else:
                            logger.error(
                                "Unknown command received", 
                                extra={'action': 'cmd_unknown', 'command': str(command)}
                            )
                    else:
                        response += printer.append_raw_print_job(command)

                logger.info("Response sent", extra={'action': 'response', 'event': 'response_sent'})
                self.request.sendall(response.encode('UTF-8'))

            except Exception as e:
                tb = sys.exc_info()[2]
                traceback.print_tb(tb)
                logger.error(
                    "Error occurred while processing request", 
                    extra={'action': 'error_caught', 'event': 'error', 'error': str(e)}
                )

        if printer.printing_raw_job:
            printer.save_raw_print_job()

        logger.info("Connection closed", extra={'action': 'close_conn', 'event': 'connection_closed'})

        # Remove filter after connection is closed
        logger.removeFilter(connection_filter)


if __name__ == "__main__":
    HOST, PORT = args.host, 9100

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    logger.info("Server started", extra={'action': 'start', 'event': 'server_start'})
    server.serve_forever()
