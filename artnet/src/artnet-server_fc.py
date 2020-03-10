# Art-Net protocol for Fadecandy
#Adapted from https://github.com/chunk100/Glediator-with-Fadecandy

#Fadecandy stuff
import opc, time

#Artnet stuff
from twisted.internet import protocol, endpoints
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

#Initialise Fadecandy stuff
numLEDs = 250
client = opc.Client('10.0.0.136:7890')
black = (0, 0, 0)
x_size = 8
y_size = 30

# This tells the software where the split between 2 universes is
uni_1_y_size = 17
uni_2_y_size = 8


gridarray = [ [0],
            [0, 0,	30,	60,	90,	120, 150, 180, 210],
            [0, 1,	31,	61,	91,	121, 151, 181, 211],
            [0, 2,	32,	62,	92,	122, 152, 182, 212],
            [0, 3,	33,	63,	93,	123, 153, 183, 213],
            [0, 4,	34,	64,	94,	124, 154, 184, 214],
            [0, 5,	35,	65,	95,	125, 155, 185, 215],
            [0, 6,	36,	66,	96,	126, 156, 186, 216],
            [0, 7,	37,	67,	97,	127, 157, 187, 217],
            [0, 8,	38,	68,	98,	128, 158, 188, 218],
            [0, 9,	39,	69,	99,	129, 159, 189, 219],
            [0, 10,	40,	70,	100, 130, 160, 190, 220],
            [0, 11,	41,	71,	101, 131, 161, 191, 221],
            [0, 12,	42,	72,	102, 132, 162, 192, 222],
            [0, 13,	43,	73,	103, 133, 163, 193, 223],
            [0, 14,	44,	74,	104, 134, 164, 194, 224],
            [0, 15,	45,	75,	105, 135, 165, 195, 225],
            [0, 16,	46,	76,	106, 136, 166, 196, 226],
            [0, 17,	47,	77,	107, 137, 167, 197, 227],
            [0, 18,	48,	78,	108, 138, 168, 198, 228],
            [0, 19,	49,	79,	109, 139, 169, 199, 229],
            [0, 20,	50,	80,	110, 140, 170, 200, 230],
            [0, 21,	51,	81,	111, 141, 171, 201, 231],
            [0, 22,	52,	82,	112, 142, 172, 202, 232],
            [0, 23,	53,	83,	113, 143, 173, 203, 233],
            [0, 24,	54,	84,	114, 144, 174, 204, 234],
            [0, 25,	55,	85,	115, 145, 175, 205, 235],
            [0, 26,	56,	86,	116, 146, 176, 206, 236],
            [0, 27,	57,	87,	117, 147, 177, 207, 237],
            [0, 28,	58,	88,	118, 148, 178, 208, 238],
            [0, 29,	59,	89,	119, 149, 179, 209, 239]]


class ArtNet(DatagramProtocol):
    def __init__(self):
        self.pixels = [ black ] * numLEDs
        self.uni_1_data_received = 0
        self.uni_2_data_received = 0

    def write_pixels(self):
        if self.uni_1_data_received == 1 and self.uni_2_data_received == 1:
            client.put_pixels(self.pixels)
            self.uni_1_data_received = 0
            self.uni_2_data_received = 0

    def datagramReceived(self, data, (host, port)):
        if ((len(data) > 18) and (data[0:8] == "Art-Net\x00")):
            rawbytes = map(ord, data)
            # print(rawbytes)
            opcode = rawbytes[8] + (rawbytes[9] << 8)
            protocolVersion = (rawbytes[10] << 8) + rawbytes[11]
            if ((opcode == 0x5000) and (protocolVersion >= 14)):
                sequence = rawbytes[12]
                physical = rawbytes[13]
                sub_net = (rawbytes[14] & 0xF0) >> 4
                universe = rawbytes[14] & 0x0F
                net = rawbytes[15]
                rgb_length = (rawbytes[16] << 8) + rawbytes[17]
                # print "seq %d phy %d sub_net %d uni %d net %d len %d" % \
                    # (sequence, physical, sub_net, universe, net, rgb_length)
                idx = 18
                x = 1

                if universe == 1:
                    y = 1

                    while ((idx < (rgb_length+18)) and (y <= uni_1_y_size)):
                        r = rawbytes[idx]
                        idx += 1
                        g = rawbytes[idx]
                        idx += 1
                        b = rawbytes[idx]
                        idx += 1
                        # print("x= " + str(x) + ", y=" + str(y) + " r=" + str(r) + ", g=" + str(g) + "b= " +str(b))
                        self.pixels[gridarray[y][x]] = (r, g, b)
                        x += 1
                        if (x > x_size):
                            x = 1
                            y += 1

                    self.uni_1_data_received = 1

                if universe == 2:
                    y = y_size - uni_2_y_size + 1

                    while ((idx < (rgb_length+18)) and (y <= y_size)):
                        r = rawbytes[idx]
                        idx += 1
                        g = rawbytes[idx]
                        idx += 1
                        b = rawbytes[idx]
                        idx += 1
                        # print("x= " + str(x) + ", y=" + str(y) + " r=" + str(r) + ", g=" + str(g) + "b= " +str(b))
                        self.pixels[gridarray[y][x]] = (r, g, b)
                        x += 1
                        if (x > x_size):
                            x = 1
                            y += 1

                    self.uni_2_data_received = 1


                self.write_pixels()


reactor.listenUDP(6454, ArtNet())
reactor.run()
