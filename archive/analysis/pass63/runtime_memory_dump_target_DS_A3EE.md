# Runtime memory dump target

To decode the strongest 4-object position table, dump these bytes while the game is running:

    DS:0xA3EE .. DS:0xA405

Length:

    24 bytes

Interpret as:

    4 records
    each record = 3 little-endian words

Record format:

    word 0 -> object +0x02
    word 1 -> object +0x04
    word 2 -> object +0x08

If using DOSBox debugger, we need current DS value and memory at DS:A3EE.
