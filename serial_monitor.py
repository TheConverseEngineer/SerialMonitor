import serial
import sys
import getopt

BYTEORDER = "little"
ENCODING_SCHEME = 'utf-8'
   
class SerialPipeline:
    def __init__(self, port_name: str, baud_rate: int, delimeter: bytes, verbose: bool):
        """
        Monitors a single serial port

            Parameters:
                port_name (string): name of this serial port
                baud_rate (int):    the baud rate of the device connected to this port
                delimeter (bytes):  the character to use to signify a complete transimision (recommended to use '\\n')
                verbose   (bool):   if true, serial data will be outputted to terminal
        """
        self.port_name = port_name
        self.serial_port = serial.Serial(port_name, baudrate=baud_rate)
        self.delimeter = int.from_bytes(delimeter, byteorder=BYTEORDER)
        self.verbose = verbose

        self.cache = bytearray()
        self.lines = []

    def update(self):
        """ Checks serial port buffer and writes to terminal if needed """
        in_buffer = self.serial_port.in_waiting
        if in_buffer > 0:
            data = self.serial_port.read(in_buffer)

            for data_byte in data:
                if data_byte == self.delimeter: # Flush cache
                    if (self.verbose): print(self.port_name + ": " + self.cache.decode(ENCODING_SCHEME))
                    self.lines.append(bytes(self.cache))
                    self.cache = bytearray()
                else:
                    self.cache.append(data_byte)

    def close(self):
        """ Closes this serial port """
        self.serial_port.close()

    def file_dump(self):
        """ Dumps serial data to a binary file """
        file_name = self.port_name + "_data.txt"
        with open(file_name, "wb") as file:
            for line in self.lines:
                file.write(line)


def main(ports: list, baud_rate: int, delimeter: bytes, verbose: bool, save_to_file: bool):
    """
    Creates and updates the serial pipelines

        Parameters:
            ports (list[string]):       the list of serial ports to monitor
            baud_rate (int):            the desired baud rate
            delimeter (byte):           the desired delimeter
            verbose (bool):             if true, all serial data will be printed to terminal
            save_to_file (bool):        if true, save all serial data to a file
    """
    pipelines = []
    for name in ports:
        pipelines.append(SerialPipeline(name, baud_rate, delimeter, verbose))

    print("All ports opened!")

    try:
        while True:
            for pipeline in pipelines:
                pipeline.update()
    except KeyboardInterrupt:
        print("Closing all serial ports!")
        for pipeline in pipelines: pipeline.close()

    if save_to_file:
        for pipeline in pipelines:
            print(f"Saving data from port {pipeline.port_name}")
            pipeline.file_dump()


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "hvb:fd:")
    if ('-h', '') in opts:
        print(
            """
            Usage: serial_monitor.py [options] [ports] 

            Options:
                -h              opens help menu
                -b [int]        specify the baud rate (defaults to 115200)
                -v              if used, serial data will be printed on terminal
                -f              if used, serial data will be saved to a file on program completion 
                -d [char]       specify the delimeter (defaults to '\\n')

            After using any options, list the desired serial ports, one after another, seperated by a space 
                ex: serial_monitor.py -v -f COM1 COM3 COM13
            """         
        )
    else:
        baud_rate = 115200
        verbose = False
        save_to_file = False
        delimiter = b'\n'

        for cmd, param in opts:
            if cmd == '-b': baud_rate = int(param)
            elif cmd == '-v': verbose = True
            elif cmd == '-f': save_to_file = True
            elif cmd == '-d': delimiter = bytes(param, ENCODING_SCHEME)
        
        main(args, baud_rate, delimiter, verbose, save_to_file)
