from homegear import Homegear
import unittest
import time
import os


class CreateNotRecursiveTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global hg
        hg = Homegear("/var/run/homegear/homegearIPC.sock")

        global path
        path = os.getcwd() + "/testingDirectory"
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def tearDownClass(cls):
        os.rmdir(path)

    def setUp(self):
        testFlow = [
            {
                "id": "n1",
                "type": "watch",
                "path": path,
                "recursive": "false",
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
        nodeIds = hg.addNodesToFlow("Watch Unit test", "unit-test", testFlow)

        if not nodeIds:
            raise SystemError('Error =>  Could not create flow.')

        global n1, n2
        n1 = nodeIds["n1"]
        n2 = nodeIds["n2"]

        if not hg.restartFlows():
            raise SystemError("Error => Could not restart flows.")

        while not hg.nodeBlueIsReady():
            time.sleep(1)

    def tearDown(self):
        hg.removeNodesFromFlow("Watch Unit test", "unit-test")
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def test_createDirectory(self):
        os.mkdir((path + "/foo"))
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[0][1]['action'], "Create", f"Payload is {inputHistory[0][1]['action']}, but should be Create)")

    def test_createDirectories(self):
        for i in range(10):
            os.mkdir((path + "/foo" + str(i)))
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Create", f"Payload is {inputHistory[0][1]['action']}, but should be Create)")

    def test_createFile(self):
        file = open((path + "/foo.txt"), "x")
        file.close()
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[2][1]['action'], "Create", f"Payload is {inputHistory[2][1]['action']}, but should be Create)")

    def test_createFiles(self):
        for i in range(10):
            file = open((path + "/foo" + str(i) + ".txt"), "x")
            file.close()
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[2][1]['action'], "Create", f"Payload is {inputHistory[2][1]['action']}, but should be Create)")


class CreateRecursiveTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global hg
        hg = Homegear("/var/run/homegear/homegearIPC.sock")

        global path
        path = os.getcwd() + "/testingDirectory"
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def tearDownClass(cls):
        os.rmdir(path)

    def setUp(self):
        testFlow = [
            {
                "id": "n1",
                "type": "watch",
                "path": path,
                "recursive": "true",
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
        nodeIds = hg.addNodesToFlow("Watch Unit test", "unit-test", testFlow)

        if not nodeIds:
            raise SystemError('Error =>  Could not create flow.')

        global n1, n2
        n1 = nodeIds["n1"]
        n2 = nodeIds["n2"]

        if not hg.restartFlows():
            raise SystemError("Error => Could not restart flows.")

        while not hg.nodeBlueIsReady():
            time.sleep(1)

    def tearDown(self):
        hg.removeNodesFromFlow("Watch Unit test", "unit-test")
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def test_createDirectory(self):
        os.mkdir((path + "/foo"))
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[0][1]['action'], "Create", f"Payload is {inputHistory[0][1]['action']}, but should be Create)")

    def test_createDirectories(self):
        for i in range(10):
            os.mkdir((path + "/foo" + str(i)))
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Create", f"Payload is {inputHistory[0][1]['action']}, but should be Create)")

    def test_createDirectoryRecursive(self):
        p = path + "/foo"
        for i in range(5):
            os.mkdir(p)
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Create", f"Payload is {inputHistory[0][1]['action']}, but should be Create)")
            p = p + "/foo"

    def test_createFile(self):
        file = open((path + "/foo.txt"), "x")
        file.close()
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[2][1]['action'], "Create", f"Payload is {inputHistory[0][1]['action']}, but should be Create)")

    def test_createFiles(self):
        for i in range(10):
            file = open((path + "/foo" + str(i) + ".txt"), "x")
            file.close()
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[2][1]['action'], "Create", f"Payload is {inputHistory[0][1]['action']}, but should be Create)")


class DeleteNotRecursiveTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global hg
        hg = Homegear("/var/run/homegear/homegearIPC.sock")

        global path
        path = os.getcwd() + "/testingDirectory"
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def tearDownClass(cls):
        os.rmdir(path)

    def setUp(self):
        testFlow = [
            {
                "id": "n1",
                "type": "watch",
                "path": path,
                "recursive": "true",
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
        nodeIds = hg.addNodesToFlow("Watch Unit test", "unit-test", testFlow)

        if not nodeIds:
            raise SystemError('Error =>  Could not create flow.')

        global n1, n2
        n1 = nodeIds["n1"]
        n2 = nodeIds["n2"]

        if not hg.restartFlows():
            raise SystemError("Error => Could not restart flows.")

        while not hg.nodeBlueIsReady():
            time.sleep(1)

    def tearDown(self):
        hg.removeNodesFromFlow("Watch Unit test", "unit-test")
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def test_deleteDirectory(self):
        p = path + "/foo"
        os.mkdir(p)
        time.sleep(1)
        os.rmdir(p)
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")

    def test_deleteDirectories(self):
        p = path + "/foo"
        for i in range(10):
            os.mkdir(p + str(i))
        time.sleep(1)
        for i in range(10):
            os.rmdir(p + str(i))
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")

    def test_deleteFile(self):
        file = open(path + "/foo.txt", "x")
        file.close()
        time.sleep(1)
        os.remove(path + "/foo.txt")
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")

    def test_deleteFiles(self):
        for i in range(10):
            file = open(path + "/foo" + str(i) + ".txt", "x")
            file.close()
        time.sleep(1)
        for i in range(10):
            os.remove(path + "/foo" + str(i) + ".txt")
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")


class DeleteRecursiveTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global hg
        hg = Homegear("/var/run/homegear/homegearIPC.sock")

        global path
        path = os.getcwd() + "/testingDirectory"
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def tearDownClass(cls):
        os.rmdir(path)

    def setUp(self):
        testFlow = [
            {
                "id": "n1",
                "type": "watch",
                "path": path,
                "recursive": "true",
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
        nodeIds = hg.addNodesToFlow("Watch Unit test", "unit-test", testFlow)

        if not nodeIds:
            raise SystemError('Error =>  Could not create flow.')

        global n1, n2
        n1 = nodeIds["n1"]
        n2 = nodeIds["n2"]

        if not hg.restartFlows():
            raise SystemError("Error => Could not restart flows.")

        while not hg.nodeBlueIsReady():
            time.sleep(1)

    def tearDown(self):
        hg.removeNodesFromFlow("Watch Unit test", "unit-test")
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def test_deleteDirectory(self):
        p = path + "/foo"
        os.mkdir(p)
        time.sleep(1)
        os.rmdir(p)
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")

    def test_deleteDirectories(self):
        p = path + "/foo"
        for i in range(10):
            os.mkdir(p + str(i))
        time.sleep(1)
        for i in range(10):
            os.rmdir(p + str(i))
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")

    def test_deleteDirectoriesRecursive(self):
        p = path + "/foo"
        for i in range(5):
            os.mkdir(p)
            p = p + "/foo"
            time.sleep(1)
        for i in range(5):
            p = p[:-4]
            os.rmdir(p)
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")

    def test_deleteFile(self):
        file = open(path + "/foo.txt", "x")
        file.close()
        time.sleep(1)
        os.remove(path + "/foo.txt")
        time.sleep(1)
        inputHistory = hg.getNodeVariable(n2, "inputHistory0")
        self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
        self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")

    def test_deleteFiles(self):
        for i in range(10):
            file = open(path + "/foo" + str(i) + ".txt", "x")
            file.close()
        time.sleep(1)
        for i in range(10):
            os.remove(path + "/foo" + str(i) + ".txt")
            time.sleep(1)
            inputHistory = hg.getNodeVariable(n2, "inputHistory0")
            self.assertTrue(len(inputHistory) >= 1, f"No message was passed on. Length is {len(inputHistory)}")
            self.assertEqual(inputHistory[0][1]['action'], "Delete", f"Payload is {inputHistory[0][1]['action']}, but should be Delete)")


if __name__ == '__main__':
    unittest.main()
