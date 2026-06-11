import supervisor
import time
import board
import pwmio
from analogio import AnalogIn
from analogio import AnalogOut

import busio
import digitalio
from mcp48xx import MCP4822

# --- Setup the SPI Bus ---
# Note: The MCP4822 only needs SCK and MOSI, as it doesn't send data back.
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)


# --- Setup the Chip Select (CS) Pin ---
# This is the crucial fix. The library requires a DigitalInOut object.
cs = digitalio.DigitalInOut(board.D10)
cs_2 = digitalio.DigitalInOut(board.D9)
# The `SPI` object and the `cs` object are the only required parameters for the MCP4822 class.

# --- Initialize the DAC ---
# Gain is not a parameter here. It's set for each channel individually later.
dac = MCP4822(spi, cs)
dac_2 = MCP4822(spi, cs_2)

# --- Configure Each Channel ---
# Channel A
dac.channel_a.gain = 2          # Use 2x gain (0 - 4.096V output). Use 1 for 0 - 2.048V.
dac.channel_a.active = True     # Turn the channel on.
# Channel B
dac.channel_b.gain = 2          # Use 2x gain
dac.channel_b.active = True     # Turn the channel on.
# Channel C
dac_2.channel_a.gain = 2          # Use 2x gain (0 - 4.096V output). Use 1 for 0 - 2.048V.
dac_2.channel_a.active = True     # Turn the channel on.
# Channel D
dac_2.channel_b.gain = 2          # Use 2x gain
dac_2.channel_b.active = True     # Turn the channel on.

def set_voltage_a(val):
    # dac.channel_a.value = 65536
    dac.channel_a.value = int(val * 16000)
    pass
def set_voltage_b(val):
    # dac.channel_a.value = 65536
    dac.channel_b.value = int(val * 16000)
    pass
def set_voltage_c(val):
    # dac.channel_a.value = 65536
    dac_2.channel_a.value = int(val * 16000)
    pass
def set_voltage_d(val):
    # dac.channel_a.value = 65536
    dac_2.channel_b.value = int(val * 16000)
    pass

# ---
# # Code for running OLED screen 
# from fourwire import FourWire
# from adafruit_ssd1331 import SSD1331
# from adafruit_display_text import label
# import displayio
# import terminalio
# import supervisor

# displayio.release_displays()

# spi = board.SPI()
# tft_cs = board.D10
# tft_dc = board.D7
# display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.D9)
# display = SSD1331(display_bus, width=96, height=64)
# ---

# ---
# # Comment this in if connecting to E-ink. Make sure to comment out lines pwm pins that are being used by E-ink.
# import displayio
# from fourwire import FourWire
# import adafruit_il91874
# from adafruit_display_text import label
# import terminalio
# from adafruit_display_text import wrap_text_to_lines

# displayio.release_displays()

# spi = board.SPI()
# epd_cs = board.D13
# epd_dc = board.D12
# epd_reset = board.D5
# epd_busy = board.D7
# ---

# pwm = pwmio.PWMOut(board.D9, frequency=500)
# pwm = pwmio.PWMOut(board.D9, duty_cycle=2 ** 15, frequency=440, variable_frequency=True)
pwm5 = pwmio.PWMOut(board.D5, duty_cycle=2 ** 15)
pwm7 = pwmio.PWMOut(board.D7, duty_cycle=2 ** 15)
# pwm9 = pwmio.PWMOut(board.D9, duty_cycle=2 ** 15)
# pwm10 = pwmio.PWMOut(board.D10, duty_cycle=2 ** 15)
pwm11 = pwmio.PWMOut(board.D11, duty_cycle=2 ** 15)
pwm12 = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15)
pwm13 = pwmio.PWMOut(board.D13, duty_cycle=2 ** 15)

# For listening for serial inputs
####
# Define names for In and Out pins
Vout0 = AnalogOut(board.A0)
Vout1 = AnalogOut(board.A1)
Vin2 = AnalogIn(board.A2)
Vin3 = AnalogIn(board.A3)
Vin4 = AnalogIn(board.A4)
Vin5 = AnalogIn(board.A5)
Vin6 = AnalogIn(board.D2) # according to pinout doc pin labelled as 2 is another AI
NRdChLim = 5 # Upper limit for no of channels that can read, previously NRdChLim = 4

B2U_Cal = 14/3

# Define the constants
# For notes on the following see
# https://learn.adafruit.com/circuitpython-basics-analog-inputs-and-outputs/analog-to-digital-converter-inputs
# ADC values in circuit python are all put in the range of 16-bit unsigned values so 0 - 65535 (-1+2**16)
Vmax = Vin2.reference_voltage # max AO/AI value
bit_scale = (-1+(2**16) )#(-1+(64*1024)) # 64 bits

# Functions to convert from 12-bit to Volt.
def dac_value(volts):
    return int(volts / 3.3 * 65535)
    #return int((volts / Vmax)*bit_scale)

def get_voltage(pin):
    return (pin.value * 3.3) / 65535
    #return ((pin.value*Vmax)/bit_scale)

def get_PWM(percentage):
    return (int(percentage/100.0*0xffff+0.5))

def Simple_Vout_A0(command):
    # If the user inputs command a<value> this will be interpreted as setting A0 to the volt level <value>
    try:
        SetVoltage = float(command[1:])
        if SetVoltage >= 0.0 and SetVoltage < Vmax: # Sets limits on the Output voltage to board specs
            Vout0.value = dac_value(SetVoltage) # Set the voltage
        else:
            Vout0.value = dac_value(0.0) # Set the voltage to zero in the event of SetVoltage range error
    except Exception as e:
        print('\nERROR: Simple_Vout_A0\n')
        print(e)

def Simple_Vout_A1(command):
    # If the user inputs command b<value> this will be interpreted as setting A1 to the volt level <value>
    try:
        SetVoltage = float(command[1:])
        if SetVoltage >= 0.0 and SetVoltage < Vmax: # Sets limits on the Output voltage to board specs
            Vout1.value = dac_value(SetVoltage) # Set the voltage
        else:
            Vout1.value = dac_value(0.0) # Set the voltage to zero in the event of SetVoltage range error
    except Exception as e:
        print('\nERROR: Simple_Vout_A1\n')
        print(e)

def Simple_Read():
    try:
        # High-impedance voltage reading Vout = Vin
        V2real = get_voltage(Vin2) # no BP-UP on A2
        V3real = get_voltage(Vin3) # no BP-UP on A3
        V4real = get_voltage(Vin4) # no BP-UP on A4
        V5real = get_voltage(Vin5) # no BP-UP on A5
        # format string to output to nearest 10 mV
        #output_str = '%(v2)0.2f, %(v3)0.2f, %(v4)0.2f, %(v5)0.2f'%{"v2":V2real, "v3":V3real, "v4":V4real, "v5":V5real}
        DC_offset = get_voltage(Vin6) # read the DC offset of the BP-UP circuit
        output_str = '%(v2)0.2f, %(v3)0.2f, %(v4)0.2f, %(v5)0.2f, %(v6)0.2f'%{"v2":V2real, "v3":V3real, "v4":V4real, "v5":V5real, "v6":DC_offset}
        print(output_str) # Prints to serial to be read by LabVIEW
    except Exception as e:
        print('\nERROR: Simple_Read\n')
        print(e)

# Function to display voltage on e-ink
# def init_eink(vage = 1, ptop = 0):
#     try:
#         displayio.release_displays()
#         # Create the displayio connection to the display pins
#         display_bus = FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
#         time.sleep(1)  # Wait a bit
#         # Create the display object - the third color is red (0xff0000)
#         display = adafruit_il91874.IL91874(
#             display_bus,
#             width=264,
#             height=176,
#             busy_pin=epd_busy,
#             highlight_color=0xFF0000,
#             rotation=90,
#         )

#         # Create a display group for our screen objects
#         g = displayio.Group()
#         # Display a ruler graphic from the root directory of the CIRCUITPY drive

#         val = "The average voltage is " + str(vage) + " volts. Peak to peak voltage is " + str(ptop) + " volts."
#         print(val)
#         wrapped_lines = wrap_text_to_lines(val, max_chars=40)
#         multi_line_text = "\n".join(wrapped_lines)
#         text_label = label.Label(terminalio.FONT, text = multi_line_text, color=0xFF0000, scale=1, line_spacing=1.25, x=10, y=30)
#         g.append(text_label)
#         # pic = displayio.OnDiskBitmap("/display-ruler.bmp")
#         # # Create a Tilegrid with the bitmap and put in the displayio group
#         # t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
#         # g.append(t)

#         # Place the display group on the screen (does not refresh)
#         display.root_group = g

#         # Show the image on the display
#         display.refresh()

#         print("refreshed")

#         # Do Not refresh the screen more often than every 180 seconds
#         #   for eInk displays! Rapid refreshes will damage the panel.
#         # time.sleep(180)
#         print("Done!")

#     except Exception as e:
#         print('\nError: init_eink\n')
#         print (e)

# # Function to read voltage from channel A2 and display on OLED screen
# def read_and_display():

#     splash = displayio.Group()
#     display.root_group = splash

#     # Green background
#     color_bitmap = displayio.Bitmap(96, 64, 1)
#     color_palette = displayio.Palette(1)
#     color_palette[0] = 0x00FF00
#     bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
#     splash.append(bg_sprite)

#     # Purple inner rectangle
#     inner_bitmap = displayio.Bitmap(86, 54, 1)
#     inner_palette = displayio.Palette(1)
#     inner_palette[0] = 0xAA0088
#     inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=5)
#     splash.append(inner_sprite)
#     text = "Booting..."
#     text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=12, y=32)
#     splash.append(text_area)
#     text_area_2 = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=12, y=52)
#     splash.append(text_area_2)
#     i = 1
#     # runs for a minute to allow other operations after without having to resent IBM4
#     while i < 122:
#         vol = get_voltage(Vin2)
#         if vol < 3.3:
#             text_area.text = str(vol) + " V"
#             display.refresh()
#             if i%2:
#                 text_area_2.text = str(i/2 - 1/2) + "/60"
#                 display.refresh()
#             else:
#                 pass
#         else:
#             text_area.text = "Out of Range"
#             display.refresh()
#             if i%2:
#                 text_area_2.text = str(i/2 - 1/2) + "/60"
#                 display.refresh()
#             else:
#                 pass
#         # Auto‑update every 0.5 seconds
#         time.sleep(0.5)
#         i = i+1
#     text_area.text = "Done!"
#     display.refresh()
#     pass

while True:
    if supervisor.runtime.serial_bytes_available:   # Listens for a serial command
        command = input()
        if command.startswith("*IDN"):
            print('ISBY-UCC-RevA.1')
        if command.startswith("Speak"):
            print('Hello Liam!')
        if command.startswith("Calibrate"):
            try:
                with open("/Calibration.txt", "r") as fp:
                    read_data = fp.read()
                    fp.close()
                    print(str(read_data))
            except OSError as e:  # When the file is not available...
                print('ERROR: Calibration file not available')

            # Split the string at the comma
            numbers = read_data.split(',')

            # Convert the substrings to floats
            K = float(numbers[0])
            KI = float(numbers[1])

        elif command.startswith("Mode"):
            TheMode = int(command[4:])
            print(TheMode)
        elif command.startswith("PWM"):
            try:
                Tokens = command[3:].split(":")
                ThePin = int(Tokens[0])
                SetPWM = float(Tokens[1])
                if ThePin == 5:
                    pwm5.duty_cycle = get_PWM(SetPWM)
                elif ThePin == 7:
                    pwm7.duty_cycle = get_PWM(SetPWM)
                # elif ThePin == 9:
                #     pwm9.duty_cycle = get_PWM(SetPWM)
                # elif ThePin == 10:
                #     pwm10.duty_cycle = get_PWM(SetPWM)
                elif ThePin == 11:
                    pwm11.duty_cycle = get_PWM(SetPWM)
                elif ThePin == 12:
                    pwm12.duty_cycle = get_PWM(SetPWM)
                elif ThePin == 13:
                    pwm13.duty_cycle = get_PWM(SetPWM)
                else:
                    print('Pin out of range: 5,7,9,10-13')
            except ValueError as ex:
                print('Vset must be an integer')
                print(ex)
            else:
                print("PWMset", ThePin, "=", str(SetPWM), end=' ')
                print()
        elif command.startswith("Write"):
            try:
                Tokens = command[5:].split(":")
                Chan = int(Tokens[0])
                SetVoltage = float(Tokens[1])
                if SetVoltage >= 0 and SetVoltage < 3.31:
                    # Sets limits on the Output voltage to board specs
                    if Chan == 0:
                        Vout0.value = dac_value(SetVoltage)  # Set the voltage
                    elif Chan == 1:
                        Vout1.value = dac_value(SetVoltage)  # Set the voltage
                    else:
                        print('Channel out of range: 0 - 1')
                else:
                    print('Vset out of range: 0 - 3.3V')
            except ValueError as ex:
                print('Vset must be a float')
                print(ex)
            except:
                print('Unknown problem')
            else:
                print("Vset", Chan, "=", str(SetVoltage), end=' ')
                print()
        elif command.startswith("Read"):
            try:
                Tokens = command[4:].split(":")
                Chan = int(Tokens[0])
                N = int(Tokens[1])
                if Chan == 0:
                    Pin = Vin2
                elif Chan == 1:
                    Pin = Vin3
                elif Chan == 2:
                    Pin = Vin4
                elif Chan == 3:
                    Pin = Vin5
                elif Chan == 4:
                    Pin = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                if N < 1:
                    print('Must read at least one value')
            except ValueError as ex:
                print('Channel must be an integer')
                print(ex)
            except:
                print('Unknown problem')
            else:
                if Chan in range(0, NRdChLim) and N > 0:
                    Ref = 0.0
                    Mult = 1
                    if TheMode == 1:
                        for i in range(100):
                            Ref += get_voltage(Vin6)
                        Ref /= 100
                        Mult = B2U_Cal
                    Values = [0] * N
                    for i in range(N):
                        Values[i] = get_voltage(Pin)
                    print("Output", Chan, "=", str((Values[0]-Ref)*Mult), end=' ')
                    for i in range(1, N):
                        print(",", str((Values[i]-Ref)*Mult), end=' ')
                    print()
        elif command.startswith("Average"):
            try:
                Tokens = command[7:].split(":")
                Chan = int(Tokens[0])
                N = int(Tokens[1])
                if Chan == 0:
                    Pin = Vin2
                elif Chan == 1:
                    Pin = Vin3
                elif Chan == 2:
                    Pin = Vin4
                elif Chan == 3:
                    Pin = Vin5
                elif Chan == 4:
                    Pin = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                if N < 1:
                    print('Must average at least one value')
            except ValueError as ex:
                print('Channel must be an integer')
                print(ex)
            except:
                print('Unknown problem')
            else:
                if Chan in range(0, NRdChLim) and N > 0:
                    Ref = 0.0
                    Mult = 1
                    if TheMode == 1:
                        for i in range(100):
                            Ref += get_voltage(Vin6)
                        Ref /= 100
                        Mult = B2U_Cal
                    Value = 0.0
                    for i in range(N):
                        Value += get_voltage(Pin)
                    Value /= N
                    print("Average", Chan, "=", str((Value-Ref)*Mult))
        elif command.startswith("BRead"):
            try:
                Tokens = command[5:].split(":")
                Chan = int(Tokens[0])
                N = int(Tokens[1])
                if Chan == 0:
                    Pin = Vin2
                elif Chan == 1:
                    Pin = Vin3
                elif Chan == 2:
                    Pin = Vin4
                elif Chan == 3:
                    Pin = Vin5
                elif Chan == 4:
                    Pin = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                if N < 1:
                    print('Must read at least one value')
            except ValueError as ex:
                print('Channel must be an integer')
                print(ex)
            except:
                print('Unknown problem')
            else:
                if Chan in range(0, NRdChLim) and N > 0:
                    Values = [0] * N
                    for i in range(N):
                        Values[i] = Pin.value
                    print("Output", Chan, "=", str(Values[0]), end=' ')
                    for i in range(1, N):
                        print(",", str(Values[i]), end=' ')
                    print()
        elif command.startswith("Diff_Read"):
            try:
                Tokens = command[9:].split(":")
                ChanPlus = int(Tokens[0])
                if ChanPlus == 0:
                    Pplus = Vin2
                elif ChanPlus == 1:
                    Pplus = Vin3
                elif ChanPlus == 2:
                    Pplus = Vin4
                elif ChanPlus == 3:
                    Pplus = Vin5
                elif ChanPlus == 4:
                    Pplus = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                ChanMinus = int(Tokens[1])
                if ChanMinus == 0:
                    Pminus = Vin2
                elif ChanMinus == 1:
                    Pminus = Vin3
                elif ChanMinus == 2:
                    Pminus = Vin4
                elif ChanMinus == 3:
                    Pminus = Vin5
                elif ChanMinus == 4:
                    Pminus = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                N = int(Tokens[2])
                if N < 1:
                    print('Must read at least one value')
            except ValueError as ex:
                print('Channel must be an integer')
                print(ex)
            except:
                print('Unknown problem')
            else:
                if ChanPlus in range(0, NRdChLim) and ChanMinus in range(0, NRdChLim) and N > 0:
                    Mult = 1
                    if TheMode == 1:
                        Mult = B2U_Cal
                    Values = [0] * N
                    for i in range(N):
                        Values[i] = get_voltage(Pplus)-get_voltage(Pminus)
                    print("Output =", str(Values[0]*Mult), end=' ')
                    for i in range(1, N):
                        print(",", str(Values[i]*Mult), end=' ')
                    print()
        elif command.startswith("Diff_Average"):
            try:
                Tokens = command[12:].split(":")
                ChanPlus = int(Tokens[0])
                if ChanPlus == 0:
                    Pplus = Vin2
                elif ChanPlus == 1:
                    Pplus = Vin3
                elif ChanPlus == 2:
                    Pplus = Vin4
                elif ChanPlus == 3:
                    Pplus = Vin5
                elif ChanPlus == 4:
                    Pplus = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                ChanMinus = int(Tokens[1])
                if ChanMinus == 0:
                    Pminus = Vin2
                elif ChanMinus == 1:
                    Pminus = Vin3
                elif ChanMinus == 2:
                    Pminus = Vin4
                elif ChanMinus == 3:
                    Pminus = Vin5
                elif ChanMinus == 4:
                    Pminus = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                N = int(Tokens[2])
                if N < 1:
                    print('Must read at least one value')
            except ValueError as ex:
                print('Channel must be an integer')
                print(ex)
            except:
                print('Unknown problem')
            else:
                if ChanPlus in range(0, NRdChLim) and ChanMinus in range(0, NRdChLim) and N > 0:
                    Mult = 1
                    if TheMode == 1:
                        Mult = B2U_Cal
                    Value = 0.0
                    for i in range(N):
                        Value += (get_voltage(Pplus) - get_voltage(Pminus))
                    Value /= N
                    print("Average =", str(Value*Mult))
        elif command.startswith("Diff_BRead"):
            try:
                Tokens = command[10:].split(":")
                ChanPlus = int(Tokens[0])
                if ChanPlus == 0:
                    Pplus = Vin2
                elif ChanPlus == 1:
                    Pplus = Vin3
                elif ChanPlus == 2:
                    Pplus = Vin4
                elif ChanPlus == 3:
                    Pplus = Vin5
                elif ChanPlus == 4:
                    Pplus = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                ChanMinus = int(Tokens[1])
                if ChanMinus == 0:
                    Pminus = Vin2
                elif ChanMinus == 1:
                    Pminus = Vin3
                elif ChanMinus == 2:
                    Pminus = Vin4
                elif ChanMinus == 3:
                    Pminus = Vin5
                elif ChanMinus == 4:
                    Pminus = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                N = int(Tokens[2])
                if N < 1:
                    print('Must read at least one value')
            except ValueError as ex:
                print('Channel must be an integer')
                print(ex)
            except:
                print('Unknown problem')
            else:
                if ChanPlus in range(0, NRdChLim) and ChanMinus in range(0, NRdChLim) and N > 0:
                    Values = [0] * N
                    for i in range(N):
                        Values[i] = Pplus.value - Pminus.value
                    print("Output =", str(Values[0]), end=' ')
                    for i in range(1, N):
                        print(",", str(Values[i]), end=' ')
                    print()
        elif command.startswith("a"):
            Simple_Vout_A0(command)
        elif command.startswith("b"):
            Simple_Vout_A1(command)
        elif command.startswith("l"):
            Simple_Read()
        elif command.startswith("Einit"):
            print("Initialising:")
            Tokens = command[6:].split(":")
            # init_eink(Tokens[0], Tokens[1])
            print("Error: Code not adjusted for E-ink")
        elif command.startswith("OLED"):
            # read_and_display()
            print("Error: Code not adjusted for OLED screen")
        elif command.startswith("DC"):
            Tokens = command[3:].split(":")
            print(Tokens[0])
            print(Tokens[1])
            if Tokens[0] == "a":
                set_voltage_a(float(Tokens[1]))
            elif Tokens[0] == "b":
                set_voltage_b(float(Tokens[1]))
            elif Tokens[0] == "c":
                set_voltage_c(float(Tokens[1]))
            elif Tokens[0] == "d":
                set_voltage_d(float(Tokens[1]))
            else:
                print("Error: Output pin not found")
        else:
            print('\nERROR: Unknown command entered\n')
#    else:
#        print('If you can read this something has gone very wrong. ')




