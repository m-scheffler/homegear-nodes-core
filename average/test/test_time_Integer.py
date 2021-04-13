from homegear import Homegear
import sys
import time
import random


def buildAverage(numbers):
    if numbers:
        return sum(numbers)/len(numbers)


def setup():
    nodeIds = hg.addNodesToFlow("Average Unit test", "unit-test", testFlow)

    if not nodeIds:
        raise SystemError('Error =>  Could not create flow.')

    n1 = nodeIds["n1"]
    n2 = nodeIds["n2"]

    if not hg.restartFlows():
        raise SystemError("Error => Could not restart flows.")

    while not hg.nodeBlueIsReady():
        time.sleep(1)

    return n1, n2


def test_average_integers():
    n1, n2 = setup()
    values = []
    for value in testValues:
        hg.setNodeVariable(n1, "fixedInput0", {"payload": int(value)})
        values.append(int(value))
    average = buildAverage(values)
    time.sleep(6)

    inputHistory = hg.getNodeVariable(n2, "inputHistory0")
    try:
        assert len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}"
        assert inputHistory[0][1]['payload'] == round(average, 0), f"Payload is {inputHistory[0][1]['payload']}, but should be {round(average, 0)}"

        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return 1
    except AssertionError as e:
        print(e)
        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return -1


def test_average_double():
    n1, n2 = setup()
    for value in testValues:
        hg.setNodeVariable(n1, "fixedInput0", {"payload": float(value)})
    average = buildAverage(testValues)
    time.sleep(6)

    inputHistory = hg.getNodeVariable(n2, "inputHistory0")
    try:
        assert len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}"
        assert inputHistory[0][1]['payload'] == round(average, 0), f"Payload is {inputHistory[0][1]['payload']}, but should be {round(average, 0)}"

        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return 1
    except AssertionError as e:
        print(e)
        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return -1


def test_average():
    n1, n2 = setup()
    for value in testValues:
        hg.setNodeVariable(n1, "fixedInput0", {"payload": value})
    average = buildAverage(testValues)
    time.sleep(6)

    inputHistory = hg.getNodeVariable(n2, "inputHistory0")
    try:
        assert len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}"
        assert inputHistory[0][1]['payload'] == round(average, 0), f"Payload is {inputHistory[0][1]['payload']}, but should be {round(average, 0)}"

        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return 1
    except AssertionError as e:
        print(e)
        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return -1


def test_average_zero():
    n1, n2 = setup()
    values = [0, 0, 0, 0, 42.42, 74, 2.56, 0, 0, 0]
    for value in values:
        hg.setNodeVariable(n1, "fixedInput0", {"payload": value})
    average = buildAverage(values)
    time.sleep(6)

    inputHistory = hg.getNodeVariable(n2, "inputHistory0")
    try:
        assert len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}"
        assert inputHistory[0][1]['payload'] == round(average, 0), f"Payload is {inputHistory[0][1]['payload']}, but should be {round(average, 0)}"

        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return 1
    except AssertionError as e:
        print(e)
        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return -1


def test_average_append():
    n1, n2 = setup()
    values = testValues
    for value in values:
        hg.setNodeVariable(n1, "fixedInput0", {"payload": value})
    time.sleep(1)
    for i in range(len(testValues)):
        if i % 2 == 0:
            hg.setNodeVariable(n1, "fixedInput0", {"payload": testValues[i]})
            values.append(testValues[i])
    average = buildAverage(values)
    time.sleep(5)

    inputHistory = hg.getNodeVariable(n2, "inputHistory0")
    try:
        assert len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}"
        assert inputHistory[0][1]['payload'] == round(average, 0), f"Payload is {inputHistory[0][1]['payload']}, but should be {round(average, 0)}"

        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return 1
    except AssertionError as e:
        print(e)
        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return -1


def test_average_negative():
    n1, n2 = setup()
    values = []
    for value in testValues:
        hg.setNodeVariable(n1, "fixedInput0", {"payload": (value * (-1))})
        values.append(value * (-1))
    average = buildAverage(values)
    time.sleep(6)

    inputHistory = hg.getNodeVariable(n2, "inputHistory0")
    try:
        assert len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}"
        assert inputHistory[0][1]['payload'] == round(average, 0), f"Payload is {inputHistory[0][1]['payload']}, but should be {round(average, 0)}"

        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return 1
    except AssertionError as e:
        print(e)
        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return -1


def test_average_random():
    n1, n2 = setup()
    values = []
    for i in range(random.randint(20, 100)):
        value = random.random() * random.random() * random.randint(0, 100)
        hg.setNodeVariable(n1, "fixedInput0", {"payload": value})
        values.append(value)
    average = buildAverage(values)
    time.sleep(6)

    inputHistory = hg.getNodeVariable(n2, "inputHistory0")
    try:
        assert len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}"
        assert inputHistory[0][1]['payload'] == round(average, 0), f"Payload is {inputHistory[0][1]['payload']}, but should be {round(average, 0)}"

        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return 1
    except AssertionError as e:
        print(e)
        hg.removeNodesFromFlow("Average Unit test", "unit-test")
        return -1


if len(sys.argv) > 1:
    hg = Homegear(sys.argv[1])
else:
    hg = Homegear("/var/run/homegear/homegearIPC.sock")

testFlow = [
    {
        "id": "n1",
        "type": "average",
        "averageOver": "time",
        "interval": "5",
        "round": "integer",
        "wires": [
            [{"id": "n2", "port": 0}]
        ]
    },
    {
        "id": "n2",
        "type": "unit-test-helper",
        "inputs": 1
    }
]

testValues = [5, 10, 42, 20, 2, 37, 4, 0.2, 4.2, 42.42]

print("testing version time with integers")
print("test 1: testing with integers")
if test_average_integers() == 1:
    print("test passed")
else:
    print("test failed")

print("test 2: testing with doubles")
if test_average_double() == 1:
    print("test passed")
else:
    print("test failed")

print("test 3: testing with integers and doubles")
if test_average() == 1:
    print("test passed")
else:
    print("test failed")

print("test 4: testing with zeros")
if test_average_zero() == 1:
    print("test passed")
else:
    print("test failed")

print("test 5: testing with negative numbers")
if test_average_negative() == 1:
    print("test passed")
else:
    print("test failed")

print("test 6: testing add in the interval")
if test_average_append() == 1:
    print("test passed")
else:
    print("test failed")

print("test 7: testing with random numbers")
if test_average_random() == 1:
    print("test passed")
else:
    print("test failed")
