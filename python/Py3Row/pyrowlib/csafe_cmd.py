"""
Description:
    Py3Row byte handling routines.
    __int2bytes
    __bytes2int
    encode -> creates a csafe frame message to hand off to the PM
    decode -> decodes a csafe response response frame message.
"""
# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
# local
from . import csafe_dic


def __int2bytes(numbytes: int, integer: int) -> list:
    byte = []
    try:
        if not 0 <= integer <= 2 ** (8 * numbytes):
            raise ValueError(f"{integer} is outside the allowable range")

        for k in range(numbytes):
            calcbyte = (integer >> (8 * k)) & 0xFF
            byte.append(calcbyte)

    except Exception as err:
        print(str(err))
    finally:
        return byte


def __bytes2int(raw_bytes):
    num_bytes = len(raw_bytes)
    integer = 0

    for k in range(num_bytes):
        integer = (raw_bytes[k] << (8 * k)) | integer

    return integer


def __bytes2ascii(raw_bytes):
    word = ""
    for letter in raw_bytes:
        word += chr(letter)

    return word


def encode(arguments: list) -> list:
    """
    Encode byte command message.
    Standard Frame structure:
        +------------+----------+----------+-----------+
        | Start Flag | Contents | Checksum | Stop Flag |
        +------------+----------+----------+-----------+
    Extended Frame structure:
        +------------+----------+---------+----------+----------+-----------+
        | Start Flag | Dest Add | Src Add | Contents | Checksum | Stop Flag |
        +------------+----------+---------+----------+----------+-----------+

    Contents.
    Long command:
        +-------------+----------------+----------
        |   command   | data byte count| data ...
        |(0x00 – 0x7F)|   (0 - 255)    | (0 - 255)
        +-------------+----------------+----------

    Short command:
        +----------------------
        | command
        |(0x80 – 0xFF)
        +----------------------

    Description:
        Given an argument list, first build the contents frame starting with
        command.

    Note, that special cases exist with command wrappers. These are commands
    set asside to wrap around propietary commands.
    """

    # priming variables
    i = 0
    message = []
    wrapper = 0
    wrapped = []
    maxresponse = 3  # start & stop flag & status

    # loop through all arguments
    while i < len(arguments):

        arg = arguments[i]
        cmdprop = csafe_dic.cmds[arg]
        command = []

        # Long commands have MSB set,
        # Short commands have MSB clear.
        #
        # load variables if command is a Long Command
        if cmdprop[0] in range(0x0, 0x7F):
            # Array of byte count, [1, 2, 1...]
            for varbytes in cmdprop[1]:
                i += 1
                intvalue = arguments[i]
                bytevalue = __int2bytes(varbytes, intvalue)
                command.extend(bytevalue)

            # data byte count
            command.insert(0, len(command))
        elif cmdprop[0] not in range(0x80, 0xFF):
            raise ValueError(f"Unsupported command {cmdprop}")

        # add command id: CMD|CNT|DATA...
        command.insert(0, cmdprop[0])

        # closes wrapper if required
        if len(wrapped) > 0 and (len(cmdprop) < 3 or cmdprop[2] != wrapper):
            wrapped.insert(0, len(wrapped))  # data byte count for wrapper
            wrapped.insert(0, wrapper)  # wrapper command id
            message.extend(wrapped)  # adds wrapper to message
            wrapped = []
            wrapper = 0

        # create or extend wrapper
        # [0xCMD, [bytes], 0xExtCMD]
        if len(cmdprop) == 3:  # checks if command needs a wrapper
            # checks if currently in the same wrapper
            if (wrapper == cmdprop[2]):
                wrapped.extend(command)
            else:  # creating a new wrapper
                wrapped = command
                wrapper = cmdprop[2]
                maxresponse += 2
            # clear command to prevent it from getting into message
            command = ([])

        # max message length
        cmdid = cmdprop[0] | (wrapper << 8)
        # double return to account for stuffing
        maxresponse += abs(sum(csafe_dic.resp[cmdid][1])) * 2 + 1

        # add completed command to final message
        message.extend(command)

        i += 1

    # closes wrapper if message ended on it
    if len(wrapped) > 0:
        wrapped.insert(0, len(wrapped))  # data byte count for wrapper
        wrapped.insert(0, wrapper)  # wrapper command id
        message.extend(wrapped)  # adds wrapper to message

    # prime variables
    checksum = 0x0
    j = 0

    # checksum and byte stuffing
    while j < len(message):
        # calculate checksum
        checksum = checksum ^ message[j]

        # byte stuffing
        if 0xF0 <= message[j] <= 0xF3:
            message.insert(j, csafe_dic.BSF)
            j += 1
            message[j] = message[j] & 0x3

        j += 1

    # add checksum to end of message
    message.append(checksum)

    # start & stop frames
    message.insert(0, csafe_dic.Standard_Frame_Start_Flag)
    message.append(csafe_dic.Stop_Frame_Flag)

    # check for frame size (96 bytes)
    if len(message) > 96:
        raise Exception("Message is too long: " + len(message))

    # report IDs
    maxmessage = max(len(message) + 1, maxresponse)

    if maxmessage <= 21:
        message.insert(0, 0x01)
        message += [0] * (21 - len(message))
    elif maxmessage <= 63:
        message.insert(0, 0x04)
        message += [0] * (63 - len(message))
    elif (len(message) + 1) <= 121:
        message.insert(0, 0x02)
        message += [0] * (121 - len(message))
        if maxresponse > 121:
            raise UserWarning(
                "Response may be too long to recieve.  Max possible length "
                + str(maxresponse)
            )
    else:
        raise Exception(
            "Message too long.  Message length " + str(len(message))
        )
        message = []

    return message


def __unpack_verify(message: list) -> list:
    # prime variables
    i = 0
    checksum = 0

    try:
        # checksum and unstuff
        while i < len(message):
            # byte unstuffing
            # 0xF3, 0x00 = F0
            # 0xF3, 0x01 = F1
            # 0xF3, 0x02 = F2
            # 0xF3, 0x03 = F3
            if message[i] == csafe_dic.Byte_Stuffing_Flag:
                stuffvalue = message.pop(i + 1)
                message[i] = 0xF0 | stuffvalue

            # calculate checksum
            checksum = checksum ^ message[i]

            i = i + 1

        # checks checksum
        if checksum != 0:
            message = []
            raise ValueError("Checksum error")

        # remove checksum from  end of message
        del message[-1]
    except Exception as err:
        print(str(err))
    finally:
        return message


def decode(transmission: list) -> list:
    """
    Decode response messages.

    Standard Frame structure:
        +------------+----------+----------+-----------+
        | Start Flag | Contents | Checksum | Stop Flag |
        +------------+----------+----------+-----------+
    Extended Frame structure:
        +------------+----------+---------+----------+----------+-----------+
        | Start Flag | Dest Add | Src Add | Contents | Checksum | Stop Flag |
        +------------+----------+---------+----------+----------+-----------+

    Response message contents:
        +--------------+--------------------------
        |    Status    | Command Response data ...
        |(0x00 – 0x7F*)|       (0 - 255)
        +--------------+-------------------------
    Command Response data:
        +-------------+-----------------+-----------
        |   Command   | Data Byte Count |   Data ...
        |(0x00 – 0xFF)|   (0 - 255)     |(0 - 255)
        +-------------+-----------------+----------

        * Note: Response Status Byte Bit-Mapping 0x80/0x30/0x0F
    """

    # prime variables
    message = []
    stopfound = False
    response = None
    dest_add = None
    src_add = None
    pFrameStatus = csafe_dic.PREV_FRAME_STATUS

    try:
        reportid = transmission.pop(0)
        startflag = transmission.pop(0)

        if startflag == csafe_dic.Extended_Frame_Start_Flag:
            dest_add = transmission.pop(0)
            src_add = transmission.pop(0)
        elif startflag != csafe_dic.Standard_Frame_Start_Flag:
            # Keeps the lint happy.
            reportid = reportid
            dest_add = dest_add
            src_add = src_add
            raise ValueError(f"Missing Start Flag: {str(transmission)}.")

        j = 0
        while j < len(transmission):
            if transmission[j] == csafe_dic.Stop_Frame_Flag:
                stopfound = True
                break
            message.append(transmission[j])
            j += 1

        if not stopfound:
            message = []
            raise ValueError(f"Missing Stop Flag: {str(transmission)}.")

        message = __unpack_verify(message)

        # Response Status Byte Bit-Mapping 0x80/0x30/0x0F
        status = message.pop(0)
        prev_frame_status = status & csafe_dic.MASK_PREVIOUS_FRAME_STATUS
        if prev_frame_status != pFrameStatus.OK:
            raise UserWarning(f"Previous message frame status:{prev_frame_status}")

        # prime variables
        response = {"CSAFE_GETSTATUS_CMD": [status]}
        k = 0
        wrapend = -1
        wrapper = 0x0

        # loop through complete frames
        while k < len(message):
            result = []

            # get command name
            msgcmd = message[k]
            if k <= wrapend:
                msgcmd = wrapper | msgcmd  # check if still in wrapper
            msgprop = csafe_dic.resp[msgcmd]
            k = k + 1

            # get data byte count
            bytecount = message[k]
            k = k + 1

            # if wrapper command then gets command in wrapper
            if msgprop[0] == "CSAFE_SETUSERCFG1_CMD" or msgprop[0] == "CSAFE_SETPMCFG_CMD" or msgprop[0] == "CSAFE_GETPMCFG_CMD":
                wrapper = message[k - 2] << 8
                wrapend = k + bytecount - 1
                if bytecount:  # If wrapper length != 0
                    msgcmd = wrapper | message[k]
                    msgprop = csafe_dic.resp[msgcmd]
                    k = k + 1
                    bytecount = message[k]
                    k = k + 1

            # Special case for capability code, response lengths differ based
            # on the capability code.
            if msgprop[0] == "CSAFE_GETCAPS_CMD":
                msgprop[1] = [1] * bytecount

            # Special case for get id, response length is variable.
            if msgprop[0] == "CSAFE_GETID_CMD":
                msgprop[1] = [
                    (-bytecount),
                ]

            # Check that the recieved data bytes is the expected length,
            # sanity check.
            if abs(sum(msgprop[1])) != 0 and bytecount != abs(sum(msgprop[1])):
                raise ValueError("Warning: bytecount is an unexpected length")

            # extract values
            for numbytes in msgprop[1]:
                raw_bytes = message[k: k + abs(numbytes)]
                value = (
                    __bytes2int(raw_bytes)
                    if numbytes >= 0
                    else __bytes2ascii(raw_bytes)
                )
                result.append(value)
                k = k + abs(numbytes)

            response[msgprop[0]] = result
    except KeyError as err:
        print(f"message:[{str(message)}], error: {str(err)}")
    except Exception as err:
        print(str(err))
    finally:
        return response
