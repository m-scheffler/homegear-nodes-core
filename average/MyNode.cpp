/* Copyright 2013-2019 Homegear GmbH
 *
 * Homegear is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Homegear is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Homegear.  If not, see <http://www.gnu.org/licenses/>.
 *
 * In addition, as a special exception, the copyright holders give
 * permission to link the code of portions of this program with the
 * OpenSSL library under certain conditions as described in each
 * individual source file, and distribute linked combinations
 * including the two.
 * You must obey the GNU General Public License in all respects
 * for all of the code used other than OpenSSL.  If you modify
 * file(s) with this exception, you may extend this exception to your
 * version of the file(s), but you are not obligated to do so.  If you
 * do not wish to do so, delete this exception statement from your
 * version.  If you delete this exception statement from all source
 * files in the program, then also delete it here.
 */

#include <homegear-base/HelperFunctions/HelperFunctions.h>
#include "MyNode.h"

namespace MyNode {

MyNode::MyNode(const std::string &path, const std::string &type, const std::atomic_bool *frontendConnected)
    : Flows::INode(path, type, frontendConnected) {
}

MyNode::~MyNode() {
  _stopThread = true;
}

bool MyNode::init(const Flows::PNodeInfo &info) {
  try {
    auto settingsIterator = info->info->structValue->find("averageOver");
    if (settingsIterator != info->info->structValue->end()) {
      if (settingsIterator->second->stringValue.compare("time") == 0)
        _type = 0;
      if (settingsIterator->second->stringValue.compare("currentValues") == 0)
        _type = 1;
    }

    settingsIterator = info->info->structValue->find("round");
    if (settingsIterator != info->info->structValue->end()){
      if (settingsIterator->second->stringValue.compare("integer") == 0)
        _inputIsDouble = false;
      if (settingsIterator->second->stringValue.compare("double") == 0)
        _inputIsDouble = true;
    }

    if (_type == 0) {
      settingsIterator = info->info->structValue->find("interval");
      if (settingsIterator != info->info->structValue->end())
        _interval = Flows::Math::getNumber(settingsIterator->second->stringValue) * 1000;

      auto values = getNodeData((const std::string) Flows::NodeInfo().id);
      for (auto value : *values->arrayValue) {
        _timeValues.emplace_back(value->floatValue);
      }
    }
    if (_type == 1) {
      settingsIterator = info->info->structValue->find("deleteAfter");
      if (settingsIterator != info->info->structValue->end())
        _deleteAfter = Flows::Math::getNumber(settingsIterator->second->stringValue) * 1000;

      auto values = getNodeData((const std::string) Flows::NodeInfo().id);
      for (auto value : *values->arrayValue) {
        ValueWithTime val = {.value = value->structValue->extract("value").mapped()->floatValue, .time = Flows::HelperFunctions::getTime()};
        _currentValues.insert_or_assign(value->structValue->extract("node").mapped()->stringValue, val);
      }
    }

    return true;
  }
  catch (const std::exception &ex) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__, ex.what());
  }
  catch (...) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__);
  }
  return false;
}

bool MyNode::start() {
  try {
    std::lock_guard<std::mutex> workerGuard(_workerThreadMutex);
    _stopThread = true;
    if (_workerThread.joinable())
      _workerThread.join();

    _stopThread = false;
    if (_type == 0){
      _workerThread = std::thread(&MyNode::averageOverTime, this);
    }

    return true;
  }
  catch (const std::exception &ex) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__, ex.what());
  }
  catch (...) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__);
  }
  return false;
}

void MyNode::stop() {
  std::lock_guard<std::mutex> workerGuard(_workerThreadMutex);
  switch (_type) {
    case 0:
      if (!_timeValues.empty()) {
        auto values = std::make_shared<Flows::Variable>(Flows::VariableType::tArray);
        values->arrayValue->reserve(_timeValues.size());
        for (auto value : _timeValues) {
          values->arrayValue->emplace_back(std::make_shared<Flows::Variable>(value));
        }
        setNodeData((const std::string) Flows::NodeInfo().id, values);
      }
      break;
    case 1:
      if (!_currentValues.empty()) {
        auto values = std::make_shared<Flows::Variable>(Flows::VariableType::tArray);
        values->arrayValue->reserve(_currentValues.size());
        for (auto element : _currentValues) {
          auto value = std::make_shared<Flows::Variable>(Flows::VariableType::tStruct);
          value->structValue->emplace("node", std::make_shared<Flows::Variable>(element.first));
          value->structValue->emplace("value", std::make_shared<Flows::Variable>(element.second.value));
          values->arrayValue->emplace_back(value);
        }
        setNodeData((const std::string) Flows::NodeInfo().id, values);
      }
      break;
  }

  _stopThread = true;
}

void MyNode::waitForStop() {
  try {
    std::lock_guard<std::mutex> workerGuard(_workerThreadMutex);
    _stopThread = true;
    if (_workerThread.joinable())
      _workerThread.join();
  }
  catch (const std::exception &ex) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__, ex.what());
  }
  catch (...) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__);
  }
}

void MyNode::averageOverTime() {
  int32_t sleepingTime = _interval;
  if (sleepingTime < 1000)
    sleepingTime = 1000;

  int64_t startTime = Flows::HelperFunctions::getTime();
  while (!_stopThread) {
    try {
      if (sleepingTime > 1000 && sleepingTime < 30000) {
        int32_t iterations = sleepingTime / 100;
        for (int32_t j = 0; j < iterations; j++) {
          std::this_thread::sleep_for(std::chrono::milliseconds(100));
          if (_stopThread)
            break;
        }
        if (sleepingTime % 100)
          std::this_thread::sleep_for(
              std::chrono::milliseconds(sleepingTime % 100));

      } else if (sleepingTime >= 30000) {
        int32_t iterations = sleepingTime / 1000;
        for (int32_t j = 0; j < iterations; j++) {
          std::this_thread::sleep_for(std::chrono::milliseconds(1000));
          if (_stopThread)
            break;
        }
        if (sleepingTime % 1000)
          std::this_thread::sleep_for(
              std::chrono::milliseconds(sleepingTime % 1000));
      }
      if (_stopThread)
        break;

      if (!_timeValues.empty()) {
        double average = 0.0;

        {
          std::lock_guard<std::mutex> valuesGuard(_valuesMutex);
          for (auto value : _timeValues) {
            average += value;
          }
          if (!_timeValues.empty()) {
            average /= _timeValues.size();
            _timeValues.clear();
          }
        }

        Flows::PVariable message = std::make_shared<Flows::Variable>(Flows::VariableType::tStruct);
        message->structValue->emplace("payload",std::make_shared<Flows::Variable>(_inputIsDouble ? average : std::lround(average)));
        output(0, message);
      }

      int64_t diff = Flows::HelperFunctions::getTime() - startTime;
      if (diff <= _interval)
        sleepingTime = _interval;

      else
        sleepingTime = _interval - (diff - _interval);

      if (sleepingTime < 1000)
        sleepingTime = 1000;

      startTime = Flows::HelperFunctions::getTime();
    }
    catch (const std::exception &ex) {
      _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__, ex.what());
    }
    catch (...) {
      _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__);
    }
  }
}

void MyNode::averageOverCurrentValues() {
  try {
    if (!_currentValues.empty()) {
      double average = 0.0;
      {
        std::list<std::string> del;
        int64_t time = Flows::HelperFunctions::getTime();
        for (auto value : _currentValues) {
          if ( time - value.second.time >= _deleteAfter)
            del.emplace_back(value.first);
          else
            average += value.second.value;
        }
        for (auto key : del) {
          _currentValues.erase(key);
        }

        if (!_currentValues.empty())
          average /= _currentValues.size();
      }

      Flows::PVariable message = std::make_shared<Flows::Variable>(Flows::VariableType::tStruct);
      message->structValue->emplace("payload",std::make_shared<Flows::Variable>(_inputIsDouble ? average : std::lround(average)));
      output(0, message);
    }
  }
  catch (const std::exception &ex) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__, ex.what());
  }
  catch (...) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__);
  }
}

void MyNode::input(const Flows::PNodeInfo &info,
                   uint32_t index,
                   const Flows::PVariable &message) { //is executed, when a new message arrives
  try {
    Flows::PVariable &input = message->structValue->at("payload");
    Flows::PVariable &nodeId = message->structValue->at("source");

    std::lock_guard<std::mutex> valuesGuard(_valuesMutex);
    if (input->type == Flows::VariableType::tInteger
        || input->type == Flows::VariableType::tInteger64) {
      switch (_type) {
        case 0:
          _timeValues.emplace_back(input->integerValue64);
          break;
        case 1:
          ValueWithTime val = {.value = (double) input->integerValue64, .time = Flows::HelperFunctions::getTime()};
          _currentValues.insert_or_assign(nodeId->stringValue, val);
          averageOverCurrentValues();
          break;
      }
      if (!_inputIsDouble)
        _inputIsDouble = false;
    } else if (input->type == Flows::VariableType::tFloat) {
      switch (_type) {
        case 0:
          _timeValues.emplace_back(input->floatValue);
          break;
        case 1:
          ValueWithTime val = {.value = input->floatValue, .time = Flows::HelperFunctions::getTime()};
          _currentValues.insert_or_assign(nodeId->stringValue, val);
          averageOverCurrentValues();
          break;
      }
    }
  }
  catch (const std::exception &ex) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__, ex.what());
  }
  catch (...) {
    _out->printEx(__FILE__, __LINE__, __PRETTY_FUNCTION__);
  }
}

}

