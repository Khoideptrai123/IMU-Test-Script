import serial
import serial.tools.list_ports
import datetime as dt
import time
import csv
import matplotlib.pyplot as plt
import numpy
import re

def find_port(number):
    ports = list(serial.tools.list_ports.comports())
    if not len(ports):
        raise IOError("No ports found")
    if number == 1:
        print("Please select the port for Wearable:")
    counter = 0
    for port in ports:
        print(str(counter) + " " + str(port))
        counter = counter + 1
    selected_port = None
    while selected_port not in range(len(ports)):
        error_message = "Please enter a valid integer from %d to %d" % (0, len(ports) - 1)
        try:
            selected_port = int(input("Choose the port: "))
            if selected_port not in range(len(ports)):
                print(error_message)
        except ValueError:
            print(error_message)
            continue
    port = str(ports[int(selected_port)]).split(" - ")[0]
    print("Port selected: %s\n" % port)
    return port

def read_live_data(wearable_port):
    """Opening of the serial port"""
    IMU1_num = []
    IMU2_num = []
    IMU3_num = []

    try:
        wearable = serial.Serial(wearable_port, baudrate=115200, timeout=5)
        #arduino = serial.Serial(arduino_port, timeout=1)
        # Delay for 2 seconds to wait for serial port to be ready.
        print("Waiting 2 seconds for serial to be ready.")
        time.sleep(2)
    except Exception as e:
        print(e)
        print('Please check the port')
        return

    input("Press Enter to continue...")
    str(wearable.write(bytes(33)))
    # Open file to store the data; filename includes date and time; format: data-YYYYMMDDHHmmss.csv
    filename = "data-" + str(dt.datetime.now().strftime("%Y%m%d%H%M%S")) + ".csv"
    filenamplot = "plot-" + str(dt.datetime.now().strftime("%Y%m%d%H%M%S")) + ".png"
    print("Opening %s" % filename)
    f = open(filename, "a+")
    # f.write("power,rpm\n")
    count = 1000
    # Get data and continuously yield Power and RPM as integers

    while (count >0):
        count = count -1
        #if arduino.in_waiting > 0:
        wearable.flushInput()

        '''
            arduino_output = arduino.readline().decode("utf_8", "strict")
            print("Distance: %s" % arduino_output)
            f.writelines("%s" % arduino_output)
            if arduino_output == "Hard Stop\r\n":
                break
            arduino_output = arduino_output.replace("\r\n", "")
            Distance.append(int(float(arduino_output)))
        '''

        try:
            data = wearable.readline().decode("utf_8", "strict")
            data = data.replace("\r\n", "\n").split()
            IMU1= data[2].replace("\n", "")
            IMU1_num.append(int(IMU1))
            IMU2 = data[3].replace("\n", "")
            IMU2_num.append(int(IMU2))
            IMU3 = data[4].replace("\n", "")
            IMU3_num.append(int(IMU3))
            print("IMU1: %s\t IMU2: %s\t IMU3: %s\t" % (IMU1, IMU2, IMU3))
            f.writelines("%s,%s,%s,%s\n" % (IMU1, IMU2, IMU3))
            yield int(IMU1), int(IMU2), int(IMU3)
        except Exception as e:
            print('error')
            f.writelines("Error\n")

    print('Program ended.')
    t = numpy.linspace(1, len(IMU1_num), len(IMU1_num))
    fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(16.0, 9.0))  # create figure & 1 axis
    ax1.plot(t, IMU1_num, t, IMU2_num,t, IMU3_num)
    ax1.set_title('IMU')
    ax1.legend(('IMU1', 'IMU2', 'IMU3'))
    # manager = plt.get_current_fig_manager()
    # manager.resize(*manager.window.maxsize())
    fig.savefig(filenamplot)
    plt.show()

    f.close()
    #arduino.close()
    wearable.close()


def main():
    #arduino_port = find_port(1)
    wearable_port = find_port(1)
    for data_row in read_live_data(wearable_port):
        print("power: %s \t rpm: %s" % (data_row[0], data_row[1], data_row[2]))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program ended by user.")
